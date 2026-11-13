import asyncio
import secrets

import discord
import json
import os
from dotenv import load_dotenv
from discord.ext import commands
load_dotenv()
token = os.getenv('token_discord')
sessoes_pendentes = {'chaves_sessoes': {}}

intents = discord.Intents.all()
bot = commands.Bot('!s', intents = intents)

@bot.event
async def on_command_error(ctx:commands.Context, error):
    embed = discord.Embed()
    if isinstance(error, commands.CommandOnCooldown):
        embed.description = f'''**Vai com calma!**
Você esta tentando mandar comandos rapido de mais, espere {error.retry_after:.0f}s antes de tentar este mesmo comando de novo!'''
        mensagem = await ctx.send(embed=embed)
        if ctx.guild:
            await ctx.message.delete()
        await asyncio.sleep(7)
        await mensagem.delete()

    if isinstance(error, commands.MissingPermissions):
        embed.description = 'Você não tem permissão para usar este comando entre em contato com um administrador!'
        mensagem = await ctx.send(embed=embed)
        await ctx.message.delete()
        await asyncio.sleep(7)
        await mensagem.delete()
    if isinstance(error, commands.MissingRequiredArgument):
        embed.description = 'Por favor adicione algum texto após o comando, este texto será sua sugestão'
        mensagem = await ctx.send(embed=embed)
        await ctx.message.delete()
        await asyncio.sleep(7)
        await mensagem.delete()
    if isinstance(error, commands.CommandInvokeError):
        embed.description = 'Houve algum problema acionar o bot, por favor tente novamente!'
        mensagem = await ctx.send(embed=embed)
        await ctx.message.delete()
        await asyncio.sleep(7)
        await mensagem.delete()
    if isinstance(error, commands.BadArgument):
        embed.description = 'Alguma informação depois do comando esta errada, por favor corrija e tente novamente!'
        mensagem = await ctx.send(embed=embed)
        await ctx.message.delete()
        await asyncio.sleep(7)
        await mensagem.delete()
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

@bot.command()
@commands.has_permissions(administrator=True)
async def _escolher_canal(ctx:commands.Context):
    if not ctx.guild:
        return
    caminho = f'servidores/{ctx.guild.id}.json'
    os.makedirs('servidores', exist_ok=True)
    if not os.path.exists(caminho):
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)
        dados = {}
    else:
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    dados['canal_operacao'] = ctx.channel.id
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    embed = discord.Embed()
    embed.description = 'Canal de sugestão definido com sucesso!'
    mensagem = await ctx.send(embed=embed)
    await ctx.message.delete()
    await asyncio.sleep(7)
    await mensagem.delete()

async def cb_botao(interacao:discord.Interaction):
    caminho = f'servidores/{interacao.guild.id}.json'
    if not os.path.exists(caminho):
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)
        dados = {}
    else:
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    user_id = str(interacao.user.id)
    msg_id = str(interacao.message.id)
    serv_id = str(interacao.guild.id)
    if msg_id not in dados:
        dados[msg_id] = {'votantes': {'id_sim': list(), 'id_nao': list()}}

    botao_clicado = interacao.data['custom_id']

    id_sim = set(dados[msg_id]['votantes']['id_sim'])
    id_nao = set(dados[msg_id]['votantes']['id_nao'])

    if botao_clicado == 'botao_sim':
        voto_removido = False

        if user_id in id_sim:
            id_sim.discard(user_id)
            voto_removido = True

        if user_id in id_nao:
            id_nao.discard(user_id)

        if not voto_removido:
            id_sim.add(user_id)

    elif botao_clicado == 'botao_nao':
        voto_removido = False
        if user_id in id_nao:
            id_nao.discard(user_id)
            voto_removido = True

        if user_id in id_sim:
            id_sim.discard(user_id)

        if not voto_removido:
            id_nao.add(user_id)

    dados[msg_id]['votantes']['id_sim'] = list(id_sim)
    dados[msg_id]['votantes']['id_nao'] = list(id_nao)

    with open(caminho, 'w', encoding='utf-8', ) as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

    contagem_sim = len(id_sim)
    contagem_nao = len(id_nao)
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
@commands.cooldown(1, 60, commands.BucketType.user)
async def _privado(ctx:commands.Context):
    if not ctx.guild:
        return
    canal_id = await procurar_canal(ctx=ctx)
    if not canal_id:
        return
    if ctx.channel.id != canal_id:
        return
    if ctx.author.id in sessoes_pendentes['chaves_sessoes']:
        embed = discord.Embed()
        embed.description = '**Você já tem uma sessão ativa!** \nPor favor conclua ou aguarde ela ser encerrada!'
        mensagem = await ctx.send(embed=embed)
        await ctx.message.delete()
        await asyncio.sleep(7)
        await mensagem.delete()
        return
    id_sessao = secrets.token_hex(3)

    await ctx.message.delete()
    embed = discord.Embed()
    embed.description ='''**Tudo pronto para a sua sugestão anônima!**
**Como enviar:**
1️⃣ Digite !s_particular aqui neste chat.
2️⃣ Dê um espaço e escreva a sua sugestão logo na frente.
3️⃣ Aperte Enter para enviar!
⏳ Nota: Esta sessão se fechará em 5 minutos. Caso não dê tempo, é só ir ''ao servidor e pedir outra.'''
    try:
        await ctx.author.send(embed=embed)
        sessoes_pendentes['chaves_sessoes'][ctx.author.id] = {'ctx': ctx, 'id_sessao': id_sessao}
        asyncio.create_task(expirar_sessao(ctx=ctx, id_sessao=id_sessao))
    except discord.Forbidden or discord.Forbidden:
        embed = discord.Embed()
        embed.description = '**Por favor ative as mensagens privadas e tente novamente**'
        mensagem = await ctx.send(embed=embed)
        await ctx.message.delete()
        await asyncio.sleep(7)
        await mensagem.delete()
        return

