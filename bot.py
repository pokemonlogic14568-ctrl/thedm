import os
import asyncio
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
#  BACKGROUND DM TASK
# ─────────────────────────────────────────────
async def send_dms(members, message, channel, invoker):
    success = 0
    failed  = 0
    for member in members:
        if member.bot:
            continue
        try:
            await member.send(message)
            success += 1
        except (discord.Forbidden, discord.HTTPException):
            failed += 1
        await asyncio.sleep(1)  # avoid rate limits

    try:
        await channel.send(
            f"{invoker.mention} ✅ DM blast done — **{success}** sent, **{failed}** failed (DMs closed).",
            delete_after=30
        )
    except Exception:
        pass

# ─────────────────────────────────────────────
#  /dm  — mass DM all members with target role
# ─────────────────────────────────────────────
@tree.command(name="dm", description="Send a DM to all members with the target role.")
@app_commands.describe(message="The message to send.")
async def dm(interaction: discord.Interaction, message: str):
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

    members = list(target_role.members)

    # Respond immediately so Discord doesn't time out
    await interaction.response.send_message(
        f"📨 Sending DMs to **{len(members)}** members in the background... I'll notify you here when done.",
        ephemeral=True
    )

    # Run DMs in background
    asyncio.create_task(send_dms(members, message, interaction.channel, interaction.user))

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
