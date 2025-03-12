import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Your Page Access Token (replace with your actual token)
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
# Your Page ID (replace with your actual page ID)
PAGE_ID = os.getenv('PAGE_ID')

# Message you want to post
message = ""

# The Graph API endpoint for posting to the page
url = f'https://graph.facebook.com/{PAGE_ID}/feed'

# The data to send in the POST request
data = {
    'message': message,
    'access_token': PAGE_ACCESS_TOKEN
}

# Send the POST request to publish the message
response = requests.post(url, data=data)

# Print the response from Facebook API
print(response.json())