async def expirar_sessao(ctx, id_sessao):
    await asyncio.sleep(300)
    if ctx.author.id in sessoes_pendentes['chaves_sessoes']:
        if sessoes_pendentes['chaves_sessoes'][ctx.author.id]['id_sessao'] == id_sessao:
            sessoes_pendentes['chaves_sessoes'].pop(ctx.author.id, None)

#comando para fazer a sugestão anonima no privado
@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def _particular(ctx:commands.Context,* ,sugestao_user):
    if ctx.guild:
        return
    if ctx.author.id not in sessoes_pendentes['chaves_sessoes']:
        embed = discord.Embed()
        embed.description = '''**Ops! Não encontrei nenhuma sessão ativa para você.**
Isso acontece se o seu tempo de 5 minutos esgotou ou se você tentou iniciar o comando direto por aqui.
**Como resolver:**
1️⃣ Vá até o canal de sugestões do servidor.
2️⃣ Digite !s_privado lá.
3️⃣ Volte aqui nesta conversa e me envie a sua sugestão!'''
        await ctx.send(embed=embed)
        return
    sugestao = str(sugestao_user).strip()
    anonimo = True
    await disparar_embed(sugestao = sugestao, ctx = ctx, anonimo = anonimo, usuario_id = ctx.author.id)

#comando para fazer uma sugestão com autor marcado na mensagem
@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def _sugerir(ctx:commands.Context,* ,sugestao_user):
    if not ctx.guild:
        return
    canal_id = await procurar_canal(ctx=ctx)
    if not canal_id:
        return
    if ctx.channel.id != canal_id:
        return
    sugestao = str(sugestao_user).strip()
    anonimo = False

    await disparar_embed(sugestao = sugestao, ctx = ctx, anonimo = anonimo, usuario_id = None)
    await ctx.message.delete()

async def procurar_canal(ctx):
    caminho = f'servidores/{ctx.guild.id}.json'
    if not os.path.exists(caminho):
        embed = discord.Embed()
        embed.description = '''**Falta pouco para começarmos!**
Nenhum canal de sugestões foi configurado por aqui ainda.
Para que eu possa receber e publicar as ideias,
um Administrador precisa ir ao canal desejado e digitar !s_escolher_canal.'''
        await ctx.send(embed=embed)
        return None
    with open(caminho, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    canal_id = dados.get('canal_operacao')
    if not canal_id:
        embed = discord.Embed()
        embed.description = '''**Falta pouco para começarmos!**
Nenhum canal de sugestões foi configurado por aqui ainda. Para que eu possa receber e publicar as ideias,
um Administrador precisa ir ao canal desejado e digitar !s_escolher_canal.'''
        await ctx.send(embed=embed)
        return None
    return canal_id

#função para disparar a embed
async def disparar_embed(ctx, sugestao, anonimo, usuario_id):
    if anonimo:
        canal_id = await procurar_canal(ctx=sessoes_pendentes['chaves_sessoes'][ctx.author.id]['ctx'])
    else:
        canal_id = await procurar_canal(ctx=ctx)
    if not canal_id:
        embed = discord.Embed()
        embed.description = '''**Falta pouco para começarmos!**
Nenhum canal de sugestões foi configurado por aqui ainda. Para que eu possa receber e publicar as ideias,
um Administrador precisa ir ao canal desejado e digitar !s_escolher_canal.'''
        await ctx.send(embed=embed)
        return
    embed_sugestao = discord.Embed()
    canal_destino = bot.get_channel(canal_id)

    #para sugestões anonimas
    if anonimo:
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
    if anonimo:
        await ctx.send(embed = embed_sugestao)
        sessoes_pendentes['chaves_sessoes'].pop(usuario_id, None)

#comando para limpar o chat
@bot.command()
@commands.has_permissions(administrator=True)
async def _limpar(ctx:commands.Context, quantidade:int = 10):
    if ctx.guild is None:
        return
    await ctx.channel.purge(limit=quantidade + 1)

#mensagem de ajuda para quem escreve "!s" no canal de sugestões
@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def _ajuda(ctx:commands.Context):
    canal_id = await procurar_canal(ctx=ctx)
    if not canal_id:
        return
    if ctx.channel.id != canal_id:
        return
    canal_destino = bot.get_channel(canal_id)
    embed = discord.Embed()
    embed.description = '''**Central de Comandos - Suggestion Bot**

!s_privado | Para uma sugestão anônima.
O bot irá chamá-lo no privado para dar as instruções com total sigilo!

!s_sugerir <sua ideia> | Para uma sugestão comum.
Sua ideia será publicada e você será marcado como o autor da sugestão.

!s_limpar <quantidade> | Limpeza de chat.
Apaga as mensagens do canal de sugestões (Exige permissões).

!s_escolher_canal | Configuração do Bot.
Avisa ao bot que ele deve operar neste canal (Apenas Administradores).'''

    mensagem_publicada = await canal_destino.send(embed=embed)

    await ctx.message.delete()
    await asyncio.sleep(7)
    await mensagem_publicada.delete()

bot.run(token)
