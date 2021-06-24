import praw
import config
import random
import firebase_admin
import time
import os
import re
from firebase_admin import credentials, firestore, db

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


#Use kiot as a test sub for now.
subreddit = reddit.subreddit('kickopenthedoor')


nu = 0
x = 0
placeholder = 0
#COMMANDS VIA COMMENTING
comments = subreddit.stream.comments(pause_after=None, skip_existing=True)
try:
	def run():
		for comment in comments:
			if comment is None:
				break
			#NEW USER CREATION
			users_ref = db.collection('users')
			users = users_ref.get()
			author = comment.author.name	
			docs = []
			for document in users:
				docs.append(document.id)
			if author not in docs:
				print("Generating...")
				doc = db.collection('users').document(author)
				doc.set({
					'inventory': {},
					'discord_id':'',
					'race':'',
					'gold':placeholder
					})
				print('Generated new profile.')
				reddit.redditor(author).message('Welcome to r/KickOpenTheDoor!', '#Welcome to r/KickOpenTheDoor!'+'\n\n'+'Your user profile has been created. You have been granted:'+'\n\n'+'*0 Gold'+'\n\n'+'Have fun slaying them monsters!')
			if comment.body.lower() == '!balance' and comment.id not in processed:
				if comment is None:
					pass
				else:
					print('Getting balance...')
					user_ref = db.collection('users').document(str(comment.author))
					user = user_ref.get()
					gold = user.get('gold')
					comment.reply(f'Your balance is: {gold} gold.') 
					f = open("processed.txt", "a")
					f.write(comment.id + ", ")
			#ATTACK SYSTEM
			monsters_ref = db.collection('monsters')
			monsters = monsters_ref.get()
			post_id = comment.link_id[3:]
			basedamage = random.randint(1, 3)
			#SHOP SYSTEM
			shop2 = db.collection(u'shop').get()
			items = []
			items2 = []
			for document in shop2:
				items.append(document.id)
			comment_buying = []
			random_low_item = db.collection('lowtieritems').get()
			for document in random_low_item:
				items2.append(document.id)
			#Command parsing goes here
			content = comment.body.lower()
			if "!attack" in content and comment.id not in processed:
				for document in monsters:
					if document.id == post_id:
						#Normal attacking (without a weapon)
						weaponname = content[8:]
						monster_ref = monsters_ref.document(post_id)
						monster = monster_ref.get()
						name = monster.get('name')
						oldhp = monster.get('hp')
						attacked = monster.get('attacked')
						if comment.author.name in attacked:
							comment.reply('You have already attacked this monster!')
						elif comment.author.name not in attacked:
							if weaponname == "":
								if oldhp > 0:
									user_ref = db.collection('users').document(comment.author.name)
									user = user_ref.get()
									try:
										oldgold = user.get('gold')
									except KeyError:
										print('User profile error, no gold class.')
										user.set({'gold':'0'},  merge=True)
										continue
									damage = basedamage
									cash = 10*damage
									user_ref.update({
										'gold':int(oldgold)+cash
										})
									monster_ref.update({
										'hp': oldhp - damage,
										'attacked': attacked + [comment.author.name],
										})
								monster = monster_ref.get()
								hp = str(monster.get('hp'))
								if int(hp) <= 0:
									comment.submission.mod.flair("Slain!")
									comment.reply(f'You attack {name}! You deal {basedamage} base damage! It has {hp} health remaining! The beast has been slain!'+'\n\n'+f'You earned {cash} gold! To view your balance, reply to this message with !balance.')								
								elif int(hp) > 0:
									comment.submission.mod.flair(f'{hp} HP remaining!')
									comment.reply(f'You attack {name}! You deal {basedamage} base damage! It has {hp} health remaining!'+'\n\n'+f'You earned {cash} gold! To view your balance, reply to this message with !balance.')
								elif oldhp <= 0:
									comment.reply('Sorry, but this beast has already been slain!')
							else:
								inventory_ref = db.collection('users').document(comment.author.name)
								inventory = inventory_ref.get()
								inv = inventory_ref.collection('inventory').document(weaponname)
								try:
									print(weaponname)
									weapon = inv.get(weaponname)
									wname = inv.get('name')
									if oldhp > 0:
										user_ref = db.collection('users').document(comment.author.name)
										user = user_ref.get()
										try:
											oldgold = user.get('gold')
										except:
											print('User profile error, no gold class.')
											all_users.set({'gold':placeholder}, merge=True)
											continue
										extradamage = weapon.get('damage')
										damage = basedamage+extradamage
										cash = 10*damage
										user_ref.update({
											'gold':oldgold+cash
											})
										monster_ref.update({
											'hp': oldhp - damage,
											'attacked': attacked + [comment.author.name],
											})
									monster = monster_ref.get()
									hp = str(monster.get('hp'))
									if int(hp) <= 0:
										comment.submission.mod.flair("Slain!")
										comment.reply(f'You attack {name}! You deal {basedamage} base damage and using {wname} deals an extra {extradamage} damage! It has {hp} health remaining! The beast has been slain!'+'\n\n'+f'You earned {cash} gold! To view your balance, reply to this message with !balance.')								
									elif int(hp) > 0:
										comment.submission.mod.flair(f'{hp} HP remaining!')
										comment.reply(f'You attack {name}! You deal {basedamage} base damage and using {wname} deals an extra {extradamage} damage! It has {hp} health remaining!'+'\n\n'+f'You earned {cash} gold! To view your balance, reply to this message with !balance.')
									elif oldhp <= 0:
										comment.reply('Sorry, but this beast has already been slain!')
								except (KeyError, AttributeError):
									print('Error')
									comment.reply('Either you don\'t have that weapon, or it doesn\'t exist!')

						print('Comment processed!')
						f = open("processed.txt", "a")
						f.write(comment.id + ", ")
			if "!buy" in comment.body and comment.id not in processed:
				while True:
					print('Buy Request Found!')
					global nu
					global x
					#Used for checking if item being purchased exists, if not add it to the excluded list and break out of while True:
					if nu > len(items):
						nu=0
						x = x + 1
					if x > 1:
						f = open("processed", "a")
						f.write(comment.id + ", ")
						x = 0
						comment.reply('That item does not exist. Please try one of these: patrician, plebian.')
						break
					#Defining more variables
					all_items = ''.join(str(e) for e in items[-nu])
					item_in_comment = re.findall(all_items, content)
					comment_buying.extend(item_in_comment)
					#Checking if there's an item in the comment, it iterates through the list one at a time
					if bool(item_in_comment) is False:
						nu = nu + 1
						print(nu)
						continue
					else:
						#More variables
						comment_shop = ''.join(str(e) for e in comment_buying[-1])
						all_users = db.collection('users').document(str(comment.author))
						total_users = all_users.get()
						try:
							gold = total_users.get('gold')
						except:
							print('User profile error, no gold class.')
							all_users.set({'gold':placeholder}, merge=True)
							continue
						shop_ref = db.collection('shop').document(comment_shop)
						shop = shop_ref.get()
						price = shop.get('price')
					#Putting the item in the user's inventory & subtracting the price
					if int(gold) < int(price):
						print('Transaction Declined!')
						comment.reply(f'You do not have enough gold for the {comment_shop} treasure card!')
					else:
						print('Item Bought!')
						if 'plebian' in comment_shop:
							low_tier_items = ''.join(str(e) for e in items2[random.randint(0,8)])
							low_tier_refs = db.collection('lowtieritems').document(low_tier_items)
							low_tier = low_tier_refs.get()
							low_items = low_tier.get('name')
							low_items_dmg = low_tier.get('dmg')
							inventory = all_users.collection('inventory').document(low_items)
							inventory.set({'name': low_items,
												'damage': int(low_items_dmg),
												'amount': 1,
												'uses': 10,
												'equipped': False}, merge=True)
							comment.reply(f'Ta-Da! You have recieved the {low_items}. It deals {low_items_dmg} bonus damage!')

							ammount_final = gold - price
							all_users.update({'gold':ammount_final})
						if 'patrician' in comment_shop:
							high_tier_items = ''.join(str(e) for e in items2[random.randint(0,8)])
							high_tier_refs = db.collection('hightieritems').document(high_tier_items)
							high_tier = high_tier_refs.get()
							high_items = high_tier.get('name')
							high_items_dmg = high_tier.get('dmg')
							inventory = all_users.collection('inventory').document(high_items)
							inventory.set({'name': high_items,
												'damage': int(high_items_dmg),
												'amount': 1,
												'uses': 10,
												'equipped': False}, merge=True)
							comment.reply(f'Ta-Da! You have recieved the {high_items}. It deals {high_items_dmg} bonus damage!')
							ammount_final = gold - price
							all_users.update({'gold':ammount_final})
						if 'tuba' in comment_shop:
								pass
					f = open("processed", "a")
					f.write(comment.id + ", ")
					break

			if '!inventory' in comment.body:
				list3 = []
				try:
					user_inventory_ref = db.collection('users').document(comment.author.name)
					user_inventory = user_inventory_ref.collection('inventory').get()
					for document in user_inventory:
						list3.append(document.id)
					print(list3)
					comment.reply(f'You have the items: {list3}')
				except (AttributeError, KeyError):
					comment.reply('VirtuousVermin messed something up, let me go end him')
			#Ending the while True:
			if comment.id in processed:
				break
except:
	pass
		
				


f = open("processed.txt", "r")
processed = f.read()
pfixed = processed.split(', ')


while True:
	run()