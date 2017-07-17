#! /usr/bin/python

import json
import os
import re

from ansible.module_utils.urls import fetch_url


def setHeaders(module, obj_type):
    auth_method = setAuth(module)
    PD_TOKEN = ''
    if auth_method == 'basic':
        # do something with username ands password
        # TODO
        print('basic auth gives me nightmares')
    elif auth_method == 'token':
        PD_TOKEN = module.params['token']
    elif auth_method == 'env':
        PD_TOKEN = os.environ['PD_TOKEN']

    if obj_type == 'teams':
        headers = {'Accept': 'application/vnd.pagerduty+json;version=2',
                   'Content-Type': 'application/json',
                   'Authorization': 'Token token=' + PD_TOKEN,
                   'From': module.params['requester_id']}
    else:
        headers = {'Accept': 'application/vnd.pagerduty+json;version=2',
                   'Content-Type': 'application/json',
                   'Authorization': 'Token token=' + PD_TOKEN}
    return headers


def setAuth(module):
    if module.params['user_name'] and module.params['password']:
        return 'basic'
    elif module.params['token']:
        return 'token'
    elif os.environ['PD_TOKEN'] != '':
        return 'env'
    else:
        return 'null'


def setFetchUrl(limit, offset, obj_type):
    if obj_type == 'users':
        return "https://api.pagerduty.com/users?include%5B%5D=contact_methods&include%5B%5D=notification_rules&include%5B%5D=teams&limit=" + str(limit) + "&offset=" + str(offset)  # nopep8
    elif obj_type == 'teams':
        return "https://api.pagerduty.com/teams?limit=" + str(limit) + "&offset=" + str(offset)  # nopep8


def setUpdateUrl(uid, tid):
    return 'https://api.pagerduty.com/teams/' + tid + '/users/' + uid


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
        response, info = fetch_url(
            module, url, method='GET', headers=setHeaders(module, obj_type))

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
            "description": module.params['desc'],
            "teams": module.params['teams'],
            "type": "user"
        }
    }
    return d


def createTeamObj(module):
    d = {
        "team": {
            "name": module.params['name'],
            "description": module.params['desc'],
            "type": "team"
        }
    }
    return d


