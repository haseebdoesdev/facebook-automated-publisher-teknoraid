from dotenv import load_dotenv
import requests
load_dotenv()
import os
ORGANIZATION_ID = os.getenv("ORG_ID")
print(ORGANIZATION_ID)
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

import requests
import os
def publish_post(message, image_paths=None):
    import os

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    author_urn = f"urn:li:organization:{ORGANIZATION_ID}"

    # TEXT ONLY POST
    if not image_paths:
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": message},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        res = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=payload)
        if res.status_code == 201:
            print("✅ Text post published.")
        else:
            print(f"❌ Failed to publish. Status: {res.status_code}")
            print(res.text)
        return

    print("📤 Uploading multiple images...")
    asset_urns = []

    for path in image_paths:
        # Step 1: Register upload
        reg_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": author_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }

        reg_res = requests.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            headers=headers,
            json=reg_payload
        )
        if reg_res.status_code != 200:
            print(f"❌ Failed to register image '{path}'")
            print(reg_res.text)
            return

        upload_info = reg_res.json()
        upload_url = upload_info["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_urn = upload_info["value"]["asset"]

        with open(path, 'rb') as f:
            image_data = f.read()

        upload_headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/octet-stream"
        }

        upload_res = requests.put(upload_url, headers=upload_headers, data=image_data)
        if upload_res.status_code not in [201, 200]:
            print(f"❌ Failed to upload image '{path}'")
            print(upload_res.text)
            return

        print(f"✅ Uploaded {os.path.basename(path)}")
        asset_urns.append({
            "status": "READY",
            "description": {"text": f"Uploaded {os.path.basename(path)}"},
            "media": asset_urn,
            "title": {"text": os.path.basename(path)}
        })

    # Step 3: Create final post
    post_payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": message
                },
                "shareMediaCategory": "IMAGE",
                "media": asset_urns
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    final_post = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=post_payload)
    if final_post.status_code == 201:
        print("✅ Multi-image post published.")
    else:
        print(f"❌ Failed to publish post. Status: {final_post.status_code}")
        print(final_post.text)

import requests

def reply_to_comment(access_token, comment_id, reply_text):
    url = "https://api.linkedin.com/v2/socialActions/{}/comments".format(comment_id)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    payload = {
        "actor": f"urn:li:organization:{ORGANIZATION_ID}",  # Replace with your actual org ID or pass as parameter
        "message": {
            "text": reply_text
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("✅ Reply posted successfully.")
    else:
        print(f"❌ Failed to reply. Status code: {response.status_code}")
        print(response.text)



message = "Hello world from the LinkedIn API via Python! 🚀"

test_image_address = r'C:\Users\ABDUL\OneDrive\Desktop\screenshots\1.png'
test_image_address2 = r'C:\Users\ABDUL\OneDrive\Desktop\screenshots\2.png'
publish_post(message,[test_image_address,test_image_address2] )