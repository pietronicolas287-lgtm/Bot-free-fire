import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

# ================= CONFIG =================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= FILAS =================
filas = {}

def key_fila(tipo, modo, plataforma, arma):
    return f"{tipo}_{modo}_{plataforma}_{arma}"

# ================= VIEW FINAL =================
class FilaFinalView(discord.ui.View):
    def __init__(self, key):
        super().__init__(timeout=None)
        self.key = key

    @discord.ui.button(label="Entrar na fila", style=discord.ButtonStyle.green)
    async def entrar(self, interaction: discord.Interaction, button: discord.ui.Button):
        fila = filas.setdefault(self.key, [])

        # Impede mais de 2 jogadores
        if len(fila) >= 2:
            await interaction.response.send_message(
                "❌ A fila já está completa (2/2).",
                ephemeral=True
            )
            return

        # Evita entrar duas vezes
        if interaction.user.id in fila:
            await interaction.response.send_message(
                "❌ Você já está nessa fila.",
                ephemeral=True
            )
            return

        fila.append(interaction.user.id)

        # Fecha a fila com 2 jogadores
        if len(fila) == 2:
            jogadores = " vs ".join([f"<@{uid}>" for uid in fila])

            await interaction.response.send_message(
                f"🔥 **FILA COMPLETA!**\n👥 {jogadores}\n🎮 A partida pode começar!",
                ephemeral=False
            )

            # ⏱️ RESET AUTOMÁTICO (5 segundos)
            await discord.utils.sleep_until(
                discord.utils.utcnow() + timedelta(seconds=5)
            )

            filas[self.key] = []

        else:
            await interaction.response.send_message(
                "✅ Você entrou na fila.\n👥 Jogadores: 1/2",
                ephemeral=True
            )

    @discord.ui.button(label="Sair da fila", style=discord.ButtonStyle.red)
    async def sair(self, interaction: discord.Interaction, button: discord.ui.Button):
        fila = filas.get(self.key, [])

        if interaction.user.id in fila:
            fila.remove(interaction.user.id)
            await interaction.response.send_message(
                "🚪 Você saiu da fila.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Você não está nessa fila.",
                ephemeral=True
            )

# ================= MENUS =================
class ArmaView(discord.ui.View):
    def __init__(self, tipo, modo, plataforma):
        super().__init__(timeout=60)
        self.tipo = tipo
        self.modo = modo
        self.plataforma = plataforma

    @discord.ui.button(label="UMP", style=discord.ButtonStyle.primary)
    async def ump(self, interaction: discord.Interaction, button):
        await criar_fila_final(interaction, self.tipo, self.modo, self.plataforma, "ump")

    @discord.ui.button(label="XM8", style=discord.ButtonStyle.primary)
    async def xm8(self, interaction: discord.Interaction, button):
        await criar_fila_final(interaction, self.tipo, self.modo, self.plataforma, "xm8")

class PlataformaView(discord.ui.View):
    def __init__(self, tipo, modo):
        super().__init__(timeout=60)
        self.tipo = tipo
        self.modo = modo

    @discord.ui.button(label="Mobile", style=discord.ButtonStyle.secondary)
    async def mobile(self, interaction, button):
        await interaction.response.edit_message(
            content="🔫 Escolha a arma:",
            view=ArmaView(self.tipo, self.modo, "mobile")
        )

    @discord.ui.button(label="Emulador", style=discord.ButtonStyle.secondary)
    async def emulador(self, interaction, button):
        await interaction.response.edit_message(
            content="🔫 Escolha a arma:",
            view=ArmaView(self.tipo, self.modo, "emulador")
        )

    @discord.ui.button(label="Misto", style=discord.ButtonStyle.secondary)
    async def misto(self, interaction, button):
        await interaction.response.edit_message(
            content="🔫 Escolha a arma:",
            view=ArmaView(self.tipo, self.modo, "misto")
        )

class ModoView(discord.ui.View):
    def __init__(self, tipo):
        super().__init__(timeout=60)
        self.tipo = tipo

    async def escolher(self, interaction, modo):
        await interaction.response.edit_message(
            content="📱 Escolha a plataforma:",
            view=PlataformaView(self.tipo, modo)
        )

    @discord.ui.button(label="1v1", style=discord.ButtonStyle.secondary)
    async def v1(self, i, b): await self.escolher(i, "1v1")

    @discord.ui.button(label="2v2", style=discord.ButtonStyle.secondary)
    async def v2(self, i, b): await self.escolher(i, "2v2")

    @discord.ui.button(label="3v3", style=discord.ButtonStyle.secondary)
    async def v3(self, i, b): await self.escolher(i, "3v3")

    @discord.ui.button(label="4v4", style=discord.ButtonStyle.secondary)
    async def v4(self, i, b): await self.escolher(i, "4v4")

class TipoView(discord.ui.View):
    @discord.ui.button(label="NORMAL", style=discord.ButtonStyle.success)
    async def normal(self, interaction, button):
        await interaction.response.edit_message(
            content="🎮 Escolha o modo:",
            view=ModoView("normal")
        )

    @discord.ui.button(label="FULL", style=discord.ButtonStyle.danger)
    async def full(self, interaction, button):
        await interaction.response.edit_message(
            content="🎮 Escolha o modo:",
            view=ModoView("full")
        )

# ================= FINAL =================
async def criar_fila_final(interaction, tipo, modo, plataforma, arma):
    key = key_fila(tipo, modo, plataforma, arma)

    embed = discord.Embed(
        title="🔥 FILA FREE FIRE",
        description=(
            f"⚔️ **Tipo:** {tipo.upper()}\n"
            f"🎮 **Modo:** {modo}\n"
            f"📱 **Plataforma:** {plataforma}\n"
            f"🔫 **Arma:** {arma.upper()}\n\n"
            "Use os botões abaixo 👇"
        ),
        color=0xffa500
    )

    await interaction.response.edit_message(
        content=None,
        embed=embed,
        view=FilaFinalView(key)
    )

# ================= SLASH COMMAND =================
@bot.tree.command(name="fila_ff", description="Abrir painel de filas Free Fire")
async def fila_ff(interaction: discord.Interaction):
    await interaction.response.send_message(
        "⚔️ Escolha o tipo da partida:",
        view=TipoView()
    )

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🔥 Bot ligado como {bot.user}")
# ================= RUN =================
bot.run(os.getenv("f2efd1e4463625b68d1b0459dc5ef32adf3817a11198f6d02a0172b8377794c0"))
