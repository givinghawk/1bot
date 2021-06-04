import discord
import os
import json
import dotenv
from discord.ext import commands
from discord.ext.commands.help import MinimalHelpCommand
dotenv.load_dotenv()


def get_prefix(client, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]


client = commands.Bot(command_prefix=get_prefix,
                      case_insensitive=True,
                      activity=discord.Game("_help"),
                      help_command=MinimalHelpCommand())


@client.event
async def on_ready():
    print("Main script is running")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BotMissingPermissions):
        async with ctx.typing():
            await ctx.send("Command failed - I don't have enough permissions to run this command!")
    elif isinstance(error, commands.MissingPermissions):
        async with ctx.typing():
            await ctx.send("You don't have enough permissions to use this command.")
    elif isinstance(error, commands.NotOwner):
        async with ctx.typing():
            await ctx.send("Only the owner of the bot can use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        async with ctx.typing():
            await ctx.send("You've missed one or more required arguments. Check the command's help for what arguments you should provide.")
    elif isinstance(error, commands.BadArgument):
        async with ctx.typing():
            await ctx.send("Bad Argument error - make sure you've typed your arguments correctly.")
    elif isinstance(error, commands.ChannelNotFound):
        async with ctx.typing():
            await ctx.send("I don't think that channel exists!")
    elif isinstance(error, commands.CommandNotFound) == False:
        print(error)


@client.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = "_"

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)


@client.event
async def on_guild_remove(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)


@client.command(help="Tests the bot's latency and displays it in miliseconds")
async def ping(ctx):
    await ctx.send(f"Pong! The bot's latency is `{round(client.latency * 1000)}ms`")


@client.command(help="Change the bot's prefix", aliases=["prefix"])
@commands.has_permissions(manage_guild=True)
async def changeprefix(ctx, prefix):
    async with ctx.typing():
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix

        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)
    await ctx.send(f"✅ Prefix for this server is set to {prefix}")


@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")
    async with ctx.typing():
        await ctx.send(f"Loaded {extension}")


@client.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    async with ctx.typing():
        await ctx.send(f"Unloaded {extension}")


@client.command(help="Get a link to the bot's source code on GitHub", aliases=["source", "sourcecode"])
async def github(ctx):
    await ctx.send("https://github.com/objectopensource/i-do-stuff-bot\nIf you want to run your own instance of the bot, clone the repository or download it as a .zip and run `main.py.` Feel free to fork the repository.")

# Loop through all files in cogs directory and load them
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(os.environ["TOKEN"])
