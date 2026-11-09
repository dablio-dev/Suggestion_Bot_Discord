import asyncio
import discord
import json
import os
from dotenv import load_dotenv
from discord.ext import commands
load_dotenv()
token = os.getenv('token_discord')
canal_sugestao = int(os.getenv('canal_sugestao'))
sessoes_pendentes = {}
votacoes = {}

intents = discord.Intents.all()
bot = commands.Bot('!s', intents = intents)

@bot.event
async def on_ready():
    botao_aprovar = discord.ui.Button(label='Aprovar', style=discord.ButtonStyle.green, emoji='✅',
                                      custom_id='botao_sim')
    botao_reprovar = discord.ui.Button(label='Reprovar', style=discord.ButtonStyle.red, emoji='✖️',
                                       custom_id='botao_nao')

    botao_aprovar.callback = cb_botao
    botao_reprovar.callback = cb_botao
    view = discord.ui.View(timeout=None)
    view.add_item(botao_aprovar)
    view.add_item(botao_reprovar)

    bot.add_view(view)
    print('Bot carregado com sucesso!')

@bot.event
async def on_message(msg):
    if msg.author.bot:
        mensagem_bot = 'Use o prefixo (!s) para requisitar uma sugestão, em caso de duvidas consulte as instruções!'
        mensagem = str(msg.content)
        if mensagem == mensagem_bot:
            await asyncio.sleep(5)
            await msg.delete()
        return

    if msg.channel.id == canal_sugestao:

        mensagem = str(msg.content)
        if mensagem[0:2] != '!s':
            mensagem_bot = 'Use o prefixo (!s) para requisitar uma sugestão, em caso de duvidas consulte as instruções!'
            await msg.channel.send(mensagem_bot)
            await msg.delete()
            return
        if mensagem == '!s':
            await mensagem_ajuda(msg)
    await bot.process_commands(msg)

async def cb_botao(interacao:discord.Interaction):
    user_id = interacao.user.id
    msg_id = interacao.message.id
    if msg_id not in votacoes:
        votacoes[msg_id] = {'votantes': {'id_sim': set(), 'id_nao': set()}}

    botao_clicado = interacao.data['custom_id']

    if botao_clicado == 'botao_sim':
        voto_removido = False

        if user_id in votacoes[msg_id]['votantes']['id_sim']:
            votacoes[msg_id]['votantes']['id_sim'].discard(user_id)
            voto_removido = True

        if user_id in votacoes[msg_id]['votantes']['id_nao']:
            votacoes[msg_id]['votantes']['id_nao'].discard(user_id)

        if not voto_removido:
            votacoes[msg_id]['votantes']['id_sim'].add(user_id)

    elif botao_clicado == 'botao_nao':
        voto_removido = False
        if user_id in votacoes[msg_id]['votantes']['id_nao']:
            votacoes[msg_id]['votantes']['id_nao'].discard(user_id)
            voto_removido = True

        if user_id in votacoes[msg_id]['votantes']['id_sim']:
            votacoes[msg_id]['votantes']['id_sim'].discard(user_id)
        if not voto_removido:
            votacoes[msg_id]['votantes']['id_nao'].add(user_id)

    contagem_sim = len(votacoes[msg_id]['votantes']['id_sim'])
    contagem_nao = len(votacoes[msg_id]['votantes']['id_nao'])
    total = contagem_sim + contagem_nao
    if total > 0:
        pct_sim = (contagem_sim / total) * 100
        pct_nao = (contagem_nao / total) * 100
    else:
        pct_sim = 0
        pct_nao = 0

    botao_aprovar = discord.ui.Button(label='Aprovar', style=discord.ButtonStyle.green, emoji='✅',
                                      custom_id='botao_sim')
    botao_reprovar = discord.ui.Button(label='Reprovar', style=discord.ButtonStyle.red, emoji='✖️',
                                       custom_id='botao_nao')

    botao_aprovar.callback = cb_botao
    botao_reprovar.callback = cb_botao

    view = discord.ui.View(timeout=None)
    view.add_item(botao_aprovar)
    view.add_item(botao_reprovar)

    botao_aprovar.label = f'Aprovar ({contagem_sim}) | {pct_sim:.1f}%'
    botao_reprovar.label = f'Reprovar ({contagem_nao}) | {pct_nao:.1f}%'

    await interacao.response.edit_message(view=view)

#comando para criar uma ordem de sugestão anonima no privado
@bot.command()
async def _privado(ctx:commands.Context):
    canal = ctx.channel.id
    if canal != canal_sugestao:
        return
    sessoes_pendentes[ctx.author.id] = {'canal_id': ctx.channel.id}
    await ctx.message.delete()
    await ctx.author.send('**Insira o comando !s_particular e logo em seguida a sua sugestão.**\n'
                          '\nVocê terá 5 minutos para fazer sua sugestão antes que esta sessão seja fechada,'
                          ' se caso a sessão feche antes que você consiga enviar sua sugestão é só abrir outra')
    asyncio.create_task(expirar_sessao(usuario_id = ctx.author.id))

