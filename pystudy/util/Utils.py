# -------------------------------------------------------------------------------
# Name:        
# Purpose:     
#
# Author:      qin.shuq
#
# Created:     
# Copyright:   (c) qin.shuq 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# -*- coding: utf8 -*-

def obtainObjectInfo(obj):
    attrs = dir(obj)
    objInfo = {}
    for attr in attrs:
        objInfo[attr] = getattr(obj, attr)
    return objInfo


def obtainEventInfo(event):
    eventInfo = 'Event Info: '
    eventName = event.GetClassName()
    eventId = event.GetId()
    eventType = event.GetEventType()
    eventInfo += '[name: %s , type: %s, id: %d]' % (eventName, str(eventType), eventId)
    return eventInfo









