import os, traceback
import interactions
from interactions import Embed, ChannelType, GuildText, OptionType, Extension, SlashContext, slash_command, slash_option, File, SlashCommandChoice, listen, Task, IntervalTrigger, TimeTrigger
from dotenv import load_dotenv
import json
import re
import requests
import time
import asyncio
import random
import sqlite3
import datetime
from datetime import datetime, timedelta, timezone
import secrets
import hashlib
import binascii

file_name = os.path.basename(__file__)
load_dotenv()
bottoken=os.getenv("TOKEN")
nodedownmessage = os.getenv("NODEDOWNMESSAGE")
sqlitedblocation = os.getenv("SQLITEDBLOCATION")
apitoken = os.getenv("APITOKEN")
cexaccount = os.getenv("CEXACCOUNT")
devfee = os.getenv("DEVFEE")
devacc = os.getenv("DEVACC")
withdrawpayload = binascii.hexlify(os.getenv("WITHDRAWPAYLOAD").encode('utf-8')).decode('utf-8')
devfeepayload = binascii.hexlify(os.getenv("DEVFEEPAYLOAD").encode('utf-8')).decode('utf-8')
imagepayload = binascii.hexlify(os.getenv("IMAGEPAYLOAD").encode('utf-8')).decode('utf-8')
operation_channel = os.getenv("OPCHANNEL")
imagecost = os.getenv("IMAGECOST")
os.makedirs(os.path.dirname(sqlitedblocation), exist_ok=True)
con = sqlite3.connect(sqlitedblocation)
cur = con.cursor()



def initsqlite():
	con = sqlite3.connect(sqlitedblocation)
	cur = con.cursor()
	res = cur.execute("SELECT name FROM sqlite_master")
	check = res.fetchone() is None
	if check == True:
		cur.execute("CREATE TABLE verification(owner, account, vernumber, verified, timestamp TIMESTAMP)")
		cur.execute("CREATE TABLE data(block)")
		cur.execute("INSERT INTO data VALUES(-1)")
		cur.execute("CREATE TABLE cex(owner, hash, balance)")
		cur.execute("CREATE TABLE price(price, currency)")
		cur.execute("CREATE TABLE verifiedops(hash, optxt)")
		cur.execute("CREATE TABLE image(user, notice, num_prompts_day)")

		con.commit()
	else:
		return
		
initsqlite()

blockcount = None
dbblock = None
response = None
blocks_missed = None
dbblockcheck = 0


