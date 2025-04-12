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




class verified_accounts(Extension):
	
	@interactions.slash_command(name="verified_accounts", description = "Display the account(s) that are verified under your name")
	@slash_option(name="visibility", description="Flex your verified accounts or no? Defaults to false", opt_type=OptionType.BOOLEAN)
	
	async def my_accounts(self, ctx, visibility: bool = False):
		total_balance = 0
		embeds = []
		author = ctx.author.display_name
		cur.execute("SELECT account FROM verification WHERE owner = ?", (author,))
		acclistdb = cur.fetchall()
		acclistformatted = [value[0] for value in acclistdb]
		
		combined = ""
		
		for value in acclistformatted:
			address = os.getenv("RPC_ADDRESS")
			port = os.getenv("RPC_PORT")
			url = f"{address}:{port}"
			
			data = {
				"jsonrpc": "2.0",
				"method": "getaccount",
				"params": {"account": value},
				"id": 123
			}
	
			headers = {"Content-Type": "application/json"}
			try:
				response = requests.post(url, json=data, headers=headers)
			except Exception as e:
				await ctx.send(nodedownmessage)
				return
			try:		
				if response.status_code == 200:
					result = json.loads(response.text)
					
					if 'result' in result:
						mainkey = result['result']
						account = mainkey['account']
						balance = mainkey['balance']
						name = mainkey['name']
						
						if name == '':
							name = "No Name."
							
						if name[0] == "#" or name[0] == "*" or name[0] == "_" :

							name = f"\{name}"
							
						total_balance = total_balance + balance
						embed = Embed(title=f"Account: {account}\nName: {name}\nBalance: {balance} PASC\n", color = [255, 165, 0])
						embeds.append(embed)
						
				
			
			except json.JSONDecodeError:
				print("error", file_name)
			except Exception as e:
				print("error", file_name)
				
		try:
			total_balance = round(total_balance, 4)
			embed = Embed(title=f"Total Balance: {total_balance} PASC", color = [255,255,255])
			embeds.append(embed)
			
			if visibility == True:
				await ctx.send("## Your accounts:", embeds = embeds)
				
				
			if visibility == False:
				await ctx.send("## Your accounts:", embeds = embeds, ephemeral = True)

				
		except Exception:
			await ctx.send("## Your accounts:", embeds = embeds, ephemeral = True)

		
