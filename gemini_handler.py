import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("No Gemini API Key found. Please set the GEMINI_API_KEY environment variable.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_fb_post_text_gemini(prompt: str) -> str:
    """
    Generates text content using the Gemini model based on a given prompt.
    """
    try:
        print("🔍 Prompt for Gemini:", prompt)
        print("✨ Generating content with Gemini...")
        response = model.generate_content(prompt)
        print("✅ Content generated successfully.")
        return response.text
    except Exception as e:
        print(f"❌ Error generating content with Gemini: {e}")
        return ""

if __name__ == '__main__':
    # 1. Define a prompt for Gemini
    prompt = "Write a short, exciting Facebook post about the launch of a new AI assistant that can code."

    # 2. Generate the post content using Gemini
    generated_post_message = generate_fb_post_text_gemini(prompt)

    print("Generated Post Message:", generated_post_message)