def createContactMethodObj(module):
    d = {
        "contact_method": {
            "summary": module.params['summary'],
            "label": module.params['label'],
            "type": module.params['type'],
            "address": module.params['address']
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
        module, url, json.dumps(data), method='POST', headers=setHeaders(module, obj_type))
    if info['status'] != 201:
        module.fail_json(
            msg="API call failed to create object: %s." % (info))


def deleteObj(obj_type, remote_d, module):
    url = "https://api.pagerduty.com/" + obj_type + "/"
    obj_delete = False
    update_obj = False
    if obj_type == 'users':
        obj_key = 'email'
    if obj_type == 'teams':
        obj_key = 'name'
    if obj_type == 'contact_method':
        obj_key = 'address'

    if obj_type == 'contact_method':
        for u in remote_d:
            if u['email'] == module.params['email']:
                uid = u['id']
                for c in u['contact_methods']:
                    if c['type'] == module.params['type']:
                        if c['address'] == module.params['address']:
                            cid = c['id']
                            obj_delete = True
                            url = "https://api.pagerduty.com/users/" + uid + "/contact_methods/" + cid
    elif obj_type != 'contact_method':
        for u in remote_d:
            if module.params[obj_key] == u[obj_key]:
                url = url + u['id']
                obj_delete = True

    if obj_delete:
        update_obj = True
        response, info = fetch_url(
            module, url, method='DELETE', headers=setHeaders(module, obj_type))
        if info['status'] != 204:
            module.fail_json(
                msg="API call failed to delete object: %s." % (info))
    return update_obj


def checkTeams(remote_user_data, module, update, t):
    obj_type = 'teams'
    email = module.params['email']
    uid = 'null'
    tid = 'null'

    # the list of all remote team names that the user is a member of
    remote_teams = []
    for u in remote_user_data:
        if u['email'] == email:
            uid = u['id']
            for r in u['teams']:
                remote_teams.append(r)
    remote_team_list = createObjectList(
        obj_type, remote_teams)

    # all the data about known teams that exist remotely
    t_data = fetchRemoteData(obj_type, module)

    # the list of all remote team names that exist
    remote_team_master = createObjectList(obj_type, t_data)

    # for t in local_team_list:
    if t in remote_team_list and module.params['state'] == 'absent':
        update = True
        for r in t_data:
            if r['name'] == t:
                tid = r['id']
    elif t not in remote_team_list and t in remote_team_master and module.params['state'] == 'present':
        update = True
        for r in t_data:
            if r['name'] == t:
                tid = r['id']

    return update, uid, tid


def updateUsers(remote_d, module, update):
    uid = ''
    for u in remote_d:
        if u['email'] == module.params['email']:
            uid = u['id']
            if not u['name'] == module.params['name']:
                update = True
            elif not u['role'] == module.params['role']:
                update = True
            elif not u['time_zone'] == module.params['time_zone']:
                update = True
            elif not u['description'] == module.params['desc']:  # nopep8
                update = True
    return update, uid


def checkContactMethod(remote_d, module, update_method, create_method):
    uid = ''
    cid = ''
    for u in remote_d:
        if u['email'] == module.params['email']:
            uid = u['id']
            for c in u['contact_methods']:
                if c['type'] == module.params['type']:
                    if c['address'] == module.params['address']:
                        cid = c['id']
                        create_method = False
                        if c['label'] != module.params['label']:
                            update_method = True

    return update_method, create_method, uid, cid


def updateTeams(remote_d, module, update):
    uid = ''
    for t in remote_d:
        if module.params['name'] == t['name']:
            if not t['description'] == module.params['desc']:
                update = True
                uid = t['id']
    return update, uid


def checkUpdateObj(obj_type, module, remote_d):
    if obj_type == 'contact_method':
        update_master = False
        update_method = False
        create_method = True
        update_method, create_method, uid, cid = checkContactMethod(
            remote_d, module, update_method, create_method)

        if update_method:
            update_master = True
            data = createContactMethodObj(module)
            url = 'https://api.pagerduty.com/users/' + uid + '/contact_methods/' + cid
            method = 'PUT'
            UpdateObj(module, url, data, method, obj_type)
        elif create_method:
            update_master = True
            data = createContactMethodObj(module)
            url = 'https://api.pagerduty.com/users/' + uid + '/contact_methods'
            method = 'POST'
            UpdateObj(module, url, data, method, obj_type)

    if obj_type == 'users':
        update_master = False
        if module.params['teams']:
            team_list = []
            for t in module.params['teams']:
                team_list.append(t)
            for t in team_list:
                update = False
                update, uid, tid = checkTeams(remote_d, module, update, t)
                if update:
                    update_master = True
                    data = ''
                    url = setUpdateUrl(uid, tid)
                    if module.params['state'] == 'present':
                        method = 'PUT'
                    elif module.params['state'] == 'absent':
                        method = 'DELETE'
                    UpdateObj(module, url, data, method, obj_type)
        update = False
        update, uid = updateUsers(remote_d, module, update)
        if update:
            update_master = True
            data = createUserObj(module)
            url = "https://api.pagerduty.com/" + obj_type + "/" + uid
            method = 'PUT'
            UpdateObj(module, url, data, method, obj_type)

    if obj_type == 'teams':
        update = False
        update_master = False
        team_update, tid = updateTeams(remote_d, module, update)
        if team_update:
            update_master = True
            data = createTeamObj(module)
            url = "https://api.pagerduty.com/" + obj_type + "/" + tid
            method = 'PUT'
            UpdateObj(module, url, data, method, obj_type)

    return update_master


def UpdateObj(module, url, data, method, obj_type):
    response, info = fetch_url(
        module, url, json.dumps(data), method=method, headers=setHeaders(module, obj_type))
    if info['status'] != 200:
        if info['status'] != 204:
            if info['status'] != 201:
                module.fail_json(
                    msg="API call failed to update object: %s." % (info))
