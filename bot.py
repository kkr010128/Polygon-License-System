import discord, os, sqlite3, datetime, uuid, json, zipfile, requests
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import CommandNotFound
from discord.ext.commands import Bot
from discord.ext.commands import has_permissions, CheckFailure
import random
import os
import asyncio
import string
from datetime import datetime
import glob, shutil

INTENTS = discord.Intents.all()

client = commands.Bot(command_prefix = ['/ ', '#'], intents=INTENTS)
webhook_url = "https://discord.com/api/webhooks/your-webhook-url"

@client.event
async def on_ready():
	print('PLS 로그인 완료')

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		print("COMMAND NOT FOUND")
	elif isinstance(error, commands.CommandOnCooldown):
		embed=discord.Embed(title=":exclamation: 너무 빨라요! :exclamation:", description="{:.2f}초 뒤에 다시 시도해주세요!".format(error.retry_after), color=0xff2f2f)
		await ctx.send("<@!" + str(ctx.author.id) + ">", embed=embed)
	elif "required argument that is missing" in str(error):
		embed=discord.Embed(title=":x: 명령어가 잘못되었습니다.", description="제대로 사용한게 맞는지 확인해주세요!", color=0xff2f2f)
		await ctx.send("<@!" + str(ctx.author.id) + ">", embed=embed)
	elif isinstance(error, CheckFailure):
		embed=discord.Embed(title=":x: 권한이 없습니다.", description="명령어를 사용할 수 있는 권한을 소지하고있는지 확인해주세요!", color=0xff2f2f)
		await ctx.send("<@!" + str(ctx.author.id) + ">", embed=embed)
	else:
		await ctx.send("*오류가 발생했습니다.*\n\n``" + str(error) + "``")

@client.command(name='log')
@has_permissions(administrator=True)
async def logging(ctx, amount=100):
    print('PLS AUTH')
    await ctx.send("> POLYGON AUTH 호스트의 콘솔로 로그가 출력되었습니다.")

