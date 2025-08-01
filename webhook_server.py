import dotenv
from flask import Flask, request, jsonify
from gemini_handler import generate_fb_post_text_gemini,craft_a_text_message
from facebook.feed_handler import create_fb_post
from facebook.messages_db_handler import *
from facebook.messages_handler import handle_message
from facebook.comment_handler import *
from facebook.util import *
from teknoraid_wordpress.main import *
import os
import json
from datetime import datetime
from dotenv import load_dotenv
dotenv.load_dotenv()
PAGE_ID = os.getenv("PAGE_ID")
app = Flask(__name__)

VERIFY_TOKEN = 'czxcxvxvxcvxcvxcvzsdsdf3ewqerqwr'


with open('prompt.txt', 'r', encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()

with open('messaging_prompt.txt', 'r', encoding="utf-8") as f:
    MESSAGING_PROMPT_TEMPLATE = f.read()

@app.route('/teknoriad_webhook', methods=['POST'])
def webhook():
    post_data = request.json
    extracted , success, error = handle_teknoraid_post(post_data)
    if not success:
        return jsonify({'status': 'error', 'error': error}), 500
    return jsonify({'status': 'received', 'extracted': extracted}), 200




@app.route('/fb_webhook', methods=['GET', 'POST'])
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
            handle_comment(data)
        return "OK", 200
    
    
if __name__ == '__main__':
    app.run(port=500)
