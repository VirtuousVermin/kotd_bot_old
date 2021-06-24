import praw
import config
import firebase_admin
from firebase_admin import credentials, firestore

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

inbox = reddit.inbox.stream()
for message in inbox:
	if '!newboss' in message.body:
		if message is None:
			break
		print('New boss!')
		message.mark_read()
		if message.author.name == 'RLiamWilloughby' or 'VirtuousVermin' or 'RPG_Ivan' or 'JManthe675_1' or 'verifypassword__' or 'Pianmeister' or 'Abrohmtoofar':
			arguments = message.body[9:]
			arg = arguments.split(', ')
			postid = arg[0]
			bossname = arg[1]
			bosshp = arg[2]
			monster_ref = db.collection('monsters').document(postid)
			monster_ref.set({
				'name': bossname,
				'hp': int(bosshp),
				'attacked': [],
				})
			print('Created!')
		else:
			print('Denied!')
			message.reply('Insufficient Permission!')
