import os
import discord
from discord.ext import commands
from discord import app_commands

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
OWNER_ROLE_ID  = 1491137838102741232
TARGET_ROLE_ID = 1488590682342953163

# ─────────────────────────────────────────────
#  BOT SETUP
# ─────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ─────────────────────────────────────────────
#  /dm  — mass DM all members with target role
# ─────────────────────────────────────────────
@tree.command(name="dm", description="Send a DM to all members with the target role.")
@app_commands.describe(message="The message to send.")
async def dm(interaction: discord.Interaction, message: str):
    # Check invoker has owner role
    owner_role = interaction.guild.get_role(OWNER_ROLE_ID)
    if owner_role not in interaction.user.roles:
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.", ephemeral=True
        )
        return

    target_role = interaction.guild.get_role(TARGET_ROLE_ID)
    if target_role is None:
        await interaction.response.send_message(
            "❌ Target role not found.", ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    success = 0
    failed  = 0

    for member in target_role.members:
        if member.bot:
            continue
        try:
            await member.send(message)
            success += 1
        except discord.Forbidden:
            failed += 1
        except discord.HTTPException:
            failed += 1

    await interaction.followup.send(
        f"✅ DM sent to **{success}** member(s). ❌ Failed: **{failed}** (DMs closed).",
        ephemeral=True
    )

# ─────────────────────────────────────────────
#  STARTUP
# ─────────────────────────────────────────────
@bot.event
async def on_ready():
    try:
        synced = await tree.sync()
        print(f"✅ Logged in as {bot.user} — synced {len(synced)} command(s).")
    except Exception as e:
        print(f"❌ Failed to sync: {e}")

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN environment variable is not set.")
    bot.run(TOKEN)
