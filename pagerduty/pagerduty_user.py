#! /usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.pagerduty_common import *

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
            # user=dict(required=False, type='str'),
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
            requester_id=dict(required=False, type='str'),
        ),
        supports_check_mode=True
    )

    acc_state = module.params['state']
    email = module.params['email']
    obj_type = 'users'
    update = False

    team_list = []
    if module.params['teams']:
        for t in module.params['teams']:
            team_list.append(t)

    # Get a json blob of remote data
    remote_d = fetchRemoteData(obj_type, module)

    # Create the master list of remote users for easy parsing
    remote_master = createObjectList(obj_type, remote_d)

    # If we don't want the user
    if acc_state == 'absent' and email not in remote_master:
        module.exit_json(changed=False, msg="User not found")
    elif acc_state == 'absent' and len(team_list) > 0 and email in remote_master:
        checkUpdateObj(obj_type, module, remote_d)
        module.exit_json(
            changed=True, msg="removed the user from the listed teams")
    elif acc_state == 'absent' and not module.params['teams'] and email in remote_master:
        deleteObj(obj_type, remote_d, module)
        module.exit_json(changed=True, msg="removed the user from pagerduty")

    if acc_state == 'present' and email not in remote_master:
        createObj(obj_type, module)
        module.exit_json(changed=True, msg="created the user: %s" %
                         (module.params['email']))
    elif acc_state == 'present' and email in remote_master:
        update = checkUpdateObj(obj_type, module, remote_d)
        if update:
            module.exit_json(changed=True,  msg="we updated the user: %s" %
                             (module.params['email']))
        else:
            module.exit_json(changed=False,  msg="no updates detected: %s" %
                             (module.params['email']))


if __name__ == '__main__':
    main()
