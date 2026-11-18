import sqlite3
def iniciar_banco():
    conexao = sqlite3.connect('suggestion_bot.db')
    conexao.close()
if __name__ == '__main__':
    iniciar_banco()