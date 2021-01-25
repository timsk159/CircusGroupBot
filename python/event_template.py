from replit import db

class EventTemplate:
  def __init__(self, name, tanks, healers, dds):
    self.name = name
    self.tanks = tanks
    self.healers = healers
    self.dds = dds

  def GetPrettyDescription(self):
    return self.name + " Tanks: " + self.tanks + " Healers: " + self.healers + " DDs: " + self.dds

def update_event_template(template_name, tanks: int, healers: int, dds: int):
  if "event_templates" in db.keys():
    event_templates = db["event_templates"]
    event_templates.append(template_name)
    db["event_templates"] = event_templates
  else:
    db["event_templates"] = [template_name]


def delete_event_template(template_name):
  if "event_templates" in db.keys():
    event_templates = db["event_templates"]
    if(template_name in event_templates):
      event_templates.remove(template_name)
      db["event_templates"] = event_templates

def list_event_templates():
  if "event_templates" in db.keys():
    event_templates = db["event_templates"]
    return event_templates


