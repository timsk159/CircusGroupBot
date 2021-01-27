import json
import jsonpickle
import datetime
import python.signup

from replit import db
from python.event_template import get_template

class Event:
  def __init__(self, eventID, name, leader, description, dateandtime, tanks = 0, healers = 0, dds = 0, messageID = -1, signups = []):
    self.eventID = eventID
    self.name = name
    self.leader = leader
    self.description = description
    self.dateandtime = dateandtime
    self.tanks = tanks
    self.healers = healers
    self.dds = dds
    self.messageID = messageID
    self.signups = signups
  
  def GetPrettyDescription(self):
    return self.name + " Tanks: " + str(self.tanks) + " Healers: " + str(self.healers) + " DDs: " + str(self.dds) + " Date: " + self.dateandtime

  def GetAnnouncement(self):
    return """
@everyone
{name} Scheduled For: {dateandtime}

Leader: <@{leader}>

{description}
""".format(name=self.name, dateandtime=self.dateandtime, leader=self.leader, description=self.description)

  def ToJSON(self):
    return jsonpickle.encode(self)

  @staticmethod
  def FromJSON(json_obj):
    return jsonpickle.decode(json_obj)




def update_event(event_name, leader, description: str, dateandtime: datetime, tanks: int = 0, healers: int = 0, dds: int = 0):
  eventID = get_new_eventID()
  event_obj = Event(eventID, event_name, leader, description, dateandtime, tanks, healers, dds)
  event_json = event_obj.ToJSON()

  if "events" in db.keys():
    events = db["events"]
    events[eventID] = event_json
    db["events"] = events
  else:
    db["events"] = {eventID: event_json}
  
  return event_obj

def update_event_by_template(template_name, event_name, leader, description: str, dateandtime: datetime):
  template = get_template(template_name)

  eventID = get_new_eventID()
  event_obj = Event(eventID, event_name, leader, description, dateandtime, template.tanks, template.healers, template.dds)
  event_json = event_obj.ToJSON()

  if "events" in db.keys():
    events = db["events"]
    events[eventID] = event_json
    db["events"] = events
  else:
    db["events"] = {eventID: event_json}

  return event_obj

def set_message_ID(event, messageID):
  event.messageID = messageID
  events = db["events"]
  events[event.eventID] = event.ToJSON()
  db["events"] = events

def update_signups(event):
  events = db["events"]
  events[event.eventID] = event.ToJSON()
  db["events"] = events

  

def get_all_events():
  if("events" in db.keys()):
    events_raw = db["events"]
    events = [Event.FromJSON(e) for e in events_raw.values()]
    return events

#I'm sure this will be fiiiiine
def get_new_eventID():
  if "events" in db.keys():
    events = db["events"]
    return str(int(max(events.keys())) + 1)
  else:
    return 1


def delete_all_events():
  if "events" in db.keys():
    del db["events"];
