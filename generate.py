import os, traceback
import interactions
from interactions import Embed, ChannelType, GuildText, OptionType, Extension, SlashContext, slash_command, slash_option, File, SlashCommandChoice, listen, Task, IntervalTrigger, TimeTrigger
from dotenv import load_dotenv
import json
import re
import requests
from requests.adapters import HTTPAdapter, Retry
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




def image_charge(author):
	global imagecost

	imagecost = float(imagecost)
	send = imagecost - 0.0001
	
	address = os.getenv("RPC_ADDRESS")
	port = os.getenv("RPC_PORT")
	url = f"{address}:{port}"
	headers = {"Content-Type": "application/json"}
	
	data = {
		"jsonrpc": "2.0",		
		"method": "sendto",	
		"params": {"sender": cexaccount,
					"target": devacc,
					"amount": send,
					"fee": 0.0001,
					"payload": imagepayload,
					"payload_method": "none",
					"id": 123
					}
		}
		
		
	cur.execute("SELECT balance FROM cex WHERE owner = ?", (author,))
	old = cur.fetchone()[0]
	old = float(old)
	if old < imagecost:
		return 2
	new = old - imagecost
	
	cur.execute("UPDATE cex SET balance = ? WHERE owner = ?", (new, author,))
	con.commit()
	
	
	
		
	try:
		response = requests.post(url, json=data, headers=headers)

	except Exception as e:
		traceback.print_exc()
		return 1



PRODIA_API_KEY = os.getenv('PRODIA_API_KEY')

class generate(Extension):

	@interactions.slash_command(
		name="generate",
		description="Generate an image using Prodia API",
	)
	@slash_option(name="prompt", description="Prompt for image generation", opt_type=OptionType.STRING, required=True)
	
	@slash_option(
	name="model", 
	description="The AI image model you want to use",
	opt_type=OptionType.STRING, 
	required = True,
	choices = 
	[
	SlashCommandChoice(name="Flux Schnell", value="inference.flux.schnell.txt2img.v2"),
	SlashCommandChoice(name="dreamlike-diffusion-1.0", value="dreamlike-diffusion-1.0.safetensors [5c9fd6e0]"),
	SlashCommandChoice(name="dreamlike-photoreal-2.0", value="dreamlike-photoreal-2.0.safetensors [fdcf65e7]"),
	SlashCommandChoice(name="openjourney_V4", value="openjourney_V4.ckpt [ca2f377f]"),
	SlashCommandChoice(name="Realistic_Vision_V1.4-pruned-fp16 ", value="Realistic_Vision_V1.4-pruned-fp16.safetensors [8d21810b]"),
	SlashCommandChoice(name="Realistic_Vision_V2.0", value="Realistic_Vision_V2.0.safetensors [79587710]"),
	SlashCommandChoice(name="Realistic_Vision_V4.0", value="Realistic_Vision_V4.0.safetensors [29a7afaa]"),
	SlashCommandChoice(name="Realistic_Vision_V5.0", value="Realistic_Vision_V5.0.safetensors [614d1063]"),
	SlashCommandChoice(name="sdv1_4", value="sdv1_4.ckpt [7460a6fa]"),
	SlashCommandChoice(name="v1-5-pruned-emaonly", value="v1-5-pruned-emaonly.safetensors [d7049739]"),
	])
	
	async def generate(self, ctx, prompt: str, model: str):
		await ctx.send("```ansi\n[31;1mAI image generation is currently disabled, thank you for your patience. No PASC was charged from your account.\n```")
		# author = ctx.author.display_name
		# cur.execute("SELECT owner FROM verification WHERE owner = ?", (author,))
		# checkver = cur.fetchone()
		# if checkver:
		# 	cur.execute("SELECT owner FROM cex WHERE owner = ?", (author,))
		# 	checkcex = cur.fetchone()
			
		# 	if checkcex:
				
		# 		cur.execute("SELECT user FROM image WHERE user = ?", (author,))
		# 		check = cur.fetchone()
				
		# 		if check == None:
					
		# 			cur.execute("INSERT INTO image VALUES(?, 1, 0)", (author,))
		# 			con.commit()
		# 			await ctx.send(embeds =  Embed(title = "Prodia AI Image Generator", description= f"This command generates images using Prodia, the cost of 1 image generation is 0.1 PASC, this will be deducted from your account every image generation. If you encounter any error and PASC was deducted, you may ask for a refund. **NOTE:** Any inappropriate images generated with this API that contain any explicit content will have concequences on the user. The consequence may be a permanent ban from this command. To continue, excecute the command again.\n\nYour prompt (just copy and paste it): \n{prompt}", color = [255, 165, 0]))
				
		# 		else:
		# 			cur.execute("SELECT num_prompts_day FROM image WHERE user = ?", (author,))
		# 			limitcheck = cur.fetchone()[0]
		# 			if limitcheck == 10:
		# 				await ctx.send("```ansi\n[31;1mYou have hit the limit of 10 prompts a day, come back tomorrow.\n```")
		# 				return
						
		# 			else:
		# 				charge = image_charge(author)
		# 				if charge == 2:
		# 					await ctx.send("```ansi\n[31;1mYou dont have enough PASC.\n```")
		# 					return
	
		# 				animation = await ctx.send(r"https://cdn.discordapp.com/emojis/1195341544476135454.gif?size=32")
		# 				url = "https://inference.prodia.com/v2/job"
					
		# 				job = {
		# 					"type": f"{model}",
		# 					"config": {
		# 						"prompt": f"{prompt}"
		# 					}
		# 				}
						
		# 				headers = {
		# 					"Accept": "image/png"
		# 					}
		# 				session = requests.Session()
		# 				retries = Retry(status_forcelist=Retry.RETRY_AFTER_STATUS_CODES)
		# 				session.mount('http://', HTTPAdapter(max_retries=retries))
		# 				session.mount('https://', HTTPAdapter(max_retries=retries))
		# 				session.headers.update({'Authorization': f"Bearer {PRODIA_API_KEY}"})

					
		# 				response = session.post(url, json=job, headers=headers)

		# 				if response.status_code == 200:

		# 						with open("image.png", 'wb') as file:
		# 							file.write(res.content)
		# 						await animation.edit(content=f"Prompt: {prompt}\nBy: {ctx.author.display_name}", file="image.png")
		# 						os.remove("image.png")
		# 						cur.execute("SELECT num_prompts_day FROM image WHERE user = ?", (author,))
		# 						old = cur.fetchone()[0]
		# 						old = int(old)
		# 						new = old + 1
		# 						cur.execute("UPDATE image SET num_prompts_day = ? WHERE user = ?", (new, author,))
		# 						con.commit()


			
		# 	else:
		# 		await ctx.send("```ansi\n[31;1mPlease use the \"/register\" command to get started.\n```")
		# 		return
				
		# else:
		# 	await ctx.send("```ansi\n[31;1mPlease use the \"/link_account\" command to get started.\n```")
		# 	return
