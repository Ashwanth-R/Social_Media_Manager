import os
import tweepy
from langchain.tools import tool
from dotenv import load_dotenv
from config import post_state, final_content
import streamlit as st
import requests
from openai import OpenAI
import json

load_dotenv()

class ThreadsTools:
	@tool("Post Threads content")
	def post_threads(content):
		"""Post a thread  with the given content."""
		if post_state["threads"] == False:
			try:
				access_token = os.getenv("THREADS_TOKEN")
				thread_user_id = os.getenv("THREADS_ID")
				
				client = OpenAI(
						api_key=os.getenv("OPENAI_API_KEY")
					)

				response = client.images.generate(
					model="dall-e-3",
					prompt=content,
					size="1024x1024",
					quality="standard",
					n=1,
				)

				image_url = response.data[0].url
			
				url = f"https://graph.threads.net/v1.0/{thread_user_id}/threads"
				payload = {
					"image_url": image_url,
					"media_type": "IMAGE",
					"text": content,
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
				if response.status_code == 200:
					post_state["threads"] = True
					final_content["threads"] = content
					st.success("Threads content published successfully!")
					return "Threads content published successfully!"
				else:
					return "Failed to published content - Threads."
			except Exception as e:
				return f"An error occurred: {str(e)}"
		else:
			return "Threads content published successfully!"

