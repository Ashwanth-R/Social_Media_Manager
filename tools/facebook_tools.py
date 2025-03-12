import requests
import os
from langchain.tools import tool
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# class FacebookTools:
# 	@tool("Post Facebook")
# 	def post_facebook(message):
# 		"""Post a message on Facebook."""
# 		try:
# 			page_access_token = os.getenv('PAGE_ACCESS_TOKEN')
# 			page_id = os.getenv('PAGE_ID')

# 			url = f'https://graph.facebook.com/{page_id}/feed'
# 			data = {
# 				'message': message,
# 				'access_token': page_access_token
# 			}

# 			response = requests.post(url, data=data)
# 			if response.status_code == 200:
# 				return "Message posted successfully!"
# 			else:
# 				return "Failed to post message."
# 		except Exception as e:
# 			return f"An error occurred: {str(e)}"

class FacebookTools:
    @tool("Post Facebook with Image")
    def post_facebook(message):
        """Post a message with an image on Facebook."""
        try:
            page_access_token = os.getenv('PAGE_ACCESS_TOKEN')
            page_id = os.getenv('PAGE_ID')
            
            client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )

            response = client.images.generate(
                model="dall-e-3",
                prompt=message,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            # Step 1: Upload the image to Facebook
            upload_url = f'https://graph.facebook.com/{page_id}/photos'
            upload_data = {
                'url': image_url,
                'access_token': page_access_token,
                'published': False  # Upload but do not publish yet
            }
            upload_response = requests.post(upload_url, data=upload_data)
            if upload_response.status_code != 200:
                return "Failed to upload image."

            # Get the photo ID from the upload response
            photo_id = upload_response.json().get('id')

            # Step 2: Post the message with the uploaded image
            post_url = f'https://graph.facebook.com/{page_id}/feed'
            post_data = {
                'message': message,
                'attached_media[0]': f'{{"media_fbid":"{photo_id}"}}',
                'access_token': page_access_token
            }
            post_response = requests.post(post_url, data=post_data)
            if post_response.status_code == 200:
                return "Media posted successfully - Facebook!"
            else:
                return "Failed to post media - Facebook!."
        except Exception as e:
            return f"An error occurred: {str(e)}"