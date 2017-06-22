#! /usr/bin/python

import json
import os

from ansible.module_utils.urls import fetch_url

PD_TOKEN = os.environ['PD_TOKEN']
machine_user_email = 'urlugal@gmail.com'
headers = {'Accept': 'application/vnd.pagerduty+json;version=2',
           'Content-Type': 'application/json',
           'Authorization': 'Token token=' + PD_TOKEN,
           'From': machine_user_email}


def setFetchUrl(limit, offset, obj):
    if obj == 'users':
        return "https://api.pagerduty.com/users?include%5B%5D=contact_methods&include%5B%5D=notification_rules&include%5B%5D=teams&limit=" + str(limit) + "&offset=" + str(offset)  # nopep8
    elif args.teams:
        return "https://api.pagerduty.com/teams?limit=" + str(limit) + "&offset=" + str(offset)  # nopep8


def parseResp(response, offset, remote_data, obj):
    if obj == 'users':
        jData = json.loads(response)
        paged = bool(jData['more'])
        offset = offset + 25
        for u in jData['users']:
            remote_data.append(u)
        return offset, paged, remote_data

    elif obj == 'teams':
        jData = json.loads(response)
        paged = bool(jData['more'])
        offset = offset + 25
        for u in jData['teams']:
            remote_data.append(json.dumps(u))


def fetchRemoteData(obj, module, remote_data):
    paged = True  # by default assume results will be paged
    offset = 0  # offset for additional calls
    limit = 25  # number of entities to grab
    timeout = 30

    while (paged == True):  # nopep8
        url = setFetchUrl(limit, offset, obj)
        response, info = fetch_url(module, url, method='GET', headers=headers)

        if info['status'] != 200:
            module.fail_json(
                msg="Failed to get remote data: %s." % (info)
            )
        offset, paged, remote_data = parseResp(
            response.read(), offset, remote_data, obj)

    return remote_data


def createUserList(data):
    users = []
    for u in data:
        users.append(u['email'])
    return users


def createUserObj(module):
    d = {
        "user": {
            "name": module.params['name'],
            "email": module.params['email'],
            "role": module.params['role'],
            "time_zone": module.params['time_zone'],
            "description": module.params['description'],
            "type": "user"
        }
    }
    return d


def createObj(obj, module):
    url = 'https://api.pagerduty.com/' + obj

    if obj == 'users':
        data = createUserObj(module)

    response, info = fetch_url(
        module, url, json.dumps(data), method='POST', headers=headers)
    if info['status'] != 201:
        module.fail_json(msg="API call failed to create object: %s." % (info))

    print(info)


def disableObj(obj, remote_d, module):
    url = "https://api.pagerduty.com/" + obj + "/"
    for u in remote_d:
        if module.params['email'] == u['email']:
            url = url + u['id']
            response, info = fetch_url(
                module, url, method='DELETE', headers=headers)
            if info['status'] != 204:
                module.fail_json(
                    msg="API call failed to delete object: %s." % (info))


def updateObj(obj, module, remote_d):
    update = False
    for u in remote_d:
        if u['email'] == module.params['email']:
            if not u['name'] == module.params['name']:
                update = True
                uid = u['id']
            elif not u['role'] == module.params['role']:
                update = True
                uid = u['id']
            elif not str(u['time_zone']) == str(module.params['time_zone']):
                update = True
                uid = u['id']
                print("this is the local: " + str(u['time_zone']) +
                      " and this is the remote: " + str(module.params['time_zone']))
            elif not str(u['description']) == str(module.params['description']):  # nopep8
                update = True
                uid = u['id']
                print("this is the local: " + str(u['description']) +
                      " and this is the remote: " + str(module.params['description']))

    if update:
        print("I am going to update a user")
        data = createUserObj(module)
        url = "https://api.pagerduty.com/" + obj + "/" + uid
        response, info = fetch_url(
            module, url, json.dumps(data), method='PUT', headers=headers)
        if info['status'] != 200:
            module.fail_json(
                msg="API call failed to update object: %s." % (info))
