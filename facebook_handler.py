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

if __name__ == '__main__':
    # Example usage
    message = "Hello, this is a test post from my Python script!"
    success, error = create_fb_post(message)
    if success:
        print("Post created successfully!")
    else:
        print(f"Failed to create post: {error}")