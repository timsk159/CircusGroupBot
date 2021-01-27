import os
import discord
import keepalive

from discord.ext import commands

from python.event_template import update_event_template
from python.event_template import delete_event_template
from python.event_template import get_all_templates
from python.event_template import get_template
from python.event_template import delete_all_templates

from python.event import update_event
from python.event import update_event_by_template
from python.event import delete_all_events
from python.event import get_all_events
from python.event import set_message_ID
from python.event import update_signups

from python.signup import Signup

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

#signups
@bot.event
async def on_raw_reaction_add(payload):
  await handle_reaction(payload)

@bot.event
async def on_raw_reaction_remove(payload):
  await handle_reaction(payload)

async def handle_reaction(payload):
  channel = bot.get_channel(payload.channel_id)
  message = await channel.fetch_message(payload.message_id)

  if(message.author.id != bot.user.id):
    return
  
  if(payload.user_id == bot.user.id):
    return

  if((payload.emoji.name != '🚑') and (payload.emoji.name != '🛡️') and (payload.emoji.name != '⚔')):
    return
  
  all_events = get_all_events()
  messageID = payload.message_id

  event = next((e for e in all_events if e.messageID == messageID), None)
  if(event is None):
    print("Didn't find event")
    return

  role = "Tank"
  if(payload.emoji.name == '🚑'):
    role = "Healer"
  elif(payload.emoji.name == '⚔'):
    role = "DD"
  
  joined = False

  signup = Signup("", -1)

  if(payload.event_type == "REACTION_ADD"):
    signup = Signup(role, payload.user_id)
    event.signups.append(signup)
    joined = True
  elif(payload.event_type == "REACTION_REMOVE"):
    signup = next((s for s in event.signups if s.memberID == payload.user_id), None)
    event.signups.remove(signup)

  await send_signup_message(channel, event, signup, joined)
  update_signups(event)

  message_str = get_event_message_str(event)
  await message.edit(content=str(message_str))

async def send_signup_message(channel, event, signup, joined):
  if(joined):
    await channel.send("<@{memberID}> Signed up to {eventname} as {role}".format(memberID=signup.memberID, eventname=event.name, role=signup.role))
  else:
    await channel.send("<@{memberID}> is no longer joining {eventname} as {role}".format(memberID=signup.memberID, eventname=event.name, role=signup.role))


#templates:

@bot.command(name='NewTemplate')
async def _create_template(ctx, template_name, tanks: int, healers: int, dds: int):
  update_event_template(template_name, tanks, healers, dds)
  await ctx.send("Created new template called: " + template_name)


@bot.command(name='DeleteTemplate')
async def _delete_template(ctx, template_name):
  delete_event_template(template_name)
  await ctx.send("Deleted template called: " + template_name)


@bot.command(name='ListTemplates')
async def _list_templates(ctx):
  templates = get_all_templates()
  for template in templates:
    await ctx.send("Template: " + template.GetPrettyDescription())

@bot.command(name='GetTemplate')
async def _get_template(ctx, template_name):
  template = get_template(template_name)
  await ctx.send("Template: " + template.GetPrettyDescription())


#events:

@bot.command(name='NewEvent')
async def _new_event(ctx, eventname, dateandtime, description = "", tanks: int = 0, healers: int = 0, dds: int = 0):
  event = update_event(eventname, ctx.author.id, description, dateandtime, tanks, healers, dds)
  await send_event_message(ctx, event)

@bot.command(name='NewEventByTemplate')
async def _new_event_by_template(ctx, templatename, eventname, dateandtime, description = ""):
  event = update_event_by_template(templatename, eventname, ctx.author.id, description, dateandtime)
  await send_event_message(ctx, event)

async def send_event_message(ctx, event):
  message_str = get_event_message_str(event)
 
  message = await ctx.send(message_str)
  set_message_ID(event, message.id)
  await add_reactions(ctx, message)

def get_event_message_str(event):
  message_str = event.GetAnnouncement()
  message_str = add_signups(message_str, event)
  message_str = add_signup_instructions(message_str, event)

  return message_str

async def add_reactions(ctx, message):
  await message.add_reaction('🛡️')
  await message.add_reaction('🚑')
  await message.add_reaction('⚔')

def add_signup_instructions(message_str, event):
  message_str += """
React with:
🛡️ to sign up as Tank
🚑 to sign up as Healer
⚔ to sign up as Damage Dealer"""
  return message_str

def add_signups(message_str, event):
  tanks = list(filter(lambda x: x.role == "Tank", event.signups))
  healers = list(filter(lambda x: x.role == "Healer", event.signups))
  dds = list(filter(lambda x: x.role == "DD", event.signups))

  empty_tanks = max(0, event.tanks - len(tanks))
  empty_healers = max(0, event.healers - len(healers))
  empty_dds = max(0, event.dds - len(dds))

  for i in range(0, len(tanks)):
      message_str += "🛡️:<@{memberID}>\n".format(memberID=tanks[i].memberID)
  for i in range(0, empty_tanks):
      message_str += "🛡️:\n"

  for i in range(0, len(healers)):
      message_str += "🚑:<@{memberID}>\n".format(memberID=healers[i].memberID)
  for i in range(0, empty_healers):
      message_str += "🚑:\n"

  for i in range(0, len(dds)):
      message_str += "⚔:<@{memberID}>\n".format(memberID=dds[i].memberID)
  for i in range(0, empty_dds):
      message_str += "⚔:\n"

  return message_str




#debug
@bot.command(name='testcommand')
async def test_command(ctx):
  await ctx.send("Hello")


@bot.command(name='cleardb')
async def _clear_db(ctx):
  delete_all_events()
  delete_all_templates()
  await ctx.send("Cleared DB")

@bot.command(name='printdb')
async def _print_db(ctx):
  templates = get_all_templates()
  events = get_all_events()

  message_str = "";

  if(templates is None):
    message_str += "No templates\n"
  else:
    message_str += "Templates:\n"
    for template in templates:
      message_str += template.GetPrettyDescription() + "\n"
  if(events is None):
    message_str += "No events\n"
  else:
    message_str += "Events:\n"
    for event in events:
      message_str += event.GetPrettyDescription() + "\n"
  await ctx.send(message_str)

  for event in events:
    print("ID: " + str(event.eventID) + " Name: " + event.name + " MsgID: " + str(event.messageID) ) 
    print("Signups:")
    for signup in event.signups:
      print(signup.role + " " + str(signup.memberID))


keepalive.keep_alive()

bot.run(os.getenv('TOKEN'))