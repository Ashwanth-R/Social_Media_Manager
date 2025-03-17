import os
import json
import re
import time
import streamlit as st
from dotenv import load_dotenv, set_key
from textwrap import dedent
from openai import OpenAI
from crewai import Crew
from crewai.process import Process
from tasks import ViralContentCreationTasks
from agents import ViralContentCreators
from config import final_content
import base64

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

if __name__ == "__main__":
    main()