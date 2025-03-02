import requests
from langchain.tools import tool
import os
from dotenv import load_dotenv

load_dotenv()

class InstagramTools:
	@tool("Post Instagram")
	def post_instagram(image_url, caption):
		"""Post an image with a caption on Instagram."""
		try:
			page_access_token = os.getenv('INSTA_TOKEN')
			instagram_account_id = os.getenv('INSTA_ID')

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
			else:
				return "Failed to create media container."

			# Step 2: Publish the uploaded media
			url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media_publish"
			params = {
				"creation_id": container_id,
				"access_token": page_access_token
			}

			response = requests.post(url, params=params)
			if response.status_code == 200:
				return "Media published successfully!"
			else:
				return "Failed to publish media."
		except Exception as e:
			return f"An error occurred: {str(e)}"