@client.command(name="라이센스", aliases=['license'])
@has_permissions(administrator=True)
async def _licenseregister(ctx, *args):
	if args[0] == "발급" or args[0] == "register":
		connection = sqlite3.connect('database.db')
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()

		cursor.execute('SELECT * FROM polygon_manager WHERE serverName = "' + args[1] + '"')
		rows = cursor.fetchall()
		if len(rows) == 0:
			license = str(uuid.uuid4())
			cursor.execute("INSERT INTO `polygon_manager` (`key`, `HWID`, `serverName`, `allowModels`, `banned`, `discordId`) VALUES ('" + license + "', 'none', '" + str(args[1]) + "', '[]', 0, '" + str(args[2]) + "');")
			connection.commit()

			embed=discord.Embed(title="라이센스가 발급되었습니다.", description="서버 이름: " + str(args[1]) + "\n\n**발급된 라이센스: " + license + "**", color=0x05ff37)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply("라이센스: " + license,embed=embed)		
		else:
			embed=discord.Embed(title="! 오류", description="이미 등록된 서버 입니다.", color=0xff0505)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)

		connection.close()
	elif args[0] == "삭제" or args[0] == "unregister" and ctx.author.id == AUTHOR_ID:
		connection = sqlite3.connect('database.db')
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()

		cursor.execute('SELECT * FROM polygon_manager WHERE key = "' + args[1] + '"')
		rows = cursor.fetchall()
		if len(rows) > 0:
			cursor.execute('DELETE FROM polygon_manager WHERE key = "' + args[1] + '"')
			connection.commit()

			embed=discord.Embed(title="라이센스 키가 삭제되었습니다.", description="**대상 라이센스: " + args[1] + "**", color=0x05ff37)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)
		else:
			embed=discord.Embed(title="! 오류", description="라이센스 키를 찾을 수 없거나 접근 권한이 없습니다.", color=0xff0505)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)

		connection.close()
	elif args[0] == "리소스추가" or args[0] == "addrsc" and ctx.author.id == AUTHOR_ID:
		connection = sqlite3.connect('database.db')
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()

		cursor.execute('SELECT * FROM polygon_manager WHERE discordId = "' + args[1] + '"')
		rows = cursor.fetchall()
		if len(rows) > 0:
			rows = rows[0]
			allowModels = json.loads(rows[4])
			allowModels.append(args[2])
			cursor.execute("UPDATE polygon_manager SET allowModels = '" + json.dumps(allowModels) + "' WHERE discordId = '" + args[1] + "'")
			connection.commit()

			embed=discord.Embed(title="해당 사용자의 라이센스에 리소스를 추가했습니다.", description="**대상 사용자: " + "<@" + args[1] + ">" + "**\n\n**현재 등록된 리소스: " + json.dumps(allowModels) + "**", color=0x05ff37)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)
		else:
			embed=discord.Embed(title="! 오류", description="라이센스 키를 찾을 수 없거나 접근 권한이 없습니다.", color=0xff0505)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)

		connection.close()
	elif args[0] == "리소스제거" or args[0] == "delrsc" and ctx.author.id == AUTHOR_ID:
		connection = sqlite3.connect('database.db')
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()

		cursor.execute('SELECT * FROM polygon_manager WHERE discordId = "' + args[1] + '"')
		rows = cursor.fetchall()
		if len(rows) > 0:
			rows = rows[0]
			allowModels = json.loads(rows[4])
			try:
				allowModels.remove(args[2])
				cursor.execute("UPDATE polygon_manager SET allowModels = '" + json.dumps(allowModels) + "' WHERE discordId = '" + args[1] + "'")
				connection.commit()

				embed=discord.Embed(title="해당 사용자의 라이센스에서 리소스를 제거했습니다.", description="**대상 사용자: " + "<@" + args[1] + ">" + "**\n\n**현재 등록된 리소스: " + json.dumps(allowModels) + "**", color=0x05ff37)
				embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
				embed.set_footer(text="Polygon")
				await ctx.reply(embed=embed)
			except:
				embed=discord.Embed(title="! 오류", description="추가되어있지 않은 리소스 입니다.\n\n**현재 등록된 리소스: " + json.dumps(allowModels) + "**", color=0xff0505)
				embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
				embed.set_footer(text="Polygon")
				await ctx.reply(embed=embed)
		else:
			embed=discord.Embed(title="! 오류", description="라이센스 키를 찾을 수 없거나 접근 권한이 없습니다.", color=0xff0505)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)


		connection.close()
	elif args[0] == "목록" or args[0] == "list":
		connection = sqlite3.connect('database.db')
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()

		cursor.execute('SELECT * FROM polygon_manager')
		rows = cursor.fetchall()
		if len(rows) > 0:
			msg = ""
			a = 0
			for i in rows:
				msg = msg + "\n[" + rows[a][3] + "] / " + str(rows[a][5]) + " / " + rows[a][4]
				a = a + 1
			await ctx.reply("```css\n" + msg + "```")
		else:
			embed=discord.Embed(title="! 오류", description="등록된게 없습니다.", color=0xff0505)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)

		connection.close()
	elif args[0] == "찾기" or args[0] == "find":
		connection = sqlite3.connect('database.db')
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()

		cursor.execute('SELECT * FROM polygon_manager WHERE discordId = "' + args[1] + '"')
		rows = cursor.fetchall()
		if len(rows) > 0:
			msg = ""
			a = 0
			for i in rows:
				msg = msg + "\n[" + rows[a][3] + "] / " + rows[a][1] + " / " + str(rows[a][2]) + " / " + str(rows[a][6]) + " / " + str(rows[a][5]) + " / " + rows[a][4]
				a = a + 1
			await ctx.reply("```css\n" + msg + "```")
		else:
			embed=discord.Embed(title="! 오류", description="등록된게 없습니다.", color=0xff0505)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)

		connection.close()
	elif args[0] == "언밴" or args[0] == "unban" and ctx.author.id == AUTHOR_ID:
		connection = sqlite3.connect('database.db')
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()

		cursor.execute('SELECT * FROM polygon_manager WHERE discordId = "' + args[1] + '"')
		rows = cursor.fetchall()
		if len(rows) > 0:
			cursor.execute('UPDATE polygon_manager SET banned = "0" WHERE discordId = "' + args[1] + '"') 
			connection.commit()

			embed=discord.Embed(title="대상의 라이센스의 차단이 해제되었습니다.", description="**대상 사용자: "+ "<@" + args[1] + ">" + "**", color=0x05ff37)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)
		else:
			embed=discord.Embed(title="! 오류", description="디스코드 아이디를 찾을 수 없거나 접근 권한이 없습니다.", color=0xff0505)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)

		connection.close()
	elif args[0] == "밴" or args[0] == "ban" and ctx.author.id == AUTHOR_ID:
		connection = sqlite3.connect('database.db')
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()

		cursor.execute('SELECT * FROM polygon_manager WHERE discordId = "' + args[1] + '"')
		rows = cursor.fetchall()
		if len(rows) > 0:
			cursor.execute('UPDATE polygon_manager SET banned = "1" WHERE discordId = "' + args[1] + '"') 
			connection.commit()

			embed=discord.Embed(title="대상의 라이센스가 차단되었습니다.", description="**대상 사용자: "+ "<@" + args[1] + ">" + "**", color=0x05ff37)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)
		else:
			embed=discord.Embed(title="! 오류", description="디스코드 아이디를 찾을 수 없거나 접근 권한이 없습니다.", color=0xff0505)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)

		connection.close()
	elif args[0] == "resethwid" and ctx.author.id == AUTHOR_ID:
		connection = sqlite3.connect('database.db')
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()

		cursor.execute('SELECT * FROM polygon_manager WHERE discordId = "' + args[1] + '"')
		rows = cursor.fetchall()
		if len(rows) > 0:
			cursor.execute('UPDATE polygon_manager SET hwid = "none" WHERE discordId = "' + args[1] + '"')
			connection.commit()

			embed=discord.Embed(title="HWID가 초기화 되었습니다.", description="**대상 라이센스: " + args[1] + "**", color=0x05ff37)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)
		else:
			embed=discord.Embed(title="! 오류", description="라이센스 키를 찾을 수 없거나 접근 권한이 없습니다.", color=0xff0505)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)

		connection.close()
            
