#! /usr/bin/python

import json
import os

from ansible.module_utils.urls import fetch_url

PD_TOKEN = os.environ['PD_TOKEN']
headers = {'Accept': 'application/vnd.pagerduty+json;version=2',
           'Authorization': 'Token token=' + PD_TOKEN}


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
