import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI GPT Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Ensure this is set in your .env file
openai.api_key = OPENAI_API_KEY

def get_best_selling_sneakers() -> str:
    """
    Calls the GPT-4 model with a prompt asking for the latest best-selling sneakers.

    Returns:
        str: The response from GPT-4 with the list of best-selling sneakers.
    """
    # Define the prompt
    prompt = (
        "What are the current best-selling athletic shoes on the market? "
        "Please provide the names and models, and include 8 examples in the following format: **Model** - description. Your answer should not include years or dates."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        # Extract and return the generated response text
        return response['choices'][0]['message']['content']
    
    except Exception as e:
        return f"An error occurred: {e}"

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
    

def get_clothing_suggestions(model: str) -> str:
    """
    Generate clothing matching suggestions for a sneaker model using GPT-4.

    :param model: The sneaker model name.
    :return: GPT-generated clothing suggestions.
    """
    # Define the prompt
    prompt = (
        f"You are a fashion expert specializing in matching sneakers with clothing. "
        f"Provide clothing matching suggestions for the '{model}' sneaker model. "
        "Include a description of clothing types and styles that would complement this sneaker model."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        
        # Extract and return the generated response text
        return response['choices'][0]['message']['content']
    
    except Exception as e:
        return f"An error occurred while generating clothing suggestions: {str(e)}"


def get_sneaker_analysis(model: str) -> str:
    """
    Generate an analysis of a sneaker model with pros and cons using GPT-4.

    :param model: The sneaker model name.
    :return: GPT-generated analysis with pros and cons.
    """
    # Define the prompt
    prompt = (
        f"You are a sneaker expert. Provide a detailed analysis of the '{model}' sneaker model, "
        "including its pros and cons. List at least three pros and three cons to help users make an informed decision."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        
        # Extract and return the generated response text
        return response['choices'][0]['message']['content']
    
    except Exception as e:
        return f"An error occurred while generating sneaker analysis: {str(e)}"
