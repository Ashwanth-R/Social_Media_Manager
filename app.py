import os
import json
import re
import time
import streamlit as st
from dotenv import load_dotenv, set_key
from textwrap import dedent

from openai import OpenAI
from openai_manager import OpenAIManager
from crewai import Crew
from crewai.process import Process
from tasks import ViralContentCreationTasks
from agents import ViralContentCreators
from config import final_content
import base64

import pandas as pd
from social_api import fetch_facebook_posts, fetch_instagram_comments, fetch_threads_comments, extract_comments
from model import load_model, perform_sentiment_analysis
from visualization import visualize_sentiment_distribution

# Load environment variables
load_dotenv()

# Disable OpenTelemetry
os.environ["OTEL_PYTHON_DISABLED"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

# Set page configuration
st.set_page_config(
    page_title="AI-Driven Social Media Content Creator",
    page_icon="icon.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1DA1F2;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #657786;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #14171A;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .platform-label {
        font-weight: 600;
        color: #1DA1F2;
        margin-bottom: 0.5rem;
    }
    .post-content {
        background-color: #F5F8FA;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1DA1F2;
        margin-bottom: 1.5rem;
    }
    .metrics-box {
        background-color: #E1E8ED;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
    }
    .stButton>button {
        background-color: #1DA1F2;
        color: white;
        font-weight: 600;
    }
    .sidebar .sidebar-content {
        background-color: #F5F8FA;
    }
    .settings-card {
        background-color: #F5F8FA;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #1DA1F2;
    }
    .success-message {
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #2E7D32;
    }
    .token-form input {
        margin-bottom: 1rem;
    }
    div.stButton > button[kind="primary"][data-testid="baseButton-primary"] {
        background-color: #FF0000;
        color: white;
        border: none;
        font-weight: bold;
        transition: all 0.2s ease;
    }
    div.stButton > button[kind="primary"][data-testid="baseButton-primary"]:hover {
        background-color: #D10000;
    }                  
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* Modern checkbox container */
    div[data-testid="stCheckbox"] > label {
        font-family: 'Segoe UI', sans-serif;
        font-size: 1.1rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        border-radius: 12px;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Hover effects */
    div[data-testid="stCheckbox"] > label:hover {
        background: rgba(255,255,255,0.15);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Custom checkbox design */
    div[data-testid="stCheckbox"] > label > div:first-child {
        border-radius: 6px !important;
        border: 2px solid #00FFFF !important;
        background: rgba(0,0,0,0.3) !important;
        width: 22px !important;
        height: 22px !important;
    }
    
    /* Checked state */
    div[data-testid="stCheckbox"] > label > div:first-child > div {
        background-color: #00FFFF !important;
        box-shadow: 0 0 10px #00FFFF;
    }
    
    /* Platform-specific colors */
    div[data-testid="stCheckbox"] > label[data-testid="stWidgetLabel"]:has(+ input[value="Facebook"]) {
        color: #1877F2;
        border-color: rgba(24, 119, 242, 0.3);
    }
    div[data-testid="stCheckbox"] > label[data-testid="stWidgetLabel"]:has(+ input[value="Instagram"]) {
        color: #E1306C;
        border-color: rgba(225, 48, 108, 0.3);
    }
    div[data-testid="stCheckbox"] > label[data-testid="stWidgetLabel"]:has(+ input[value="Threads"]) {
        color: #000000;
        border-color: rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize tasks and agents
tasks = ViralContentCreationTasks()
agents = ViralContentCreators()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to update environment variables in .env file
def update_env_variable(key, value):
    if value:  # Only update if value is not empty
        # Update in current session
        os.environ[key] = value
        
        # Update in .env file
        env_path = ".env"
        try:
            set_key(env_path, key, value)
            return True
        except Exception as e:
            st.error(f"Failed to update {key} in .env file: {e}")
            return False
    return False

# Cache function to store results between runs
@st.cache_data
def run_content_crew(niche):
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

    result = crew.kickoff()
    usage_metrics = crew.usage_metrics
    
    # For demo purposes, use final_content but in production would parse result
    posts = final_content
    
    return posts, usage_metrics

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

def display_loading_animation():
    """Display a custom loading animation"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 2rem 0;">
            <div style="font-size: 1.2rem; margin-bottom: 1rem; color: #1DA1F2; font-weight: 600;">
                Our AI crew is working on your content
            </div>
            <div style="display: flex; justify-content: center; gap: 1rem;">
                <div style="text-align: center;">
                    <div style="font-weight: 600; color: #657786; margin-bottom: 0.5rem;">Researching Trends</div>
                    <div class="spinner"></div>
                </div>
                <div style="text-align: center;">
                    <div style="font-weight: 600; color: #657786; margin-bottom: 0.5rem;">Analyzing Content</div>
                    <div class="spinner"></div>
                </div>
                <div style="text-align: center;">
                    <div style="font-weight: 600; color: #657786; margin-bottom: 0.5rem;">Creating Posts</div>
                    <div class="spinner"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Add CSS for spinner animation
    st.markdown("""
    <style>
    .spinner {
        width: 40px;
        height: 40px;
        background-color: #1DA1F2;
        border-radius: 100%;
        -webkit-animation: sk-scaleout 1.5s infinite ease-in-out;
        animation: sk-scaleout 1.5s infinite ease-in-out;
    }
    @-webkit-keyframes sk-scaleout {
        0% { -webkit-transform: scale(0) }
        100% { -webkit-transform: scale(1.0); opacity: 0; }
    }
    @keyframes sk-scaleout {
        0% { transform: scale(0); -webkit-transform: scale(0) }
        100% { transform: scale(1.0); -webkit-transform: scale(1.0); opacity: 0; }
    }
    </style>
    """, unsafe_allow_html=True)

def display_social_media_card(platform, icon, content):
    """Display a nicely formatted social media post card"""
    st.markdown(f"""
    <div style="margin-bottom: 2rem; border: 1px solid #E1E8ED; border-radius: 15px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 1.8rem; margin-right: 0.5rem;">{icon}</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #14171A;">{platform}</div>
        </div>
        <div style="background-color: #F5F8FA; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #1DA1F2;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


def comments_analysis_page():
    """Display the comments analysis functionality for all platforms"""
    st.markdown('<div class="main-header">📊 Multi-Platform Comments Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Analyze sentiment of comments across Facebook, Instagram, and Threads</div>', unsafe_allow_html=True)
    
    # Check credentials
    has_facebook = os.getenv("PAGE_ID") and os.getenv("PAGE_ACCESS_TOKEN")
    has_instagram = os.getenv("INSTA_ID") and os.getenv("INSTA_TOKEN")
    has_threads = os.getenv("THREADS_ID") and os.getenv("THREADS_TOKEN")
    
    if not any([has_facebook, has_instagram, has_threads]):
        st.error("No platform credentials configured. Please set up at least one platform in Settings.")
        return
    
    # Platform selection
    st.markdown('<div class="section-header">🔮 Platform Selection</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        analyze_facebook = st.checkbox("Facebook", value=has_facebook, disabled=not has_facebook)
    with col2:
        analyze_instagram = st.checkbox("Instagram", value=has_instagram, disabled=not has_instagram)
    with col3:
        analyze_threads = st.checkbox("Threads", value=has_threads, disabled=not has_threads)

    
    if st.button("Analyze Comments", 
             type="primary",  # Ensures the CSS selector matches
             key="analyze_comments_btn",  # Unique identifier
             use_container_width=True,
             help="Click to analyze comments across selected platforms"):
        if not any([analyze_facebook, analyze_instagram, analyze_threads]):
            st.error("Please select at least one platform to analyze")
            return
            
        try:
            with st.spinner("Loading sentiment analysis model..."):
                model, vectorizer, reverse_label_mapping, metrics = load_model()
            
            all_results = []
            platform_names = []
            llm = OpenAIManager(model_name="gpt-4").create_llm(temperature=0.7)

            # ========== FACEBOOK ANALYSIS ==========
            if analyze_facebook and has_facebook:
                with st.spinner("Analyzing Facebook comments..."):
                    data = fetch_facebook_posts(os.getenv("PAGE_ID"), os.getenv("PAGE_ACCESS_TOKEN"))
                    comment_texts, post_ids, captions, post_urls = extract_comments(data, 'facebook')
                    
                    if comment_texts:
                        predicted_sentiments = perform_sentiment_analysis(comment_texts, model, vectorizer, reverse_label_mapping)
                        facebook_results = pd.DataFrame({
                            'Platform': 'Facebook',
                            'Post ID': post_ids,
                            'Post Caption': captions,
                            'Post URL': post_urls,
                            'Comment': comment_texts,
                            'Sentiment': predicted_sentiments
                        })
                        all_results.append(facebook_results)
                        
                        posts = {}
                        for post_id, caption, comment, sentiment, url in zip(post_ids, captions, comment_texts, predicted_sentiments, post_urls):
                            if post_id not in posts:
                                posts[post_id] = {
                                    'caption': caption,
                                    'url': url,
                                    'comments': [],
                                    'sentiments': []
                                }
                            posts[post_id]['comments'].append(comment)
                            posts[post_id]['sentiments'].append(sentiment)
                        
                        with st.expander("📘 Facebook Analysis", expanded=True):
                            st.subheader("Facebook Sentiment Analysis")
                            
                            for post_id, post_data in posts.items():
                                with st.container():
                                    # Facebook-styled post card
                                    st.markdown(f"""
                                    <div style="
                                        background: linear-gradient(145deg, #1877F2, #4599FF, #A0C4FF);
                                        border-radius: 10px;
                                        padding: 15px;
                                        margin-bottom: 20px;
                                        color: white;
                                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                                        transition: all 0.3s ease;
                                    ">
                                        <h4 style="margin-top:0;">
                                            <a href="{post_data['url']}" target="_blank" style="color: white; text-decoration: none;">
                                                {post_data['caption'][:100]}{'...' if len(post_data['caption']) > 100 else ''}
                                            </a>
                                        </h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Sentiment metrics
                                    post_sentiments = post_data['sentiments']
                                    pos_count = post_sentiments.count('Positive')
                                    neu_count = post_sentiments.count('Neutral')
                                    neg_count = post_sentiments.count('Negative')
                                    total = len(post_sentiments)
                                    
                                    st.markdown(f"""
                                    <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                                        <div style="flex: 1; background: #4CAF5010; border-left: 4px solid #4CAF50; border-radius: 5px; padding: 10px;">
                                            <div style="font-size: 12px; color: #4CAF50;">Positive</div>
                                            <div style="font-size: 16px; font-weight: bold;">{pos_count} ({pos_count/total*100:.1f}%)</div>
                                        </div>
                                        <div style="flex: 1; background: #FFC10710; border-left: 4px solid #FFC107; border-radius: 5px; padding: 10px;">
                                            <div style="font-size: 12px; color: #FFC107;">Neutral</div>
                                            <div style="font-size: 16px; font-weight: bold;">{neu_count} ({neu_count/total*100:.1f}%)</div>
                                        </div>
                                        <div style="flex: 1; background: #F4433610; border-left: 4px solid #F44336; border-radius: 5px; padding: 10px;">
                                            <div style="font-size: 12px; color: #F44336;">Negative</div>
                                            <div style="font-size: 16px; font-weight: bold;">{neg_count} ({neg_count/total*100:.1f}%)</div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Comments display
                                    for comment, sentiment in zip(post_data['comments'], post_data['sentiments']):
                                        color = "#4CAF50" if sentiment == "Positive" else "#F44336" if sentiment == "Negative" else "#FFC107"
                                        emoji = "😊" if sentiment == "Positive" else "😞" if sentiment == "Negative" else "😐"
                                        
                                        st.markdown(f"""
                                        <div style="
                                            background: {color}10;
                                            border-left: 4px solid {color};
                                            border-radius: 4px;
                                            padding: 10px;
                                            margin: 5px 0;
                                            font-size: 14px;
                                        ">
                                            <div style="display: flex; align-items: center; gap: 8px;">
                                                <span style="font-size: 18px;">{emoji}</span>
                                                <span>{comment}</span>
                                            </div>
                                            <div style="margin-top: 5px; font-size: 12px; color: {color};">
                                                Sentiment: <strong>{sentiment}</strong>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)

                                    # # Generate AI recommendations for this post
                                    # with st.spinner("Generating AI insights..."):
                                    #     try:
                                    #         # Prepare comment samples for context
                                    #         sample_comments = "\n".join([f"- {c}" for c in post_data['comments'][:5]])
                                            
                                    #         response = llm.invoke(f"""
                                    #         Analyze this Facebook post and its comments to provide 2-3 actionable recommendations:

                                    #         Post Content: {post_data['caption']}
                                            
                                    #         Sentiment Distribution:
                                    #         - Positive: {pos_count} ({pos_count/total*100:.1f}%)
                                    #         - Neutral: {neu_count} ({neu_count/total*100:.1f}%)
                                    #         - Negative: {neg_count} ({neg_count/total*100:.1f}%)
                                            
                                    #         Sample Comments:
                                    #         {sample_comments}
                                            
                                    #         Provide concise recommendations focusing on:
                                    #         1. How to improve engagement based on positive feedback
                                    #         2. How to address any concerns from negative comments
                                    #         3. Content strategy adjustments if needed
                                            
                                    #         Format as bullet points with 🚀, 🛠️, and 💡 emojis.
                                    #         """)
                                            
                                    #         # Display recommendations in styled card
                                    #         st.markdown(f"""
                                    #         <div style="
                                    #             background: #F5F8FA;
                                    #             border-radius: 10px;
                                    #             padding: 15px;
                                    #             margin: 20px 0;
                                    #             border-left: 4px solid #1DA1F2;
                                    #         ">
                                    #             <h4 style="margin-top:0; color: #1DA1F2;">AI Recommendations</h4>
                                    #             {response.content}
                                    #         </div>
                                    #         """, unsafe_allow_html=True)
                                    #     except Exception as e:
                                    #         st.error(f"Couldn't generate recommendations: {str(e)}")

                            
                            platform_names.append('Facebook')

            # ========== INSTAGRAM ANALYSIS ==========
            if analyze_instagram and has_instagram:
                with st.spinner("Analyzing Instagram comments..."):
                    data = fetch_instagram_comments(os.getenv("INSTA_ID"), os.getenv("INSTA_TOKEN"))
                    comment_texts, post_ids, captions, post_urls = extract_comments(data, 'instagram')
                    
                    if comment_texts:
                        predicted_sentiments = perform_sentiment_analysis(comment_texts, model, vectorizer, reverse_label_mapping)
                        instagram_results = pd.DataFrame({
                            'Platform': 'Instagram',
                            'Post ID': post_ids,
                            'Post Caption': captions,
                            'Post URL': post_urls,
                            'Comment': comment_texts,
                            'Sentiment': predicted_sentiments
                        })
                        all_results.append(instagram_results)
                        
                        posts = {}
                        for post_id, caption, comment, sentiment, url in zip(post_ids, captions, comment_texts, predicted_sentiments, post_urls):
                            if post_id not in posts:
                                posts[post_id] = {
                                    'caption': caption,
                                    'url': url,
                                    'comments': [],
                                    'sentiments': []
                                }
                            posts[post_id]['comments'].append(comment)
                            posts[post_id]['sentiments'].append(sentiment)
                        
                        with st.expander("📷 Instagram Analysis", expanded=True):
                            st.subheader("Instagram Sentiment Analysis")
                            
                            for post_id, post_data in posts.items():
                                with st.container():
                                    # Instagram-styled post card
                                    st.markdown(f"""
                                    <div style="
                                        background: linear-gradient(145deg, #833AB4, #E1306C, #FCAF45);
                                        border-radius: 10px;
                                        padding: 15px;
                                        margin-bottom: 20px;
                                        color: white;
                                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                                    ">
                                        <h4 style="margin-top:0;">
                                            <a href="{post_data['url']}" target="_blank" style="color: white; text-decoration: none;">
                                                {post_data['caption'][:100]}{'...' if len(post_data['caption']) > 100 else ''}
                                            </a>
                                        </h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Sentiment metrics
                                    post_sentiments = post_data['sentiments']
                                    pos_count = post_sentiments.count('Positive')
                                    neu_count = post_sentiments.count('Neutral')
                                    neg_count = post_sentiments.count('Negative')
                                    total = len(post_sentiments)
                                    
                                    st.markdown(f"""
                                    <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                                        <div style="flex: 1; background: #4CAF5010; border-left: 4px solid #4CAF50; border-radius: 5px; padding: 10px;">
                                            <div style="font-size: 12px; color: #4CAF50;">Positive</div>
                                            <div style="font-size: 16px; font-weight: bold;">{pos_count} ({pos_count/total*100:.1f}%)</div>
                                        </div>
                                        <div style="flex: 1; background: #FFC10710; border-left: 4px solid #FFC107; border-radius: 5px; padding: 10px;">
                                            <div style="font-size: 12px; color: #FFC107;">Neutral</div>
                                            <div style="font-size: 16px; font-weight: bold;">{neu_count} ({neu_count/total*100:.1f}%)</div>
                                        </div>
                                        <div style="flex: 1; background: #F4433610; border-left: 4px solid #F44336; border-radius: 5px; padding: 10px;">
                                            <div style="font-size: 12px; color: #F44336;">Negative</div>
                                            <div style="font-size: 16px; font-weight: bold;">{neg_count} ({neg_count/total*100:.1f}%)</div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Comments display
                                    for comment, sentiment in zip(post_data['comments'], post_data['sentiments']):
                                        color = "#4CAF50" if sentiment == "Positive" else "#F44336" if sentiment == "Negative" else "#FFC107"
                                        emoji = "🌟" if sentiment == "Positive" else "💔" if sentiment == "Negative" else "💭"
                                        
                                        st.markdown(f"""
                                        <div style="
                                            background: {color}10;
                                            border-left: 4px solid {color};
                                            border-radius: 4px;
                                            padding: 10px;
                                            margin: 5px 0;
                                            font-size: 14px;
                                        ">
                                            <div style="display: flex; align-items: center; gap: 8px;">
                                                <span style="font-size: 18px;">{emoji}</span>
                                                <span>{comment}</span>
                                            </div>
                                            <div style="margin-top: 5px; font-size: 12px; color: {color};">
                                                Sentiment: <strong>{sentiment}</strong>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    # # Generate AI recommendations for this post
                                    # with st.spinner("Generating AI insights..."):
                                    #     try:
                                    #         # Prepare comment samples for context
                                    #         sample_comments = "\n".join([f"- {c}" for c in post_data['comments'][:5]])
                                            
                                    #         response = llm.invoke(f"""
                                    #         Analyze this Instagram post and its comments to provide 2-3 actionable recommendations:

                                    #         Post Content: {post_data['caption']}
                                            
                                    #         Sentiment Distribution:
                                    #         - Positive: {pos_count} ({pos_count/total*100:.1f}%)
                                    #         - Neutral: {neu_count} ({neu_count/total*100:.1f}%)
                                    #         - Negative: {neg_count} ({neg_count/total*100:.1f}%)
                                            
                                    #         Sample Comments:
                                    #         {sample_comments}
                                            
                                    #         Provide concise recommendations focusing on:
                                    #         1. How to improve visual content based on engagement
                                    #         2. How to respond to negative feedback
                                    #         3. Hashtag or caption strategy adjustments
                                            
                                    #         Format as bullet points with 📸, 💬, and 🔍 emojis.
                                    #         """)
                                            
                                    #         # Display recommendations in styled card
                                    #         st.markdown(f"""
                                    #         <div style="
                                    #             background: #F5F8FA;
                                    #             border-radius: 10px;
                                    #             padding: 15px;
                                    #             margin: 20px 0;
                                    #             border-left: 4px solid #E1306C;
                                    #         ">
                                    #             <h4 style="margin-top:0; color: #E1306C;">AI Recommendations</h4>
                                    #             {response.content}
                                    #         </div>
                                    #         """, unsafe_allow_html=True)
                                    #     except Exception as e:
                                    #         st.error(f"Couldn't generate recommendations: {str(e)}")
                            
                            platform_names.append('Instagram')

            # ========== THREADS ANALYSIS ==========
            if analyze_threads and has_threads:
                with st.spinner("Analyzing Threads comments..."):
                    data = fetch_threads_comments(os.getenv("THREADS_ID"), os.getenv("THREADS_TOKEN"))
                    comment_texts, post_ids, captions, post_urls = extract_comments(data, 'threads', os.getenv("THREADS_TOKEN"))
                    
                    if comment_texts:
                        predicted_sentiments = perform_sentiment_analysis(comment_texts, model, vectorizer, reverse_label_mapping)
                        threads_results = pd.DataFrame({
                            'Platform': 'Threads',
                            'Post ID': post_ids,
                            'Post Caption': captions,
                            'Post URL': post_urls,
                            'Comment': comment_texts,
                            'Sentiment': predicted_sentiments
                        })
                        all_results.append(threads_results)
                        
                        posts = {}
                        for post_id, caption, comment, sentiment, url in zip(post_ids, captions, comment_texts, predicted_sentiments, post_urls):
                            if post_id not in posts:
                                posts[post_id] = {
                                    'caption': caption,
                                    'url': url,
                                    'comments': [],
                                    'sentiments': []
                                }
                            posts[post_id]['comments'].append(comment)
                            posts[post_id]['sentiments'].append(sentiment)
                        
                        with st.expander("🧵 Threads Analysis", expanded=True):
                            st.subheader("Threads Sentiment Analysis")
                            
                            for post_id, post_data in posts.items():
                                with st.container():
                                    # Threads-styled post card
                                    st.markdown(f"""
                                    <div style="
                                        background: linear-gradient(145deg, #000000, #333333, #8A3FFC);
                                        border-radius: 10px;
                                        padding: 15px;
                                        margin-bottom: 20px;
                                        color: white;
                                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                                        transition: all 0.3s ease;
                                        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
                                    ">
                                        <h4 style="margin-top:0;">
                                            <a href="{post_data['url']}" target="_blank" style="color: white; text-decoration: none;">
                                                {post_data['caption'][:100]}{'...' if len(post_data['caption']) > 100 else ''}
                                            </a>
                                        </h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Sentiment metrics
                                    post_sentiments = post_data['sentiments']
                                    pos_count = post_sentiments.count('Positive')
                                    neu_count = post_sentiments.count('Neutral')
                                    neg_count = post_sentiments.count('Negative')
                                    total = len(post_sentiments)
                                    
                                    st.markdown(f"""
                                    <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                                        <div style="flex: 1; background: #4CAF5010; border-left: 4px solid #4CAF50; border-radius: 5px; padding: 10px;">
                                            <div style="font-size: 12px; color: #4CAF50;">Positive</div>
                                            <div style="font-size: 16px; font-weight: bold;">{pos_count} ({pos_count/total*100:.1f}%)</div>
                                        </div>
                                        <div style="flex: 1; background: #FFC10710; border-left: 4px solid #FFC107; border-radius: 5px; padding: 10px;">
                                            <div style="font-size: 12px; color: #FFC107;">Neutral</div>
                                            <div style="font-size: 16px; font-weight: bold;">{neu_count} ({neu_count/total*100:.1f}%)</div>
                                        </div>
                                        <div style="flex: 1; background: #F4433610; border-left: 4px solid #F44336; border-radius: 5px; padding: 10px;">
                                            <div style="font-size: 12px; color: #F44336;">Negative</div>
                                            <div style="font-size: 16px; font-weight: bold;">{neg_count} ({neg_count/total*100:.1f}%)</div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Comments display
                                    for comment, sentiment in zip(post_data['comments'], post_data['sentiments']):
                                        color = "#4CAF50" if sentiment == "Positive" else "#F44336" if sentiment == "Negative" else "#FFC107"
                                        emoji = "👍" if sentiment == "Positive" else "👎" if sentiment == "Negative" else "💬"
                                        
                                        st.markdown(f"""
                                        <div style="
                                            background: {color}10;
                                            border-left: 4px solid {color};
                                            border-radius: 4px;
                                            padding: 10px;
                                            margin: 5px 0;
                                            font-size: 14px;
                                        ">
                                            <div style="display: flex; align-items: center; gap: 8px;">
                                                <span style="font-size: 18px;">{emoji}</span>
                                                <span>{comment}</span>
                                            </div>
                                            <div style="margin-top: 5px; font-size: 12px; color: {color};">
                                                Sentiment: <strong>{sentiment}</strong>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    # # Generate AI recommendations for this thread
                                    # with st.spinner("Generating AI insights..."):
                                    #     try:
                                    #         # Prepare comment samples for context
                                    #         sample_comments = "\n".join([f"- {c}" for c in post_data['comments'][:5]])
                                            
                                    #         response = llm.invoke(f"""
                                    #         Analyze this Threads post and its replies to provide 2-3 actionable recommendations:

                                    #         Post Content: {post_data['caption']}
                                            
                                    #         Sentiment Distribution:
                                    #         - Positive: {pos_count} ({pos_count/total*100:.1f}%)
                                    #         - Neutral: {neu_count} ({neu_count/total*100:.1f}%)
                                    #         - Negative: {neg_count} ({neg_count/total*100:.1f}%)
                                            
                                    #         Sample Comments:
                                    #         {sample_comments}
                                            
                                    #         Provide concise recommendations focusing on:
                                    #         1. How to improve engagement based on positive feedback
                                    #         2. How to address any concerns from negative comments
                                    #         3. Content strategy adjustments if needed
                                            
                                    #         Format as bullet points with �, 🧶, and 🪡 emojis.
                                    #         """)
                                            
                                    #         # Display recommendations in styled card
                                    #         st.markdown(f"""
                                    #         <div style="
                                    #             background: #F5F8FA;
                                    #             border-radius: 10px;
                                    #             padding: 15px;
                                    #             margin: 20px 0;
                                    #             border-left: 4px solid #000000;
                                    #         ">
                                    #             <h4 style="margin-top:0; color: #000000;">AI Recommendations</h4>
                                    #             {response.content}
                                    #         </div>
                                    #         """, unsafe_allow_html=True)
                                    #     except Exception as e:
                                    #         st.error(f"Couldn't generate recommendations: {str(e)}")
                            
                            platform_names.append('Threads')

            # ========== RESULTS DISPLAY ==========
            if not all_results:
                st.warning("No comments found for the selected platforms.")
                return
                
            results_df = pd.concat(all_results, ignore_index=True)
            
            # Visualization and download sections
            st.markdown('<div class="section-header">📊 Analysis Results</div>', unsafe_allow_html=True)
            
            # Platform tabs
            tabs = st.tabs([f"{platform} Results" for platform in platform_names])
            for i, platform in enumerate(platform_names):
                with tabs[i]:
                    platform_df = results_df[results_df['Platform'] == platform]
                    st.dataframe(platform_df)
                    
                    sentiment_counts = platform_df['Sentiment'].value_counts(normalize=True) * 100
                    st.markdown(f"**Sentiment Distribution for {platform}**")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Positive", f"{sentiment_counts.get('Positive', 0):.1f}%")
                    col2.metric("Negative", f"{sentiment_counts.get('Negative', 0):.1f}%")
                    col3.metric("Neutral", f"{sentiment_counts.get('Neutral', 0):.1f}%")
            
            # Visualizations
            st.markdown('<div class="section-header">📈 Combined Sentiment Analysis</div>', unsafe_allow_html=True)
            visualize_sentiment_distribution(results_df)
            
            # Model metrics
            st.markdown('<div class="section-header">🤖 Model Performance</div>', unsafe_allow_html=True)
            st.table(pd.DataFrame({
                'Metric': ['Accuracy', 'F1 Score', 'Precision', 'Recall'],
                'Value': [f"{metrics['accuracy']:.4f}", f"{metrics['f1_score']:.4f}", f"{metrics['precision']:.4f}", f"{metrics['recall']:.4f}"]
            }))
            
            # Download options
            st.markdown('<div class="section-header">📥 Download Results</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            col1.download_button(
                "Download as CSV",
                data=results_df.to_csv(index=False),
                file_name="multi_platform_sentiment.csv",
                mime="text/csv",
                use_container_width=True
            )
            col2.download_button(
                "Download as JSON",
                data=results_df.to_json(orient='records'),
                file_name="multi_platform_sentiment.json",
                mime="application/json",
                use_container_width=True
            )
                
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")


def settings_page():
    """Display and handle the settings page"""
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Configure your API credentials and platform settings</div>', unsafe_allow_html=True)
    
    # OpenAI API settings
    st.markdown('<div class="section-header">🤖 OpenAI API Settings</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        openai_api_key = st.text_input("OpenAI API Key", 
                                        value=os.getenv("OPENAI_API_KEY", ""), 
                                        type="password",
                                        help="Your OpenAI API key for accessing GPT models")
        
        model = st.selectbox("OpenAI Model", 
                             options=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"],
                             index=0,
                             help="Select which OpenAI model to use")
        
        col1, col2 = st.columns(2)
        with col1:
            save_openai = st.button("Save OpenAI Settings", use_container_width=True)
        
        if save_openai:
            updated_openai = update_env_variable("OPENAI_API_KEY", openai_api_key)
            updated_model = update_env_variable("MODEL", model)
            
            if updated_openai and updated_model:
                st.markdown('<div class="success-message">✅ OpenAI settings saved successfully!</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Facebook settings
    st.markdown('<div class="section-header">📘 Facebook Settings</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            fb_page_token = st.text_input("Facebook Page Access Token", 
                                         value=os.getenv("PAGE_ACCESS_TOKEN", ""), 
                                         type="password",
                                         help="Your Facebook Page Access Token")
        
        with col2:
            fb_page_id = st.text_input("Facebook Page ID", 
                                      value=os.getenv("PAGE_ID", ""),
                                      help="Your Facebook Page ID")
        
        col1, col2 = st.columns(2)
        with col1:
            save_fb = st.button("Save Facebook Settings", use_container_width=True)
        
        if save_fb:
            updated_fb_token = update_env_variable("PAGE_ACCESS_TOKEN", fb_page_token)
            updated_fb_id = update_env_variable("PAGE_ID", fb_page_id)
            
            if updated_fb_token and updated_fb_id:
                st.markdown('<div class="success-message">✅ Facebook settings saved successfully!</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Instagram settings
    st.markdown('<div class="section-header">📸 Instagram Settings</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            insta_token = st.text_input("Instagram Token", 
                                        value=os.getenv("INSTA_TOKEN", ""), 
                                        type="password",
                                        help="Your Instagram API Token")
        
        with col2:
            insta_id = st.text_input("Instagram Account ID", 
                                     value=os.getenv("INSTA_ID", ""),
                                     help="Your Instagram Account ID")
        
        col1, col2 = st.columns(2)
        with col1:
            save_insta = st.button("Save Instagram Settings", use_container_width=True)
        
        if save_insta:
            updated_insta_token = update_env_variable("INSTA_TOKEN", insta_token)
            updated_insta_id = update_env_variable("INSTA_ID", insta_id)
            
            if updated_insta_token and updated_insta_id:
                st.markdown('<div class="success-message">✅ Instagram settings saved successfully!</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Threads settings
    st.markdown('<div class="section-header">🧵 Threads Settings</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            threads_token = st.text_input("Threads Token", 
                                          value=os.getenv("THREADS_TOKEN", ""), 
                                          type="password",
                                          help="Your Threads API Token")
        
        with col2:
            threads_id = st.text_input("Threads Account ID", 
                                       value=os.getenv("THREADS_ID", ""),
                                       help="Your Threads Account ID")
        
        col1, col2 = st.columns(2)
        with col1:
            save_threads = st.button("Save Threads Settings", use_container_width=True)
        
        if save_threads:
            updated_threads_token = update_env_variable("THREADS_TOKEN", threads_token)
            updated_threads_id = update_env_variable("THREADS_ID", threads_id)
            
            if updated_threads_token and updated_threads_id:
                st.markdown('<div class="success-message">✅ Threads settings saved successfully!</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Testing connection
    st.markdown('<div class="section-header">🔄 Test Connections</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        test_connections = st.button("Test All Platform Connections", use_container_width=True)
        
        if test_connections:
            # Testing logic would go here in a production app
            # For this demo, we'll just show success messages
            
            missing_configs = []
            
            if not os.getenv("OPENAI_API_KEY"):
                missing_configs.append("OpenAI API Key")
            
            if not os.getenv("PAGE_ACCESS_TOKEN") or not os.getenv("PAGE_ID"):
                missing_configs.append("Facebook credentials")
            
            if not os.getenv("INSTA_TOKEN") or not os.getenv("INSTA_ID"):
                missing_configs.append("Instagram credentials")
            
            if not os.getenv("THREADS_TOKEN") or not os.getenv("THREADS_ID"):
                missing_configs.append("Threads credentials")
            
            if missing_configs:
                st.warning(f"⚠️ The following configurations are missing: {', '.join(missing_configs)}")
            else:
                st.markdown('<div class="success-message">✅ All platform connections tested successfully!</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Reset all settings
    st.markdown('<div class="section-header">🗑️ Reset Settings</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.warning("⚠️ This will clear all your saved API keys and credentials.")
        reset_all = st.button("Reset All Settings", use_container_width=True)
        
        if reset_all:
            # Clear all environment variables
            update_env_variable("OPENAI_API_KEY", "")
            update_env_variable("MODEL", "")
            update_env_variable("PAGE_ACCESS_TOKEN", "")
            update_env_variable("PAGE_ID", "")
            update_env_variable("INSTA_TOKEN", "")
            update_env_variable("INSTA_ID", "")
            update_env_variable("THREADS_TOKEN", "")
            update_env_variable("THREADS_ID", "")
            
            st.success("All settings have been reset.")
            
            # Add a button to refresh the page
            st.button("Refresh Page", on_click=lambda: st.rerun())
        st.markdown('</div>', unsafe_allow_html=True)

def home_page():
    """Display the home page with content generation functionality"""
    # Header
    st.markdown('<div class="main-header">Social Media Automation Crew</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Create viral content for multiple platforms using AI</div>', unsafe_allow_html=True)
    
    # Main input area
    st.markdown('<div class="section-header">What should we create content about?</div>', unsafe_allow_html=True)
    
    # Create columns for input and button
    col1, col2 = st.columns([3, 1])
    with col1:
        niche = st.text_input("Enter a topic, niche, or product", placeholder="e.g., sports, trump, sustainable fashion, crypto investing, vegan cooking...")
    with col2:
        generate_button = st.button("Generate Content", use_container_width=True)

    if not os.getenv('MODEL') or not os.getenv('OPENAI_API_KEY'):
        st.warning("⚠️ OpenAI API key or model not configured. Please visit the Settings page to configure your API keys.")

    # Initialize session state to track progress
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'completed' not in st.session_state:
        st.session_state.completed = False
    if 'posts' not in st.session_state:
        st.session_state.posts = None
    if 'metrics' not in st.session_state:
        st.session_state.metrics = None
    if 'post_state' not in st.session_state:
        st.session_state.post_state = {
            "threads": False,
            "instagram": False,
            "facebook": False
        }
    if 'final_content' not in st.session_state:
        st.session_state.final_content = {
            "threads": "",
            "instagram": "",
            "facebook": ""
        }

    # Process request
    if generate_button and niche and not st.session_state.processing:
        # Reset post_state and final_content when generate is clicked again
        st.session_state.post_state = {
            "threads": False,
            "instagram": False,
            "facebook": False
        }
        st.session_state.final_content = {
            "threads": "",
            "instagram": "",
            "facebook": ""
        }
        
        # Check if API keys are configured
        if not os.getenv('MODEL') or not os.getenv('OPENAI_API_KEY'):
            st.error("Please configure your OpenAI API key and model in the Settings page first.")
            return
            
        st.session_state.processing = True
        st.session_state.completed = False
        
        # Display loading animation
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            display_loading_animation()
        
        try:
            # Run the AI crew
            posts, usage_metrics = run_content_crew(niche)
            
            # Store results in session state
            st.session_state.posts = posts
            st.session_state.metrics = usage_metrics
            st.session_state.completed = True
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            st.session_state.processing = False
            loading_placeholder.empty()
    
    # Display results if completed
    if st.session_state.completed and st.session_state.posts:
        posts = st.session_state.posts
        
        st.markdown('<div class="section-header">🎉 Your Social Media Content</div>', unsafe_allow_html=True)
        
        # Display posts for each platform
        display_social_media_card("Threads", "🧵", posts.get("threads", "Content not available"))
        display_social_media_card("Instagram", "📸", posts.get("instagram", "Content not available"))
        display_social_media_card("Facebook", "📘", posts.get("facebook", "Content not available"))
        
        # Display metrics
        if st.session_state.metrics:
            st.markdown('<div class="section-header">📊 AI Usage Metrics</div>', unsafe_allow_html=True)
            st.markdown('<div class="metrics-box">', unsafe_allow_html=True)
            metrics = st.session_state.metrics
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Tokens Used", metrics.get("total_tokens", "N/A"))
                st.metric("Input Tokens", metrics.get("prompt_tokens", "N/A"))
            with col2:
                st.metric("Output Tokens", metrics.get("completion_tokens", "N/A"))
                st.metric("successful Requests", metrics.get('successful_requests', "N/A"))
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Download options
        st.markdown('<div class="section-header">📥 Download Your Content</div>', unsafe_allow_html=True)
        
        # Convert posts to downloadable format
        download_content = json.dumps(posts, indent=2)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download as JSON",
                data=download_content,
                file_name=f"social_media_content_{niche.replace(' ', '_')}.json",
                mime="application/json"
            )
        with col2:
            # Create markdown version for download
            markdown_content = f"""# Social Media Content for: {niche}

## Threads Post
{posts.get('threads', 'Content not available')}

## Instagram Post
{posts.get('instagram', 'Content not available')}

## Facebook Post
{posts.get('facebook', 'Content not available')}

---
Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            st.download_button(
                label="Download as Markdown",
                data=markdown_content,
                file_name=f"social_media_content_{niche.replace(' ', '_')}.md",
                mime="text/markdown"
            )

def main():
    # Initialize session state for navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Sidebar navigation
    with st.sidebar:
        st.image("social_media_crew_logo_streamlit-removebg-preview.png", use_container_width=True)
        st.markdown("---")
        
        # Navigation buttons
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = 'home'
        
        if st.button("📊 Comments Analysis", use_container_width=True):
            st.session_state.page = 'comments'
        
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.page = 'settings'
        
        st.markdown("---")
        
        # Display configuration status
        st.markdown("### Configuration Status")
        
        # OpenAI config
        openai_status = "✅ Configured" if os.getenv("OPENAI_API_KEY") else "⚠️ Not Configured"
        st.markdown(f"**OpenAI**: {openai_status}")
        
        # Facebook config
        fb_status = "✅ Configured" if (os.getenv("PAGE_ACCESS_TOKEN") and os.getenv("PAGE_ID")) else "⚠️ Not Configured"
        st.markdown(f"**Facebook**: {fb_status}")
        
        # Instagram config
        insta_status = "✅ Configured" if (os.getenv("INSTA_TOKEN") and os.getenv("INSTA_ID")) else "⚠️ Not Configured"
        st.markdown(f"**Instagram**: {insta_status}")
        
        # Threads config
        threads_status = "✅ Configured" if (os.getenv("THREADS_TOKEN") and os.getenv("THREADS_ID")) else "⚠️ Not Configured"
        st.markdown(f"**Threads**: {threads_status}")
        
        st.markdown("---") 
        st.markdown("### About")
        st.info("""
        SocialCrewAI uses a team of AI agents to research trending topics and create tailored content for multiple social media platforms.
        
        Version 1.0.0
        """)
    
    # Render the appropriate page based on navigation state
    if st.session_state.page == 'home':
        home_page()
    elif st.session_state.page == 'settings':
        settings_page()
    elif st.session_state.page == 'comments':
        comments_analysis_page()

if __name__ == "__main__":
    main()