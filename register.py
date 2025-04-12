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

class register(Extension):
	
	@interactions.slash_command(name="register", description="Register your account with Discord to unlock buying things and AI image generation.")
	
		
	async def register_cex(self, ctx):
		author = ctx.author.display_name
		cur.execute("SELECT owner FROM cex WHERE owner = ?", (author,))
		
		try:
			registered_check = cur.fetchone()[0]
			if registered_check	== author:
				await ctx.send("```ansi\n[1;31mYou are already registered on the database.\n```", ephemeral = True)
				
		except Exception:
			def random_string(length):
				return secrets.token_hex(length)
			
			def short_hash(input_string):
				hash_object = hashlib.sha256(input_string.encode())
				hex_dig = hash_object.hexdigest()
				short_hash = hex_dig[:10]
				return short_hash
				
			random_input = random_string(10)
			hashed_input = short_hash(random_input)
			
			cur.execute("INSERT INTO cex VALUES(?, ?, 0)", (author, hashed_input,))
			con.commit()
			await ctx.send(embeds = Embed(title = "Registration Complete!", description=f"For depositing, you must send PASC to **{cexaccount}** with the payload **{hashed_input}**, make sure the payload is unencrypted (select \"Dont encrypt\" (Public payload) and you set the payload type to **\"String\"** in the Pascal wallet when depositing)\n\nBy registering, you agree that the responsibility of any loss of balance due to an incorrect payload or other fault is upon YOU.", color = [255, 165, 0]), ephemeral = True)
	
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
	
