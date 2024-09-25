import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI GPT Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Ensure this is set in your .env file
openai.api_key = OPENAI_API_KEY

def generate_recommendation(model: str, size: float, sneaker_data: list, engine: str = "gpt-4", temperature: float = 0.7, max_tokens: int = 150) -> str:
    """
    Generate sneaker recommendations using OpenAI's GPT.

    :param model: The sneaker model.
    :param size: The sneaker size.
    :param sneaker_data: List of sneaker information dictionaries.
    :param engine: The OpenAI model to use.
    :param temperature: Controls the creativity of the response.
    :param max_tokens: Maximum number of tokens in the response.
    :return: GPT-generated recommendation string.
    """
    try:
        prompt = f"""
        You are a sneaker expert. Based on the following sneaker listings, provide personalized recommendations for the user. Consider factors like price, availability, and brand reputation.

        Model: {model}, Size: {size}

        Listings:
        """
        for sneaker in sneaker_data:
            prompt += f"- Website: {sneaker['website']}, Price: ${sneaker['price']}, Stock: {sneaker['stock']}\n"

        prompt += "\nRecommendations:"

        response = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            n=1,
            stop=None
        )

        recommendation = response.choices[0].text.strip()
        return recommendation

    except Exception as e:
        return f"Error generating recommendation: {str(e)}"
