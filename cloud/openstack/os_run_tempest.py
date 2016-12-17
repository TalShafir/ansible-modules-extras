#!/usr/bin/python

from ansible.module_utils.basic import *
import os

DOCUMENTATION = '''
---
module: os_run_tempest
short_description: this module runs Tempest (OpenStack)
description:
    - run Tempest according to the configuration file in the workspace given
      and using python virtual environment if given.
    - for more information about Tempest: http://docs.openstack.org/developer/tempest/
author: "Tal Shafir , @TalShafir"
requirements:
    - Tempest(and initialized workspace)
options:
    virtualenv:
        description:
            -path to the virtual environment Tempest is installed at,
            if not provided will be assumed Tempest is installed in /usr/bin
        required: False
        default: ''
    workspace:
        description:
            -the workspace as was configured in 'Tempest init <workspace>'
        required: True
'''


def main():
    module = AnsibleModule(argument_spec={
        "virtualenv": {"type": "path", "required": False, "default": ""},
        "workspace": {"type": "path", "required": True}
    })

    if not module.params['virtualenv']:
        module.fail_json(msg="missing virtualenv")
    if not module.params['workspace']:
        module.fail_json(msg="missing Tempest workspace")

    if module.params['virtualenv']:
        activate_virtual_environment(os.path.abspath(os.path.expanduser(module.params['virtualenv'])))

    if not module.params['workspace']:
        module.fail_json(msg='missing workspace argument')

    command = 'tempest run --workspace ' + module.params['workspace']

    rc, stdout, stderr = module.run_command(command)

    if rc == 0:  # TODO: check if rc!=0 in case of test/s fail or only if there are errors
        module.exit_json(msg='tempest ran successfully', changed=True, stdout=stdout, stderr=stderr)
    else:
        module.fail_json(msg='tempest running failed', changed=True, stdout=stdout, stderr=stderr)


def activate_virtual_environment(environment_path):
    """
        Activate the python virtual environment in the given path
        :param environment_path: A path to the python virtual environment
        :type environment_path: str
        """
    activation_script_suffix = '/bin/activate_this.py'
    activate_venv = environment_path + activation_script_suffix
    execfile(activate_venv, dict(__file__=activate_venv))


if __name__ == '__main__':
    main()
