import discord

from python.events import update_event_template
from python.events import delete_event_template
from python.events import list_event_templates

async def parse_message(message):
  msg = message.content

  if(msg.startsWith("!create-event-template")):
    update_event_template()
  elif(msg.startsWith("!delete-event-template")):
    delete_event_template()
  elif(msg.startsWith("!list-event-templates")):
    list_event_templates()
