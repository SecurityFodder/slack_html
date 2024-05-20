import json
import os
import requests
from datetime import datetime
from collections import Counter

# Load the Slack conversation history JSON file
with open('slack_history.json', 'r') as file:
    data = json.load(file)

# Slack API token
SLACK_API_TOKEN = 'YOUR_SLACK_API_TOKEN'
HEADERS = {'Authorization': f'Bearer {SLACK_API_TOKEN}'}

# Define a function to convert timestamps to readable dates
def convert_timestamp(ts):
    return datetime.fromtimestamp(float(ts)).strftime('%Y-%m-%d %H:%M:%S')

# Define a function to replace emojis with their Unicode equivalents
def replace_emojis(text):
    emoji_map = {
        ":smile:": "😄",
        ":thumbsup:": "👍",
        ":heart:": "❤️",
        ":grin:": "😁",
        ":cry:": "😢",
        ":laughing:": "😆",
        ":sunglasses:": "😎",
        ":wink:": "😉",
        ":neutral_face:": "😐",
        ":blush:": "😊",
        ":sob:": "😭",
        ":joy:": "😂",
        ":clap:": "👏",
        ":wave:": "👋",
        # Add more emoji mappings here
    }
    for emoji, unicode_char in emoji_map.items():
        text = text.replace(emoji, unicode_char)
    return text

# Define a function to download images
def download_image(url, local_path):
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(response.content)
        return True
    return False

# Define a function to fetch thread replies
def fetch_thread_replies(channel, thread_ts):
    url = f'https://slack.com/api/conversations.replies?channel={channel}&ts={thread_ts}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get('messages', [])
    return []

# Create a directory for images if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# Start generating HTML content
html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slack Conversation History</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
        }
        .message {
            margin-bottom: 20px;
        }
        .timestamp {
            color: gray;
            font-size: 0.8em;
        }
        img {
            max-width: 100%;
        }
        .thread {
            margin-left: 20px;
            border-left: 2px solid #ccc;
            padding-left: 10px;
        }
    </style>
    <script>
        function searchMessages() {
            var input, filter, messages, message, text, i;
            input = document.getElementById("searchInput");
            filter = input.value.toLowerCase();
            messages = document.getElementsByClassName("message");

            for (i = 0; i < messages.length; i++) {
                message = messages[i];
                text = message.textContent || message.innerText;
                if (text.toLowerCase().indexOf(filter) > -1) {
                    message.style.display = "";
                } else {
                    message.style.display = "none";
                }
            }
        }
    </script>
</head>
<body>
<h1>Slack Conversation History</h1>
<input type="text" id="searchInput" onkeyup="searchMessages()" placeholder="Search for messages..">
'''

# Parse messages and add them to the HTML content
for message in data['messages']:
    user = message.get('user', 'Unknown user')
    ts = convert_timestamp(message['ts'])
    text = message.get('text', '')

    # Replace emojis in the text
    text = replace_emojis(text)

    # Check for images and download them
    if 'files' in message:
        for file in message['files']:
            if file['mimetype'].startswith('image/'):
                image_url = file["url_private"]
                local_image_path = os.path.join('images', file["id"] + ".png")
                if download_image(image_url, local_image_path):
                    text += f'<br><img src="{local_image_path}" alt="Image">'

    # Add the message to the HTML
    html_content += f'''
    <div class="message">
        <div class="user"><strong>{user}</strong></div>
        <div class="timestamp">{ts}</div>
        <div class="text">{text}</div>
    '''

    # Fetch and include thread messages
    if 'thread_ts' in message:
        thread_ts = message['thread_ts']
        thread_replies = fetch_thread_replies(data['channel'], thread_ts)
        for reply in thread_replies:
            reply_user = reply.get('user', 'Unknown user')
            reply_ts = convert_timestamp(reply['ts'])
            reply_text = replace_emojis(reply.get('text', ''))
            if 'files' in reply:
                for file in reply['files']:
                    if file['mimetype'].startswith('image/'):
                        image_url = file["url_private"]
                        local_image_path = os.path.join('images', file["id"] + ".png")
                        if download_image(image_url, local_image_path):
                            reply_text += f'<br><img src="{local_image_path}" alt="Image">'

            html_content += f'''
            <div class="thread">
                <div class="user"><strong>{reply_user}</strong></div>
                <div class="timestamp">{reply_ts}</div>
                <div class="text">{reply_text}</div>
            </div>
            '''

    html_content += '</div>'  # Close message div

# End of HTML content
html_content += '''
</body>
</html>
'''

# Write the HTML content to a file
with open('slack_history.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

print("HTML file has been generated successfully.")
