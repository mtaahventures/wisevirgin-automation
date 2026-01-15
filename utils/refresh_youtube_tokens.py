"""
YouTube OAuth Token Refresh Script
Refreshes expired YouTube API tokens using client credentials
"""
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth scopes required for YouTube uploads
SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
          'https://www.googleapis.com/auth/youtube',
          'https://www.googleapis.com/auth/youtube.force-ssl']

def refresh_token(account_number=1, credentials_dir='/root/youtube_credentials', token_dir='/root/youtube_tokens'):
    """Refresh YouTube OAuth token for specified account"""
    
    # File paths
    client_secrets_file = os.path.join(credentials_dir, f'credentials_{account_number}.json')
    token_file = os.path.join(token_dir, f'credentials_{account_number}_token.pickle')
    
    print(f'Refreshing token for account {account_number}...')
    print(f'Client secrets: {client_secrets_file}')
    print(f'Token file: {token_file}')
    
    # Check if files exist
    if not os.path.exists(client_secrets_file):
        raise FileNotFoundError(f'Client secrets not found: {client_secrets_file}')
    
    creds = None
    
    # Load existing token
    if os.path.exists(token_file):
        print('Loading existing token...')
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
    
    # Refresh or create new credentials
    if creds and creds.expired and creds.refresh_token:
        print('Token expired, refreshing...')
        try:
            creds.refresh(Request())
            print('✄ Token refreshed successfully')
        except Exception as e:
            print(f'❌ Token refresh failed: {e}')
            print('Initiating new OAuth flow...')
            creds = None
    
    # If refresh failed or no credentials, start new OAuth flow
    if not creds or not creds.valid:
        print('Starting OAuth flow (browser will open)...')
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
        creds = flow.run_local_server(port=0)
        print('✔ New credentials obtained')
    
    # Save refreshed token
    with open(token_file, 'wb') as f:
        pickle.dump(creds, f)
    print(f'✔ Token saved to: {token_file}')
    
    return creds

def refresh_all_tokens():
    """Refresh all YouTube account tokens (1-3)"""
    for account_num in range(1, 4):
        try:
            print("\n" + "="*60)
            refresh_token(account_num)
            print("="*60)
        except FileNotFoundError as e:
            print(f'Skipping account {account_num}: {e}')
        except Exception as e:
            print(f'Error refreshing account {account_num}: {e}')

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        account = int(sys.argv[1])
        refresh_token(account)
    else:
        print('Usage: python refresh_youtube_tokens.py [account_number]')
        print('Example: python refresh_youtube_tokens.py 1')
        print('\nRefreshing account 1 by default...')
        refresh_token(1)
