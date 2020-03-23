import discord
import random
import os
import urllib.request
import logging
import asyncio
import time
import sqlite3

from config import TOKEN
from discord.ext import commands
from discord.utils import get
from bs4 import BeautifulSoup
from googletrans import Translator

moderator_roles = ["Mastermind", "Moderator"]
channels = [687013888603979776, 688041352839036959]

translator = Translator()

logging.basicConfig(filename='bot.log', format='%(asctime)s -%(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
logging.info("--------------------------------------------------------------------------------------------------------------------------")
logging.info("New program seance started.")

bot = commands.Bot(command_prefix='#') # Префикс бота.

#-------------------------------------------------------------------------------------------------------
# Events

@bot.event
# Когда бот будет готов к работе, в консоль выводится "Бот готов."
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name="actively updating! (#help)",type=discord.ActivityType.listening))
    print("Бот готов.")

@bot.event
async def on_member_join(member):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT role_id FROM autoroles WHERE guild_id = ?", (member.guild.id, ))
        role_id = cursor.fetchone()
    except Exception:
        return
    else:
        if role_id == None:
            return
        role = member.guild.get_role(*role_id)
        try:
            await member.add_roles(role)
        except Exception:
            print("Эта роль сликом высока для меня!")
    
            
@bot.event
async def on_guild_join(guild):
    print(f"I'm joined server '{guild.name}'!")
        
#-------------------------------------------------------------------------------------------------------
# Commands

@bot.command(help=" <---  This command sets up an role, which will be given to a new member.")
@commands.has_any_role("Mastermind")
# Задавание роли, которая будет выдаватся автоматически новому участнику.
async def autorole(ctx,*,name):
    if name == "reset":
        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM autoroles WHERE guild_id = ?", (ctx.guild.id, ))
        conn.commit()
        await ctx.send("Автороль сброшена.")
        return
    for role in ctx.guild.roles:
        check = True
        if role.name == name:
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS autoroles (guild_id INTEGER, role_id INTEGER)")
            conn.commit()
            cursor.execute("SELECT guild_id FROM autoroles WHERE guild_id = ?", (ctx.guild.id, ))
            res = cursor.fetchall()
            if len(res) != 0:
                cursor.execute("UPDATE autoroles SET role_id = ? WHERE guild_id = ?", (role.id, ctx.guild.id, ))
                conn.commit()
            else:
                cursor.execute("INSERT INTO autoroles (guild_id, role_id) VALUES (?,?)", (ctx.guild.id, role.id, ))
                conn.commit()

            await ctx.send(f"Теперь '{name}' это роль по умолчанию.")
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
@commands.has_any_role(*moderator_roles)
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
async def translate(ctx,*,text, lang = "en"):
    response = translator.translate(dest=lang,text=text)
    for i in response.text:
        if i in ctx.guild.members:
            response.text.replace(i, i.mention)
    await ctx.send(f"Translate is: {response.text}")

@bot.command(help=" This command turn on parsing daily best articles on 'Habr.com'")
@commands.has_any_role(*moderator_roles)
async def habr_start(ctx):
    if ctx.channel.id not in channels:
        await ctx.send(f"Нет, {ctx.message.author.mention}, здесь я парсить не буду!")
        return
    global habr_status
    main_url = "https://habr.com/ru/top/"
    soup = BeautifulSoup(urllib.request.urlopen(main_url), features="html.parser")
    habr_status = True
    count = 0

    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS articles (article text)")
    conn.commit()

    await ctx.channel.purge(limit = 1)

    while habr_status:
        articles = soup.find("ul", class_="content-list content-list_posts shortcuts_items").find_all("a", class_="post__title_link")
        pages = soup.find("ul", class_="toggle-menu toggle-menu_pagination")
        if pages != None:
            pages = pages.find_all("a")
            pages_list = [i.get("href") for i in pages]
        else:
            pages_list = []
        for page in pages_list:
            try:
                page_soup = BeautifulSoup(urllib.request.urlopen(main_url + page), features="html.parser")
                articles.extend(page_soup.find("ul", class_="content-list content-list_posts shortcuts_items").find_all("a", class_="post__title_link"))
            except Exception:
                count += 1
                print(f"Фронтендеры нагадили в {count} раз!")
                pass
        for post in articles:
            cursor.execute("SELECT article FROM articles WHERE article = ?",(post.get("href"),))
            res = cursor.fetchone()
            if res != None:
                pass
            else:
                cursor.execute("INSERT INTO articles (article) VALUES (?)", (post.get("href"),))
                await ctx.send(post.get("href"))
                conn.commit()
                time.sleep(0.5)
        await asyncio.sleep(10)

@bot.command(help=" This command turn off parsing daily best articles on 'Habr.com'")
@commands.has_any_role(*moderator_roles)
async def habr_stop(ctx):
    global habr_status
    habr_status = False
    await ctx.send("Парсинг окончен.")

@bot.command()
@commands.has_any_role("Mastermind")
async def db_clear(ctx):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE articles")
    await ctx.send("Таблица статей очищена.")

bot.run(TOKEN)
