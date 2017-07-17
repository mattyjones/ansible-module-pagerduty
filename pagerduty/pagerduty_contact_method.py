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
            summary=dict(default='Managed by Ansible',
                         required=False, type='str'),
            token=dict(required=False, type='str'),
            user_name=dict(required=False, type='str'),
            password=dict(required=False, type='str'),
            email=dict(required=True, type='str'),
            address=dict(required=True, type='str'),
            type=dict(required=True, type='str', choices=[
                      'email_contact_method', 'phone_contact_method', 'push_notification_contact_method', 'sms_contact_method']),
            label=dict(required=True, type='str'),
        ),
        supports_check_mode=True
    )

    acc_state = module.params['state']
    email = module.params['email']
    obj_type = 'contact_method'
    update = False

    # Get a json blob of remote data
    remote_d = fetchRemoteData('users', module)

    # Create the master list of remote users for easy parsing
    remote_master = createObjectList('users', remote_d)

    # If we don't want the contact_method
    if acc_state == 'absent' and email not in remote_master:
        module.exit_json(changed=False, msg="User not found")

    elif acc_state == 'absent' and email in remote_master:
        delete_obj = deleteObj(obj_type, remote_d, module)
        if delete_obj:
            module.exit_json(
                changed=True, msg="removed the contact method from %s" % (
                    module.params['email']))
        else:
            module.exit_json(changed=False,  msg="contact method not detected for %s" %
                             (module.params['email']))

    if acc_state == 'present' and email not in remote_master:
        module.exit_json(changed=False, msg="the user %s must be created first" %
                         (module.params['email']))
    elif acc_state == 'present' and email in remote_master:
        update = checkUpdateObj(obj_type, module, remote_d)
        if update:
            module.exit_json(changed=True,  msg="we updated %s's contact methods" %
                             (module.params['email']))
        else:
            module.exit_json(changed=False,  msg="no updated contact methods detected for %s" %
                             (module.params['email']))


if __name__ == '__main__':
    main()
