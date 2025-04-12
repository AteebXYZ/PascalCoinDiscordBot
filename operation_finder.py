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




class operation_info(Extension):
	
	@interactions.slash_command(name="operation_finder", description="Find an operation using the OpHash")
	@slash_option(
	name = "ophash",
	description = "The operation hash",
	opt_type=OptionType.STRING,
	required = True
	)
	
	async def operation_info(self, ctx, ophash: str):
		address = os.getenv("RPC_ADDRESS")
		port = os.getenv("RPC_PORT")
		url = f"{address}:{port}"
		data = {
			"jsonrpc": "2.0",
			"method": "findoperation",
			"params": {"ophash": ophash},
			"id": 123
		}
		
		headers = {"Content-Type": "application/json"}
		try:
			response = requests.post(url, json=data, headers=headers)
		except Exception as e:
			await ctx.send(nodedownmessage)
			return
		
		try:
			result = json.loads(response.text)
			if response.status_code == 200:
				
				
				if 'result' in result:
					mainkey = result['result']
					block = mainkey['block']
					account = mainkey['account']
					signer_account = mainkey['signer_account']
					optxt = mainkey['optxt']
					fee = mainkey['fee']
					enc_payload = mainkey['payload']
					payload = bytes.fromhex(enc_payload).decode('utf-8')
					if payload == "":
						payload = "No payload."
					
					
					embed = Embed(title="Operation Finder", color = [255, 165, 0])
					embed.add_field(name=":hash: Hash:", value=f"```{ophash}```")
					embed.add_field(name=":ice_cube: Block:", value=f"```{block}```")
					embed.add_field(name=":hash: Account:", value=f"```{account}```")
					embed.add_field(name=":hash: Signer Account:", value=f"```{signer_account}```")
					embed.add_field(name=":triangular_flag_on_post: Operation:", value=f"```{optxt}```")
					embed.add_field(name=":package: Payload:", value=f"```{payload}```")
					embed.add_field(name=f"{pascemoji} Fee:", value=f"```{fee}```")
					
					
					await ctx.send(embeds = embed)
				else:
					await ctx.send(f"```ansi\n\u001b[1;31mInvalid OpHash: {ophash}\n```")
					
				
		except requests.exceptions.ConnectionError as e:
			traceback.print_exc()
		except requests.exceptions.ConnectionRefusedError as e:
			traceback.print_exc()
		except Exception as e:
			traceback.print_exc()
	
	
	
	
	
	
	
	
	
	
	
	
	
