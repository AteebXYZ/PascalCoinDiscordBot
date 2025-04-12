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




class link_account(Extension):
	
	@interactions.slash_command(name="link_account", description="Link a PASA with your Discord ID using verification")
	@slash_option(name="account", description="The PASA you want to link to Discord", opt_type=OptionType.INTEGER, required = True)
	
	async def link_account(self, ctx, account : int):
		initsqlite()
	
		random_number = random.randint(1, 40000)
		timestamp = datetime.now(timezone.utc)
	
		cur.execute("SELECT * FROM verification WHERE account = ?", (account,))
		exists = cur.fetchone()
		if exists:
			cur.execute("SELECT verified FROM verification WHERE account = ?", (account,))
			verified = cur.fetchone()[0]
			if verified == 1:
				await ctx.send("```ansi\n[31;1mAccount already verified\n```", ephemeral = True)
				return
			else:
				cur.execute("SELECT vernumber FROM verification WHERE account = ?", (account,))
				vernumber = cur.fetchone()[0]
				await ctx.send(f"```ansi\n[31;1mSet {vernumber} as your account type.\n```", ephemeral = True)
				return
		
		cur.execute(f"INSERT INTO verification VALUES(0, ?, ?, 0, ?)", (account, random_number, timestamp))
		con.commit()
		await ctx.send(f"```ansi\n[32;1mYou are going to link the PASA: {account}, by setting its account type to:\n\n{random_number}\n\nUse the command \"/verify\" to successfully link your PASA to your Discord account. Note: You have 2 hours to verify the account or else you have to get a new verification number.\n```", ephemeral = True)
		
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
