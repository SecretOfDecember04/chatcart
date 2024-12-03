import os
import discord
import gpt_service
from discord.ext import commands
from discord import app_commands
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from gpt_service import generate_recommendation, get_clothing_suggestions, get_sneaker_analysis
from elastic_search import fetch_and_display_products_by_model
from elastic_search import select_product_and_size
# from elastic_search import select_product_and_size
# from elastic_search import fetch_product_prices
import time
import csv

# Load environment variables
load_dotenv()

cloud_id = 'My_deployment:dXMtZWFzdC0yLmF3cy5lbGFzdGljLWNsb3VkLmNvbSRjMGVjZWU3NTQ4N2Y0ZmM0YTJiMjcxMGFkYjkxZmI1MiRhNTgyN2EwZGUwNWE0ZjJmODAwMWRhYTU2MGM4NWU1Mw==' 
api_key = 'VlA1TGlwTUJaSEZnUDlMSkV3cDc6T3B5Q3p0Q2hScXE4aWVLelZDX056QQ==' 

# Elasticsearch connection (using Cloud ID and API key)
es = Elasticsearch(
    cloud_id=cloud_id,
    api_key=api_key
)

def run_chatcart():
    # Discord Bot Token
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


    # Initialize Discord Bot
    intents = discord.Intents.all()
    client = discord.Client(intents=intents, description="Chat Cart Bot")
    tree = app_commands.CommandTree(client)

    # Guild ID for "ChatCart" Server
    ServerID = discord.Object(id=1284660112786456648)

    user_favorites = {}

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
    async def search_by_product_id(ctx, product_id: int):
        """Search for a sneaker by product ID and display price/stock information using Elasticsearch."""
        try:
            query = {
                "query": {
                    "term": {
                        "product_id": product_id 
                    }
                }
            }

            response = es.search(index="products", body=query)

            if response['hits']['total']['value'] > 0:
                product = response['hits']['hits'][0]['_source'] 

                response_message = (
                    f"**Product ID:** {product['product_id']}\n"
                    f"**Brand:** {product['brand']}\n"
                    f"**Model:** {product['model']}\n"
                    f"**Description:** {product['description']}\n"
                    "--------------------------------------\n"
                )

                prices = product['prices']
                if prices:
                    sizes = [price['size'] for price in prices]
                    response_message += f"\nAvailable sizes: {', '.join(map(str, sizes))}\n"
                    
                    for price_info in prices:
                        size_details = (
                            f"\nDetails for size {price_info['size']}:\n"
                            f"**Source:** {price_info['source']}\n"
                            f"**Price:** {price_info['price']}\n"
                            f"**Stock Level:** {price_info['stock_level']}\n"
                            f"**Last Update:** {price_info['last_update']}\n"
                            "--------------------------------------\n"
                        )
                        response_message += size_details
                    
                    await ctx.response.send_message(response_message)
                else:
                    await ctx.response.send_message(f"No price or stock information available for product ID '{product_id}'.")

            else:
                await ctx.response.send_message(f"No product found with ID '{product_id}'.")

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
            response = es.search(index=products, body={"query": query})
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
    - `/search_by_product_id <product_id>`: Search for a sneaker by product ID.
    - `/recommend <model> <size>`: Get recommendations based on available sneakers.
    - `/clothing_suggestions <model>`: Get clothing matching suggestions for a sneaker model.
    - `/sneaker_analysis <model>`: Get an analysis of a sneaker model with pros and cons.
    - `/latest_bestselling_sneakers`: Get info about the latest best-selling sneakers.
    - `/help`: Show this help message.
    """
        await ctx.response.send_message(help_text)

    @tree.command()
    async def clothing_suggestions(ctx, model: str):
        """Get clothing matching suggestions for a selected sneaker model."""
        try:
            await ctx.response.send_message("Generating clothing suggestions...")
            suggestions = get_clothing_suggestions(model)
            await ctx.channel.send(f"**Clothing Suggestions for '{model}':**\n{suggestions}")
        except Exception as e:
            await ctx.response.send_message(f"An error occurred: {str(e)}")

    @tree.command()
    async def sneaker_analysis(ctx, model: str):
        """Get an analysis of a sneaker model with pros and cons."""
        try:
            await ctx.response.send_message("Fetching sneaker analysis...")
            analysis = get_sneaker_analysis(model)
            await ctx.channel.send(f"**Analysis of '{model}':**\n{analysis}")
        except Exception as e:
            await ctx.response.send_message(f"An error occurred: {str(e)}")

    @tree.command()
    async def add_to_favorites(ctx, product_id: int):
        """Add a sneaker to your favorites."""
        user_id = str(ctx.user.id)
        if user_id not in user_favorites:
            user_favorites[user_id] = []
        user_favorites[user_id].append(product_id)
        await ctx.response.send_message(f"Product ID {product_id} has been added to your favorites.")

    @tree.command()
    async def view_favorites(ctx):
        """View your favorite sneakers."""
        user_id = str(ctx.user.id)
        if user_id in user_favorites and user_favorites[user_id]:
            favorite_ids = user_favorites[user_id]
            details = []
            for product_id in favorite_ids:
                query = {
                    "query": {
                        "term": {
                            "product_id": product_id
                        }
                    }
                }
                response = es.search(index="products", body=query)
                if response['hits']['total']['value'] > 0:
                    details.append(response['hits']['hits'][0]['_source'])

            if details:
                # Prepare formatted response
                response_message = "**Your Favorite Sneakers:**\n\n"
                for product in details:
                    response_message += (
                        f"**Product ID:** {product['product_id']}\n"
                        f"**Brand:** {product['brand']}\n"
                        f"**Model:** {product['model']}\n"
                        f"**Description:** {product['description']}\n"
                        "--------------------------------------\n"
                    )
                await ctx.response.send_message(response_message)
            else:
                await ctx.response.send_message("Could not retrieve details for your favorites.")
        else:
            await ctx.response.send_message("Your favorites list is empty.")

    def get_top_discounted_sneakers(csv_file, top_n=10):
        # List to hold the processed shoe data
        sneakers = []
        
        try:
            # Read the CSV file and process each line
            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    brand_model = row['Shoe Brand & Model']
                    original_price = float(row['Original Price'])
                    discounted_price = float(row['Discounted Price'])
                    
                    # Calculate the discount percentage
                    discount_percentage = ((original_price - discounted_price) / original_price) * 100
                    
                    sneakers.append({
                        'brand_model': brand_model,
                        'original_price': original_price,
                        'discounted_price': discounted_price,
                        'discount_percentage': discount_percentage
                    })
                    
            # Sort the list by discount_percentage in descending order and pick the top N items
            top_discounted_sneakers = sorted(sneakers, key=lambda x: x['discount_percentage'], reverse=True)[:top_n]
            return top_discounted_sneakers
        
        except Exception as e:
            print(f"Error processing the CSV file: {str(e)}")
            return None

    # Add the new command to your bot
    @tree.command()
    async def top_discounted_sneakers(ctx):
        """Get the top 10 sneakers with the largest discounts."""
        try:
            # Path to the CSV file
            csv_file = 'dealmoon_deals.csv'

            # Get the top 10 discounted sneakers
            top_sneakers = get_top_discounted_sneakers(csv_file, top_n=10)
            
            if top_sneakers:
                # Prepare the response message with the top 10 discounted sneakers
                response_message = "**Top 10 Discounted Sneakers:**\n\n"
                for sneaker in top_sneakers:
                    response_message += (
                        f"**{sneaker['brand_model']}**\n"
                        f"Original Price: ${sneaker['original_price']:.2f}\n"
                        f"Discounted Price: ${sneaker['discounted_price']:.2f}\n"
                        f"Discount: {sneaker['discount_percentage']:.2f}%\n"
                        "--------------------------------------\n"
                    )
                await ctx.response.send_message(response_message)
            else:
                await ctx.response.send_message("Sorry, there was an error retrieving the data.")

        except Exception as e:
            await ctx.response.send_message(f"An error occurred while fetching the top discounted sneakers: {str(e)}")



    # Run the bot
    client.run(DISCORD_TOKEN)