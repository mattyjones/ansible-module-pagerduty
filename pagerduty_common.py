#! /usr/bin/python

import json
import os

from ansible.module_utils.urls import fetch_url

PD_TOKEN = os.environ['PD_TOKEN']
machine_user_email = 'urlugal@gmail.com'
headers = {'Accept': 'application/vnd.pagerduty+json;version=2',
           'Authorization': 'Token token=' + PD_TOKEN
           'From': machine_user_email}


def setUrl(limit, offset, obj):
    if obj == 'users':
        return "https://api.pagerduty.com/users?include%5B%5D=contact_methods&include%5B%5D=notification_rules&include%5B%5D=teams&limit=" + str(limit) + "&offset=" + str(offset)  # nopep8
    elif args.teams:
        return "https://api.pagerduty.com/teams?limit=" + str(limit) + "&offset=" + str(offset)  # nopep8


def parseResp(response, offset, remote_data, obj, count):
    if obj == 'users':
        jData = json.loads(response)
        paged = bool(jData['more'])
        offset = offset + 25
        for u in jData['users']:
            count = count + 1
            remote_data.append(u)
        return offset, paged, remote_data, count

    elif obj == 'teams':
        jData = json.loads(response)
        paged = bool(jData['more'])
        offset = offset + 25
        for u in jData['teams']:
            remote_data.append(json.dumps(u))


def fetchRemoteData(obj, module, remote_data, count):

    paged = True  # by default assume results will be paged
    offset = 0  # offset for additional calls
    limit = 25  # number of entities to grab
    timeout = 30

    while (paged == True):  # nopep8
        url = setUrl(limit, offset, obj)
        response, info = fetch_url(module, url, method='GET', headers=headers)

        if info['status'] != 200:
            module.fail_json(
                msg="Failed to get remote data: %s." % (info)
            )
        offset, paged, remote_data, count = parseResp(
            response.read(), offset, remote_data, obj, count)

    # print(count)
    return remote_data


def createUserList(data):
    users = []
    for u in data:
        users.append(u['email'])
    return users


def createDisabledList(data):
    users = []
    for u in data:
        if u['status'] == 'disabled':
            users.append(u['email'])
    return users


def createUser(obj, l_list, r_list, module):
    users = []
    url = 'https://api.pagerduty.com/' + obj
    for l in l_list:
        if l not in r_list:
            users.append(l)
            l_list.remove(l)

    if len(users) > 0:
        for u in users:

            # acc_status = module.params['acc_status']
            # acc_type = module.params['acc_type']
            # description = module.params['description']
            # email = module.params['email']
            # name = module.params['name']
            # role = module.params['role']
            # timezone = module.params['timezone']

    data = {
        "user": {
            "type": "user",
            "name": module.params['name'],
            "email": module.params['email'],
            "time_zone": module.params['timezone'],
            "role": module.params['role'],
            "description": "Managed by Ansible"
        }
    }

    response, info = fetch_url(
        module, url, method='POST', data, headers=headers)


def disableUser(obj, d_list, l_list, r_data, module):
    ids = []
    url = "https://api.pagerduty.com/" + obj + "/"
    for u in d_list:
        for d in r_data:
            if u == d['email']:
                ids.append(d['id'])
                d_list.remove(u)
                l_list.remove(u)
        d_list.remove(u)
        l_list.remove(u)

    if len(ids) > 0:
        for i in ids:
            url = url + i
            response, info = fetch_url(
                module, url, method='DELETE', headers=headers)
            if info['status'] != 204:
                module.fail_json(
                    msg="API call failed to delete object: %s." % (info)
                )

    if len(d_list) > 0:
        module.fail_json(msg="Object failed to be deleted")
    return l_list


def detectKeyChanges(remote_d, local_d, obj):
    update_objs = []
    key_count = 0
    for l in local_d[obj]:
        for r in remote_d:
            l_keys = l.keys()
            r_keys = r.keys()
        for k in l_keys:
            if k != 'status':
                if k in r_keys:
                    detectValueChanges

                if k not in r_keys:
                    update_objs.append(k)

    return update_objs


def detectValueChanges(remote_d, local_d):
    print("this is a placeholder and will not be fun to code")

# Generate a list of disabled objects to be removed from the remote instance


def objStatus(local_d):
    disabled_objs = []
    for o in local_d['users']:
        if o['status'] == 'disabled':
            disabled_objs.append(o['email'])
    return disabled_objs
