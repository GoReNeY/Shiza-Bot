import discord
import nacl
import ffmpeg
import random
import json
import json_manipulate as helper
import os
import urllib.request


from config import TOKEN
from discord.ext import commands
from discord.utils import get
from bs4 import BeautifulSoup
from googletrans import Translator


translator = Translator()

global last_post
last_post = None

bot = commands.Bot(command_prefix='.') # Префикс бота.

#-------------------------------------------------------------------------------------------------------
# Events

@bot.event
# Когда бот будет готов к работе, в консоль выводится "Бот готов."
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name="actively updating!",type=discord.ActivityType.listening))
    print("Бот готов.")

@bot.event
#При заходе на сервер нового участника, бот автоматически выдаст ему роль, которая прописана в autoroles.json с помощью команды autorole.
async def on_member_join(member):
    tmp = helper.read("autoroles.json")
    autoroles = tmp.get("auto_roles")
    ID = member.guild.id
    for key in autoroles:
        if key == str(ID):
            role = member.guild.get_role(autoroles.get(key))
            try: await member.add_roles(role)
            except Exception: print("Bot cannot give this role bcs it's too high for him!")
            break

@bot.event
async def on_guild_join(guild):
    print(f"I'm Joined server '{guild.name}'!")
        
#-------------------------------------------------------------------------------------------------------
# Commands

@bot.command(help=" <---  This command sets up an role, which will be given to a new member.")
@commands.has_permissions(administrator=True)
# Задавание роли, которая будет выдаватся автоматически новому участнику.
async def autorole(ctx,*,name):
    for i in ctx.guild.roles:
        check = True
        if i.name == name:
            await ctx.send(f"Теперь '{ctx.guild.get_role(i.id).name}' это роль по умолчанию.")
            temp = helper.read("autoroles.json")
            temp["auto_roles"][str(ctx.guild.id)] = i.id
            helper.write(temp, "autoroles.json")
            check = False
            break
    if check == True:
        await ctx.send(f"Похоже, роли {name} не существует!")

@bot.command(aliases=["Ping","png","Png"])
# Команда, отправляющая сообщение "Pong!" и задержку бота в милисекундах.
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command(aliases=["8ball"])
# Команда, выводящая сообщением случайный ответ из списка "responses".
async def _8ball(ctx, * , question):
    responses = ["Да","Нет"]
    await ctx.send(f"Вопрос: {question}\nОтвет: {random.choice(responses)}")

@bot.command()
@commands.has_permissions(administrator=True)
#Команда, удаляющая amount число сообщений, и после выводящая отчёт, содержащий количество удаленных сообщений и объект участника, который его отправил.
async def clear(ctx,amount=1):             
    await ctx.channel.purge(limit=amount+1) 
    await ctx.send(f"Я удалил {amount} сообщений по просьбе {ctx.message.author.mention}")

@bot.command(aliases=["Choose"])
# Команда, которая выбирает случайный вариант из тех, что ввел участник, разделенные "|", и выводит сообщением.
async def choose(ctx, * , question):
    questions = question.split("|")
    await ctx.send(f"Я думаю, {random.choice(questions)}")

@bot.command(help=" <---- This command translates a string you send, in format 'destination language, text'")
# Команда, переводящая строку, заданную командой, с принятием языка, на который нужно перевести.
async def translate(ctx,lang,*,text):
    response = translator.translate(dest=lang,text=text)
    await ctx.send(f"Translate is: {response.text}")

@bot.command(help=" This command turn on parcing daily best articles on 'Habr.com'")
@commands.has_permissions(administrator=True)
async def habr_start(ctx):
    await ctx.send("Парсинг начат.")
    global last_post, habr_status
    responce = urllib.request.urlopen("https://habr.com/ru/top/")
    soup = BeautifulSoup(responce)
    habr_status = True

    while habr_status:
        articles = soup.find("ul", class_="content-list content-list_posts shortcuts_items").find_all("a", class_="post__title_link")
        for post in articles:
            if habr_status == False:
                break
            if post == last_post:
                break
            await ctx.send(post.get("href"))
        last_post = articles[0]

@bot.command(help=" This command turn off parcing daily best articles on 'Habr.com'")
@commands.has_permissions(administrator=True)
async def habr_stop(ctx):
    global habr_status
    habr_status = False
    await ctx.send("Парсинг окончен.")

bot.run(TOKEN)