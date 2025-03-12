import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Replace with your values
page_access_token = os.getenv('INSTA_TOKEN')
instagram_account_id = os.getenv('INSTA_ID')
image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTABCaDmsViQuZNzN14duW3mdONHeF8wIO05w&s'
caption = 'Your caption here'

# Step 1: Create a media container
url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media"
params = {
    "image_url": image_url,
    "caption": caption,
    "access_token": page_access_token
}

response = requests.post(url, params=params)
if response.status_code == 200:
    container_id = response.json().get("id")
    print("Media container created. Container ID:", container_id)
else:
    print("Failed to create media container.")
    print("Error:", response.json())
    exit()

# Step 2: Publish the uploaded media
url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media_publish"
params = {
    "creation_id": container_id,
    "access_token": page_access_token
}

response = requests.post(url, params=params)
if response.status_code == 200:
    print("Media published successfully!")
    print("Post ID:", response.json().get("id"))
else:
    print("Failed to publish media.")
    print("Error:", response.json())
