import json
import jsonpickle

from replit import db

class EventTemplate:
  def __init__(self, name, tanks, healers, dds, runners):
    self.name = name
    self.tanks = tanks
    self.healers = healers
    self.dds = dds
    self.runners = runners

  def GetPrettyDescription(self):
    return self.name + " Tanks: " + str(self.tanks) + " Healers: " + str(self.healers) + " DDs: " + str(self.dds) + " Runners: " + str(self.runners)
  
  def ToJSON(self):
    return jsonpickle.encode(self)

  @staticmethod
  def FromJSON(json_obj):
    return jsonpickle.decode(json_obj)


def update_event_template(template_name, tanks: int, healers: int, dds: int, runners: int):
  template_obj = EventTemplate(template_name, tanks, healers, dds, runners)
  template_json = template_obj.ToJSON()
 
  if "event_templates" in db.keys():
    event_templates = db["event_templates"]
    event_templates[template_name] = template_json
    db["event_templates"] = event_templates
  else:
    db["event_templates"] = {template_name: template_json}


def delete_event_template(template_name):
  if "event_templates" in db.keys():
    event_templates = db["event_templates"]
    if(template_name in event_templates):
      del event_templates[template_name]
      db["event_templates"] = event_templates

def get_all_templates():
  if "event_templates" in db.keys():
    event_templates_raw = db["event_templates"]
    event_templates = [EventTemplate.FromJSON(e) for e in event_templates_raw.values()]
    return event_templates

def get_template(template_name):
  if "event_templates" in db.keys():
    event_templates = db["event_templates"]
    if(template_name in event_templates):
      raw_json = event_templates[template_name]
      template = EventTemplate.FromJSON(raw_json)
      return template

def delete_all_templates():
  if("event_templates" in db.keys()):
    del db["event_templates"];
