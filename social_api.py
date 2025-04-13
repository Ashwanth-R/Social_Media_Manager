import requests
import os
from typing import List, Tuple

def fetch_facebook_posts(page_id: str, access_token: str) -> dict:
    """Fetch posts from Facebook page with URLs"""
    url = f"https://graph.facebook.com/v19.0/{page_id}/posts"
    params = {
        'access_token': access_token,
        'fields': 'id,message,permalink_url,comments{message,from}',
        'limit': 100
    }
    response = requests.get(url, params=params)
    return response.json()

def fetch_instagram_comments(instagram_id: str, access_token: str) -> dict:
    """Fetch comments from Instagram posts with URLs"""
    url = f"https://graph.facebook.com/v19.0/{instagram_id}/media"
    params = {
        'access_token': access_token,
        'fields': 'id,caption,permalink,comments{text,username}',
        'limit': 100
    }
    response = requests.get(url, params=params)
    return response.json()

def fetch_threads_comments(threads_id: str, access_token: str) -> dict:
    """Fetch comments from Threads posts"""
    # Note: Threads API may have different endpoints - this is a placeholder
    url = f"https://graph.threads.net/v1.0/{threads_id}/replies"
    params = {
        'access_token': access_token,
        'fields': 'text,permalink,replied_to{id}',
        'limit': 100
    }
    response = requests.get(url, params=params)
    return response.json()


def extract_comments(data: dict, platform: str, access_token: str = None) -> Tuple[List[str], List[str], List[str], List[str]]:
    """Extract comments from platform data"""
    comments = []
    post_ids = []
    captions = []
    post_urls = []
    
    if platform == 'facebook':
        for post in data.get('data', []):
            post_url = post.get('permalink_url', f"https://facebook.com/{post['id']}")
            for comment in post.get('comments', {}).get('data', []):
                comments.append(comment.get('message', ''))
                post_ids.append(post['id'])
                captions.append(post.get('message', ''))
                post_urls.append(post_url)
    
    elif platform == 'instagram':
        for media in data.get('data', []):
            post_url = media.get('permalink', f"https://instagram.com/p/{media['id']}")
            for comment in media.get('comments', {}).get('data', []):
                comments.append(comment.get('text', ''))
                post_ids.append(media['id'])
                captions.append(media.get('caption', ''))
                post_urls.append(post_url)
    
    elif platform == 'threads':
        for reply in data.get('data', []):
            # Get the reply text and URL
            comments.append(reply.get('text', ''))
            post_urls.append(reply.get('permalink', ''))
            
            # Store the reply ID
            post_ids.append(reply.get('id', ''))
            
            # Get the original post caption using replied_to ID
            replied_to_id = reply.get('replied_to', {}).get('id', '')
            if replied_to_id and access_token:
                try:
                    caption = fetch_thread_post_caption(replied_to_id, access_token)
                    captions.append(caption)
                except Exception as e:
                    captions.append('')  # If we can't fetch, add empty string
                    print(f"Error fetching caption for post {replied_to_id}: {str(e)}")
            else:
                captions.append('')
    
    return comments, post_ids, captions, post_urls

def fetch_thread_post_caption(post_id: str, access_token: str) -> str:
    """Fetch the text/caption of a Threads post"""
    url = f"https://graph.threads.net/v1.0/{post_id}"
    params = {
        'access_token': access_token,
        'fields': 'text'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get('text', '')