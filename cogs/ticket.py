import asyncio
import json

import discord
from discord.ext import commands
from discord.ui import View
from discord.commands import slash_command, Option


CATEGORY_ROLES = {
            "Support": "Discord Staff",
            "Report": "Discord Staff",
            "Minecraft Support": "MC Staff",
            "Claim Media role": "head of ticket",
            "Partnership": "head of ticket",
            "Other": "Discord Staff"
        }

def load_data(self):
    with open("ticket_data.json", "r") as f:
        return json.load(f)

def save_data(self, data):
    with open("ticket_data.json", "w") as f:
        json.dump(data, f, indent=4)


class ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ticketselect())  
        self.bot.add_view(ticketwelcome())


    @slash_command(description="Creates a ticket panel")
    async def panel(self, ctx):

        
        ticket_embed = discord.Embed(
            title="Ticket | Support",
            description="Select a category to create a ticket",
            color=discord.Color.yellow()
        )

        await ctx.response.defer(ephemeral=True)
        await ctx.channel.send(embed=ticket_embed, view=ticketselect())
        await ctx.respond("The ticket panel has been created!", ephemeral=True)

    



def setup(bot):
    bot.add_cog(ticket(bot))




class ticketselect(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


    options = [
            discord.SelectOption(label="Support", description="Get help with general questions or problems related to the Discord server."),
            discord.SelectOption(label="Report", description="Report a user or issue"),
            discord.SelectOption(label="Minecraft Support", description="Report issues or ask for help related to the Minecraft server."),
            discord.SelectOption(label="Claim Media role", description="Request the media role if you create content about the server."),
            discord.SelectOption(label="Partnership", description="Inquire about partnership opportunities with our server."),
            discord.SelectOption(label="Other", description="Other issues or questions")
        ]

    @discord.ui.select(
            min_values=1,
            max_values=1,
            placeholder="Select a category",
            options=options,
            custom_id="ticket_select"
    )

    async def callback(self, select, interaction):
        category = select.values[0]

        role_name = CATEGORY_ROLES.get(category)
        role = discord.utils.get(interaction.guild.roles, name=role_name)

        if role:
            content = role.mention
        else:
            content = "No staff role found"

        channel_category = interaction.channel.category

        
        
        #Old ticket naming system, replaced with ticket ID generation to avoid issues with duplicate names and to allow more than 2 tickets per user

        # existing = discord.utils.get(interaction.guild.text_channels, name=f"ticket-{interaction.user.name}")
        # if existing:
        #     existing2 = discord.utils.get(interaction.guild.text_channels, name=f"ticket-{interaction.user.name}_2")
        #     if existing2:
        #         await interaction.response.send_message("You already have 2 open tickets! Please close one before creating a new one.", ephemeral=True)
        #         return

        #     else:
        #         channel_name = f"ticket-{interaction.user.name}_2"
        # else:
        #         channel_name = f"ticket-{interaction.user.name}"


        # Check for existing open tickets
        data = load_data(self)

        open_tickets = [
            t for t in data["tickets"].values()
            if t == interaction.user.id
        ]

        if len(open_tickets) >= 2:
            await interaction.response.send_message(
                "You already have 2 open tickets.",
                ephemeral=True
            )
            return

        # Ticket ID generation
        data["ticket_counter"] += 1
        ticket_id = str(data["ticket_counter"]).zfill(4)

        save_data(self, data)

        channel_name = f"ticket-{ticket_id}"



        channel = await interaction.guild.create_text_channel(
            category = channel_category,
            name = channel_name,
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                discord.utils.get(interaction.guild.roles, name="Discord Staff"): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                discord.utils.get(interaction.guild.roles, name="RAZ Ticket"): discord.PermissionOverwrite(read_messages=True, send_messages=True)

            }
        )

        #data = load_data(self)
        data["tickets"][str(channel.id)] = interaction.user.id
        save_data(self, data)

        ticket_created_embed = discord.Embed(
            title="Ticket Created",
            description=f"New ticket: {channel.mention}.",
            color=discord.Color.green()
        )

        ticket_created_embed.add_field(name="Category:", value=category, inline=False)

        await interaction.response.send_message(embed=ticket_created_embed, ephemeral=True)


        ticket_welcome_embed = discord.Embed(
            title="Welcome to your ticket!",
            description=f"Please describe your issue in detail and a staff member will be with you shortly.\nTo close the ticket, click the button below. \n",
            color=discord.Color.green()
        )

        ticket_welcome_embed.add_field(name="Ticket ID:", value=ticket_id, inline=False)
        ticket_welcome_embed.add_field(name="Category:", value=category, inline=False)
        ticket_welcome_embed.add_field(name="Created by:", value=interaction.user.mention, inline=True)


        staff_role = discord.utils.get(interaction.guild.roles, name="Discord Staff")
        await channel.send(
            f"{content}", 
            embed=ticket_welcome_embed, 
            view=ticketwelcome()
            )





class ticketwelcome(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    

    @discord.ui.button(label="Close", 
                       style=discord.ButtonStyle.red, 
                       custom_id="close_button"
                       )
    async def close_callback(self, button, interaction):

        data = load_data(self)

        channel_id = str(interaction.channel.id)

        if channel_id in data["tickets"]:
            del data["tickets"][channel_id]

        if channel_id in data["claims"]:
            del data["claims"][channel_id]

        save_data(self, data)


        await interaction.response.send_message("The ticket will be closed in 5 seconds.", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()


    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green, custom_id="claim_ticket")
    async def claim(self, button, interaction):
        


        data = load_data(self)
        claims = data["claims"]


        #check for staff role
        staff_role = discord.utils.get(interaction.guild.roles, name="Discord Staff")
        if staff_role not in interaction.user.roles:
            return await interaction.response.send_message("You are not staff.", ephemeral=True)

        channel_id = str(interaction.channel.id)

        if channel_id in claims:            
            user = interaction.guild.get_member(claims[channel_id])
            if user == interaction.user:

                del claims[channel_id]
                save_data(self, data)

                await interaction.channel.set_permissions(discord.utils.get(interaction.guild.roles, name="Discord Staff"), read_messages=True, send_messages=True)
                await interaction.channel.set_permissions(interaction.user, read_messages=True, send_messages=False)

                button.label = "Claim"
                button.style = discord.ButtonStyle.green
                await interaction.message.edit(view=self)

                return await interaction.response.send_message(
                    f"{interaction.user.mention} unclaimed the ticket."
                )


            return await interaction.response.send_message(
                f"Ticket already claimed by {user.mention}",
                ephemeral=True
            )

        claims[channel_id] = interaction.user.id
        save_data(self, data)

        await interaction.channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await interaction.channel.set_permissions(discord.utils.get(interaction.guild.roles, name="Discord Staff"), read_messages=True, send_messages=False)

        button.label = "Unclaim"
        button.style = discord.ButtonStyle.gray

        await interaction.message.edit(view=self)
        await interaction.response.send_message(
            f"Ticket claimed by {interaction.user.mention}"
        )
