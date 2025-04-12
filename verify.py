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




class verify(Extension):
	
	@interactions.slash_command(name="verify", description="Use this to verify that your PASA has the verification number.")
	@slash_option(name="account", description="The PASA you want to verify.", opt_type=OptionType.INTEGER, required=True)
	
	async def verify(self, ctx, account: int):
		initsqlite()
		try:
			cur.execute("SELECT verified FROM verification WHERE account = ?", (account,))
			isverified = cur.fetchone()[0]
			if isverified or isverified == 0:
				if isverified == 1:
					await ctx.send(f"Account {account} already verified.", ephemeral = True)
	
					return
				else:
					cur.execute("SELECT vernumber FROM verification WHERE account = ?", (account,))
					vernumber = cur.fetchone()[0]
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
						if response.status_code:
							if response.status_code == 200:
								result = json.loads(response.text)
								
								if 'result' in result:
									mainkey = result['result']
									acctype = mainkey['type']
									if acctype == vernumber:
										cur.execute("UPDATE verification SET verified = ? WHERE account =?", (1, account,))
										owner = ctx.author.display_name
										cur.execute("UPDATE verification SET owner = ? WHERE account = ?", (owner, account,))
										con.commit()
										await ctx.send("```ansi\n[32;1mVerification successful! You may change your account type back.\n```", ephemeral = True)
										accrolecheck = interactions.utils.get(ctx.guild.roles, name=f"{account}")
										if accrolecheck == None:
											accrole = await ctx.guild.create_role(name=f"{account}", color = 16753920 )
											accroleid = accrole.id
											accroleid = int(accroleid)
											await ctx.author.add_role(accroleid)
										else:
											accroleid = accrolecheck.id
											accroleid = int(accroleid)
											await ctx.author.add_role(accroleid)
										
										verrolecheck = interactions.utils.get(ctx.guild.roles, name="Verified")
		
										
										if verrolecheck == None:
											verrole = await ctx.guild.create_role(name="Verified", hoist = True)
											verroleid = verrole.id
											await ctx.author.add_role(verroleid)
											
										else:
											
											verroleid = verrolecheck.id
											verroleid = int(verroleid)
	
											await ctx.author.add_role(verroleid)
											
		
											
		
		
									else:
										await ctx.send("```ansi\n[31;1mVerification failed.\n```", ephemeral = True)
				
							
								else:
									await ctx.send(f"```ansi\n[31;1mInvalid account number: {account}\n```", ephemeral = True)
									
						else:
							await ctx.send(nodedownmessage)
							
					except Exception as e:
						traceback.print_exc()
						await ctx.send(f"```ansi\n[31;1mSomething went wrong, please try again later.\n{e}\n```", ephemeral = True)
			else:
				await ctx.send("```ansi\n[31;1mPlease use the \"/link_account\" command first\n```", ephemeral = True)
				
	
		except Exception as e:
			await ctx.send("```ansi\n[31;1mPlease use the \"/link_account\" command first.\n```", ephemeral = True)
			traceback.print_exc()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
