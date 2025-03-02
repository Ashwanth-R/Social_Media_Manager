import os
import json
from dotenv import load_dotenv
import tweepy.errors
load_dotenv()
from textwrap import dedent
import time

import tweepy
import re
from groq import Groq
from crewai import Crew
from crewai.process import Process
from tasks import ViralContentCreationTasks
from agents import ViralContentCreators
import openai
from instabot import Bot
import facebook
from openai import OpenAI

tasks = ViralContentCreationTasks()
agents = ViralContentCreators()

print("## Welcome to the Social Media Content Creation Crew")
print('-------------------------------')
niche = input("What topic you want me to create content?\n")

model = os.getenv('MODEL')
print(f"Model - {model}")
if not model:
    raise ValueError("MODEL environment variable is not set.")
# groqClient = Groq(
#     api_key=os.getenv("GROQ_API_KEY"),
# )
client = OpenAI( 
    api_key=os.getenv("OPENAI_API_KEY")
)

def get_posts_from_llm(content):
    chat_completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": dedent("""\
                    You are a helpful assistant that receives some text from the user. 
                    The text contains a couple of social media posts.
                    You extract all the posts from the text and create a valid JSON array of posts.
                    Return only the JSON array in the format: ["post_1", "post_2", ...], where post_1 is the
                    first post, post_2 is the second post, and so on. Ensure the JSON is valid and does not
                    contain any newline characters or other invalid formatting.
                """)
            },
            {
                "role": "user",
                "content": dedent(f"""\
                    Generate an array of 1 post each for Twitter, Instagram, and Facebook based on the content below.
                    Return only the JSON array of posts in the format: ["post_1", "post_2", ...], where post_1 is the
                    first post, post_2 is the second post, and so on. Ensure the JSON is valid and does not
                    contain any newline characters or other invalid formatting.
                    Content: {content}
                """),
            }
        ]
    )
    
    response_text  = chat_completion.choices[0].message.content

    response_text = response_text.replace("\n", " ").strip()
    
    match = re.search(r'\[.*\]', response_text , re.DOTALL)
    
    if match:
        posts_array = match.group(0)
        try:
            print("posts_array: ")
            print(posts_array)
            posts_list = json.loads(posts_array)
            return posts_list
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            return []
    else:
        print("No valid JSON array found in the response.")
        return []

def generate_image(prompt):
    # response = openai.Image.create(
    #     prompt=prompt,
    #     n=1,
    #     size="1024x1024"
    # )
    # image_url = response['data'][0]['url']
    response = client.images.generate(
        model="dall-e-3",
        prompt="a white siamese cat",
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url

def download_image(url, filepath):
    import requests
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
    else:
        raise Exception(f"Failed to download image from {url}")

def process_tweet(tweet):
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

    tweet_params = {"text": tweet}
    print("Tweet - params : ")
    print(tweet_params)

    try:
        response = client.create_tweet(text=tweet_params['text'])
        time.sleep(60)
        print("Tweet posted successfully!", response.data)
        return response
    except Exception as e:
        print("Error during tweeting:", e)
        return e

def process_instagram_post(post, image_url):
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    if not username or not password:
        raise ValueError("Instagram username/password is not set.")

    bot = Bot()
    bot.login(username=username, password=password)

    image_path = "instagram_image.jpg"
    download_image(image_url, image_path)

    try:
        bot.upload_photo(image_path, caption=post)
        print("Instagram post uploaded successfully!")
    except Exception as e:
        print("Error during Instagram posting:", e)

def process_facebook_post(post, image_url):
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    page_id = os.getenv('FACEBOOK_PAGE_ID')

    if not access_token or not page_id:
        raise ValueError("Facebook access token/page ID is not set.")

    graph = facebook.GraphAPI(access_token)
    
    image_path = "facebook_image.jpg"
    download_image(image_url, image_path)

    try:
        with open(image_path, "rb") as image:
            graph.put_photo(image=image, message=post, album_path=f"{page_id}/photos")
        print("Facebook post uploaded successfully!")
    except Exception as e:
        print("Error during Facebook posting:", e)

# Create Agents
trending_topic_researcher_agent = agents.trending_topic_researcher_agent()
content_researcher_agent = agents.content_researcher_agent()
creative_agent = agents.creative_content_creator_agent()
content_posting_agent = agents.content_posting_agent()

# Create Tasks
topic_analysis = tasks.topic_analysis(trending_topic_researcher_agent, niche)
content_research = tasks.content_research(content_researcher_agent, niche)
social_media_posts = tasks.create_social_media_posts(creative_agent, niche)
post_content_task = tasks.post_content(content_posting_agent)

# Create Crew
crew = Crew(
    agents=[
        trending_topic_researcher_agent,
        content_researcher_agent,
        creative_agent
        # content_posting_agent
    ],
    tasks=[
        topic_analysis,
        content_research,
        social_media_posts
        # post_content_task
    ],
    process=Process.sequential,
    verbose=True,
)

print("Hi")
result = crew.kickoff()

print("Crew usage", crew.usage_metrics)

# Print results
print("\n\n########################")
print("## Here is the result")
print("########################\n")
print(result)

posts = get_posts_from_llm(result)
print("\nPosts: ")
print(posts)
print(f"\nLength of posts: {len(posts)}\n")

# Process each post
twitter_post, instagram_post, facebook_post = posts

print(f"Twitter : {twitter_post}\n")
print(f"Instagram : {instagram_post}\n")
print(f"Facebook : {facebook_post}\n")

# print(twitter_post)
# process_tweet(twitter_post)

# print(instagram_post)
# image_prompt = "Generate an image related to the following post: " + instagram_post
# image_url = generate_image(image_prompt)
# process_instagram_post(instagram_post, image_url)

# print(facebook_post)
# image_prompt = "Generate an image related to the following post: " + facebook_post
# image_url = generate_image(image_prompt)
# process_facebook_post(facebook_post, image_url)
