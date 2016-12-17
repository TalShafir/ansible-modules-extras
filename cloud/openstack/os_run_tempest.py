#!/usr/bin/python

from ansible.module_utils.basic import *
import os
from cStringIO import StringIO

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

    try:
        import tempest.cmd.main
    except ImportError as e:
        module.fail_json(msg="failed to import os_testr.subunit2html", error=str(e))

    # save the original stdout and stderr
    _stdout, _stderr = sys.stdout, sys.stderr

    # replace stdout and stderr
    sys.stdout, sys.stderr = StringIO(), StringIO()

    # run tempest
    try:
        rc = tempest.cmd.main.main(['run', '--workspace', module.params['workspace']])
    except:
        rc = 1

    # save tempest's stdout and stderr
    tempest_stdout, tempest_stderr = sys.stdout, sys.stderr

    # restore the original stdout and stderr
    sys.stdout, sys.stderr = _stdout, _stderr

    if rc == 0:
        module.exit_json(out=tempest_stdout.getvalue(), err=tempest_stderr.getvalue())
    else:
        module.fail_json(msg="Tempest running has failed", out=tempest_stdout.getvalue(),
                         err=tempest_stderr.getvalue())


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
