"""
YouTube API wrapper - leverages existing credentials
"""
import os
import pickle
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class YouTubeAPI:
    def __init__(self, credentials_dir='/root/youtube_credentials', token_dir='/root/youtube_tokens'):
        self.credentials_dir = credentials_dir
        self.token_dir = token_dir
        self.youtube = None
        
    def authenticate(self, account_number=1):
        """Authenticate with YouTube using existing credentials"""
        # Load existing token
        token_file = os.path.join(self.token_dir, f'credentials_{account_number}_token.pickle')
        
        if not os.path.exists(token_file):
            raise FileNotFoundError(f'Token file not found: {token_file}')
        
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        
        self.youtube = build('youtube', 'v3', credentials=creds)
        return self.youtube
    
    def search(self, query, max_results=10, order='relevance'):
        """Search YouTube videos"""
        if not self.youtube:
            self.authenticate()
        
        request = self.youtube.search().list(
            q=query,
            part='snippet',
            maxResults=max_results,
            order=order,
            type='video'
        )
        response = request.execute()
        return response
    
    def get_video_stats(self, video_id):
        """Get video statistics"""
        if not self.youtube:
            self.authenticate()
        
        request = self.youtube.videos().list(
            part='statistics',
            id=video_id
        )
        response = request.execute()
        return response
    
    def get_channel_videos(self, channel_id, max_results=10):
        """Get latest videos from a channel"""
        if not self.youtube:
            self.authenticate()
        
        request = self.youtube.search().list(
            channelId=channel_id,
            part='snippet',
            maxResults=max_results,
            order='date',
            type='video'
        )
        response = request.execute()
        return response