async def expirar_sessao(usuario_id):
    await asyncio.sleep(300)
    sessoes_pendentes.pop(usuario_id, None)

#comando para fazer a sugestão anonima no privado
@bot.command()
async def _particular(ctx:commands.Context,* ,sugestao_user):
    if ctx.guild is not None:
        return
    if ctx.author.id not in sessoes_pendentes:
        await ctx.send('Nenhum chamado registrado ou chamado expirado, por favor vá no canal de sugestões'
                       ' do servidor que deseja e dispare o comando **!s_privado**!')
        return
    sugestao = str(sugestao_user).strip().capitalize()
    anonimo = True
    await disparar_embed(sugestao = sugestao, ctx = ctx, anonimo = anonimo, usuario_id = ctx.author.id)

#comando para fazer uma sugestão com autor marcado na mensagem
@bot.command()
async def _sugerir(ctx:commands.Context,* ,sugestao_user):
    if ctx.channel.id != canal_sugestao:
        return
    sugestao = str(sugestao_user).strip().capitalize()
    anonimo = False

    await disparar_embed(sugestao = sugestao, ctx = ctx, anonimo = anonimo, usuario_id = None)
    await ctx.message.delete()

#função para disparar a embed
async def disparar_embed(ctx, sugestao, anonimo, usuario_id):
    embed_sugestao = discord.Embed()
    canal_destino = bot.get_channel(canal_sugestao)

    #para sugestões anonimas
    if anonimo:
        canal_destino = bot.get_channel(sessoes_pendentes[usuario_id]['canal_id'])
        if not canal_destino:
            await ctx.send('Canal o canal de sugestões não foi encontrado, por favor repita o processo!')
            return
        sessoes_pendentes.pop(usuario_id, None)
        embed_sugestao.description = (f'__**UM USUÁRIO FEZ UMA SUGESTÃO!**__\n\n'
                                      f'**{sugestao}**')
        if canal_destino.guild.icon:
            embed_sugestao.set_thumbnail(url=canal_destino.guild.icon.url)
        else:
            embed_sugestao.set_thumbnail(url='https://cdn.discordapp.com/embed/avatars/0.png')

    #para sugestões publicas
    elif not anonimo:
        embed_sugestao.description = (f'__**O USUÁRIO {ctx.author.mention} FEZ UMA SUGESTÃO!**__\n\n'
                                      f'**{sugestao}**')
        embed_sugestao.set_thumbnail(url=ctx.author.display_avatar.url)

    embed_sugestao.set_author(name = 'Suggestion Bot', icon_url = 'https://github.com/dablio-dev/Bot-Estude-a'
                                                                  '-Mudan-a-para-discord/blob/main/Perfil_Suggestion_Bot'
                                                                  '.jpg?raw=true', url = 'https://github.com/dablio-dev')

    if anonimo:
        await ctx.send(embed = embed_sugestao)



    botao_aprovar = discord.ui.Button(label='Aprovar', style=discord.ButtonStyle.green, emoji='✅',
                                      custom_id='botao_sim')
    botao_reprovar = discord.ui.Button(label='Reprovar', style=discord.ButtonStyle.red, emoji='✖️',
                                       custom_id='botao_nao')

    botao_aprovar.callback = cb_botao
    botao_reprovar.callback = cb_botao
    view = discord.ui.View(timeout=None)
    view.add_item(botao_aprovar)
    view.add_item(botao_reprovar)

    mensagem_publicada = await canal_destino.send(embed = embed_sugestao, view=view)
    msg_id = mensagem_publicada.id
    votacoes[msg_id] = {'votantes': {'id_sim': set(), 'id_nao': set()}}

#comando para limpar o chat
@bot.command()
async def _limpar(ctx:commands.Context, quantidade:int = 10):
    if ctx.guild is None:
        return
    await ctx.channel.purge(limit=quantidade + 1)

#mensagem de ajuda para quem escreve "!s" no canal de sugestões
async def mensagem_ajuda(msg):
    mensagem_publicada = await msg.channel.send('''Comandos para uso ideal do Suggestion Bot!

**!s_privado: Para uma sugestão anônima.** 
O Suggestion Bot irá chama-lo no privado e te dar instruções para continuar!

**!s_sugerir: Para uma sugestão comum.**
Onde Suggestion Bot irá marca-lo como criador da sugestão!

**!s_Limpar: Para limpar o canal de sugestões**
(Permissão necessaria)''')

    await msg.delete()
    await asyncio.sleep(7)
    await mensagem_publicada.delete()

bot.run(token)