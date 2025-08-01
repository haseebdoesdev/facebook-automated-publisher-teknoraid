from dotenv import load_dotenv
import os
from facebook.feed_handler import create_fb_post
from teknoraid_wordpress.util import *
from gemini_handler import generate_fb_post_text_gemini
load_dotenv()


with open('prompt.txt', 'r', encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()


def extract_post_info(post_data):
    post = post_data.get('post', {})
    taxonomies = post_data.get('taxonomies', {})
    categories = taxonomies.get('category', {}) if isinstance(taxonomies, dict) else {}
    tags_or_categories = [cat.get('name') for cat in categories.values()] if isinstance(categories, dict) else []
    return {
        'post_title': post.get('post_title', ''),
        'post_excerpt': post.get('post_excerpt', ''),
        'post_content': post.get('post_content', ''),
        'post_url': 'https://teknoraid.com/' + to_url_slug(post.get('post_title', '')),
        'tags_or_categories': tags_or_categories
    }



def handle_teknoraid_post(post_data):
    print("📩 New post received:")
    print(post_data)
    extracted = extract_post_info(post_data)
    PROMPT_TEMPLATE_FILLED = PROMPT_TEMPLATE.format(**extracted)
    print("Extracted post info:", extracted)
    generated_post_message = generate_fb_post_text_gemini(PROMPT_TEMPLATE_FILLED)
    print("Generated Facebook post message:", generated_post_message)
    success, error = create_fb_post(generated_post_message, extracted['post_url'])
    if success:
        print("✅ Facebook post created successfully!")
    else:
        print(f"❌ Failed to create Facebook post: {error}")
    
    return extracted, success, error