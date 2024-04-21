import discord
from discord import app_commands
from discord.embeds import Embed
import requests
import json
import asyncio  # Add this import statement for asyncio


MY_GUILD = discord.Object(id=1231367123520196728)  # Replace with your guild ID
ALLOWED_ROLE_ID = 1231368359829049467
class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command()
async def stock(interaction: discord.Interaction):
    url = "https://dateless.000webhostapp.com/"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        counts = {
            "1 Week": {"Advanced": len(data["weekadvanced"]), "Basic": len(data["weekbasic"])},
            "1 Month": {"Advanced": len(data["monthadvanced"]), "Basic": len(data["monthbasic"])}
        }

        embed = Embed(title="Stock Counts")
        embed.set_thumbnail(url="https://headshot.su/assets/images/logo.png")  # Replace with your thumbnail URL
        for period, details in counts.items():
            value = ""
            for key, count in details.items():
                value += f"{key}: {count}\n"
            embed.add_field(name=period, value=value, inline=True)

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Failed to fetch data from the server.")

@client.tree.command(guild=MY_GUILD)
async def add(interaction: discord.Interaction, duration: str, code: str):
    if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("You do not have permission to use this command.")
        return
    if not duration or not code:
        await interaction.response.send_message("Invalid format. Please provide the duration and the code.")
        return
    if duration not in ["weekbasic", "weekadvanced", "monthadvanced", "monthbasic"]:
        await interaction.response.send_message("Invalid Duration. Please use 'weekbasic' or 'weekadvanced' or 'monthadvanced' or 'monthbasic'.")
        return

    link = f"https://dateless.000webhostapp.com/asdoah928y.php?code={code}&table={duration}"
    response = requests.get(link)

    if response.status_code == 200:
        await interaction.response.send_message("Key added successfully.")
    else:
        await interaction.response.send_message("Error adding key.")

@client.tree.command()
async def remove(interaction: discord.Interaction, code: str):
    if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("You do not have permission to use this command.")
        return
    await removekey(interaction, code)


@client.tree.command()
async def use(interaction: discord.Interaction, duration: str, user: discord.User):
    if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("You do not have permission to use this command.")
        return
    try:
        if interaction.response.is_done():
            return  # Ignore if interaction has already been responded to

        duration = duration.lower()
        if duration not in ["weekbasic", "weekadvanced", "monthbasic", "monthadvanced"]:
            await interaction.response.send_message("Invalid duration provided.")
            return

        key = get_key_from_website(duration)
        if key:
            await send_key_to_user(user, key)
            await interaction.response.send_message(f"Key sent to {user.mention}.")
        else:
            await interaction.response.send_message("Failed to retrieve key from the website.")
    except discord.errors.InteractionResponded:
        pass  # Ignore if interaction has already been responded to


def get_key_from_website(duration: str) -> str:
    # Fetch the raw data from the website
    response = requests.get("https://dateless.000webhostapp.com/")
    if response.status_code == 200:
        # Parse the JSON data
        data = json.loads(response.text)
        # Extract the key based on the duration
        keys = data.get(duration, [])
        if keys:
            return keys[0]  # Return the full key including brackets
    return "FAILED"

async def removekey(interaction,key):
    url = f"https://dateless.000webhostapp.com/removekey.php?code={key}"
    response = requests.get(url)
    if response.status_code == 200:
        await interaction.response.send_message(f"`{key}` removed")
    else:
        await interaction.response.send_message("Failed to remove key. Please try again later.")

async def send_key_to_user(user, key):
    url = f"https://dateless.000webhostapp.com/removekey.php?code={key}"
    response = requests.get(url)
    if response.status_code == 200:
        await user.send(f"Here is your key `{key}`")
    else:
        await user.send("Failed to send key. Please try again later.")


client.run('MTIzMTQxNDEzODEwMjYxMjAwOQ.GIsJp8.X-h-4T_g01_l5mfjq_sILmV-n2AdU5736GQaE4')
