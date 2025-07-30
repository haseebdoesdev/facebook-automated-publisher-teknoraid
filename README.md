# TeknoRaid - Automated Facebook Publisher

This project is an automated social media publishing system designed for the [TeknoRaid](https://teknoraid.com/) tech blog. It leverages Google's Gemini AI and the Facebook Graph API to automatically generate and publish unique, context-aware Facebook posts whenever a new article is published on the WordPress site.

## How It Works

The workflow is triggered by a new post on WordPress and is designed to be seamless and efficient:

1.  **WordPress Post:** An author publishes a new article on the TeknoRaid WordPress site.
2.  **Webhook Trigger:** WordPress automatically sends a webhook containing the new post's data (title, excerpt, URL, categories, etc.) to our Flask server.
3.  **Flask Server:** The `webhook_server.py` application receives the webhook.
4.  **Data Extraction:** The server parses the incoming data to extract key information about the blog post.
5.  **AI Prompt Generation:** It uses a predefined template (`prompt.txt`) to construct a detailed prompt for the AI, including the post's title, summary, and tags.
6.  **Gemini AI Content Creation:** The prompt is sent to the Google Gemini API (`gemini_handler.py`), which generates a fresh and engaging Facebook post tailored to the article's content.
7.  **Facebook Publishing:** The AI-generated text is then sent to the Facebook Graph API (`facebook_handler.py`) and published on the official TeknoRaid Facebook page.

  <!-- You can create and link a diagram here -->

## Features

- **Fully Automated:** From blog publication to social media post, the entire process is hands-off.
- **AI-Powered Content:** Uses Google's Gemini to create unique and relevant social media content, avoiding repetitive posts.
- **Context-Aware:** The generated posts are based on the actual title, content, and tags of the new article.
- **Secure:** All API keys and sensitive credentials are kept out of the code and managed via a `.env` file.

## Tech Stack

- **Backend:** Python, Flask
- **AI:** Google Gemini API
- **Social Media:** Facebook Graph API
- **Trigger:** WordPress Webhooks

## Setup and Installation

Follow these steps to get the project running on your own server.

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd facebook-teknoraid
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies
Create a `requirements.txt` file with the necessary libraries and install them.
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and add your secret credentials. **This file is git-ignored for security.**

```ini
# .env
GEMINI_API_KEY="YOUR_GOOGLE_AI_STUDIO_API_KEY"
PAGE_ID="YOUR_FACEBOOK_PAGE_ID"
PAGE_ACCESS_TOKEN="YOUR_FACEBOOK_PAGE_ACCESS_TOKEN"
```

### 5. Create the AI Prompt Template
Create a `prompt.txt` file. The webhook server will use this template to create the prompt for Gemini. Use placeholders that match the keys in the `extract_post_info` function.

```txt
# prompt.txt
Please write an engaging Facebook post for my tech blog, TeknoRaid.
The post should be based on the following article details:
- Title: {post_title}
- Summary: {post_excerpt}
- Link: {post_url}
- Topics: {tags_or_categories}

The post should be exciting, encourage clicks, and include relevant hashtags.
```

## Usage

1.  **Run the Flask Server:**
    ```bash
    python webhook_server.py
    ```
    The server will start listening for requests on `http://127.0.0.1:500/`.

2.  **Configure WordPress Webhook:**
    In your WordPress admin panel (using a plugin like "WP Webhooks"), set up a new webhook to trigger on "Post Published". Point it to your server's public URL, e.g., `http://your-server-ip:500/webhook`.
