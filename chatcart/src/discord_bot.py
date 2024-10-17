import os
import discord
import gpt_service
from discord.ext import commands
from discord import app_commands
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from gpt_service import generate_recommendation
from cloud_search import fetch_and_display_products
import time

# Load environment variables
load_dotenv()

def run_chatcart():
    # Discord Bot Token
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


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
    async def latest_bestselling_sneakers(ctx):
        """Get info about latest best-selling sneakers on the market!"""
        try:
            await ctx.response.send_message("Give me a second!")
            response = gpt_service.get_best_selling_sneakers()
            await ctx.channel.send(f"{response}") 

        except Exception as e:
            await ctx.response.send_message(f"An error occurred while fetching the latest best-selling sneakers: {str(e)}")

    @tree.command()
    async def search_by_model(ctx, model_name: str):
        """Search for sneakers by model name using Elasticsearch."""
        try:
            # Call the fetch_and_display_products function with the model name.
            print(f"Searching for products with model name: {model_name}")
            product_map = fetch_and_display_products(model_name)

            # Prepare and send response to Discord
            if product_map:
                response = f"Found {len(product_map)} products for model '{model_name}':\n"
                for product_id, product in product_map.items():
                    response += (
                        f"**Product ID:** {product['product_id']}\n"
                        f"**Brand:** {product['brand']}\n"
                        f"**Model:** {product['model']}\n"
                        f"**Description:** {product['description']}\n"
                        "--------------------------------------\n"
                    )
            else:
                response = f"No products found for model '{model_name}'."
            await ctx.response.send_message(response)
            # await ctx.channel.send(response)
            time.sleep(5)
        except Exception as e:
            # await ctx.channel.send(f"An error occurred while searching: {str(e)}")
            await ctx.response.send_message(f"An error occurred while searching: {str(e)}")

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
    **Chat Cart Bot Commands:**
    - `/search <model> <size>`: Search for sneakers by model and size.
    - `/recommend <model> <size>`: Get recommendations based on available sneakers.
    - `/help`: Show this help message.
    """
        await ctx.response.send_message(help_text)



    # Run the bot
    client.run(DISCORD_TOKEN)