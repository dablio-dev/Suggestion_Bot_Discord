from time import sleep
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands, tasks
load_dotenv()
token = os.getenv('token_discord')
canal_sugestao = int(os.getenv('canal_sugestao'))

intents = discord.Intents.all()
bot = commands.Bot('!sugerir', intents = intents)

@bot.event
async def on_ready():
    print('Bot carregado com sucesso!')

@bot.event
async def on_message(msg):
    if msg.author.bot:
        mensagem_bot = 'Use o prefixo (!sugerir) para requisitar uma sugestão, em caso de duvidas consulte as instruções!'
        mensagem = str(msg.content)
        if mensagem == mensagem_bot:
            sleep(5)
            await msg.delete()
        return

    if msg.channel.id == canal_sugestao:
        mensagem = str(msg.content)
        if not '!sugerir' in mensagem:
            mensagem_bot = 'Use o prefixo (!sugerir) para requisitar uma sugestão, em caso de duvidas consulte as instruções!'
            await msg.channel.send(mensagem_bot)
            await msg.delete()
    await bot.process_commands(msg)


@bot.command()
async def _privado(ctx:commands.Context):
    canal = ctx.channel.id
    if canal != canal_sugestao:
        return
    await ctx.message.delete()
    await ctx.author.send(f'Insira o comando !sugerir_particular e logo em seguida a sua sugestão.')

@bot.command()
async def _particular(ctx:commands.Context,* ,sugestao_user):
    if ctx.guild != None:
        return
    sugestao = str(sugestao_user).strip().capitalize()

    await disparar_embed(sugestao = sugestao, ctx = ctx)

async def disparar_embed(ctx, sugestao):
    embed_sugestao = discord.Embed()
    embed_sugestao.title = 'Um usuário enviou uma sugestão!'
    embed_sugestao.description = sugestao
    embed_sugestao.set_author(name = 'Suggestion Bot', icon_url = 'https://github.com/dablio-dev/Bot-Estude-a'
                                                                  '-Mudan-a-para-discord/blob/main/Perfil_Suggestion_Bot'
                                                                  '.jpg?raw=true', url = 'https://github.com/dablio-dev')
    canal_destino = bot.get_channel(int(canal_sugestao))

    await ctx.send(embed = embed_sugestao)
    mensagem_publicada = await canal_destino.send(embed = embed_sugestao)
    await mensagem_publicada.add_reaction('✅')
    await mensagem_publicada.add_reaction('❌')

@bot.command()
async def _limparc(ctx:commands.Context, quantidade:int = 10):
    if ctx.guild == None:
        return
    await ctx.channel.purge(limit=quantidade + 1)

bot.run(token)