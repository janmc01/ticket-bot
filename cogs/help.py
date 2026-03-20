import discord
from discord.ext import commands
from discord.commands import slash_command, Option


class Help(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="help", description="displays all available commands")
    async def help(self, ctx: discord.ApplicationContext):
        
        embed = discord.Embed(
            title="📖 Help",
            description="All Commands:",
            color=discord.Color.blurple()
        )

        for command in self.bot.application_commands:
            embed.add_field(
                name=f"/{command.name}",
                value=command.description or "No description available.",
                inline=False
            )

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Help(bot))