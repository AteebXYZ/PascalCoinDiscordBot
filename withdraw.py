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

def decimals(value):
	value_str = str(value)
	
	parts = value_str.split('.')
	
	if len(parts) == 2 and len(parts[1]) >= 5:
		return True
	else:
		return False

	

fee = None

class withdraw(Extension):
	@interactions.slash_command(name="withdraw", description = "Withdraw a given amount of PASC from your account.")
	@slash_option(name="amount", description="The amount of PASC you want to withdraw", opt_type=OptionType.STRING, required = True)
	@slash_option(name="account", description="The account to which the PASC will go to.", opt_type=OptionType.INTEGER, required = True)
	
	async def withdraw(self, ctx, amount: str, account: int):
		global fee
		global devfee
		global devacc
		author = ctx.author.display_name
		cur.execute("SELECT owner FROM cex WHERE owner = ?", (author,))
		registered_check = cur.fetchone()
		if registered_check:
			cur.execute("SELECT balance FROM cex WHERE owner = ?", (author,))
			current_balance = cur.fetchone()[0]
			cur.execute("SELECT balance FROM cex WHERE owner = ?", (author,))
			dbbalance = cur.fetchone()[0]
			current_balance = float(current_balance)
	
	
			devfee = float(devfee)
			fee = devfee + 0.0001
			current_balance = current_balance - 0.0001 - fee 
			current_balance = round(current_balance, 4)
			withdrawal_limit = fee + 0.0002
			try:
				if amount == 'all':
					pass
				else:
					amount = float(amount)
			except Exception:
				await ctx.send("```ansi\n\u001b[1;31mInvalid amount to withdraw, please check your input.\n```", ephemeral = True)
				return
			
			
			if amount == 'all':
				amount = current_balance
			if decimals(amount) == True:
				await ctx.send("```ansi\n\u001b[1;31mYou cant withdraw an amount with 5 decimal places\n```", ephemeral = True)
				return
			if current_balance < 0:
				await ctx.send(f"```ansi\n\u001b[1;31mYou only have {dbbalance} PASC in your account, you cant withdraw {amount} PASC\n```", ephemeral = True)
				return
			if amount < 0 or amount == 0:
				await ctx.send("```ansi\n\u001b[1;31mYou cant withdraw 0 PASC or a negative amount of PASC.\n```", ephemeral = True)
				return
			if amount < withdrawal_limit:
				await ctx.send(f"```ansi\n\u001b[1;31mThe minimum withdrawal amount is {withdrawal_limit}\n```", ephemeral = True)
				return
			if amount > current_balance :
				await ctx.send(f"```ansi\n\u001b[1;31mYou can only withdraw {current_balance} PASC from your account (0.0001 Pascal Fee & {fee} Developer Fee), you tried to withdraw {amount} PASC\n```", ephemeral = True)
				return
	
			else:
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
				
				try:
					if response.status_code == 200:
						result = json.loads(response.text)
						if 'result' in result:
							
							data = {
								"jsonrpc": "2.0",
								"method": "sendto",
								"params": {"sender": cexaccount,
											"target": account,
											"amount": amount,
											"fee": 0.0001,
											"payload": withdrawpayload,
											"payload_method": "none",
											"id": 123
											}
								}
							headers = {"Content-Type": "application/json"}
							
							
							try:
								response = requests.post(url, json=data, headers=headers)
								feesend = fee - 0.0001
								data = {
									"jsonrpc": "2.0",
									"method": "sendto",
									"params": {"sender": cexaccount,
												"target": devacc,
												"amount": feesend,
												"fee": 0.0001,
												"payload": devfeepayload,
												"payload_method": "none",
												"id": 123
												}
										}
								headers = {"Content-Type": "application/json"}
								try:
									response = requests.post(url, json=data, headers=headers)
	
									new_balance = current_balance - amount
									cur.execute("UPDATE cex SET balance = ? WHERE owner = ?", (new_balance, author))
									con.commit()
									cur.execute("SELECT balance FROM cex WHERE owner = ?", (author,))
									current_balance = cur.fetchone()[0]
									current_balance = round(current_balance, 4)
	
									await ctx.send(f"```ansi\n\u001b[1;32mSuccess! you withdrew {amount} PASC, you  have {current_balance} PASC remaining in your account.\n```", ephemeral = True)
									channel = await self.bot.fetch_channel(operation_channel)
									await channel.send(embeds = Embed(f"{author} withdrew {amount} PASC", color = [255,165,0]))
								except Exception as e:
									traceback.print_exc()
									
							except Exception as e:
								await ctx.send(nodedownmessage)
								
	
							
							
						else:
							await ctx.send(f"```ansi\n\u001b[1;31mInvalid account: {account}\n```")
				except Exception as e:
					traceback.print_exc()	
		else:
			await ctx.send("```ansi\n\u001b[1;31mUse the \"/register\" command to get started.\n```")
