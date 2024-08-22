# -*- coding: utf-8 -*-

from faulthandler import disable
import discord
import datetime
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
from discord import Interaction, ui, ButtonStyle, SelectOption, Button
import random
import asyncio
import string
from datetime import datetime

INTENTS = discord.Intents.all()

client = commands.Bot(command_prefix=['/', '#'], intents=INTENTS)

@client.command(name='log')
@has_permissions(administrator=True)
async def logging(ctx, amount=100):
    print('PMD POLYGON')
    await ctx.send("> PMD(POLYGON) 호스트의 콘솔로 로그가 출력되었습니다.")


@client.event
async def on_ready():
    print('POLYGON BOT 로그인 완료')

    await client.change_presence(activity=discord.Activity(type=1, name="모델링 강좌", url='https://twitch.tv/twitch'))

    def is_me(m):
        return m.author.id == AUTHOR_ID

    channel = client.get_channel(CHANNEL_ID)
    await channel.purge(limit=3, check=is_me)

    button = ui.Button(style=ButtonStyle.green, label="거래 신청서 작성", emoji="📜")
    view = ui.View(timeout=None)
    view.add_item(button)

    async def button_callback(interaction: Interaction):
        sellerSelect = ui.Select(placeholder="판매자를 선택하세요")
        sellerSelect.add_option(
            label="판매자1", value="seller1", description="판매자1의 상품을 구매하고 싶다면 눌러주세요!", emoji="🥩")
        sellerSelect.add_option(
            label="판매자2", value="seller2", description="판매자2의 상품을 구매하고 싶다면 눌러주세요!", emoji="🐸")
        sellerSelect.add_option(
            label="판매자3", value="seller3", description="판매자3의 상품을 구매하고 싶다면 눌러주세요!", emoji="😈")

        view = ui.View()
        view.add_item(sellerSelect)

        async def select_callback(interaction: Interaction):
            if sellerSelect.values[0] == "seller1":
                await interaction.response.send_modal(TicketSeller1Modal())
            elif sellerSelect.values[0] == "seller2":
                await interaction.response.send_modal(TicketSeller2Modal())
            elif sellerSelect.values[0] == "seller3":
                await interaction.response.send_modal(TicketSeller3Modal())

        sellerSelect.callback = select_callback
        await interaction.response.send_message(view=view, ephemeral=True)

    button.callback = button_callback

    embed = discord.Embed(title="<:polygon_sym:1050824598289121371> **Be New, POLYGON 거래 신청서**",
                          description="상품 사용권 거래를 원하시는 경우 위의 규정을 숙지한 후 판매자를 선택하여 거래 신청서를 작성하세요!", color=0xb833ff)
    await channel.send(embed=embed, view=view)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print("COMMAND NOT FOUND")
    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title=":exclamation: 너무 빨라요! :exclamation:",
                              description="{:.2f}초 뒤에 다시 시도해주세요!".format(error.retry_after), color=0xff2f2f)
        await ctx.send("<@!" + str(ctx.author.id) + ">", embed=embed)
    elif "required argument that is missing" in str(error):
        embed = discord.Embed(title=":x: 명령어가 잘못되었습니다.",
                              description="제대로 사용한게 맞는지 확인해주세요!", color=0xff2f2f)
        await ctx.send("<@!" + str(ctx.author.id) + ">", embed=embed)
    elif isinstance(error, CheckFailure):
        embed = discord.Embed(
            title=":x: 권한이 없습니다.", description="명령어를 사용할 수 있는 권한을 소지하고있는지 확인해주세요!", color=0xff2f2f)
        await ctx.send("<@!" + str(ctx.author.id) + ">", embed=embed)
    else:
        await ctx.send("*오류가 발생했습니다.*\n\n``" + str(error) + "``")


@client.command(name='처벌')
@has_permissions(administrator=True)
async def _punish(ctx, member: discord.Member, *, arg):
    user_name = ctx.message.author.display_name
    embed = discord.Embed(title="🤬 블랙리스트 안내", color=0xfb0025)
    embed.add_field(name="디스코드 ID", value="<@" +
                    str(member.id) + ">, " + str(member.id), inline=True)
    embed.add_field(name="닉네임", value=member.display_name, inline=True)
    embed.add_field(name="사유", value=arg, inline=False)
    embed.set_footer(text="관리자 : " + user_name + " • POLYGON")
    embed.timestamp = datetime.utcnow()
    channel = client.get_channel(CHANNEL_BAN)
    await channel.send("@everyone", embed=embed)
    try:
        await ctx.send("<@!" + str(ctx.author.id) + ">\n<#CHANNEL_BAN> 채널에 업로드 및 차단된 사용자에게 DM이 전송되었습니다.")
        await member.send(embed=embed)
    except:
        await ctx.send("<@!" + str(ctx.author.id) + ">\n<#CHANNEL_BAN> 채널에 업로드 되었습니다.")
    await member.ban(reason=arg)


@client.command(name='공지')
@has_permissions(administrator=True)
async def _ann(ctx, *, arg):
    user_name = ctx.message.author.display_name

    embed = discord.Embed(
        title="[POLYGON] 공지사항", description=arg, color=0xdbd000)
    embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
    embed.set_footer(text="관리자 : " + user_name)
    embed.timestamp = datetime.utcnow()

    channel = client.get_channel(1018071962670596096)
    await channel.send("@everyone", embed=embed)

    await ctx.send("업로드 완료.")


