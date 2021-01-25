import json
import jsonpickle
import datetime

from replit import db

class Event:
  def __init__(self, ID, name, leader, description, dateandtime, tanks = 0, healers = 0, dds = 0):
    self.name = name
    self.leader = leader
    self.description = description
    self.dateandtime = dateandtime
    self.tanks = tanks
    self.healers = healers
    self.dds = dds
  
  def GetAnnouncement(self):
    return 
    """@everyone\n
    {name} Scheduled For: {dateandtime}\n
    \n
    Leader: {leader}
    """.format(name=self.name, dateandtime=self.dateandtime, leader=self.leader)

  def ToJSON(self):
    return jsonpickle.encode(self)

  @staticmethod
  def FromJSON(json_obj):
    return jsonpickle.decode(json_obj)

def update_event(event_name, leader, description: str, dateandtime: datetime, tanks: int, healers: int, dds: int):
  eventID = get_new_eventID
  event_obj = Event(event_name, leader, description, dateandtime, tanks, healers, dds)
  event_json = event_obj.ToJSON()

  if "events" in db.keys():
    events = db["events"]
    events[eventID] = event_json
    db["events"] = events
  else:
    db["events"] = {eventID: event_json}

#I'm sure this will be fiiiiine
def get_new_eventID():
  if "events" in db.keys():
    events = db["events"]
    return max(events.keys())
  else:
    return 1