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




class balance(Extension):	
	@interactions.slash_command(name="balance", description="Display details of the balance of your account.")
	
	async def balance(self, ctx):
		global devfee	
		author = ctx.author.display_name	
		cur.execute("SELECT owner FROM cex WHERE owner = ?", (author,))	
		check = cur.fetchone()	
		if check:	
			cur.execute("SELECT balance FROM cex WHERE owner = ?", (author,))	
			balance = cur.fetchone()[0]	
			balance = float(balance)	
			devfee = float(devfee)	
			balance = round(balance, 4)	
			devfee = round(devfee, 4)	
			withdrawable = balance - (devfee + 0.0002)	
			withdrawable = round(withdrawable, 4)
			if balance == 0 :
				await ctx.send(embeds = Embed(f"You have **{balance} PASC** in your account.", color = [255, 165, 0]), ephemeral = True)
				return
			if withdrawable < 0:
				await ctx.send(embeds = Embed(f"You have **{balance} PASC** in your account, you cannot withdraw an amount this small using \"/withdraw\".", color = [255, 165, 0]), ephemeral = True)
				return
				
				
			await ctx.send(embeds = Embed(f"You have **{balance} PASC** in your account, if you want to withdraw all of it, you can only withdraw **{withdrawable} PASC** (0.0001 Pascal Fee & {devfee + 0.0001} Developer Fee)", color = [255, 165, 0]), ephemeral = True)	
				
		else:	
			await ctx.send("```ansi\n[31;1mPlease use the \"/register\" command to get started.\n```")	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
