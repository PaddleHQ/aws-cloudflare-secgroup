import os
import boto3
from botocore.vendored import requests


def get_cloudflare_ip_list():
    """ Call the CloudFlare API and return a list of IPs """
    response = requests.get('https://api.cloudflare.com/client/v4/ips')
    temp = response.json()
    if 'result' in temp:
        return temp['result']
    raise Exception("Cloudflare response error")


def get_aws_security_group(group_id):
    """ Return the defined Security Group """
    ec2 = boto3.resource('ec2')
    group = ec2.SecurityGroup(group_id)
    if group.group_id == group_id:
        return group
    raise Exception('Failed to retrieve Security Group')


def check_ipv4_rule_exists(rules, address, port):
    """ Check if the rule currently exists """
    for rule in rules:
        for ip_range in rule['IpRanges']:
            try:
                if ip_range['CidrIp'] == address and rule['FromPort'] == port:
                    print("ip range already exists", ip_range)
                    return True
            except KeyError:
                pass
    return False


def add_ipv4_rule(group, address, port):
    """ Add the IP address/port to the security group """
    group.authorize_ingress(IpProtocol="tcp",
                            CidrIp=address,
                            FromPort=port,
                            ToPort=port)
    print("Added %s : %i  " % (address, port))


def delete_ipv4_rule(group, address, port):
    """ Remove the IP address/port from the security group """
    group.revoke_ingress(IpProtocol="tcp",
                         CidrIp=address,
                         FromPort=port,
                         ToPort=port)
    print("Removed %s : %i  " % (address, port))


def check_ipv6_rule_exists(rules, address, port):
    """ Check if the rule currently exists """
    for rule in rules:
        for ip_range in rule['Ipv6Ranges']:
            try:
                if ip_range['CidrIpv6'] == address and rule['FromPort'] == port:
                    print("ip range already exists", ip_range)
                    return True
            except KeyError:
                pass
    return False


def add_ipv6_rule(group, address, port):
    """ Add the IP address/port to the security group """
    group.authorize_ingress(IpPermissions=[{
        'IpProtocol': "tcp",
        'FromPort': port,
        'ToPort': port,
        'Ipv6Ranges': [
            {
                'CidrIpv6': address
            },
        ]
    }])
    print("Added %s : %i  " % (address, port))


def delete_ipv6_rule(group, address, port):
    """ Remove the IP address/port from the security group """
    group.revoke_ingress(IpPermissions=[{
        'IpProtocol': "tcp",
        'FromPort': port,
        'ToPort': port,
        'Ipv6Ranges': [
            {
                'CidrIpv6': address
            },
        ]
    }])
    print("Removed %s : %i  " % (address, port))


def delete_port_completely(group, to_port, from_port):
    """ Remove the IP address/port from the security group """
    group.revoke_ingress(IpProtocol="tcp",
                         ToPort=to_port,
                         FromPort=from_port)
    print("Removed rules to port %i from port %i " % (to_port, from_port))


# BUG - this revoke_ingress seems to be ignored!!!!!
def delete_protocol_completely(group, protocol):
    """ Remove the IP address/port from the security group """
    group.revoke_ingress(IpPermissions=[{'IpProtocol': protocol}])
    print("Removed rules for protocol : %s  " % (protocol))


def lambda_handler(event, context):
    """ AWS Lambda main function """
    ports = [int(x) for x in os.environ['PORTS_LIST'].split(",")]
    if not ports:
        ports = [80]

    security_group = get_aws_security_group(os.environ['SECURITY_GROUP_ID'])
    current_rules = security_group.ip_permissions
    ip_addresses = get_cloudflare_ip_list()

    print("IP CIDRs from cloudflare: ", str(ip_addresses))
    print("ports: ", str(ports))

    # IPv4 - add new addresses
    for ipv4_cidr in ip_addresses['ipv4_cidrs']:
        for port in ports:
            if not check_ipv4_rule_exists(current_rules, ipv4_cidr, port):
                add_ipv4_rule(security_group, ipv4_cidr, port)

    # remove old addresses
    for port in ports:
        for rule in current_rules:
            # is it necessary/correct to check both From and To?
            try:
                if rule['FromPort'] != port or rule['ToPort'] != port:
                    continue
            except KeyError:
                continue
            for ip_range in rule['IpRanges']:
                if ip_range['CidrIp'] not in ip_addresses['ipv4_cidrs']:
                    delete_ipv4_rule(security_group, ip_range['CidrIp'], port)

    # IPv6 -- because of boto3 syntax, this has to be separate
    # add new addresses
    for ipv6_cidr in ip_addresses['ipv6_cidrs']:
        for port in ports:
            if not check_ipv6_rule_exists(current_rules, ipv6_cidr, port):
                add_ipv6_rule(security_group, ipv6_cidr, port)

    # remove old addresses
    for port in ports:
        for rule in current_rules:
            for ip_range in rule['Ipv6Ranges']:
                try:
                    if ip_range['CidrIpv6'] not in ip_addresses['ipv6_cidrs'] and port == ip_range['FromPort']:
                        delete_ipv6_rule(security_group, ip_range['CidrIpv6'], port)
                except KeyError:
                    pass

    # remove extraneous rules
    for rule in current_rules:
        if rule['IpProtocol'] != 'tcp':
            delete_protocol_completely(security_group, rule['IpProtocol'])
            continue
        try:
            if rule['ToPort'] in ports and rule['FromPort'] == rule['ToPort']:
                continue
        except KeyError:
            continue
        delete_port_completely(security_group, rule['ToPort'], rule['FromPort'])


def main():
    print("calling lambda_handler with empty event")
    lambda_handler(None, None)
    print("finished calling lambda_handler")


if __name__ == '__main__':
    main()