@client.command(name='dm공지')
@has_permissions(administrator=True)
async def _ann(ctx, *, arg):
    user_name = ctx.message.author.display_name

    embed = discord.Embed(
        title="[POLYGON] 공지사항", description=arg, color=0xdbd000)
    embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
    embed.set_footer(text="관리자 : " + user_name,
                     icon_url=ctx.message.author.avatar_url)
    embed.timestamp = datetime.utcnow()

    for member in ctx.guild.members:
        try:
            await member.send(embed=embed)
        except:
            await ctx.send("한 명 전송 실패. (권한 없음)")

    await ctx.send("모든 유저에게 메세지가 전송되었습니다.")


@client.command(name='dm공지역할')
@has_permissions(administrator=True)
async def _ann(ctx, role: discord.Role, *, arg):
    user_name = ctx.message.author.display_name

    embed = discord.Embed(
        title="[POLYGON] 공지사항", description=arg, color=0xdbd000)
    embed.set_thumbnail(url="https://i.imgur.com/PqlKUmN.png")
    embed.set_footer(text="관리자 : " + user_name)
    embed.timestamp = datetime.utcnow()

    for member in ctx.guild.members:
        try:
            if role.name.lower() in [y.name.lower() for y in member.roles]:
                await member.send(embed=embed)
        except:
            await ctx.send("한 명 전송 실패. (권한 없음)")

    await ctx.send("모든 유저에게 메세지가 전송되었습니다.")


@client.command(name='지우기')
@has_permissions(administrator=True)
async def _clear(ctx, amount=100):
    await ctx.channel.purge(limit=amount+1)
    mmessage = await ctx.send("> " + str(amount) + "개의 메세지를 지웠습니다.")
    await asyncio.sleep(5)
    await mmessage.delete()

class TicketSeller1Modal(ui.Modal, title="거래 신청서 작성 (🥩 판매자1)"):
    # 구매 품목:\n구매자 성명:\n본인명의 계좌번호 및 거래 은행:\n본인명의 휴대전화:\n적용 대상 서버:\n디스코드 태그:

    product = ui.TextInput(
        label="구매 품목명을 기재해주세요.(주문제작의 경우 커스텀오더로 기재해주세요.)",
        style=discord.TextStyle.short,
        required= True,
        min_length= 1,
        max_length= 50
    )

    bank = ui.TextInput(
        label="본인명의 계좌번호 및 거래 은행 ex) 3333100012345 카카오뱅크 홍길동",
        placeholder="ex) 3333100012345 카카오뱅크 홍길동",
        style=discord.TextStyle.short,
        required= True,
        min_length= 1,
        max_length= 50
    )

    phone = ui.TextInput(
        label="본인명의 휴대전화 번호(기호(-)를 포함하여 적어주세요.)",
        placeholder="ex) 010-1234-1234",
        style=discord.TextStyle.short,
        required= True,
        min_length= 1,
        max_length= 50
    )

    nameandserver = ui.TextInput(
        label="구매자 성명 및 적용 대상 서버",
        placeholder="ex) 홍길동 서버이름",
        style=discord.TextStyle.short,
        required= True,
        min_length= 1,
        max_length= 50
    )

    agree = ui.TextInput(
        label="본인은 위 내용에 거짓이 없으며, 판매 규정에 동의해 거래를 신청합니다.",
        placeholder="채널 상단 내용 숙지 후 위 내용을 따라 적어주세요.",
        style=discord.TextStyle.short,
        required= True,
        min_length= 40,
        max_length= 40
    )

    async def on_submit(self, interaction: Interaction):
        if self.agree.value == "본인은 위 내용에 거짓이 없으며, 판매 규정에 동의해 거래를 신청합니다.":
            guild = client.get_guild(GUILD_ID)
            
            category = discord.utils.get(guild.categories, name="Seller1 Orders")
            target_user = await client.fetch_user(SELLER_ID)
            channel = await guild.create_text_channel("🥩 " + interaction.user.display_name + " " +self.nameandserver.value, category=category)

            await channel.set_permissions(guild.default_role, view_channel=False)
            await channel.set_permissions(interaction.user, view_channel=True)

            await interaction.response.send_message(
                content="> **거래 채널이 생성되었습니다. 판매자와 연락하세요!**\n> <#" + str(channel.id) + ">", ephemeral=True
            )

            await channel.send("> 판매자 멘션: <@" + str(target_user.id) + ">")
            await channel.send("||<@" + str(interaction.user.id) + '>||\n```css\n[POLYGON_ 구매자 권한 안내]\n\n상품 수령 후 7일 이내 후기 작성시 Thank You 권한이 부여됩니다.\nThank You 권한은 VIP 권한 부여와 애프터서비스에 필수적이니 꼭 작성해주세요!```\n```cs\n# POLYGON 규정을 숙지하지 않아 발생할 수 있는 모든 상황의 책임은 구매자에게 있습니다.```')
            await channel.send("||<@" + str(interaction.user.id) + '>||\n```cs\n# 거래 신청서\n\n구매 품목: {}\n본인명의 계좌번호 및 거래 은행: {}\n본인명의 휴대전화: {}\n구매자 성명 및 적용 대상 서버: {}\n디스코드 태그: {}\n계약 내용 동의 여부: {}```'.format(self.product.value, self.bank.value, self.phone.value, self.nameandserver.value, interaction.user, self.agree.value))
            await channel.send("> 판매자가 확인 대기중입니다.\n> 추가로 더 필요한 내용이 있다면 이 채널에 남겨주세요.\n> 판매자 멘션은 자제 부탁드립니다. \n> \n> 원활한 거래를 위해 거래중에는 **방해금지 모드를 해제** 해주시기 바랍니다. \n> 거래가 완료되어도 서비스 관리를 위해 **채널 알림을 켜주세요**. <@" + str(interaction.user.id) + ">")
        else:
            await interaction.response.send_message("> 구매가 취소 되었습니다. 오타에 주의해 정확하게 입력해주세요!", ephemeral=True)



















client.run(
    "BOT_TOKEN")
