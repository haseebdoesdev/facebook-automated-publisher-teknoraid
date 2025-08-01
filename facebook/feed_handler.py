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


def create_video_story(page_id, access_token, video_path=None, video_url=None):
    """
    Creates and publishes a video story on a Facebook Page.
    
    Args:
        page_id (str): The ID of the Facebook Page
        access_token (str): Valid Page access token with required permissions
        video_path (str, optional): Path to local video file
        video_url (str, optional): URL to hosted video file
        
    Returns:
        dict: Response containing success status and post_id
    """
    # Step 1: Initialize upload session
    init_url = f"https://graph.facebook.com/v23.0/{page_id}/video_stories"
    init_payload = {
        "upload_phase": "start",
        "access_token": access_token
    }
    
    try:
        init_response = requests.post(init_url, data=init_payload)
        init_response.raise_for_status()
        init_data = init_response.json()
        
        video_id = init_data.get("video_id")
        upload_url = init_data.get("upload_url")
        
        if not video_id or not upload_url:
            return {"success": False, "error": "Failed to initialize upload session"}
            
        # Step 2: Upload video
        upload_headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        if video_url:
            # Upload hosted file
            upload_headers["file_url"] = video_url
            upload_response = requests.post(upload_url, headers=upload_headers)
        else:
            # Upload local file
            file_size = os.path.getsize(video_path)
            upload_headers.update({
                "offset": "0",
                "file_size": str(file_size)
            })
            
            with open(video_path, 'rb') as video_file:
                upload_response = requests.post(
                    upload_url,
                    headers=upload_headers,
                    data=video_file
                )
                
        upload_response.raise_for_status()
        upload_data = upload_response.json()
        
        if not upload_data.get("success"):
            return {"success": False, "error": "Video upload failed"}
            
        # Step 3: Publish video story
        publish_payload = {
            "video_id": video_id,
            "upload_phase": "finish",
            "access_token": access_token
        }
        
        publish_response = requests.post(init_url, data=publish_payload)
        publish_response.raise_for_status()
        return publish_response.json()
        
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}
        
def create_photo_story(page_id, access_token, photo_path):
    """
    Creates and publishes a photo story on a Facebook Page.
    
    Args:
        page_id (str): The ID of the Facebook Page
        access_token (str): Valid Page access token with required permissions
        photo_path (str): Path to local photo file
        
    Returns:
        dict: Response containing success status and post_id
    """
    # Step 1: Upload photo
    photo_url = f"https://graph.facebook.com/v23.0/{page_id}/photos"
    photo_payload = {
        "published": "false",
        "access_token": access_token
    }
    
    try:
        with open(photo_path, 'rb') as photo_file:
            photo_response = requests.post(
                photo_url,
                files={"source": photo_file},
                data=photo_payload
            )
            
        photo_response.raise_for_status()
        photo_data = photo_response.json()
        photo_id = photo_data.get("id")
        
        if not photo_id:
            return {"success": False, "error": "Photo upload failed"}
            
        # Step 2: Publish photo story
        story_url = f"https://graph.facebook.com/v23.0/{page_id}/photo_stories"
        story_payload = {
            "photo_id": photo_id,
            "access_token": access_token
        }
        
        story_response = requests.post(story_url, data=story_payload)
        story_response.raise_for_status()
        return story_response.json()
        
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}



