import boto3
import getopt
import requests
import sys

# boto3    - The AWS SDK for Python
# getopt   - Helps scripts to parse the args in sys.argv
# requests - Python HTTP for Humans
# sys      - Provides access to variables used by the interpreter

# define global variables
sg_id = ""
profile = "default" # Still need to add in functionality to use other AWS profiles
port = 22 # setting default as 22
protocol = "tcp" # Hard coding tcp as default protocol

    # Create a function to get current PUBLIC IP, returns correctly formated CIDR
def get_current_ip():
    """Returns your current IP in correct CIDR format for AWS"""
    global current_ip
    r = requests.get(r'http://jsonip.com')
    ip = r.json()['ip']
    current_ip = ip + '/32'

def add_ip(client, current_ip):
    """Add current IP to the security group"""
    global sg_id
    global port
    global protocol

    # execute security group ingress Boto3 commands
    # TODO: Add in try for graceful error handling
    response = client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpProtocol=protocol,
        FromPort=port,
        ToPort=port,
        CidrIp=current_ip
    )
    print response

# Define the usage of the app
def usage():
    """Prints usage information"""
    print
    print "AWS Security Group IP Updater"
    print
    print "Usage: FILENAMEHERE.py -s sg_id -p profile_from_aws_config"
    print " NOTE: This does require the AWSCLI be installed and configured"
    print "-h --help                 - this message"
    print "-s --sg_id                - id of the security group"
    print "-f --profile              - profile name to use from AWSCLI config"
    print "-p --port                 - port for rule"
    print "-t --protocol             - networking protcal for the rule"
    print
    print
    print "Examples:"
    print "aws-sg-ip-updater.py --sg_id sg-d07a2ca8"
    print "aws-sg-ip-updater.py --sg_id sg-d07a2ca8 --port 22 --protocol tcp"
    print
    sys.exit(0)

def main():
    global sg_id
    global profile
    global port
    global profile
    global protocol

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:f:p:t:",
                                   ["help", "sg_id=", "profile=", "port=", "protocol="])
    except getopt.GetoptError as err:
        # print error and help information
        print str(err) # will print something like "option -q not recognized"
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-s", "--sg_id"):
            sg_id = a
        elif o in ("-f", "--profile"):
            profile = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-t", "--protocol"):
            protocol = a
        else:
            assert False, "Unhandled Option"

    session = boto3.Session(profile_name=profile)
    # Any clients created from this session will use credentials
    # from the [dev] section of ~/.aws/credentials.
    # setup client for ec2
    client = session.client("ec2")

    # get current public ip
    get_current_ip()
    # add current ip to the security group
    add_ip(client, current_ip)

if __name__ == "__main__":
    main()
