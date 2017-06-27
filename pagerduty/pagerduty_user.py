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
            avatar_url=dict(
                required=False, default='https://static.comicvine.com/uploads/scale_small/0/77/236205-57083-alfred-e-neuman.jpg',  # nopep8
                type='str'),
            color=dict(required=False, default='green', type='str'),
            description=dict(default='Managed by Ansible',
                             required=False, type='str'),
            email=dict(required=True, type='str'),
            job_title=dict(required=False, default='', type='str'),
            name=dict(required=True, type='str'),
            role=dict(required=False, default='limited_user', type='str', choices=[  # nopep8
                      'admin', 'limited_user', 'owner', 'read_only_user', 'user']),  # nopep8
            teams=dict(required=False, type='list'),
            time_zone=dict(required=False, default='Etc/UTC', type='str'),
        ),
        supports_check_mode=True
    )

    acc_status = module.params['acc_status']
    email = module.params['email']
    obj_type = 'users'

    # Get a json blob of remote data
    remote_d = pd.fetchRemoteData(obj_type, module)

    # Create the master list of remote users for easy parsing
    remote_master = pd.createObjectList(obj_type, remote_d)

    if acc_status == 'absent' and email in remote_master:
        print("I am disabling a user")
        pd.disableObj(obj_type, remote_d, module)
    # elif acc_status == 'absent' and email not in remote_master:
        print("The user is not in the remote list")
    elif acc_status == 'present' and email not in remote_master:
        print("I am creating a user")
        pd.createObj(obj_type, module)
    elif acc_status == 'present' and email in remote_master:
        print("I am going to determine if an update is needed")
        pd.updateObj(obj_type, module, remote_d)
    else:
        print("I am lost and have no idea what you want me to do")

    module.exit_json(changed=True, result="12345", msg="debugging")


if __name__ == '__main__':
    main()
