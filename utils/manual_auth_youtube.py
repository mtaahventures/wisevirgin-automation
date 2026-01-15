"""
Manual YouTube OAuth Authentication (Headless Server)
Generates auth URL for user to visit, then accepts auth code to create tokens
"""
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth scopes required for YouTube uploads
SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
          'https://www.googleapis.com/auth/youtube',
          'https://www.googleapis.com/auth/youtube.force-ssl']

def manual_auth(account_number=1, credentials_dir='/root/youtube_credentials', token_dir='/root/youtube_tokens'):
    """Manual OAuth flow for headless servers"""

    client_secrets_file = os.path.join(credentials_dir, f'credentials_{account_number}.json')
    token_file = os.path.join(token_dir, f'credentials_{account_number}_token.pickle')

    print(f"\n{'='*70}")
    print(f"YouTube OAuth Manual Authentication - Account {account_number}")
    print(f"{'='*70}\n")

    if not os.path.exists(client_secrets_file):
        raise FileNotFoundError(f'Client secrets not found: {client_secrets_file}')

    # Create OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)

    # Generate authorization URL
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # Manual copy/paste mode
    auth_url, _ = flow.authorization_url(prompt='consent')

    print("STEP 1: Open this URL in your browser:")
    print("-" * 70)
    print(auth_url)
    print("-" * 70)
    print("\nSTEP 2: Authorize the application and copy the authorization code\n")

    # Wait for user to input the authorization code
    auth_code = input("STEP 3: Paste the authorization code here: ").strip()

    # Exchange code for credentials
    print("\nExchanging authorization code for credentials...")
    flow.fetch_token(code=auth_code)

    creds = flow.credentials

    # Save credentials
    with open(token_file, 'wb') as f:
        pickle.dump(creds, f)

    print(f"\n✓ Success! Token saved to: {token_file}")
    print(f"✓ Account {account_number} is now authenticated\n")

    return creds

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        account = int(sys.argv[1])
    else:
        account = 1
        print("No account specified, using account 1")
        print("Usage: python manual_auth_youtube.py [account_number]\n")

    manual_auth(account)
