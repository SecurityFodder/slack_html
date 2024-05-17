import json
import os
import requests
from datetime import datetime

# Load the Slack conversation history JSON file
with open('slack_history.json', 'r') as file:
    data = json.load(file)

# Define a function to convert timestamps to readable dates
def convert_timestamp(ts):
    return datetime.fromtimestamp(float(ts)).strftime('%Y-%m-%d %H:%M:%S')

# Define a function to replace emojis with their respective images
def replace_emojis(text):
    emoji_base_url = "https://emoji.slack-edge.com/TXXXXXXXX/"
    emoji_map = {
        ":smile:": "smile.png",
        ":thumbsup:": "thumbsup.png",
        ":heart:": "heart.png",
        ":grin:": "grin.png",
        ":cry:": "cry.png",
        ":laughing:": "laughing.png",
        ":sunglasses:": "sunglasses.png",
        ":wink:": "wink.png",
        ":neutral_face:": "neutral_face.png",
        ":blush:": "blush.png",
        ":sob:": "sob.png",
        ":joy:": "joy.png",
        ":clap:": "clap.png",
        ":wave:": "wave.png",
        # Add more emoji mappings here
    }
    for emoji, img_file in emoji_map.items():
        text = text.replace(emoji, f'<img src="{emoji_base_url}{img_file}" alt="{emoji}" width="20" height="20">')
    return text

# Define a function to download images
def download_image(url, local_path):
    response = requests.get(url, headers={'Authorization': f'Bearer YOUR_SLACK_API_TOKEN'})
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(response.content)
        return True
    return False

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

    html_content += f'''
    <div class="message">
        <div class="user"><strong>{user}</strong></div>
        <div class="timestamp">{ts}</div>
        <div class="text">{text}</div>
    </div>
    '''

# End of HTML content
html_content += '''
</body>
</html>
'''

# Write the HTML content to a file
with open('slack_history.html', 'w') as file:
    file.write(html_content)

print("HTML file has been generated successfully.")
