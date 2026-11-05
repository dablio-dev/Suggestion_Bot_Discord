from asyncio import sleep
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands, tasks
load_dotenv()
token = os.getenv('token_discord')
canal_sugestao = int(os.getenv('canal_sugestao'))

intents = discord.Intents.all()
bot = commands.Bot('!s', intents = intents)

@bot.event
async def on_ready():
    print('Bot carregado com sucesso!')

@bot.event
async def on_message(msg):
    if msg.author.bot:
        mensagem_bot = 'Use o prefixo (!s) para requisitar uma sugestão, em caso de duvidas consulte as instruções!'
        mensagem = str(msg.content)
        if mensagem == mensagem_bot:
            await sleep(5)
            await msg.delete()
        return

    if msg.channel.id == canal_sugestao:

        mensagem = str(msg.content)

        if not '!s' in mensagem:
            mensagem_bot = 'Use o prefixo (!s) para requisitar uma sugestão, em caso de duvidas consulte as instruções!'
            await msg.channel.send(mensagem_bot)
            await msg.delete()
            return
        if mensagem == '!s':
            await mensagem_ajuda(msg)



    await bot.process_commands(msg)


@bot.command()
async def _privado(ctx:commands.Context):
    canal = ctx.channel.id
    if canal != canal_sugestao:
        return
    await ctx.message.delete()
    await ctx.author.send(f'Insira o comando !s_particular e logo em seguida a sua sugestão.')

async def mensagem_ajuda(msg):
    mensagem_publicada = await msg.channel.send('''Comandos para uso ideal do Suggestion Bot!
    
**!s_privado: Para uma sugestão anônima.** 
O Suggestion Bot irá chama-lo no privado e te dar instruções para continuar!

**!s_sugerir: Para uma sugestão comum.**
Onde Suggestion Bot irá marca-lo como criador da sugestão!

**!s_Limpar: Para limpar o canal de sugestões**
(Permissão necessaria)''')
    await msg.delete()
    await sleep(7)
    await mensagem_publicada.delete()

@bot.command()
async def _particular(ctx:commands.Context,* ,sugestao_user):
    if ctx.guild != None:
        return
    sugestao = str(sugestao_user).strip().capitalize()
    anonimo = True
    await disparar_embed(sugestao = sugestao, ctx = ctx, anonimo = anonimo)

@bot.command()
async def _sugerir(ctx:commands.Context,* ,sugestao_user):
    if ctx.channel.id != canal_sugestao:
        return
    sugestao = str(sugestao_user).strip().capitalize()
    anonimo = False

    await disparar_embed(sugestao = sugestao, ctx = ctx, anonimo = anonimo)

async def disparar_embed(ctx, sugestao, anonimo):
    embed_sugestao = discord.Embed()
    canal_destino = bot.get_channel(canal_sugestao)
    if anonimo:
        embed_sugestao.description = (f'__**UM USUÁRIO FEZ UMA SUGESTÃO!**__\n\n'
                                      f'**{sugestao}**')
        if canal_destino.guild.icon:
            embed_sugestao.set_thumbnail(url=canal_destino.guild.icon.url)
        else:
            embed_sugestao.set_thumbnail(url='https://cdn.discordapp.com/embed/avatars/0.png')
    elif not anonimo:
        embed_sugestao.description = (f'__**O USUÁRIO {ctx.author.mention} FEZ UMA SUGESTÃO!**__\n\n'
                                      f'**{sugestao}**')
        embed_sugestao.set_thumbnail(url=ctx.author.display_avatar.url)

    embed_sugestao.set_author(name = 'Suggestion Bot', icon_url = 'https://github.com/dablio-dev/Bot-Estude-a'
                                                                  '-Mudan-a-para-discord/blob/main/Perfil_Suggestion_Bot'
                                                                  '.jpg?raw=true', url = 'https://github.com/dablio-dev')
    canal_destino = bot.get_channel(int(canal_sugestao))
    if anonimo:
        await ctx.send(embed = embed_sugestao)
    mensagem_publicada = await canal_destino.send(embed = embed_sugestao)
    await mensagem_publicada.add_reaction('✅')
    await mensagem_publicada.add_reaction('❌')

@bot.command()
async def _limpar(ctx:commands.Context, quantidade:int = 10):
    if ctx.guild == None:
        return
    await ctx.channel.purge(limit=quantidade + 1)

bot.run(token)