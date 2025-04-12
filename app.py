import os, traceback
import interactions
from interactions import StringSelectMenu, Embed, ChannelType, GuildText, OptionType, Extension, SlashContext, slash_command, slash_option, File, SlashCommandChoice, listen, Task, IntervalTrigger, TimeTrigger
from interactions.ext.paginators import Paginator
from interactions.ext.jurigged import Jurigged
from interactions.api.events import Component
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
import jurigged

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

def adapt_datetime(ts):
	return ts.strftime("%Y-%m-%d %H:%M:%S.%f")

sqlite3.register_adapter(datetime, adapt_datetime)


bot = interactions.Client(token=bottoken)
bot.load_extension("price")
bot.load_extension("account_info")
bot.load_extension("operation_finder")
bot.load_extension("link_account")
bot.load_extension("verify")
bot.load_extension("verified_accounts")
bot.load_extension("unlink_account")
bot.load_extension("register")
bot.load_extension("withdraw")
bot.load_extension("deposit")
bot.load_extension("generate")
bot.load_extension("balance")
bot.load_extension("request_pasa")
bot.load_extension("time_events")








@interactions.slash_command(name = "help", description="Display information on how to use this bot.")

async def help(ctx):
	
	
	embeds = [
		Embed(title = "/price", description = "This command diplays the current price of PascalCoin, you must input a fiat currency with it too, for example /price usd.", color = 16753920),
		
		Embed(title = "/account_info", description = "This diplays the information of the PASA number you enter, for example 2173, note that you dont put in the last 2 digits (2173-98), only the digits before the '-'", color = 16753920), 
		
		Embed(title = "/operation_finder", description = "This displays the information about an operation in the Pascal blockchain using its operation hash, for example:\n\n\"49D40C007D080000F9000000BB5F677D0F6E80F9CC345374A95681B1921D7DDC\"", color = 16753920),
		
		Embed(title = "/link_account", description = "/link_account\n\nThis is basically step 1 of the /verify command. You execute the command by inputting the PASA you want to link to your Discord account, then you set the number given to you by the command as your account type and proceed by using /verify.", color = 16753920), 
		
		Embed(title= "/verify", description = "This is the last step of the verification process, you exexute this after using /link_account, by verifying your account, you can access features such as:\n\n\u2022 Depositing PASC so you can pay for AI image generation fees (currently not active)\n\u2022 Buying virtual discord ranks and items from the shop\n\u2022 Gifting registered users PASC.", color = 16753920),
		
		Embed(title = "/verified_accounts", description = "This command displays the information about the account(s) that you verified using /verify.", color = 16753920), 
		
		Embed(title = "/unlink_account", description = "This removes your PASA from the verified accounts list, it will also remove the role with the PASA number you unlinked.", color = 16753920),
		
		Embed(title = "/register", description = "This allows you to deposit PASC into an account with a given secret code, you will be able to use this PASC for things like AI image generation and buying items.", color = 16753920), 
		
		Embed(title = "/withdraw", description = "This command allows you to withdraw PASC from your account, if the amount field is 'all', it will withdraw all the PASC availabe in your account", color = 16753920),
		
		Embed(title="/deposit", description = "Display the instructions on how to deposit into your registered account.", color = 16753920),
		
		Embed(title="/generate", description = "This command allows you to generate AI images for a fee that will be deducted from your account on each generation. You only have 10 prompts a day. This command requires you to have at least one verified PASA linked with your Discord account and to be registered for PASC deposits.", color = 16753920),
		
		Embed(title = "/balance", description = "This command displays the balance in your registered account.", color = 16753920)
		]
	
	
	paginator = Paginator.create_from_embeds(bot, *embeds)
	paginator.show_back_button = False
	paginator.show_next_button = False
	paginator.show_last_button = False
	paginator.show_first_button = False
	paginator.show_select_menu = True
	
	await paginator.send(ctx, ephemeral = True)


@interactions.slash_command(name = "transfer", description="Transfer a given amount of PASC to another user, they must be registered.")
@slash_option(name="receiver", description="Who will the PASC go to", opt_type=OptionType.MENTIONABLE, required = True)
@slash_option(name="amount", description="The amount of PASC", opt_type=OptionType.STRING, required = True)

async def transfer(ctx, receiver, amount):
	author = ctx.author.display_name
	if receiver.display_name == author:
		await ctx.send("```ansi\n[1;31mYou cant send yourself PASC\n```", ephemeral = True)
		return

	if receiver.display_name == bot.user.display_name:
		randint = random.randint(0, 1)
		if randint == 0:
			await ctx.send("```ansi\n[1;33mDid you really just try sending PASC to me?\n```", ephemeral = True)
			return
		
		if randint == 1:
			await ctx.send("```ansi\n[1;33mWhy would you try sending PASC to me? Im just a bot in a server.\n```", ephemeral = True)
			return
		
	try:
		amount = float(amount)
	except Exception:
		await ctx.send(f"```ansi\n[1;31mYou entered an invalid value for \"amount\", please enter a valid amount of pasc.\n```", ephemeral = True)
		return
	
	if amount < 0:
		await ctx.send(f"```ansi\n[1;31mYou cant send a negative amount of PASC.\n```", ephemeral = True)
		return
	
	if amount == 0:
		await ctx.send(f"```ansi\n[1;31mYou cant send 0 PASC.\n```", ephemeral = True)
		return

	
	cur.execute("SELECT owner FROM cex WHERE owner = ?", (author,))
	registercheck = cur.fetchone()
	if registercheck is None:
		await ctx.send(f"```ansi\n[1;31mYou are not registered to be sending PASC, please use \"/register\" to continue.\n```", ephemeral = True)

	else:
		cur.execute("SELECT owner FROM cex WHERE owner = ?", (receiver.display_name,))
		registercheck = cur.fetchone()

		if registercheck is None:
			await ctx.send(f"```ansi\n[1;31mThe user \"{receiver.display_name}\" is not registered, they must use \"/register\" to receive PASC\n```", ephemeral = True)

		else:
			cur.execute("SELECT balance FROM cex WHERE owner = ?", (author,))
			balance = round(float(cur.fetchone()[0]), 4)

			if amount > balance:
				await ctx.send(f"```ansi\n[1;31mYou tried to give {receiver.display_name} {amount} PASC, but you only have {balance} PASC available.\n```", ephemeral = True)

			else:
				sender_new_balance = balance - amount
				cur.execute("UPDATE cex SET balance = ? WHERE owner = ?", (sender_new_balance, author,))
				cur.execute("SELECT balance FROM cex WHERE owner = ?", (receiver.display_name,))
				receiver_old_balance = round(float(cur.fetchone()[0]), 4)
				receiver_new_balance = receiver_old_balance + amount

				
				cur.execute("UPDATE cex SET balance = ? WHERE owner = ?", (receiver_new_balance, receiver.display_name,))
				con.commit()
				await ctx.send(f"```ansi\n[1;32mSuccess! you transferred {amount} PASC, to {receiver.display_name}.\n```", ephemeral = True)



bot.load_extension("interactions.ext.jurigged", poll = 1)
bot.start()
