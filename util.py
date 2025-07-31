import re

def to_url_slug(text):
    # Remove non-alphanumeric characters except spaces
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Convert to lowercase
    return text.lower().strip('-')

def is_messaging_notification(webhook_data):
    """
    Returns True if the webhook payload is a messaging notification.
    """
    if not isinstance(webhook_data, dict):
        return False
    if webhook_data.get('object') != 'page':
        return False
    entries = webhook_data.get('entry', [])
    for entry in entries:
        if 'messaging' in entry and isinstance(entry['messaging'], list) and entry['messaging']:
            return True
    return False

def is_comment_on_a_post(webhook_data):
    """
    Returns True if the webhook payload is a comment on a post.
    """
    if not isinstance(webhook_data, dict):
        return False
    