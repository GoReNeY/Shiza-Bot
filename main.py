import discord
from discord.ext import commands
import random
from config import TOKEN

bot = commands.Bot(command_prefix='.') # Префикс бота.

global auto_role
auto_role = "@everyone"
#-------------------------------------------------------------------------------------------------------
# Events

@bot.event
async def on_ready():                # Когда бот будет готов к работе, в консоль выводится "Бот готов."
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name="actively updating!",type=discord.ActivityType.listening))
    print("Бот готов.")

@bot.event
async def on_member_join(member):                               # При заходе нового участника на сервер, ему автоматически выдается роль с ID "auto_role",
    global auto_role                                            # которая задается командой "auto". По умолчанию auto_role = @everyone 
    await member.add_roles(member.guild.get_role(auto_role))

#-------------------------------------------------------------------------------------------------------
# Commands

@bot.command(help=" <---  This command sets up an role, what will be given to a new member.")
@commands.has_permissions(administrator=True)
async def autorole(ctx,*,name):    # Задавание роли, которая будет выдаватся автоматически новому участнику.
    global auto_role
    check = auto_role          # check - проверяющая переменная, если check == auto_role, тоесть роль не изменилась, выводится сообщение о неправильной роли.
    for i in ctx.guild.roles:
        if i.name == name:
            auto_role = i.id
            await ctx.send(f"Теперь '{ctx.guild.get_role(auto_role).name}' это роль по умолчанию.")
    if check == auto_role:
        await ctx.send(f"Похоже, роли '{name}' не существует!")

@bot.command(aliases=["Ping","png","Png"])  # Команда, отправляющая сообщение "Pong!" и задержку бота в милисекундах.
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command(aliases=["8ball"])
async def _8ball(ctx, * , question):        # Команда, выводящая сообщением случайный ответ из списка "responses".
    responses = ["Да","Нет"]
    await ctx.send(f"Вопрос: {question}\nОтвет: {random.choice(responses)}")

@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx,amount=1):              # Команда, удаляющая amount число сообщений, и после выводящая отчёт, содержащий количество удаленных
    await ctx.channel.purge(limit=amount+1) # сообщений и объект участника, который его отправил.
    await ctx.send(f"Я удалил {amount} сообщений по просьбе {ctx.message.author.mention}")

@bot.command(aliases=["Choose"])            # Команда, которая выбирает случайный вариант из тех, что ввел участник, разделенные "|", и выводит сообщением.
async def choose(ctx, * , question):
    questions = question.split("|")
    await ctx.send(f"Я думаю, {random.choice(questions)}")

bot.run(TOKEN)
