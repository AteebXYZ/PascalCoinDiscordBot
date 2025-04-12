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




class unlink_account(Extension):
	
	@interactions.slash_command(name="unlink_account", description="Unlink a PASA from your Discord account.")
	@slash_option(name="account", description="The PASA you want to unlink.", opt_type=OptionType.INTEGER, required = True)
	
	async def unlink_account(self, ctx, account: int):
		initsqlite()	
		author = ctx.author.display_name
		
		try:
			cur.execute("SELECT owner FROM verification WHERE account = ?", (account,))
			acccheck = cur.fetchone()[0]
			if author == acccheck:
				cur.execute("DELETE FROM verification WHERE account = ?", (account,))
				con.commit()
				unverrole = interactions.utils.get(ctx.guild.roles, name = f"{account}")
				print(unverrole)
				try:
					await unverrole.delete()
					await ctx.send(f"```ansi\n[32;1mAccount {account} successfully removed from database.\n```", ephemeral = True)
				except Exception as e:
					traceback.print_exc()
					await ctx.send("```ansi\n[31;1mThe bot has not been added with administrator permissions.\n```")
					return
			else:
				await ctx.send(f"```ansi\n[31;1mAccount \"{account}\" does not belong to you, if you believe this was a mistake, contact the administrator.```", ephemeral = True)
		except Exception as e:
			await ctx.send(f"```ansi\n[31;1mAccount: {account} was not found on the database or invalid account was entered.\n```", ephemeral = True)
	
