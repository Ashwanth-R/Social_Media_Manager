import requests
import os
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

class FacebookTools:
	@tool("Post Facebook")
	def post_facebook(message):
		"""Post a message on Facebook."""
		try:
			page_access_token = os.getenv('PAGE_ACCESS_TOKEN')
			page_id = os.getenv('PAGE_ID')

			url = f'https://graph.facebook.com/{page_id}/feed'
			data = {
				'message': message,
				'access_token': page_access_token
			}

			response = requests.post(url, data=data)
			if response.status_code == 200:
				return "Message posted successfully!"
			else:
				return "Failed to post message."
		except Exception as e:
			return f"An error occurred: {str(e)}"
