import os
import tweepy
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

class TwitterTools:
	@tool("Post Tweet")
	def post_tweet(content):
		"""Post a tweet with the given content."""
		try:
			api_key = os.getenv('TWITTER_API_KEY')
			api_secret_key = os.getenv('TWITTER_API_SECRET_KEY')
			access_token = os.getenv('TWITTER_ACCESS_TOKEN')
			access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
			bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

			if not api_key or not api_secret_key or not access_token or not access_token_secret or not bearer_token:
				raise ValueError("Twitter key/secret is not set.")

			client = tweepy.Client(
				consumer_key=api_key,
				consumer_secret=api_secret_key,
				access_token=access_token,
				access_token_secret=access_token_secret
			)

			response = client.create_tweet(text=content)
			return "Tweet posted successfully!"
		except Exception as e:
			return f"An error occurred: {str(e)}"

