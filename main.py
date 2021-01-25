import discord
import os
from discord.ext import commands

from python.event_template import update_event_template
from python.event_template import delete_event_template
from python.event_template import list_event_templates

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    

@bot.command()
async def test_command(ctx, arg):
  print("Hello")
  await ctx.send("Hello")


@bot.command()
async def create_template(ctx, template_name, tanks: int, healers: int, dds: int):
  update_event_template(template_name, tanks, healers, dds)
  await ctx.send("Created new template called: " + template_name)


@bot.command()
async def delete_template(ctx, template_name):
  delete_event_template(template_name)
  await ctx.send("Deleted template called: " + template_name)

#
@bot.command()
async def list_templates(ctx):
  templates = list_event_templates()
  await ctx.send(templates)

bot.run(os.getenv('TOKEN'))