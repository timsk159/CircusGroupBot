import json
import jsonpickle
import datetime

from replit import db

from python.event_template import get_template

from python.signup import Signup
from python.signup import Role

class Event:
  def __init__(self, eventID, name, leader, description, dateandtime, tanks = 0, healers = 0, dds = 0, runners = 0, messageID = -1):
    self.eventID = eventID
    self.name = name
    self.leader = leader
    self.description = description
    self.dateandtime = dateandtime
    self.tanks = tanks
    self.healers = healers
    self.dds = dds
    self.runners = runners
    self.messageID = messageID
    self.signups = []
    for i in range(0, tanks):
      self.signups.append(Signup(Role.Tank, -1, True))
    for i in range(0, healers):
      self.signups.append(Signup(Role.Healer, -1, True))
    for i in range(0, dds):
      self.signups.append(Signup(Role.DD, -1, True))
    for i in range(0, runners):
      self.signups.append(Signup(Role.Runner, -1, True))
  
  def GetPrettyDescription(self):
    return self.name + " Tanks: " + str(self.tanks) + " Healers: " + str(self.healers) + " DDs: " + str(self.dds) + " Runners: " + str(self.runners) + " Date: " + self.dateandtime

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

  def add_signup(self, role, memberID):
    signup = next((s for s in self.signups if s.role == role and s.memberID == -1), None)
    if (signup is None):
      signup = Signup(role, memberID, False)
      self.signups.append(signup)
    else:
      signup.memberID = memberID

    self.update_signups()
    return signup

  def remove_signup(self, role, memberID):
    signup = next((s for s in self.signups if s.role == role and s.memberID == memberID), None)
    if(signup is None):
      return
    
    if(signup.isRequired):
      signup.memberID = -1
    else:
      self.signups.remove(signup)

    self.update_signups()
    return signup

  def update_signups(self):
    events = db["events"]
    events[self.eventID] = self.ToJSON()
    db["events"] = events

  def set_message_ID(self, messageID):
    self.messageID = messageID
    events = db["events"]
    events[self.eventID] = self.ToJSON()
    db["events"] = events




def update_event(event_name, leader, description: str, dateandtime: datetime, tanks: int = 0, healers: int = 0, dds: int = 0, runners: int = 0):
  eventID = get_new_eventID()
  event_obj = Event(eventID, event_name, leader, description, dateandtime, tanks, healers, dds, runners)
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
  event_obj = Event(eventID, event_name, leader, description, dateandtime, template.tanks, template.healers, template.dds, template.runners)
  event_json = event_obj.ToJSON()

  if "events" in db.keys():
    events = db["events"]
    events[eventID] = event_json
    db["events"] = events
  else:
    db["events"] = {eventID: event_json}

  return event_obj

def get_all_events():
  if("events" in db.keys()):
    events_raw = db["events"]
    events = [Event.FromJSON(e) for e in events_raw.values()]
    return events

def get_new_eventID():
  if "events" in db.keys():
    events = db["events"]
    maxKey = int(max(events, key=int))
    maxKey += 1
    return str(maxKey)
  else:
    return 1


def delete_all_events():
  if "events" in db.keys():
    del db["events"];
