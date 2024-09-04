FROM python:3.11

RUN apt-get update && \
    apt-get install -y openvpn iptables git

RUN git clone https://github.com/pomo-mondreganto/ad_net_control.git

COPY network/* ./
COPY vpns/jury/* ./
COPY vpns/team/* ./
COPY vpns/vuln/* ./


CMD for conf in $(ls *.conf); do \
        openvpn --config "$conf" --daemon; \
    done && \
    tail -f /dev/null
