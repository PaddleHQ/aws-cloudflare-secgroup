Feature: read IP addresses from cloudflare and update
In order to ensure that cloudflare keeps working properly cloudflare
CDN users would like to ensure that all cloudflare IP addresses are
entered into the security group that they use.

  @wip
  Scenario: fill in security group from empty
    given that I have a security group which is empty
    and that I have deployed my updater to update that security group
    when I trigger my IP address updater lambda
    then that security group should be updated with cloudflare IP addresses