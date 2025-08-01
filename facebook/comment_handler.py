from datetime import datetime
import json
import os
from dotenv import load_dotenv
import requests
from gemini_handler import craft_a_text_message


load_dotenv()
PAGE_ID = os.getenv("PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

# A separate prompt for comments allows for different instructions than private messages.
with open(r'facebook\comment_handler_prompt.txt', 'r', encoding="utf-8") as f:
    COMMENT_PROMPT_TEMPLATE = f.read()




def handle_comment(data):
    """
    Processes an incoming comment webhook event from Facebook.

    This function orchestrates the process of handling a new comment:
    1. Parses the webhook to extract comment details.
    2. Ignores comments made by the page itself to prevent reply loops.
    3. Saves the incoming comment to the database.
    4. Uses Gemini AI to decide if a reply is needed and to craft it.
    5. Sends the reply to the comment via the Graph API.
    6. Saves the outgoing reply to the database.

    Args:
        data (dict): The raw webhook payload from Facebook.
    """
    try:
        # --- 1. Parse Incoming Webhook Data ---
        change = data['entry'][0]['changes'][0]['value']

        # --- 2. Ignore comments from the Page itself ---
        sender_id = change.get('from', {}).get('id')
        if sender_id == PAGE_ID:
            print("Ignoring comment from page itself.")
            return

        comment_id = change.get('comment_id')
        post_id = change.get('post_id')
        comment_text = change.get('message')
        sender_name = change.get('from', {}).get('name')
        created_time = datetime.utcfromtimestamp(change.get('created_time'))

        print(f"New comment from {sender_name} ({sender_id}) on post {post_id}: '{comment_text}'")


        # --- 4. Craft a Response with Gemini ---
        prompt_data = {'user_name': sender_name, 'comment_text': comment_text}
        filled_prompt = COMMENT_PROMPT_TEMPLATE.format(**prompt_data)
        response_str = craft_a_text_message(filled_prompt).replace("```json", "").replace("```", "")
        response_json = json.loads(response_str)
        print(response_json)

        # --- 5. Parse AI response and store in variables ---
        action = response_json.get('action')
        reply_text = response_json.get('reply_text')
        is_escalation_needed = response_json.get('is_escalation_needed')
        escalation_type = response_json.get('escalation_type')
        complaint_summary = response_json.get('complaint_summary')

        # --- 6. Reply if needed ---
        if action in ['reply', 'allow'] and reply_text:
            response_data = reply_to_comment(comment_id, reply_text)
            print(f"Replied to comment {comment_id}: '{reply_text}'")
            
            if response_data and 'id' in response_data:
                reply_comment_id = response_data.get('id')

        # --- 7. Handle Escalation ---
        if is_escalation_needed and escalation_type == 'complaint':
            conversation_id = f"{post_id}_{sender_id}"
            print(f"Escalation created for comment {comment_id}")

    except Exception as e:
        print(f"Error handling comment: {e}")

def reply_to_comment(comment_id: str, message: str):
    """
    Replies to a specific comment on Facebook.
    """
    if not PAGE_ACCESS_TOKEN:
        raise ValueError("PAGE_ACCESS_TOKEN is not set in environment.")
    
    url = f'https://graph.facebook.com/v23.0/{comment_id}/comments'
    payload = {
        'message': message,
        'access_token': PAGE_ACCESS_TOKEN
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error replying to comment {comment_id}: {e}")
        print(f"Response: {e.response.text if e.response else 'No response'}")
        return None
