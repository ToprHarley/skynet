#!/usr/bin/python
import sys
import os
import commands


def getNotification():
    notification_dict = {}
    isEndOfDictionary = False
    for line in sys.stdin:
        if not line.strip():
            isEndOfDictionary = True
            continue
        if isEndOfDictionary:
            break
        key, value = line.split(':')
        notification_dict[key] = value.lstrip()[:-1]
    return notification_dict, line


def postTheNotificationToSaltMaster():
    salt_payload = {}
    threshold_dict = {}
    threshold_dict['tags'], threshold_dict['message'] = getNotification()
    threshold_dict['severity'] = threshold_dict['tags']["Severity"]
    tag = "skyring/collectd/node/{0}/threshold/{1}/{2}".format(
        threshold_dict['tags']["Host"],
        threshold_dict['tags']["Plugin"],
        threshold_dict['tags']["Severity"])
    cmd = "sudo salt-call event.fire "'"%s"'" "'"%s"'"" %(str(threshold_dict), tag)
    commands.getstatusoutput(cmd)


if __name__ == '__main__':
    postTheNotificationToSaltMaster()
