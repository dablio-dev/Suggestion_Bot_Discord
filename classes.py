import discord
class BotaoVotacao(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.votos_sim = 0
        self.votos_nao = 0
        self.votantes = set()

    def calcular_porcentagem(self):
        total = self.votos_sim + self.votos_nao

        if total == 0:
            return

        pct_sim = (self.votos_sim / total) * 100
        pct_nao = (self.votos_nao / total) * 100

    @discord.ui.button(label='aprovar', style=discord.ButtonStyle.green)
    async def botao_sim(self, interacao:discord.Interaction, botao:discord.ui.Button):
        pct_sim, pct_nao = (self.calcular_porcentagem())
    @discord.ui.button(label='reprovar', style=discord.ButtonStyle.red)
    async def botao_nao(self, interacao:discord.Interaction, botao:discord.ui.Button):
        self.votos_nao += 1
        self.votantes.add(interacao.user.id)

        pct_sim, pct_nao = (self.calcular_porcentagem())

        self.children[0].label = f'Aprovar ({self.votos_sim}) - {pct_sim:.1f}'
        botao.label = f'Reprovar ({self.votos_nao}) - {pct_nao:.1f}'
        await interacao.response.edit_message(view=self)