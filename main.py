import discord
from discord.ext import commands
from discord.ext import bridge
from discord.commands import Option
import os
from dotenv import load_dotenv

intents = discord.Intents.all()


status = discord.Status.online
activity = discord.CustomActivity("/help")

bot = bridge.Bot(intents=intents, 
                status=status,
                activity=activity,
                command_prefix="§"
                )


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")




@bot.slash_command(description="display the latency of the bot")
async def lat(ctx):
    await ctx.respond(f"```Latency is {bot.latency} ms```")



if __name__ == "__main__":
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")


    load_dotenv()
    bot.run(os.getenv("TOKEN"))