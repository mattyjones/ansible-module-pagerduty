#! /usr/bin/python


from ansible.module_utils.basic import AnsibleModule
import pagerduty_common as pd


try:
    import json
except ImportError:
    import simplejson as json

remote_user_data = []


def main():
    module = AnsibleModule(
        argument_spec=dict(
            acc_status=dict(required=True),
            acc_type=dict(required=False, default='user'),
            description=dict(default='Managed by Ansible', required=False),
            email=dict(required=True),
            name=dict(required=True),
            role=dict(required=False, default='limited_user'),
            time_zone=dict(required=False, default='Etc/UTC'),
        ),
        supports_check_mode=True
    )

    acc_status = module.params['acc_status']
    acc_type = module.params['acc_type']
    description = module.params['description']
    email = module.params['email']
    name = module.params['name']
    role = module.params['role']
    time_zone = module.params['time_zone']

    obj = 'users'

    # Get a json blob of remote users
    remote_d = pd.fetchRemoteData(obj, module, remote_user_data)

    # Create the master list of remote users for easy parsing
    remote_master = pd.createUserList(remote_d)

    if acc_status == 'disabled' and email in remote_master:
        print("I am disabling a user")
        pd.disableObj(obj, remote_d, module)
    elif acc_status == 'disabled' and email not in remote_master:
        print("The user is not in the remote list")
    elif acc_status == 'active' and email not in remote_master:
        print("I am creating a user")
        pd.createObj(obj, module)
    elif acc_status == 'active' and email in remote_master:
        print("I am going to try an update")
        pd.updateObj(obj, module, remote_d)
    else:
        print("I am lost and have no idea what you want me to do")

    module.exit_json(changed=True, result="12345", msg="debugging")


if __name__ == '__main__':
    main()