class events(Extension):	
	@Task.create(IntervalTrigger(minutes=10))
	async def update_price(self):
	
		# Fetch all distinct currencies from the price table
		cur.execute("SELECT DISTINCT currency FROM price")
		currencies = cur.fetchall()
	
		for currency in currencies:
			# Dynamically construct the URL based on the currency parameter
			url = f"https://api.coingecko.com/api/v3/simple/price?ids=pascalcoin&vs_currencies={currency[0]}"
			response = requests.get(url)
	
			if response.status_code == 200:
				data = response.json()
				coin_name = list(data.keys())[0]
				price = data[coin_name][currency[0]]
	
				# Update the database with the new price
				cur.execute("SELECT currency FROM price WHERE currency = ?", (currency[0],))
				check = cur.fetchone()
				if check:
					cur.execute("UPDATE price SET price = ? WHERE currency = ?", (price, currency[0]))
				else:
					cur.execute("INSERT INTO price VALUES(?, ?)", (price, currency[0]))
				con.commit()
				
	
	@Task.create(IntervalTrigger(seconds=30))	
	async def delete_expired(self):

		now = datetime.now(timezone.utc)
		cutoff = now - timedelta(hours=2)
		cur.execute("DELETE FROM verification WHERE timestamp < ? AND verified = 0", (cutoff,))
		con.commit()
		
	
	
	
	
	
	
	@Task.create(IntervalTrigger(seconds=3))
	async def update_balance(self):

			
		global blockcount
		global dbblock
		global response
		global blocks_missed
		global dbblockcheck
		
	
		address = os.getenv("RPC_ADDRESS")
		port = os.getenv("RPC_PORT")
		url = f"{address}:{port}"
		headers = {"Content-Type": "application/json"}
		
		blockdata = {
			"jsonrpc": "2.0",
			"method": "getblockcount",
			"id": 123
			}
			
		try:
			response = requests.post(url, json=blockdata, headers=headers)
	
		except Exception as e:
			print(e)
			print(f"Something went wrong, Pascal wallet/daemon is not running on your system")
			return
			
			
		try:		

			if response.status_code == 200:
				blockcount = json.loads(response.text)['result'] -1
				cur.execute("SELECT block FROM data")
				newcheck = cur.fetchone()[0]
				newcheck = int(newcheck)
	
				
				if newcheck == -1:
					cur.execute("UPDATE data SET block = ?", (blockcount,))
					con.commit()
					return
				
				
				if dbblockcheck == 0:
					cur.execute("SELECT block FROM data")
					dbblock = cur.fetchone()[0]
					dbblock = int(dbblock) 
					blocks_missed = blockcount - dbblock
					blocks_missed = blocks_missed 
					dbblockcheck = 1
				
				if blocks_missed < 0:
					cur.execute("UPDATE data SET block = ?", (blockcount,))
					blocks_missed = 0
					con.commit()
					
				if blocks_missed > 0:
					dbblockcheck = 0

				
				if blocks_missed == 0:	
					dbblockcheck = 0
					pass

						
				else:
	
					if blocks_missed == 0:
						dbblockcheck = 0
						pass

					else:
						blocks_missed = blocks_missed - 1
						cur.execute("SELECT block FROM data")
						old = cur.fetchone()[0]
						old = int(old)
						new = old + 1
						cur.execute("UPDATE data SET block = ?", (new,))
						con.commit()
						cur.execute("SELECT block FROM data")
						dbblock = cur.fetchone()[0]
						dbblock = int(dbblock) 
						
						data = {
							"jsonrpc": "2.0",
							"method": "getblockoperations",
							"params": {"block": dbblock},
							"id": 123
							}
						
						try:
							response = requests.post(url, json=data, headers=headers)
						
						except Exception as e:
							traceback.print_exc()
						
						
						try:		
							if response.status_code == 200:
								result = json.loads(response.text)
								acc = cexaccount
								
					
								
						
								if 'result' in result:
									if dbblock != blockcount:
										print(f"Syncing database with blockchain... Block {dbblock + 1} out of {blockcount}")
									num_operations = len(result['result']) 
	
									for operation in result['result']:
										if operation['optype'] == 1 and f"{acc}" in f"{operation['receivers'][0]['account']}":
											print(operation['optxt'])
											receiver = str(operation['receivers'][0]['account'])
											acc = str(acc)
											senders = operation['senders']
											receivers = operation['receivers']
											
											
											
											payload = operation['payload']
											payloadbdata = bytes.fromhex(payload)
											payloadunc = payloadbdata.decode('utf-8')
											deducted = operation['amount']
											try:
		
												cur.execute("SELECT balance FROM cex WHERE hash = ?", (payloadunc,))
												old_balance = cur.fetchone()[0]
												deposited = deducted - deducted - deducted
												deposited = float(deposited)
												old_balance = float(old_balance)
												
		
												new_balance = old_balance + deposited
												
												ophash = operation['ophash']
												
											
												try:
													
													cur.execute("SELECT hash FROM verifiedops WHERE hash = ?", (ophash,))
	
													
													opexists = cur.fetchone()
													if opexists:
														return
													
													else:
														author = senders[0]['account']
														channel = await self.bot.fetch_channel(operation_channel)
														optxt = operation['optxt']
														
														cur.execute("UPDATE cex SET balance = ? WHERE hash = ?", (new_balance, payloadunc,))
														
														cur.execute("INSERT INTO verifiedops VALUES(?, ?)", (ophash, optxt,))
														
														cur.execute("SELECT owner FROM verification WHERE account = ?", (author,))
														owner = cur.fetchone()
														if owner:
															owner = owner[0]
															await channel.send(embeds = Embed(f"{owner} deposited {receivers[0]['amount']} PASC", color = [255,165,0]))
														
														else:
															await channel.send(embeds = Embed(f"{senders[0]['account']} deposited {receivers[0]['amount']} PASC", color = [255,165,0]))
		
												except Exception as e:
													traceback.print_exc()
												
		
											except Exception as e:
												print(f"Payload incorrect: {e}")
		
		
						
						
						except json.JSONDecodeError:
							print("Error decoding JSON response from the server.")
						except Exception as e:
							print(f"An error occurred: {e}")
		
						except Exception as e:
							traceback.print_exc()
	
				if dbblock > blockcount:
					print(f"\n\n\n{blockcount}")
					print("RESET")
					print(blocks_missed)
					print (f"{dbblock}\n\n\n")	
					
					dbblock = blockcount - 1
					blocks_missed = blockcount - dbblock
					cur.execute("UPDATE data SET block = ?", (dbblock,))
					con.commit()
					dbblockcheck = 0
						
				
		except Exception as e:
			traceback.print_exc()
		
		
	@Task.create(TimeTrigger(hour=12))
	async def reset_image(self):
	
		cur.execute("UPDATE image SET num_prompts_day = 0")
		con.commit()
	
	@listen()
	async def on_ready(self):
		print(self.bot.user.display_name)
		
		self.update_price.start()
		self.delete_expired.start()
		self.update_balance.start()
