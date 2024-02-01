import subprocess

from OpenSSL import crypto


def strip_zeros(formatted_num):
    return formatted_num.lstrip('0').zfill(1)


def make_key_pair(algorithm=crypto.TYPE_RSA, num_bits=2048):
    pkey = crypto.PKey()
    pkey.generate_key(algorithm, num_bits)
    return pkey


def make_csr(pkey, CN, email=None, hash_algorithm='sha256WithRSAEncryption'):
    req = crypto.X509Req()
    subj = req.get_subject()

    subj.CN = CN

    if email:
        subj.emailAddress = email

    req.set_pubkey(pkey)
    # noinspection PyTypeChecker
    req.sign(pkey, hash_algorithm)
    return req


def create_ca(CN, hash_algorithm='sha256WithRSAEncryption', *args):
    ca_key = make_key_pair()
    ca_req = make_csr(ca_key, CN=CN, *args)
    ca_cert = crypto.X509()
    ca_cert.set_serial_number(0)
    ca_cert.gmtime_adj_notBefore(0)
    ca_cert.gmtime_adj_notAfter(60 * 60 * 24 * 365 * 10)  # 10 years
    ca_cert.set_issuer(ca_req.get_subject())
    ca_cert.set_subject(ca_req.get_subject())
    ca_cert.set_pubkey(ca_req.get_pubkey())
    ca_cert.set_version(2)

    ca_cert.add_extensions([
        crypto.X509Extension(b'basicConstraints', True, b'CA:TRUE'),
        crypto.X509Extension(b'subjectKeyIdentifier', False, b'hash', subject=ca_cert)
    ])

    ca_cert.add_extensions([
        crypto.X509Extension(
            b'authorityKeyIdentifier',
            False, b'issuer:always, keyid:always',
            issuer=ca_cert,
            subject=ca_cert,
        )
    ])

    # noinspection PyTypeChecker
    ca_cert.sign(ca_key, hash_algorithm)
    return ca_cert, ca_key


def create_slave_certificate(csr, ca_key, ca_cert, serial, is_server=False, hash_algorithm='sha256WithRSAEncryption'):
    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(60 * 60 * 24 * 365 * 10)  # 10 years
    cert.set_issuer(ca_cert.get_subject())
    cert.set_subject(csr.get_subject())
    cert.set_pubkey(csr.get_pubkey())
    cert.set_version(2)

    extensions = [
        crypto.X509Extension(b'basicConstraints', False, b'CA:FALSE'),
        crypto.X509Extension(b'subjectKeyIdentifier', False, b'hash', subject=cert),
        crypto.X509Extension(
            b'authorityKeyIdentifier',
            False, b'keyid:always,issuer:always',
            subject=ca_cert,
            issuer=ca_cert,
        ),
    ]

    if is_server:
        extensions.extend([
            crypto.X509Extension(b'keyUsage', False, b'digitalSignature,keyEncipherment'),
            crypto.X509Extension(b'extendedKeyUsage', False, b'serverAuth'),
        ])

    cert.add_extensions(extensions)
    # noinspection PyTypeChecker
    cert.sign(ca_key, hash_algorithm)

    return cert


def dump_file_in_mem(material, file_format=crypto.FILETYPE_PEM):
    if isinstance(material, crypto.X509):
        dump_func = crypto.dump_certificate
    elif isinstance(material, crypto.PKey):
        dump_func = crypto.dump_privatekey
    elif isinstance(material, crypto.X509Req):
        dump_func = crypto.dump_certificate_request
    else:
        raise Exception(f"Invalid file_format: {type(material)} {material}")

    return dump_func(file_format, material)


def load_file(path, obj_type, file_format=crypto.FILETYPE_PEM):
    if obj_type is crypto.X509:
        load_func = crypto.load_certificate
    elif obj_type is crypto.X509Req:
        load_func = crypto.load_certificate_request
    elif obj_type is crypto.PKey:
        load_func = crypto.load_privatekey
    else:
        raise Exception(f"Unsupported material type: {obj_type}")

    with open(path, 'r') as fp:
        buf = fp.read()

    material = load_func(file_format, buf)
    return material


def load_key_file(path):
    return load_file(path, crypto.PKey)


def load_csr_file(path):
    return load_file(path, crypto.X509Req)


def load_cert_file(path):
    return load_file(path, crypto.X509)


def get_dhparam():
    dhparam_url = 'https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem'
    p = subprocess.Popen(['curl', dhparam_url], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, _ = p.communicate()
    return stdout.decode().strip('\n')


def generate_static_key():
    p = subprocess.Popen(
        ['openvpn', '--genkey', '--secret', '/dev/stdout'],
        stdout=subprocess.PIPE,
    )
    stdout, _ = p.communicate()
    return stdout.decode().strip('\n')


def dump_object(obj, path):
    with open(path, 'w') as f:
        f.write(dump_file_in_mem(obj).decode())


def generate_subnet_certs(ca_cert, ca_key, client_name, serial, is_server):
    key = make_key_pair()
    csr = make_csr(key, client_name)
    cert = create_slave_certificate(csr, ca_key, ca_cert, serial, is_server=is_server)

    key = dump_file_in_mem(key).decode().strip('\n')
    cert = dump_file_in_mem(cert).decode().strip('\n')

    return cert, key
