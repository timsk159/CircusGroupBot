import json
import jsonpickle

from replit import db

class EventTemplate:
  def __init__(self, name, tanks, healers, dds):
    self.name = name
    self.tanks = tanks
    self.healers = healers
    self.dds = dds

  def GetPrettyDescription(self):
    return self.name + " Tanks: " + str(self.tanks) + " Healers: " + str(self.healers) + " DDs: " + str(self.dds)
  
  def ToJSON(self):
    return jsonpickle.encode(self)

  @staticmethod
  def FromJSON(json_obj):
    return jsonpickle.decode(json_obj)


def update_event_template(template_name, tanks: int, healers: int, dds: int):
  template_obj = EventTemplate(template_name, tanks, healers, dds)
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

def list_event_templates():
  if "event_templates" in db.keys():
    event_templates_raw = db["event_templates"]
    event_templates = [EventTemplate.FromJSON(e) for e in event_templates_raw.values()]
    print(event_templates)
    return event_templates

def get_template(template_name):
    if template_name in db.keys():
      raw_json = db[template_name];
      json_obj = json.loads(raw_json)
      template = EventTemplate.FromJSON(json_obj)
      return template



