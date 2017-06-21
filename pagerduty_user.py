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
            timezone=dict(required=False, default='UTC'),
        ),
        supports_check_mode=True
    )

    acc_status = module.params['acc_status']
    acc_type = module.params['acc_type']
    description = module.params['description']
    email = module.params['email']
    name = module.params['name']
    role = module.params['role']
    timezone = module.params['timezone']

    count = 0
    obj = 'users'

    # Get a json blob or remote users
    remote_d = pd.fetchRemoteData(obj, module, remote_user_data, count)

    # get the local user data
    with open('test.json') as json_data:
        local_d = json.load(json_data)
        json_data.close()

    # Generate a list of user to remove remotely if needed
    removal_list = pd.objStatus(local_d)

    # Generate a list of objects that need to be updated
    updates_needed = pd.detectKeyChanges(remote_d, local_d, obj)

    module.exit_json(changed=True, result="12345", msg=remote_d)
    # if matty != 'foo':
    #     module.exit_json(changed=True, result="12345", msg="good job")
    # else:
    #     module.fail_json(msg="Something fatal happened", result='go away')


# 1. pull the current list of user with their attributes
# 2. get the list of local users that we want to affect
# 3. compile a list of users that will need to be created or updated


if __name__ == '__main__':
    main()
