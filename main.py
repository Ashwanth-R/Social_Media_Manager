import os
import json
import re
import time
import streamlit as st
from dotenv import load_dotenv
from textwrap import dedent
from openai import OpenAI
from crewai import Crew
from crewai.process import Process
from tasks import ViralContentCreationTasks
from agents import ViralContentCreators
from config import final_content

# Load environment variables
load_dotenv()

# Disable OpenTelemetry
os.environ["OTEL_PYTHON_DISABLED"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

# Initialize tasks and agents
tasks = ViralContentCreationTasks()
agents = ViralContentCreators()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_posts_from_llm(content):
    chat_completion = client.chat.completions.create(
        model=os.getenv('MODEL'),
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
                    Generate an array of 1 post each for Threads, Instagram, and Facebook based on the content below.
                    Return only the JSON array of posts in the format: ["post_1", "post_2", ...], where post_1 is the
                    first post, post_2 is the second post, and so on. Ensure the JSON is valid and does not
                    contain any newline characters or other invalid formatting.
                    Content: {content}
                """),
            }
        ]
    )
    
    response_text = chat_completion.choices[0].message.content
    response_text = response_text.replace("\n", " ").strip()
    
    match = re.search(r'\[.*\]', response_text, re.DOTALL)
    
    if match:
        posts_array = match.group(0)
        try:
            posts_list = json.loads(posts_array)
            return posts_list
        except json.JSONDecodeError as e:
            st.error(f"Failed to decode JSON: {e}")
            return []
    else:
        st.error("No valid JSON array found in the response.")
        return []

def main():
    st.title("Social Media Content Creation Crew")
    st.write("## Welcome to the Social Media Content Creation Crew")
    st.write('-------------------------------')

    # Input for niche/topic
    niche = st.text_input("What topic do you want me to create content about?")

    if niche:
        st.write(f"Model - {os.getenv('MODEL')}")
        if not os.getenv('MODEL'):
            st.error("MODEL environment variable is not set.")
            return

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
                creative_agent,
                content_posting_agent
            ],
            tasks=[
                topic_analysis,
                content_research,
                social_media_posts,
                post_content_task
            ],
            process=Process.sequential,
            verbose=True,
        )

        st.write("Running the crew...")
        result = crew.kickoff()

        st.write("Crew usage", crew.usage_metrics)

        # Print results
        st.write("\n\n########################")
        st.write("## Here is the result")
        st.write("########################\n")
        # st.write(result)

        # posts = get_posts_from_llm(result)
        # st.write("\nPosts: ")
        # st.write(posts)
        # st.write(f"\nLength of posts: {len(posts)}\n")

        posts = final_content
        st.write("\nPosts: ")
        st.write(posts.get("threads"))
        st.write(posts.get("instagram"))
        st.write(posts.get("facebook"))

        # # Process each post
        # if len(posts) == 3:
        #     twitter_post, instagram_post, facebook_post = posts
        #     st.write(f"Threads : {twitter_post}\n")
        #     st.write(f"Instagram : {instagram_post}\n")
        #     st.write(f"Facebook : {facebook_post}\n")
        # else:
        #     st.error("Expected 3 posts (Threads, Instagram, Facebook), but got a different number.")

if __name__ == "__main__":
    main()