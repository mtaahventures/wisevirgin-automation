"""
ENGINE 4.1: YouTube Uploader  
Uploads videos to YouTube using existing authenticated credentials
Leverages: /root/youtube_credentials/ and /root/youtube_tokens/
"""
import os
import sys
import pickle
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('youtube_uploader', get_daily_log_file())

class YouTubeUploader:
    def __init__(self, credentials_dir='/root/youtube_credentials', token_dir='/root/youtube_tokens'):
        self.credentials_dir = credentials_dir
        self.token_dir = token_dir
        self.youtube = None
    
    def authenticate(self, account_number=1):
        """Authenticate with existing YouTube credentials"""
        token_file = os.path.join(self.token_dir, f'credentials_{account_number}_token.pickle')
        
        if not os.path.exists(token_file):
            raise FileNotFoundError(f'Token file not found: {token_file}')
        
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        
        self.youtube = build('youtube', 'v3', credentials=creds)
        logger.info(f'Authenticated with account {account_number}')
        
        return self.youtube
    
    def upload_video(self, video_file, metadata, account_number=1):
        """Upload video to YouTube"""
        logger.info(f'Uploading video: {video_file}')
        
        if not self.youtube:
            self.authenticate(account_number)
        
        # Prepare metadata
        body = {
            'snippet': {
                'title': metadata.get('title', 'Untitled Video'),
                'description': metadata.get('description', ''),
                'tags': metadata.get('tags', []),
                'categoryId': metadata.get('category_id', '26')
            },
            'status': {
                'privacyStatus': metadata.get('privacy_status', 'public'),
                'selfDeclaredMadeForKids': metadata.get('made_for_kids', False)
            }
        }
        
        # Upload video file
        media = MediaFileUpload(
            video_file,
            chunksize=1024*1024,  # 1MB chunks
            resumable=True,
            mimetype='video/mp4'
        )
        
        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        # Execute upload
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f'Upload progress: {int(status.progress() * 100)}%')
        
        video_id = response['id']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        
        logger.info(f'Upload complete! Video ID: {video_id}')
        logger.info(f'Video URL: {video_url}')
        
        return {
            'video_id': video_id,
            'video_url': video_url,
            'title': metadata.get('title'),
            'status': 'uploaded'
        }
    
    def set_thumbnail(self, video_id, thumbnail_file, account_number=1):
        """Set custom thumbnail for video"""
        if not self.youtube:
            self.authenticate(account_number)
        
        logger.info(f'Setting thumbnail for video {video_id}')
        
        self.youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_file)
        ).execute()
        
        logger.info('Thumbnail set successfully')

if __name__ == '__main__':
    uploader = YouTubeUploader()
    print("YouTube uploader ready (leverages existing credentials)")
    print(f"Credentials dir: {uploader.credentials_dir}")
    print(f"Token dir: {uploader.token_dir}")
