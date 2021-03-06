import os
import discord
import keepalive
import asyncio
import typing

from datetime import datetime, timedelta

from discord.ext import commands
from discord.ext.commands import has_permissions

from python.event_template import update_event_template
from python.event_template import delete_event_template
from python.event_template import get_all_templates
from python.event_template import get_template
from python.event_template import delete_all_templates

from python.event import update_event
from python.event import update_event_by_template
from python.event import delete_all_events
from python.event import get_all_events
from python.event import find_event_with_commandMsg
from python.event import Event

from python.signup import Signup
from python.signup import Role

from replit import db

bot = commands.Bot(command_prefix='$')

sem = asyncio.Semaphore()

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message_edit(before, after):
  foundEvent = find_event_with_commandMsg(before.id)
  if(foundEvent is not None):
    try:
        print("Found event when editing, processing")
        await bot.process_commands(after)
    except:
        print("Something went wrong when editing event")

#signups
@bot.event
async def on_raw_reaction_add(payload):
  await handle_reaction(payload)

@bot.event
async def on_raw_reaction_remove(payload):
  await handle_reaction(payload)

async def handle_reaction(payload):
  async with sem:
    channel = bot.get_channel(payload.channel_id)
    
    if(payload.user_id == bot.user.id):
      return

    role = Role.GetRoleFromEmoji(payload.emoji.name)

    if(role == None):
      return
    
    all_events = get_all_events()
    messageID = payload.message_id

    event = next((e for e in all_events if e.messageID == messageID), None)
    if(event is None):
      print("Didn't find event " + " msgID: " + str(messageID))
      return

    joined = False

    signup = Signup(None, -1, False)

    if(payload.event_type == "REACTION_ADD"):
      if(event.has_space_for_signup(role)):
        signup = event.add_signup(role, payload.user_id)
        joined = True
      else:
        await channel.send("Sorry <@{memberID}> we don't need anymore {role}\'s".format(memberID=payload.user_id, role=Role.GetEmoji(role)))
        message = await channel.fetch_message(payload.message_id)
        
        await message.remove_reaction(payload.emoji, payload.member)
        return
    elif(payload.event_type == "REACTION_REMOVE"):
      signup = event.remove_signup(role, payload.user_id)

    await send_signup_message(channel, event, signup.role, payload.user_id, joined)

    message_str = get_event_message_str(event)
    message = await channel.fetch_message(payload.message_id)
    await message.edit(content=str(message_str))

async def send_signup_message(channel, event, role, memberID, joined):
  role_emoji = Role.GetEmoji(role)

  if(joined):
    await channel.send("<@{memberID}> Signed up to {eventname} as {role}".format(memberID=memberID, eventname=event.name, role=role_emoji))
  else:
    await channel.send("<@{memberID}> is no longer joining {eventname} as {role}".format(memberID=memberID, eventname=event.name, role=role_emoji))


#templates:

@bot.command(name='NewTemplate')
@commands.has_role("ESO Officer")
async def _create_template(ctx, template_name, tanks: int, healers: int, dds: int, runners: int = 0):

  update_event_template(template_name, tanks, healers, dds, runners)
  await ctx.send("Created new template called: " + template_name)


@bot.command(name='DeleteTemplate')
@commands.has_role("ESO Officer")
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
async def _new_event(ctx, eventname: str, dateandtime: str,
tanks: typing.Optional[int] = 0, healers: typing.Optional[int] = 0, 
dds: typing.Optional[int] = 0, runners: typing.Optional[int] = 0,
description: typing.Optional[str] = None):
  rolesSum = tanks + healers + dds + runners
  if(tanks > 16 or healers > 16 or dds > 16 or runners > 16 or rolesSum > 16):
    await ctx.send("Sorry, you've asked for too many people! Was your command correct?")
    return
  event = update_event(eventname, ctx.author.id, description, dateandtime, tanks, healers, dds, runners, ctx.message.id)
  await send_event_message(ctx, event)

@bot.command(name='NewEventByTemplate')
async def _new_event_by_template(ctx, templatename, eventname, dateandtime, description = ""):
  event = update_event_by_template(templatename, eventname, ctx.author.id, description, dateandtime)
  await send_event_message(ctx, event)


async def send_event_message(ctx, event):
  message_str = get_event_message_str(event)
  message = None;

  if(event.messageID is not None and event.messageID > -1):
    print("Event has a messageID already, editing")
    message = await ctx.fetch_message(event.messageID)
    print(message_str)
    await message.edit(content=message_str)
  else:
    message = await ctx.send(message_str)
    try:
      await message.pin()
    except:
      print("Unable to pin message")

  event.set_message_ID(message.id)
  await add_reactions(ctx, message, event)

def get_event_message_str(event):
  message_str = event.GetAnnouncement()
  message_str = add_signups_to_message(message_str, event)
  message_str += "\n"
  message_str = add_signup_instructions(message_str, event)

  return message_str

async def add_reactions(ctx, message, event):
  for role in Role:
    if(role == Role.Runner and event.runners == 0):
      continue
    await message.add_reaction(Role.GetEmoji(role))

def add_signup_instructions(message_str, event):
  message_str += "React with:\n"
  allRoles = list(Role)
  for role in allRoles:
    if(role == Role.Runner):
      if(event.runners == 0):
        continue
    message_str += Role.GetEmoji(role) + " to sign up as " + Role.GetPrettyString(role) + "\n"

  return message_str

def add_signups_to_message(message_str, event):
  allSignups = event.signups
  
  for signup in allSignups:
    if(signup.isRequired and signup.memberID == -1):
      message_str += Role.GetEmoji(signup.role) + ":\n"
    else:
      message_str += Role.GetEmoji(signup.role) + ":<@{memberID}>\n".format(memberID=signup.memberID)

  return message_str




#debug
@bot.command(name='testcommand')
async def test_command(ctx):
  await ctx.send("Hello")


@bot.command(name='cleardb')
@commands.has_role("ESO Officer")
async def _clear_db(ctx):
  delete_all_events()
  delete_all_templates()
  await ctx.send("Cleared DB")

@bot.command(name='printdb')
@commands.has_role("ESO Officer")
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
  #await ctx.send(message_str)

  if(not events is None):
    for event in events:
      print("ID: " + str(event.eventID) + " Name: " + event.name + " dateandtime: " + str(event.dateandtime) + " MsgID: " + str(event.messageID) ) 
      print("Signups:")
      for signup in event.signups:
        print(Role.GetPrettyString(signup.role) + " " + str(signup.memberID))

@bot.command(name='deleteoldevents')
@commands.has_role("ESO Officer")
async def _delete_old_events(ctx):
  events = get_all_events()
  eventsToRemove = []

  allChannels = await ctx.guild.fetch_channels()

  message = None

#this is SUPER slow, need to find a better way...
  for event in events:
    for channel in allChannels:
      try:
        message = await channel.fetch_message(event.messageID)
      except:
        continue
      if message is None:
        continue

#Usually means event was created in another guild (e.g: my test guild)
    if(message is None):
      continue

    delta = datetime.now() - message.created_at

    if(delta.days > 14):
      eventsToRemove.append(event)
      continue

  rawEvents = db["events"]

  for eventToRemove in eventsToRemove:
    print("Would delete event with ID: " + str(eventToRemove.eventID))
    del rawEvents[eventToRemove.eventID]

  db["events"] = rawEvents

  await ctx.send("Deleted: " + str(len(eventsToRemove)) + " Events")


keepalive.keep_alive()

bot.run(os.getenv('TOKEN'))