import os
import discord
from discord.ext import commands
from discord import app_commands
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from gpt_service import generate_recommendation 

# Load environment variables
load_dotenv()

# Discord Bot Token
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')  # Set this in your .env file

# ElasticSearch Configuration
ELASTIC_HOST = os.getenv('ELASTIC_HOST', 'http://localhost:9200')
ELASTIC_INDEX = os.getenv('ELASTIC_INDEX', 'sneakers')

# Initialize ElasticSearch client
es = Elasticsearch(ELASTIC_HOST)

# Initialize Discord Bot
intents = discord.Intents.all()
client = discord.Client(intents=intents, description="Chat Cart Bot")
tree = app_commands.CommandTree(client)

# Guild ID for "ChatCart" Server
ServerID = discord.Object(id=1284660112786456648)

@client.event
async def on_ready():
    tree.copy_global_to(guild=ServerID)
    await tree.sync(guild=ServerID)
    print(f'{client.user} is now running!')

@tree.command()
async def search_sneakers(ctx, model: str, size: float):
    """Search for sneakers by model and size."""
    query = {
        "bool": {
            "must": [
                {"match": {"model": model}},
                {"match": {"size": size}}
            ]
        }
    }

    try:
        response = es.search(index=ELASTIC_INDEX, body={"query": query})
        hits = response['hits']['hits']
        
        if not hits:
            await ctx.channel.send(f"No results found for model '{model}' and size '{size}'.")
            return

        # Prepare the response message
        message = f"Results for **{model}**, size **{size}**:\n"
        for hit in hits:
            source = hit['_source']
            message += f"- **Website**: {source['website']}\n  **Price**: ${source['price']}\n  **Stock**: {source['stock']}\n  **URL**: {source['url']}\n"

        await ctx.channel.send(message)

    except Exception as e:
        await ctx.channel.send(f"An error occurred while searching: {str(e)}")

@tree.command()
async def recommend_sneakers(ctx, model: str, size: float):
    """Fetch similar sneakers from ElasticSearch."""
    query = {
        "bool": {
            "must": [
                {"match": {"model": model}},
                {"match": {"size": size}}
            ]
        }
    }

    try:
        response = es.search(index=ELASTIC_INDEX, body={"query": query})
        hits = response['hits']['hits']
        
        if not hits:
            await ctx.channel.send(f"No data available to provide recommendations for model '{model}' and size '{size}'.")
            return

        # Extract relevant data for GPT
        sneaker_data = []
        for hit in hits:
            source = hit['_source']
            sneaker_data.append({
                "website": source['website'],
                "price": source['price'],
                "stock": source['stock']
            })

        # Generate recommendation using the GPT service
        recommendation = generate_recommendation(model, size, sneaker_data)
        await ctx.channel.send(f"**Recommendations:**\n{recommendation}")

    except Exception as e:
        await ctx.send(f"An error occurred while generating recommendations: {str(e)}")

@tree.command()
async def help_command(ctx):
    """Show available commands."""
    help_text = """
**Sneaker Info Bot Commands:**
- `/search <model> <size>`: Search for sneakers by model and size.
- `/recommend <model> <size>`: Get recommendations based on available sneakers.
- `/help`: Show this help message.
"""
    await ctx.channel.send(help_text)

# Run the bot
client.run(DISCORD_TOKEN)
