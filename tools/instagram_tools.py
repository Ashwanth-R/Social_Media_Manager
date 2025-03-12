import requests
from langchain.tools import tool
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class InstagramTools:
	@tool("Post Instagram")
	def post_instagram(image_url, caption):
		"""Post an image with a caption on Instagram."""
		try:
			page_access_token = os.getenv('INSTA_TOKEN')
			instagram_account_id = os.getenv('INSTA_ID')

			client = OpenAI(
				api_key=os.getenv("OPENAI_API_KEY")
			)

			response = client.images.generate(
				model="dall-e-3",
				prompt=caption,
				size="1024x1024",
				quality="standard",
				n=1,
			)

			# image_url = 'https://imagesvs.oneindia.com/img/2025/03/trump-hamas-02-1741227051.jpg'
			image_url = response.data[0].url

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
				return "Media published successfully - Instagram!"
			else:
				return "Failed to publish media - Instagram."
		except Exception as e:
			return f"An error occurred: {str(e)}"
