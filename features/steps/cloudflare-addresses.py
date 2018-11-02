from __future__ import print_function

import subprocess
import sys
from hamcrest import assert_that, has_item


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def call_ansible_step(step_name, playbook="test-system.yml", extra_vars=None):
    """call_ansible_step - run a step by running a matching ansible tag"""

    proc_res = subprocess.run(args=["ansible-playbook", "--list-tags", playbook],
                              capture_output=True)
    if proc_res.returncode > 0:
        eprint("Ansible STDOUT:\n", proc_res.stdout, "Ansible STDERR:\n", proc_res.stderr)
        raise Exception("ansible failed while listing tags")

    lines = [x.lstrip() for x in proc_res.stdout.split(b"\n")]
    steps_lists = [x[10:].rstrip(b"]").lstrip(b"[ ").split(b",") for x in lines if x.startswith(b"TASK TAGS:")]
    steps = [x.lstrip() for y in steps_lists for x in y]
    eprint(b"\n".join([bytes(x) for x in steps]))
    assert_that(steps, has_item(bytes(step_name, 'latin-1')))

    eprint("calling ansible with: ", step_name)
    ansible_args = ["ansible-playbook", "-vvv", "--tags", step_name, playbook]
    if extra_vars is not None:
        ansible_args.extend(["--extra-vars", extra_vars])
    proc_res = subprocess.run(args=ansible_args, capture_output=True)
    eprint("Ansible STDOUT:\n", proc_res.stdout, "Ansible STDERR:\n", proc_res.stderr)
    if proc_res.returncode > 0:
        raise Exception("ansible failed")


@given(u'that I have deployed my updater to update that security group')
@then(u'that security group should be updated with cloudflare IP addresses')
@when(u'I trigger my IP address updater lambda')
@given(u'that I have a security group which is empty')
def step_impl(context):
    call_ansible_step(context.this_step.step_type + " " + context.this_step.name)
    # extra_vars="security_group_name=cloudflare_lambda_demo_sg")
