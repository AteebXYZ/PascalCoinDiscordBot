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

async def store_price(currency):
	# Dynamically construct the URL based on the currency parameter
	url = f"https://api.coingecko.com/api/v3/simple/price?ids=pascalcoin&vs_currencies={currency}"
	response = requests.get(url)

	if response.status_code == 200:
		data = response.json()
		coin_name = list(data.keys())[0]
		
		try:
			price = data[coin_name][currency]
		
			# Update the database with the new price
			cur.execute("SELECT currency FROM price WHERE currency = ?", (currency,))
			check = cur.fetchone()
			if check:
				cur.execute("UPDATE price SET price = ? WHERE currency = ?", (price, currency))
				con.commit()
			else:
				cur.execute("INSERT INTO price VALUES(?, ?)", (price, currency))
				con.commit()
				
			
		except Exception:
			return 1


class price(Extension):
	@interactions.slash_command(name="price", description="Display the price of PascalCoin")
	@slash_option(name="currency", description="Any fiat currency, input the abreviation, 3 or 4 letters", opt_type=OptionType.STRING, required = True)
	async def price(self, ctx, currency: str):
		currency = currency.lower()
		try:			
			cur.execute("SELECT price FROM price WHERE currency = ?", (currency,))
			price = cur.fetchone()[0]
			price = float(price)
			await ctx.send(embeds = Embed(title = f"**Price:**", description = f"1 **PASC** = {price} **{currency.upper()}**\n1 **{currency.upper()}** = {round(1/price, 4)} **PASC**", color = [255, 165, 0]))
	
		except Exception as e:

			await store_price(currency)
			if await store_price(currency) == 1:
				await ctx.send("```ansi\n[1;31mInvalid currency, please try using a different fiat currency.\n```")
				return
			time.sleep(0.2)
			cur.execute("SELECT price FROM price WHERE currency = ?", (currency,))
			price = cur.fetchone()
			if price:
				price = price[0]
				await ctx.send(embeds = Embed(title = f"**Price:**", description = f"1 **PASC** = {price} **{currency.upper()}**\n1 **{currency.upper()}** = {round(1/price, 4)} **PASC**", color = [255, 165, 0]))
				
