import os
import discord
import gpt_service
from discord.ext import commands
from discord import app_commands
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from gpt_service import generate_recommendation
from elastic_search import fetch_and_display_products_by_model
from elastic_search import fetch_product_by_id
from elastic_search import fetch_product_prices
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
            product_map = fetch_and_display_products_by_model(model_name)

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
    async def search_by_product_id(ctx, product_id: str):
        """Search for a sneaker by product ID and display price/stock information using Elasticsearch."""
        try:
            # Call the fetch_product_by_id function with the product ID.
            print(f"Searching for product with ID: {product_id}")
            product = fetch_product_by_id(product_id)

            # Prepare and send product details to Discord
            if product:
                response = (
                    f"**Product ID:** {product['product_id']}\n"
                    f"**Brand:** {product['brand']}\n"
                    f"**Model:** {product['model']}\n"
                    f"**Description:** {product['description']}\n"
                    "--------------------------------------\n"
                )
                
                # Fetch prices and stock information
                prices = fetch_product_prices(product_id)
                if prices:
                    sizes = [price['size'] for price in prices]
                    response += f"\nAvailable sizes: {', '.join(map(str, sizes))}\n"
                    await ctx.response.send_message(response)

                    # Simulate user entering a size (you can later modify this for actual input handling)
                    size_input = input("\nEnter the size you are interested in: ")
                    try:
                        size = float(size_input)
                        valid_size = False

                        for price_info in prices:
                            if price_info['size'] == size:
                                valid_size = True
                                size_details = (
                                    f"\nDetails for size {size}:\n"
                                    f"**Source:** {price_info['source']}\n"
                                    f"**Price:** {price_info['price']}\n"
                                    f"**Stock Level:** {price_info['stock_level']}\n"
                                    f"**Last Update:** {price_info['last_update']}\n"
                                    "--------------------------------------\n"
                                )
                                await ctx.response.send_message(size_details)
                        
                        if not valid_size:
                            await ctx.response.send_message(f"Size {size} is not available for this model.")
                    except ValueError:
                        await ctx.response.send_message(f"'{size_input}' is not a valid size. Please enter a numeric size.")
                else:
                    await ctx.response.send_message(f"No price or stock information available for product ID '{product_id}'.")

            else:
                await ctx.response.send_message(f"No product found with ID '{product_id}'.")
            
            time.sleep(5)
        except Exception as e:
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