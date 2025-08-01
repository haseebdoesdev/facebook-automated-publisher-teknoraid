
from facebook.messages_db_handler import *
from datetime import datetime
from gemini_handler import craft_a_text_message
import json
from dotenv import load_dotenv
import os
import requests
# Load environment variables from the .env file in the project root
load_dotenv()
# Get the Facebook Page ID from environment variables
PAGE_ID = os.getenv("PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

# Open and read the messaging prompt template from a file.
# This template will be used to construct the prompt for the Gemini AI.
with open('messaging_prompt.txt', 'r', encoding="utf-8") as f:
    MESSAGING_PROMPT_TEMPLATE = f.read()


def send_typing_action(recipient_id):
    url = f'https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}'
    headers = {"Content-Type": "application/json"}

    payload = {
        'recipient': {'id': recipient_id},
        'sender_action': 'typing_on'
    }
    requests.post(url, json=payload, headers=headers)

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def handle_message(data):
    """
    Processes an incoming message webhook event from Facebook.

    This function orchestrates the entire process of handling a new message:
    1. Parses the incoming webhook data to extract message details.
    2. Saves the incoming message to the database.
    3. Updates the conversation session.
    4. Builds a context from recent messages.
    5. Uses Gemini AI to craft a response.
    6. Sends the crafted response back to the user.
    7. Saves the outgoing message to the database.
    8. Handles potential escalations flagged by the AI.

    Args:
        data (dict): The raw webhook payload from Facebook.
    """
    try:
        # --- 1. Parse Incoming Webhook Data ---
        # Navigate through the nested dictionary to get the core messaging event
        entry = data.get('entry', [])[0]
        messaging_event = entry.get('messaging', [])[0]
        # Extract the sender's unique ID (PSID)
        sender_id = messaging_event.get('sender', {}).get('id')
        send_typing_action(sender_id)
        # Extract the text content of the message
        message_text = messaging_event.get('message', {}).get('text')
        # Convert the Facebook timestamp (milliseconds) to a Python datetime object
        timestamp = datetime.utcfromtimestamp(messaging_event.get("timestamp") / 1000.0)

        print(f"Sender ID: {sender_id}, Message: {message_text}")

        # --- 2. Prepare Data for AI and Database ---
        # Create a dictionary to hold message data for easy use later
        message_data = {
            'sender_id': sender_id,
            'message_text': message_text
        }
        # Save the full incoming message payload to the database
        save_incoming_message_to_db(data)
        # Create a new conversation record or update the existing one's timestamp
        upsert_conversation_session(sender_id,PAGE_ID , timestamp, "incoming")

        # --- 3. Build Context and Craft AI Response ---
        # Retrieve recent message history for this conversation to provide context to the AI
        message_data['context'] = build_llm_context(f'{PAGE_ID}_{sender_id}')
        print(message_text)
        # Use the Gemini AI to generate a response.
        # The prompt is formatted with the current message and conversation history.
        # The AI's response is expected to be a JSON string, which is cleaned up and parsed.
        filled_template = MESSAGING_PROMPT_TEMPLATE.format(**message_data)
        crafted_message_json_str = craft_a_text_message(filled_template).replace("```json", "").replace("```", "")
        crafted_message_json = json.loads(crafted_message_json_str)
        print(crafted_message_json)

        # --- 4. Process AI Response and Handle Escalation ---
        # Extract the response text and escalation flags from the AI's JSON output
        crafted_message = crafted_message_json.get('message_text')
        is_escalation_needed = crafted_message_json.get('isEscalationNeeded')
        escalation_type = crafted_message_json.get('escalationType')
        escalation_summary = crafted_message_json.get('escalationSummary')
        conversation_id = f'{PAGE_ID}_{sender_id}'
        # Check if the AI determined that the conversation needs to be escalated
        if is_escalation_needed:
            if escalation_type == "complaint":
                # If it's a complaint, create a complaint record in the database.
                # Note: This function call is missing required arguments and will likely fail.
                create_complaint(conversation_id,sender_id, message_text,escalation_summary) # This will likely cause an error as it's missing arguments.
        print(crafted_message, is_escalation_needed,escalation_type)

        # --- 5. Send Response and Update Database ---
        # Send the AI-crafted message back to the user via the Facebook Send API
        response = send_message(sender_id, crafted_message)
        # Save the outgoing message (our reply) to the database for a complete record
        save_outgoing_message_to_db(response, PAGE_ID, sender_id, crafted_message)
        # Update the conversation session again to reflect our reply
        upsert_conversation_session(PAGE_ID, sender_id, datetime.utcnow(), "outgoing")
    
    except Exception as e:
        # Catch-all for any errors during the process to prevent the server from crashing
        print(f"Error handling message: {e}")