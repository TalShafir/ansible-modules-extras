#!/usr/bin/python

from ansible.module_utils.basic import *
import os

DOCUMENTATION = '''
---
module: os_run_tempest
short_description: this module runs Tempest(OpenStack)
description:
    - run Tempest according to the configuration file in the workspace given
      and using python virtual environment if given.
author: "Tal Shafir , @TalShafir"
requirements:
    - Tempest(and initialized workspace)
options:
    virtualenv:
        description:
            -path to the virtual environment Tempest is installed at
        required: False
        default: '/usr'
    workspace:
        description:
            -the path of the workspace as was configured in 'Tempest init <workspace>'
        required: True
'''


def main():
    module = AnsibleModule(argument_spec={
        "virtualenv": {"type": "path", "required": False, "default": "/usr"},
        "workspace": {"type": "path", "required": True}
    })

    if not module.params['virtualenv']:
        module.fail_json(msg="missing virtualenv")
    if not module.params['workspace']:
        module.fail_json(msg="missing Tempest workspace")

    if module.params['virtualenv'] != "/usr":
        activate_virtual_environment(module.params['virtualenv'])

    # TODO: check which is better to run tempest, the function or the module.run_command

    tempest_path = os.path.abspath(os.path.expanduser(module.params['virtualenv'] + '/bin/tempest'))

    command = tempest_path + ' run'
    if module.params['workspace']:
        # command += ' --workspace ' + os.path.abspath(os.path.expanduser(module.params['workspace']))
        command += ' --workspace ' + module.params['workspace']
    else:
        module.fail_json(msg='missing workspace argument')

    rc, stdout, stderr = module.run_command(command)

    if rc == 0:  # TODO: check if rc!=0 in case of test/s fail or only if there are errors
        msg = 'tempest ran successfully'
        module.exit_json(msg=msg, changed=True, stdout=stdout, stderr=stderr)

    else:
        msg = 'tempest running failed'
        module.fail_json(msg=msg, changed=True, stdout=stdout, stderr=stderr)


def activate_virtual_environment(enviroment_path):
    activation_script_suffix = '/bin/activate_this.py'
    activate_venv = enviroment_path + activation_script_suffix
    execfile(activate_venv, dict(__file__=activate_venv))


if __name__ == '__main__':
    main()
