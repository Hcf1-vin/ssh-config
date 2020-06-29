import boto3
import os
from jinja2 import Environment, FileSystemLoader

def get_user(ami_id):

    response = client.describe_images(
        ImageIds=[ami_id]
    )

    for a in response["Images"]:
        if a["OwnerId"] in ["602401143452","286198878708"]:
            return "ec2-user"
        else:
            return "ubuntu"

def get_hosts():

    instances = []

    response = client.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running',
                ]
            }
        ]
    )
    for a in response["Reservations"]:
        for b in a["Instances"]:
            instance = {}
            if "Platform" not in str(b):
                
                instance["ip"] = b["PrivateIpAddress"]

                instance["key"] = (os.path.expanduser("~")+"/.ssh/" + b["KeyName"] + ".pem")

                instance["user"] = get_user(b["ImageId"])

                if "Tags" in str(b):
                    for c in b["Tags"]:
                        if "Name" in str(c):
                            if c["Key"] == "Name":
                                instance["name"] = c["Value"]
                        
                                instances.append(instance)

    return instances

def render_template(instances):

    file_loader = FileSystemLoader(os.path.join(os.path.dirname(os.path.realpath(__file__)),"templates"))
    env = Environment(loader=file_loader)
    template = env.get_template("config.j2")
    output = template.render(instances=instances)
    return output

def write_conf(conf_content):
    ssh_conf_file = os.path.expanduser("~/.ssh/config") 
    f= open(ssh_conf_file,"w+")
    f.write(conf_content)
    f.close() 

if __name__ == "__main__":
    instance_list = []
    for profile in ['dev','qa','prod']:
        session = boto3.Session(profile_name=profile,region_name='eu-west-1')
        client = session.client('ec2')
        for i in get_hosts():
            instance_list.append(i)
    
    conf_content = render_template(instance_list)
    write_conf(conf_content)    