import discord
from discord.ext import commands
import asyncio
import requests
import json
import os

results_folder = "ping_results"

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="?", intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

@bot.command()
async def website(ctx, url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    try:
        response = requests.get(url, timeout=5)
        ping_result = {
            "url": url,
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "timestamp": str(ctx.message.created_at)
        }
    except requests.RequestException:
        ping_result = {
            "url": url,
            "status_code": None,
            "response_time": None,
            "timestamp": str(ctx.message.created_at)
        }

    ping_results = load_ping_results(ctx.author.id)
    ping_results.append(ping_result)

    save_ping_results(ctx.author.id, ping_results)

    await ctx.send(f"Ping result for {url} saved.")

def load_ping_results(user_id):
    file_path = get_file_path(user_id)
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_ping_results(user_id, ping_results):
    file_path = get_file_path(user_id)
    with open(file_path, "w") as file:
        json.dump(ping_results, file, indent=4)

def get_file_path(user_id):
    return f"{results_folder}/{user_id}_ping_results.json"

@bot.command()
async def view_results(ctx):
    ping_results = load_ping_results(ctx.author.id)
    if ping_results:
        embed = discord.Embed(title="Ping Results", description="Here are your saved ping results:")
        for result in ping_results:
            embed.add_field(name="URL", value=result["url"], inline=False)
            embed.add_field(name="Status Code", value=result["status_code"], inline=False)
            embed.add_field(name="Response Time", value=result["response_time"], inline=False)
            embed.add_field(name="Timestamp", value=result.get("timestamp", "N/A"), inline=False)
            embed.add_field(name="-----------------", value="-----------------", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("No ping results found.")

@bot.command()
async def clear_results(ctx):
    file_path = get_file_path(ctx.author.id)
    if os.path.exists(file_path):
        os.remove(file_path)
        await ctx.send("Ping results cleared.")
    else:
        await ctx.send("No ping results found.")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Website Pinger Bot Help", description="List of available commands:")
    embed.add_field(name="?website [url]", value="Ping a website and save the result.", inline=False)
    embed.add_field(name="?view_results", value="Show the saved ping results.", inline=False)
    embed.add_field(name="?clear_results", value="Clear all saved ping results.", inline=False)
    await ctx.send(embed=embed)

bot.run("")
