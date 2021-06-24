import praw
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import config
import firebase_admin
from firebase_admin import credentials, firestore, db
import string
import random
import time

print("Initializing Firebase...")
cred = credentials.Certificate("credentials.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()
print("OK!")

print("Logging into Reddit...")
reddit = praw.Reddit(user_agent='KickOpenTheDoor bot by u/RPG_Ivan and u/VirtuousVermin',
                  client_id=config.client_id,
                  client_secret=config.client_secret,
                  username=config.username,
                  password=config.password)
print("OK!")

print("Logging into Discord...")

description = '''Mr Kicky for r/KickOpenTheDoor by u/RPG_Ivan.'''
bot  = commands.Bot(command_prefix='.', description=description)
@bot.event
async def on_ready():
        members = 0
        for server in bot.servers:
                for member in server.members:
                        members = members+1
        members = str(members)
        await bot.change_presence(game=discord.Game(name=f'Kicking open the door with {members} others!'))
        print("OK!")

@bot.command(pass_context=True)
async def link(ctx, redditname):
        id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        await bot.say(f'To link your accounts, PM u/kickitopen_bot on reddit with the following in the message body: {id}. This code expires in 3 minutes.')
        userid = ctx.message.author.id
        inbox = reddit.inbox.stream(pause_after = 10)
        for message in inbox:
                if comment is None:
                        await bot.say('Timed out.')
                        break
                message.mark_read()
                if message.author.name == redditname:
                        if message.body == id:
                                user_ref = db.collection('users').document(redditname)
                                user_ref.update({
                                        "discord_id": userid,
                                        })
                                await bot.say('Successfully linked!')
                                linked = True
                                times = 0



                                                        
bot.run("NTEzOTM1MTQ0MzE1Mzg3OTIx.DtPPRA.NotaSv_MHDP8cAyiqqAB4yIxHjM")
