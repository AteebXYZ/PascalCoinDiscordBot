import os, traceback
import interactions
from interactions import ChannelType, GuildText, OptionType, Extension, SlashContext, slash_command, slash_option, File, SlashCommandChoice, listen, Task, IntervalTrigger, TimeTrigger
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


class request_pasa(Extension):
	@interactions.slash_command(name="request_pasa", description="Request a PASA through dispenser.pascalcoin.org")
	@slash_option(name="public_key", description="Your wallet public key", opt_type = OptionType.STRING, required= True)
	
	async def request_pasa(self, ctx, public_key: str):
		url = "https://dispenser.pascalcoin.org/api.php"
	
		data = {
			'request': 'requestPASADiscordAPI',
			'handle': f'{ctx.author.display_name}',
			'token': apitoken,
			'publicKey' : f'{public_key}'
		}
		
		
		response = requests.post(url, data=data)
	
		if response.status_code == 200:
			data = json.loads(response.text)
			if data['status'] == 1:
				await ctx.send(f"```ansi\n[31;1mError: {data['error']}\n```", ephemeral = True)
			if data['status'] == 0:
				await ctx.send(f"```ansi\n[32;1m{data['data']['message']}\n```", ephemeral = True)
