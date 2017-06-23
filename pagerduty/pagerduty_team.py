#! /usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import pagerduty_common as pd

try:
    import json
except ImportError:
    import simplejson as json


def main():
    module = AnsibleModule(
        argument_spec=dict(
            acc_status=dict(required=True, type='str',
                            choices=['present', 'absent']),
            description=dict(default='Managed by Ansible',
                             required=False, type='str'),
            name=dict(required=True, type='str'),
        ),
        supports_check_mode=True
    )

    acc_status = module.params['acc_status']
    obj_type = 'teams'
    name = module.params['name']

    # Get a json blob of remote data
    remote_d = pd.fetchRemoteData(obj_type, module)

    # for d in remote_d:
    #     print(d)

    # Create the master list of remote objects for easy parsing
    remote_master = pd.createObjectList(obj_type, remote_d)

    if acc_status == 'absent' and name in remote_master:
        print("I am disabling the team")
        pd.disableObj(obj_type, remote_d, module)
    elif acc_status == 'absent' and name not in remote_master:
        print("The team is not in the remote list")
    elif acc_status == 'present' and name not in remote_master:
        print("I am creating the team")
        pd.createObj(obj_type, module)
    elif acc_status == 'present' and name in remote_master:
        print("I am going to determine if an update is needed")
        pd.updateObj(obj_type, module, remote_d)
    else:
        print("I am lost and have no idea what you want me to do")

    module.exit_json(changed=True, result="12345", msg="debugging")


if __name__ == '__main__':
    main()
