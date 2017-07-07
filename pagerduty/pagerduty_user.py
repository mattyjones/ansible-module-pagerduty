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
            state=dict(required=True, type='str',
                       choices=['present', 'absent']),
            desc=dict(default='Managed by Ansible',
                      required=False, type='str'),
            token=dict(required=False, type='str'),
            user_name=dict(required=False, type='str'),
            password=dict(required=False, type='str'),
            users=dict(required=False, type='list'),
            avatar_url=dict(
                required=False, default='https://static.comicvine.com/uploads/scale_small/0/77/236205-57083-alfred-e-neuman.jpg',  # nopep8
                type='str'),
            color=dict(required=False, default='green', type='str'),
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

    acc_state = module.params['state']
    email = module.params['email']
    obj_type = 'users'

    # Get a json blob of remote data
    remote_d = pd.fetchRemoteData(obj_type, module)

    # Create the master list of remote users for easy parsing
    remote_master = pd.createObjectList(obj_type, remote_d)

    if acc_state == 'absent' and email not in remote_master:
        print("The user does not exist remotely")
    elif acc_state == 'absent' and module.params['teams'] and email in remote_master:
        print("I am removing a user from the teams in the list")
        pd.checkUpdateObj(obj_type, remote_d, module)
    elif acc_state == 'absent' and not module.params['teams'] and email in remote_master:
        print("I am deleting a user")
        pd.deleteObj(obj_type, remote_d, module)

    if acc_state == 'present' and email not in remote_master:
        print("I am creating a user")
        pd.createObj(obj_type, module)
    elif acc_state == 'present' and email in remote_master:
        print("I am going to determine if an update is needed")
        pd.checkUpdateObj(obj_type, module, remote_d)

    module.exit_json(changed=True, result="12345", msg="debugging")


if __name__ == '__main__':
    main()
