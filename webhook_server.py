from flask import Flask, request, jsonify
from facebook_handler import create_fb_post

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    post_data = request.json
    print("📩 New post received:")
    print(post_data)
    message = post_data.get('message')
    if not message:
        return jsonify({'status': 'error', 'error': 'No message provided'}), 400
    success, error = create_fb_post(message)
    if success:
        return jsonify({'status': 'success', 'message': 'Facebook post created'}), 200
    else:
        return jsonify({'status': 'error', 'error': error}), 500

if __name__ == '__main__':
    app.run(port=500)
