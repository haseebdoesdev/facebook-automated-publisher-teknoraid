import requests
from dotenv import load_dotenv
import os

load_dotenv()

PAGE_ID = os.getenv("PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

def create_fb_post(message: str,link:str):
    """
    Create a Facebook post with the given message.
    Returns (True, None) if successful, (False, error_message) otherwise.
    """
    if not PAGE_ID or not PAGE_ACCESS_TOKEN:
        return False, "PAGE_ID or PAGE_ACCESS_TOKEN is not set in environment."
    url = f'https://graph.facebook.com/v23.0/{PAGE_ID}/feed'
    payload = {
        'message': message,
        'access_token': PAGE_ACCESS_TOKEN,
        'link' : link
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return True, None
        else:
            error_msg = f"Status Code: {response.status_code}, Response: {response.text}"
            return False, error_msg
    except Exception as e:
        return False, str(e)


def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def send_typing_action(recipient_id):
    url = f'https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}'
    headers = {"Content-Type": "application/json"}

    payload = {
        'recipient': {'id': recipient_id},
        'sender_action': 'typing_on'
    }
    requests.post(url, json=payload, headers=headers)

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
if __name__ == '__main__':


    # Example usage
    message = "Hello, this is a test post from my Python script!"
    success, error = create_fb_post(message)
    if success:
        print("Post created successfully!")
    else:
        print(f"Failed to create post: {error}")