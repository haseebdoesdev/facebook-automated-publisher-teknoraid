import re

def to_url_slug(text):
    # Remove non-alphanumeric characters except spaces
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Convert to lowercase
    return text.lower().strip('-')