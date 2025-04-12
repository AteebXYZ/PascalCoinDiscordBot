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
pascemoji = os.getenv("PASCEMOJI")
if pascemoji == None:
	pascemoji = ":coin:"
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




class account_info(Extension):
	@interactions.slash_command(name="account_info", description="Display information about a PASA")
	@slash_option(
	name="account",
	description="The PASA account number",
	opt_type=OptionType.INTEGER,
	required=True
	)
	
	async def account_info(self, ctx, account :int):
		address = os.getenv("RPC_ADDRESS")
		port = os.getenv("RPC_PORT")
		url = f"{address}:{port}"
		
		data = {
			"jsonrpc": "2.0",
			"method": "getaccount",
			"params": {"account": account},
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
					state = mainkey['state']
					name = mainkey['name']
					acctype = mainkey['type']
					
					if name == '':
						name = "No Name."
					embed = Embed(title="Account Info", color = [255,165,0])
					embed.add_field(name=":hash: Account:", value=f"```{account}```")
					embed.add_field(name=":identification_card: Name:", value=f"```{name}```")
					embed.add_field(name=f"{pascemoji} Balance:", value=f"```{balance}```")
					embed.add_field(name=":hash: Account Type", value=f"```{acctype}```")
					if state == 'listed':
						embed.add_field(name=":gear: Account State:", value=f"```{state}```")
						
						price = mainkey['price']
						selleracc = mainkey['seller_account']
						embed.add_field(name=f"{pascemoji} Price:", value=f"```{price}```")
						embed.add_field(name=":money_mouth: Seller Account:", value=f"```{selleracc}```")
						
					else:
						embed.add_field(name=":gear: Account State:", value=f"```{state}```")

					
					await ctx.send(embed=embed)
			
				else:
					await ctx.send(f"```ansi\n\u001b[1;31mInvalid account number: {account}\n```")
	
		except json.JSONDecodeError:
			await ctx.send("Error decoding JSON response from the server.")
		except Exception as e:
			await ctx.send(f"An error occurred: {e}")
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
