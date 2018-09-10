This is Paddle's lambda for updating security groups used for cloudflare access.

The cf-security-group-update.py script is based on one from

   https://github.com/johnmccuk/cloudflare-ip-security-group-update

Written by John McCracken (johnmccuk email at sign gmail dotcom).

updated to the one from

   https://github.com/harvard-lil/cloudflare-ip-security-group-update

Written by Harvard Library Innovation Laboratory (lil email at sign law dot harvard dot edu).


and is licensed under the MIT license - see the file script-license.txt

The test cases are based on ones taken from Ansible and are licenced
under the GPLv3.  Please see the file COPYING.


N.B. Important BUG:

This lambda does not properly clean out security groups of extraneous
rules.  It's possible, for example, to leave in the default rule of a
newly created security group.  It is recommended to either start with
an empty security group or carefully check all the rules after
running.