@client.command(name="리소스등록", aliases=['uploadrsc'])
@has_permissions(administrator=True)
async def _resourceregister(ctx, arg1):
	if ctx.author.id == AUTHOR_ID:
		try:
			await ctx.message.attachments[0].save(arg1 + ".zip")
			try:
				shutil.rmtree(r"./models/" + arg1)
			except:
				pass
			with zipfile.ZipFile("./" + arg1 + ".zip", 'r') as zip_ref:
				zip_ref.extractall("./models/" + arg1)
			os.remove("./" + arg1 + ".zip")
			embed=discord.Embed(title="등록 성공!.", description="등록을 완료했습니다.", color=0x05ff37)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)
		except:
			embed=discord.Embed(title="! 오류", description="파일을 업로드하세요.", color=0xff0505)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)
	else:
		await ctx.send('권한이 없습니다.')
		
@client.command(name="더미리소스등록", aliases=['uploadrscdummy'])
@has_permissions(administrator=True)
async def _resourcedummyregister(ctx, arg1):
	if ctx.author.id == AUTHOR_ID:
		
		try:
			await ctx.message.attachments[0].save(arg1 + ".zip")
			try:
				shutil.rmtree(r"./models_dummy/" + arg1)
			except:
				pass
			with zipfile.ZipFile("./" + arg1 + ".zip", 'r') as zip_ref:
				zip_ref.extractall("./models_dummy/" + arg1)
			os.remove("./" + arg1 + ".zip")
			embed=discord.Embed(title="등록 성공!.", description="Dummy 등록을 완료했습니다.", color=0x05ff37)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)
		except:
			embed=discord.Embed(title="! 오류", description="Dummy 파일을 업로드하세요.", color=0xff0505)
			embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
			embed.set_footer(text="Polygon")
			await ctx.reply(embed=embed)
	else:
		await ctx.send('권한이 없습니다.')
            
@client.command(name="리소스목록", aliases=['listrsc'])
@has_permissions(administrator=True)
async def _resourcelist(ctx):
	l = glob.glob("./models/*")
	msg = ""
	a = 0
	for i in l:
		msg = msg + "\n[" + l[a].replace("./models/", "") + "]"
		a = a + 1
	await ctx.reply("```css\n" + msg + "```")

@client.command(name="모델링")
async def _model(ctx, *args):
	if args[0] == "라이센스":
		connection = sqlite3.connect('database.db')
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()

		cursor.execute('SELECT * FROM polygon_manager WHERE discordId = ' + str(ctx.author.id) + ' LIMIT 1')
		rows = cursor.fetchall()
		if len(rows) > 0:
			msg = ""
			a = 0
			for i in rows:
				msg = msg + "\n[" + rows[a][3] + "] / " + rows[a][1] + " / " + rows[a][4]
				a = a + 1
			await ctx.reply("> DM으로 라이센스 정보가 전송되었습니다.")
			await ctx.author.send("구매한 파일을 다운받으시려면 다음 명령어를 사용해주세요!\n> \n> 1. `/ 모델링 라이센스` - 보유하고 계신 라이센스와 리소스 목록을 전송합니다.\n> 2. `/ 모델링 다운로드 [리소스]` - 해당 리소스 파일을 전송합니다.\n```css\n[ 서버 이름 ] / [ 라이센스 ] / [ 구매 모델링 ]" + msg + "```")
		else:
			await ctx.reply("> 라이센스가 없습니다.")

		connection.close()
	elif args[0] == "다운로드":
		if args[1]:
			connection = sqlite3.connect('database.db')
			connection.row_factory = sqlite3.Row
			cursor = connection.cursor()

			cursor.execute('SELECT * FROM polygon_manager WHERE discordId = ' + str(ctx.author.id) + ' LIMIT 1')
			rows = cursor.fetchall()
			if len(rows) > 0:
				allowedModels = []
				for i in json.loads(rows[0][4]):
					allowedModels.append(i)

				if args[1] in allowedModels:
					shutil.copytree("./models_dummy/" + args[1], "./" + args[1])
					zipf = zipfile.ZipFile("./" + args[1] + ".zip", 'w', zipfile.ZIP_DEFLATED)
					for root, dirs, files in os.walk("./" + args[1]):
						for file in files:
							zipf.write(os.path.join(root, file))
					zipf.close()
					shutil.rmtree(r"./" + args[1])
					try:
						await ctx.author.send(file=discord.File(r"./" + args[1] + ".zip"))
						await ctx.reply("> DM으로 모델링 파일이 전송되었습니다.")
					except:
						await ctx.reply("> DM을 허용해주세요.")
					os.remove(r"./" + args[1] + ".zip")
				else:
					await ctx.reply("> 해당 모델링을 다운로드 할 권한이 없거나 존재하지 않습니다.")
			else:
				await ctx.reply("> 라이센스가 없습니다.")

			connection.close()

client.run("token_here")
