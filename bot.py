import discord
from discord.ui import Button, View
from discord import ButtonStyle, Interaction, Embed

intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

# Faixas com preço
faixas = [
    ("10-20M", 7),
    ("21-30M", 15),
    ("31-40M", 21),
    ("41-60M", 29),
    ("61-80M", 35),
    ("81-90M", 39),
    ("91-150M", 50),
    ("151-258M", 75)
]

# Cores agrupadas
cores_faixa = ["🟢","🟢","🟡","🟡","🟠","🟠","🔴","🔴"]

# Adicionais
adicionais = ["Mais de 50M Base?", "Evento Raro ou Mutação Rara?"]

# Escolhas por usuário
user_choices = {}

class BrainrotView(View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=900)
        self.user = user
        self.create_buttons()

    def create_buttons(self):
        for idx, (faixa, valor) in enumerate(faixas):
            cor = cores_faixa[idx]
            btn = Button(
                label=f"{cor} {faixa}",
                style=ButtonStyle.primary,
                custom_id=f"faixa:{faixa}"
            )
            btn.callback = self.faixa_callback
            btn.row = idx // 4
            self.add_item(btn)

        for idx, add in enumerate(adicionais):
            btn_sim = Button(
                label=f"✅ {add}", style=ButtonStyle.success, custom_id=f"add_sim:{add}"
            )
            btn_nao = Button(
                label=f"❌ {add}", style=ButtonStyle.danger, custom_id=f"add_nao:{add}"
            )
            btn_sim.callback = self.adicional_callback
            btn_nao.callback = self.adicional_callback
            btn_sim.row = idx + 2
            btn_nao.row = idx + 2
            self.add_item(btn_sim)
            self.add_item(btn_nao)

        reset_btn = Button(label="🔄 Reset", style=ButtonStyle.secondary, custom_id="reset")
        reset_btn.callback = self.reset_callback
        reset_btn.row = len(adicionais) + 2
        self.add_item(reset_btn)

    async def faixa_callback(self, interaction: Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("Este painel não é seu!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        escolha = interaction.data['custom_id'].split(":")[1]

        if self.user.id not in user_choices:
            user_choices[self.user.id] = {"faixa": None, **{a: None for a in adicionais}}

        if user_choices[self.user.id]["faixa"]:
            await interaction.followup.send(
                f"Você já escolheu a faixa {user_choices[self.user.id]['faixa']}. Clique em Reset para mudar.",
                ephemeral=True
            )
            return

        user_choices[self.user.id]["faixa"] = escolha
        await interaction.followup.send(f"✅ Faixa selecionada: {escolha}", ephemeral=True)
        await self.check_complete(interaction)

    async def adicional_callback(self, interaction: Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("Este painel não é seu!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        if self.user.id not in user_choices:
            user_choices[self.user.id] = {"faixa": None, **{a: None for a in adicionais}}

        data = interaction.data['custom_id']
        escolha_tipo, add = data.split(":")
        user_choices[self.user.id][add] = escolha_tipo == "add_sim"

        await interaction.followup.send(
            f"✅ {add}: {'Sim' if user_choices[self.user.id][add] else 'Não'}",
            ephemeral=True
        )

        await self.check_complete(interaction)

    async def reset_callback(self, interaction: Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("Este painel não é seu!", ephemeral=True)
            return

        user_choices[self.user.id] = {"faixa": None, **{a: None for a in adicionais}}
        await interaction.response.send_message("🔄 Suas escolhas foram resetadas!", ephemeral=True)

    async def check_complete(self, interaction: Interaction):
        choices = user_choices.get(self.user.id)
        if not choices:
            return

        if choices["faixa"] is not None and all(choices[a] is not None for a in adicionais):
            faixa_valor = next(valor for f, valor in faixas if f == choices["faixa"])
            total = faixa_valor

            if choices["Mais de 50M Base?"]:
                total += total * 0.15

            if choices["Evento Raro ou Mutação Rara?"]:
                total += total * 0.05

            total = round(total, 2)

            embed = Embed(
                title="🧠 Malevolent Store - Calculadora Brainrot",
                description="Este é o preço final do seu Brainrot!",
                color=0xFF0000
            )

            embed.add_field(name="Usuário", value=f"{interaction.user.mention}", inline=False)
            embed.add_field(name="Faixa", value=f"{choices['faixa']} / {faixa_valor} R$", inline=False)

            for add in adicionais:
                embed.add_field(name=add, value="Sim" if choices[add] else "Não", inline=False)

            embed.add_field(name="💰 Total", value=f"{total} R$", inline=False)

            await interaction.followup.send(embed=embed, ephemeral=True)

            user_choices[self.user.id] = {"faixa": None, **{a: None for a in adicionais}}

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}!")

@bot.slash_command(name="calcular_brainrot", description="Calcula o valor do seu brainrot")
async def calcular_brainrot(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral=True)

    view = BrainrotView(user=ctx.user)

    embed = Embed(
        title="🧠 Malevolent Store - Calculadora Brainrot",
        description="Clique nos botões abaixo para selecionar suas opções.\nSomente você verá suas escolhas.",
        color=0xFF0000
    )

    await ctx.followup.send(embed=embed, view=view, ephemeral=True)

import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot online!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()

bot.run(os.getenv("TOKEN"))

