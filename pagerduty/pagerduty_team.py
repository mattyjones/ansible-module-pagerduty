#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'supported_by': 'community',
    'status': 'preview'
}

DOCUMENTATION = '''
module: pagerduty_team
short_description: Create PagerDuty teams
description:
    - This module will let you manage PagerDuty teams, including CRUD, and adding/removing users

version_added: ""
author:
    - "Matty Jones" (@mattyjones)"
requirements:
    - PagerDuty API access
options:
    state:
        description:
            - Create or destroy a team.
        required: true
        default: null
        choices: [ absent", "present" ]
        aliases: []
    name:
        description:
            - The name of the Pagerduty team.
        required: true
        default: null
        choices: []
        aliases: []
        type: string
    desc:
        description:
            - A description of the team
        required: false
        default: "Managed by Ansible"
        choices: []
        aliases: []
        type:string
    token:
        description:
            - A pagerduty token, generated on the pagerduty site. Should be used instead of
              user/passwd combination.
        required: true
        default: null
        choices: []
        aliases: []
        type: string
    requester_id:
        description:
            - Email of user making the request.
        required: true
        default: null
        choices: []
        aliases: []
        type: string
    user_name:
        description:
            - PagerDuty user ID.
        required: true
        default: null
        choices: []
        aliases: []
        type: string
    passwd:
        description:
            - PagerDuty user password.
        required: true
        default: null
        choices: []
        aliases: []
        type: string
'''

EXAMPLES = '''
- name: Create a new team with a username and password
  pagerduty_team:
    name:      ops
    user_name: example@example.com
    passwd:    password123
    state:     present
    desc:      'traditional operations team'

- name: Create a new team with a token
  pagerduty_team:
    name:  engineering
    token: xxxxxxxxxxxxxx
    state: present
    desc:  'traditional engineering team'

- name: Update a team
  pagerduty_team:
    name:  engineering
    token: xxxxxxxxxxxxxx
    state: present
    desc:  'this team makes life hard'

- name: Delete a team
  pagerduty_team:
    name:  engineering
    token: xxxxxxxxxxxxxx
    state: absent
'''

RETURN = '''
name:
    description: team name
    returned: changed
    type: string
    sample: engineering
id:
    description: the Pagerduty id
    returned: success
    type: string
    sample: PNQ57GY
'''

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
            name=dict(required=True, type='str'),
            token=dict(required=False, type='str'),
            user_name=dict(required=False, type='str'),
            password=dict(required=False, type='str'),
            users=dict(required=False, type='list'),
            requester_id=dict(required=True, type='str'),
        ),
        supports_check_mode=True
    )

    acc_state = module.params['state']
    obj_type = 'teams'
    team_name = module.params['name']

    # Get a json blob of remote data
    remote_d = pd.fetchRemoteData(obj_type, module)

    # Create the master list of remote objects for easy parsing
    remote_master = pd.createObjectList(obj_type, remote_d)

    # If we don't want the team
    if acc_state == 'absent' and team_name in remote_master:
        print("I am deleting the team")
        pd.deleteObj(obj_type, remote_d, module)
    elif acc_state == 'absent' and team_name not in remote_master:
        print("The team is not in the remote list")

    # If we do want the team
    if acc_state == 'present' and team_name not in remote_master:
        print("I am creating the team")
        pd.createObj(obj_type, module)
    elif acc_state == 'present' and team_name in remote_master:
        print("I am going to determine if an update is needed")
        pd.checkUpdateObj(obj_type, module, remote_d)

    module.exit_json(changed=True, result="12345", msg="debugging")


if __name__ == '__main__':
    main()
