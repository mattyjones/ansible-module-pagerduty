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


def setFetchUrl(limit, offset, obj_type):
    if obj_type == 'users':
        return "https://api.pagerduty.com/users?include%5B%5D=contact_methods&include%5B%5D=notification_rules&include%5B%5D=teams&limit=" + str(limit) + "&offset=" + str(offset)  # nopep8
    elif obj_type == 'teams':
        return "https://api.pagerduty.com/teams?limit=" + str(limit) + "&offset=" + str(offset)  # nopep8


def parseResp(response, offset, remote_data, obj_type):
    if obj_type == 'users':
        jData = json.loads(response)
        paged = bool(jData['more'])
        offset = offset + 25
        for u in jData['users']:
            remote_data.append(u)
        return offset, paged, remote_data

    elif obj_type == 'teams':
        jData = json.loads(response)
        paged = bool(jData['more'])
        offset = offset + 25
        for t in jData['teams']:
            remote_data.append(t)
        return offset, paged, remote_data


def fetchRemoteData(obj_type, module):
    remote_data = []
    paged = True  # by default assume results will be paged
    offset = 0  # offset for additional calls
    limit = 25  # number of entities to grab
    timeout = 30

    while (paged == True):  # nopep8
        url = setFetchUrl(limit, offset, obj_type)
        response, info = fetch_url(module, url, method='GET', headers=headers)

        if info['status'] != 200:
            module.fail_json(
                msg="Failed to get remote data: %s." % (info)
            )
        offset, paged, remote_data = parseResp(
            response.read(), offset, remote_data, obj_type)

    return remote_data


def createObjectList(obj_type, data):
    objects = []
    if obj_type == 'users':
        obj_key = 'email'
    elif obj_type == 'teams':
        obj_key = 'name'
    for d in data:
        objects.append(d[obj_key])
    return objects


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


def createTeamObj(module):
    d = {
        "team": {
            "name": module.params['name'],
            "description": module.params['description'],
            "type": "team"
        }
    }
    return d


def createObj(obj_type, module):
    url = 'https://api.pagerduty.com/' + obj_type

    if obj_type == 'users':
        data = createUserObj(module)
    elif obj_type == 'teams':
        data = createTeamObj(module)

    response, info = fetch_url(
        module, url, json.dumps(data), method='POST', headers=headers)
    if info['status'] != 201:
        module.fail_json(msg="API call failed to create object: %s." % (info))

    print(info)


def disableObj(obj_type, remote_d, module):
    url = "https://api.pagerduty.com/" + obj_type + "/"
    if obj_type == 'users':
        obj_key = 'email'
    if obj_type == 'teams':
        obj_key = 'name'

    for u in remote_d:
        if module.params[obj_key] == u[obj_key]:
            url = url + u['id']
            response, info = fetch_url(
                module, url, method='DELETE', headers=headers)
            if info['status'] != 204:
                module.fail_json(
                    msg="API call failed to delete object: %s." % (info))


def updateUsers(remote_d, module, update):
    uid = ''
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
            elif not str(u['description']) == str(module.params['description']):  # nopep8
                update = True
                uid = u['id']
    return update, uid


def updateTeams(remote_d, module, update):
    uid = ''
    for t in remote_d:
        if u['name'] == module.params['name']:
            if not u['name'] == module.params['name']:
                update = True
                uid = u['id']
            elif not str(u['description']) == str(module.params['description']):  # nopep8
                update = True
                uid = u['id']
    return update, uid


def updateObj(obj_type, module, remote_d):
    update = False
    if obj_type == 'users':
        update, uid = updateUsers(remote_d, module, update)
        if update:
            data = createUserObj(module)
    elif obj_type == 'teams':
        update, uid = updateTeams(remote_d, module, update)
        if update:
            data = createTeamObj(module)

    if update:
        # print("I am going to update the object")
        url = "https://api.pagerduty.com/" + obj_type + "/" + uid
        response, info = fetch_url(
            module, url, json.dumps(data), method='PUT', headers=headers)
        if info['status'] != 200:
            module.fail_json(
                msg="API call failed to update object: %s." % (info))
