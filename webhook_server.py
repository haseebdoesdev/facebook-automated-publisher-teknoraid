import dotenv
from flask import Flask, request, jsonify
from gemini_handler import generate_fb_post_text_gemini,craft_a_text_message
from facebook_handler import create_fb_post, send_message
from messages_db_handler import *
from messages_handler import handle_message
from util import *
import os
import json
from datetime import datetime
from dotenv import load_dotenv
dotenv.load_dotenv()
PAGE_ID = os.getenv("PAGE_ID")
app = Flask(__name__)

with open('prompt.txt', 'r', encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()

with open('messaging_prompt.txt', 'r', encoding="utf-8") as f:
    MESSAGING_PROMPT_TEMPLATE = f.read()
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
VERIFY_TOKEN = 'czxcxvxvxcvxcvxcvzsdsdf3ewqerqwr'

@app.route('/messaging', methods=['GET', 'POST'])
def messaging():
    if request.method == 'GET':
        # Facebook webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print('Webhook verified successfully.')
            return challenge, 200
        else:
            return 'Verification failed', 403

    elif request.method == 'POST':
        # Handle incoming messages
        data = request.get_json()
        print("Received webhook:", data)
        if is_messaging_notification(data):
            handle_message(data)
        if is_comment_on_a_post(data):
            handle_message(data)
        return "OK", 200
    
    
if __name__ == '__main__':
    app.run(port=500)
