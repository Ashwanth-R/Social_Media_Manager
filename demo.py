# from groq import Groq
# import os 
# from dotenv import load_dotenv
# load_dotenv()


# client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# response = client.chat.completions.create(
#     model="llama3-8b-8192",  # Replace with a valid model
#     messages=[{"role": "user", "content": "Hello"}]
# )

# print(response)

# import os
# from dotenv import load_dotenv
# load_dotenv()
# # print(os.getenv("HUGGINGFACE_MODEL"))

# import tweepy

# api_key = os.getenv('TWITTER_API_KEY')
# api_secret_key = os.getenv('TWITTER_API_SECRET_KEY')
# access_token = os.getenv('TWITTER_ACCESS_TOKEN')
# access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
# bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

# client = tweepy.Client(
#     consumer_key=api_key,
#     consumer_secret=api_secret_key,
#     access_token=access_token,
#     access_token_secret=access_token_secret
# )

# tweet = "Hello Twitter! #Testing"

# try:
#     response = client.create_tweet(text=tweet)
#     print("Tweet posted successfully!", response.data)
# except tweepy.errors.Forbidden as e:
#     print("403 Forbidden Error:", e)
# except Exception as e:
#     print("Error during tweeting:", e)


# import facebook
# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Get the Facebook access token from environment variables
# access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')

# # Check if the access token is set
# if not access_token:
#     raise ValueError("Facebook access token is not set.")

# try:
#     # Initialize the Facebook Graph API client
#     graph = facebook.GraphAPI(access_token)
    
#     # Get the list of pages the user manages
#     pages = graph.get_object('me/accounts')

#     # Log the raw response for debugging
#     print("Raw response:", pages)

#     # Check if the response contains data
#     if 'data' in pages and pages['data']:
#         # Print the name and ID of each page
#         for page in pages['data']:
#             print(f"Page Name: {page['name']}, Page ID: {page['id']}")
#     else:
#         print("No pages found or insufficient permissions.")
# except facebook.GraphAPIError as e:
#     print(f"GraphAPIError: {e}")
# except Exception as e:
#     print(f"An error occurred: {e}")


import os
import requests
import json
import tweepy
from langchain.tools import tool
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
def post_tweet(content=""):
		"""Post a tweet with the given content."""
		try:
			access_token = os.getenv("THREADS_TOKEN")
			thread_user_id = os.getenv("THREADS_ID")
			
			message = "Bcci new rules"
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
		
			url = f"https://graph.threads.net/v1.0/{thread_user_id}/threads"
			payload = {
				"image_url": image_url,
				"media_type": "IMAGE",
				"text": message,
				"alt_text": "my_alt_text",
				"access_token": access_token
			}
			response = requests.post(url, params=payload)	
			data = response.json()
			print(json.dumps(data, indent=4))
			creation_id = data["id"]
			print(f"Creation ID: {creation_id}")

			post_url = f"https://graph.threads.net/v1.0/{thread_user_id}/threads_publish"
			payload = {
				"creation_id": creation_id,
				"access_token": access_token
			}
			response = requests.post(post_url, params=payload)
			data = response.json()
			print(json.dumps(data, indent=4))
			media_id = data["id"]
			print(f"Media ID: {media_id}")
		except Exception as e:
			return f"An error occurred: {str(e)}"

print(post_tweet())

