# Suggestion Bot Discord

Bot para gerenciamento de sugestões em servidores Discord, desenvolvido em Python.

### Funcionalidades
- Recebimento privado de sugestões.
- Publicação automática em canal configurado.
- Votação por reações (✅ e ❌).
- Comando para limpeza de mensagens.

### Instalação

Instale as dependências:

```bash
pip install discord.py python-dotenv
```

Configure um arquivo `.env` na pasta do projeto:

```env
token_discord=SEU_TOKEN
canal_sugestao=ID_DO_CANAL
```

Execute o bot:

```bash
python main.py
```

### Comandos

| Comando | Descrição |
|---|---|
| `!sugerir_privado` | Inicia o envio privado de uma sugestão. |
| `!sugerir_particular <texto>` | Envia uma sugestão ao bot. |
| `!sugerir_limparc <quantidade>` | Limpa mensagens do canal. |

### Sobre o projeto

Projeto pessoal e educativo, desenvolvido como parte do meu aprendizado em Python. Sua construção tem sido uma oportunidade de colocar em prática o que venho estudando e aprender coisas novas durante o desenvolvimento.

O projeto ainda está em desenvolvimento e será disponibilizado gratuitamente, com código aberto.

**Desenvolvido por [dablio-dev](https://github.com/dablio-dev)**
