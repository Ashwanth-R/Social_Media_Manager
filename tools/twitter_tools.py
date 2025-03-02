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
			api_secret = os.getenv('TWITTER_API_SECRET')
			access_token = os.getenv('TWITTER_ACCESS_TOKEN')
			access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

			auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
			api = tweepy.API(auth)

			api.update_status(content)
			return "Tweet posted successfully!"
		except Exception as e:
			return f"An error occurred: {str(e)}"
