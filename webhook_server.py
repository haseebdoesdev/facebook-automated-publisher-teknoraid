from flask import Flask, request, jsonify
from gemini_handler import generate_fb_post_text_gemini
from facebook_handler import create_fb_post
from util import to_url_slug
import os

app = Flask(__name__)

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

@app.route('/webhook', methods=['POST'])
def webhook():
    post_data = request.json
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

    return jsonify({'status': 'received', 'extracted': extracted}), 200

if __name__ == '__main__':
    app.run(port=500)
