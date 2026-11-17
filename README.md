# Suggestion Bot Discord

Bot de sugestões para servidores Discord, desenvolvido em Python com `discord.py`.

Projeto pessoal e educativo, gratuito e em desenvolvimento.

## Funcionalidades

- Sugestões públicas, com identificação do autor, ou anônimas, enviadas por mensagem privada.
- Publicação automática no canal definido por um administrador.
- Votação por botões de aprovação e reprovação, com opção de alterar ou remover o voto.
- Armazenamento local das configurações e dos votos em arquivos JSON, separados por servidor.
- Sessões para sugestões anônimas com duração de 5 minutos.
- Cooldowns, verificação de permissões e comando de limpeza de mensagens.

## Instalação

Instale as dependências:

```bash
pip install discord.py python-dotenv
```

Crie um arquivo `.env` na pasta do projeto:

```env
token_discord=SEU_TOKEN
```

No [Discord Developer Portal](https://discord.com/developers/applications), habilite **Message Content Intent** nas configurações do bot. Conceda as permissões de leitura e envio de mensagens, incorporação de links e gerenciamento de mensagens nos canais em que ele será utilizado.

Inicie o bot:

```bash
python main.py
```

Depois, no canal escolhido do servidor, um administrador deve executar `!s_escolher_canal`.

## Comandos

| Comando | Descrição |
|---|---|
| `!s_escolher_canal` | Define o canal de sugestões (administradores). |
| `!s_sugerir <texto>` | Publica uma sugestão com identificação do autor. |
| `!s_privado` | Inicia uma sessão para enviar uma sugestão anônima por DM. |
| `!s_particular <texto>` | Envia a sugestão anônima na conversa privada com o bot, após iniciar a sessão. |
| `!s_ajuda` | Exibe os comandos no canal configurado. |
| `!s_limpar <quantidade>` | Remove mensagens do canal (administradores; padrão: 10). |

**Observação:** os dados são armazenados na pasta `servidores/`. Em uma hospedagem, essa pasta precisa ter armazenamento persistente para manter as configurações e os votos após reinicializações.

## Sobre o projeto

O Suggestion Bot é um projeto de aprendizado em Python, desenvolvido para colocar em prática conceitos de programação e integração com o Discord. O código está disponível publicamente e o projeto continua recebendo melhorias.

**Desenvolvido por [dablio-dev](https://github.com/dablio-dev).**
