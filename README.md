# AD

CLI for deploying CTF Attack-Defense competition in the Yandex Cloud with [ForcAD](https://github.com/pomo-mondreganto/ForcAD)

## Requirements

To work with the cloud, you will need cli tool `yc` - [link](https://yandex.cloud/ru/docs/cli/quickstart)

What you need to create in Yandex Cloud:
- Service account and profile for terraform - [link](https://yandex.cloud/ru/docs/tutorials/infrastructure-management/terraform-quickstart#get-credentials)


Install Terraform and the provider for Yandex Cloud  - [link](https://yandex.cloud/ru/docs/tutorials/infrastructure-management/terraform-quickstart#configure-provider)

Install Ansible
````
pip install --upgrade pip
pip install ansible passlib
````

## Usage

The CLI tool `ad.py` should be used to manage the entire infrastructure of the competition

Starting AD:
1. Configure the `config.yml` for the entire infrastructure
2. Run `pip install -r requirements.txt`
3. Run `./ad.py create` for create all infrastructure
4. Run `./ad.py generate-ansible` for generate Ansible inventory file
5. Run `./ad.py ping`  until you get a successful ping (everything must be green)
6. Run `./ad.py provision` for provision all infrastructure
7. Run `./ad.py start-services` for start services on the vulnboxes
8. Run `./ad.py generate-result` for generate readme.txt for teams in `result` folder

For destroying all infrastructure:

1. Run `./ad.py destroy` for delete all resources in Yandex Cloud

## Configuration

ForcAD configuration part see [here](https://github.com/pomo-mondreganto/ForcAD)
 
There is a `config.yml` file to configure the infrastructure
* `cloud` contains cloud setting
    * `subnet_id` - subnet id from Yandex Cloud
    * `dns_zone_id` - dns zone id from Yandex Cloud
    * `cpu` - count of cpu cores
    * `mem` - memory size
    * `disk` - disk size
* `teams` here you need to specify only the names of the teams, the rest will be generated


