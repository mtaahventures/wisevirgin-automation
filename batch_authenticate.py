"""
Batch authenticate multiple Google Cloud Projects with the SAME WiseVirgin channel

This allows 60-100 videos per day by having multiple quota pools
but all uploading to the same channel.
"""
import os
import sys
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes required for YouTube upload
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate_account(credentials_file, token_file, start_from=None):
    """
    Authenticate a single Google Cloud Project with WiseVirgin channel owner

    Args:
        credentials_file: Path to client_secret.json
        token_file: Path to save token pickle
        start_from: Account number to resume from (optional)
    """
    print(f"\n{'='*80}")
    print(f"Authenticating: {os.path.basename(credentials_file)}")
    print(f"Token will be saved to: {token_file}")
    print(f"{'='*80}\n")

    if os.path.exists(token_file):
        print(f"⚠️  Token already exists: {token_file}")
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Skipped.\n")
            return False

    # Create OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_file,
        SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Console-based flow
    )

    # Get authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')

    print("\n" + "="*80)
    print("IMPORTANT: Log in with the WISEVIRGIN CHANNEL OWNER account!")
    print("="*80)
    print(f"\nStep 1: Visit this URL in your browser:\n")
    print(auth_url)
    print(f"\nStep 2: Log in with the WiseVirgin channel owner Google account")
    print(f"Step 3: Grant permissions")
    print(f"Step 4: Copy the authorization code\n")

    # Get authorization code from user
    code = input("Paste the authorization code here: ").strip()

    if not code:
        print("❌ No code provided. Skipping.\n")
        return False

    # Exchange code for credentials
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Save token
        with open(token_file, 'wb') as token:
            pickle.dump(credentials, token)

        # Test the credentials by getting channel info
        youtube = build('youtube', 'v3', credentials=credentials)
        request = youtube.channels().list(part='snippet', mine=True)
        response = request.execute()

        if 'items' in response and len(response['items']) > 0:
            channel_title = response['items'][0]['snippet']['title']
            channel_id = response['items'][0]['id']

            print(f"\n✅ SUCCESS!")
            print(f"   Channel: {channel_title}")
            print(f"   Channel ID: {channel_id}")
            print(f"   Token saved: {token_file}\n")

            return True
        else:
            print("\n❌ Authentication succeeded but no channel found.\n")
            return False

    except Exception as e:
        print(f"\n❌ Authentication failed: {e}\n")
        return False

def batch_authenticate(credentials_dir='/root/youtube_credentials',
                       token_dir='/root/youtube_tokens',
                       start_account=5,
                       end_account=15):
    """
    Batch authenticate multiple accounts

    Args:
        credentials_dir: Directory containing credentials JSON files
        token_dir: Directory to save token pickles
        start_account: First account number to authenticate
        end_account: Last account number to authenticate
    """
    print("\n" + "="*80)
    print("WISEVIRGIN - BATCH AUTHENTICATION")
    print("Authenticate Multiple Google Cloud Projects with Same Channel")
    print("="*80)

    # Ensure directories exist
    os.makedirs(credentials_dir, exist_ok=True)
    os.makedirs(token_dir, exist_ok=True)

    success_count = 0
    failed_count = 0
    skipped_count = 0

    for account_num in range(start_account, end_account + 1):
        credentials_file = os.path.join(credentials_dir, f'credentials_{account_num}.json')
        token_file = os.path.join(token_dir, f'credentials_{account_num}_token.pickle')

        # Check if credentials file exists
        if not os.path.exists(credentials_file):
            print(f"\n⚠️  Credentials not found: {credentials_file}")
            print(f"   Skipping account {account_num}")
            skipped_count += 1
            continue

        # Authenticate
        success = authenticate_account(credentials_file, token_file)

        if success:
            success_count += 1
        else:
            failed_count += 1

        # Pause between accounts
        if account_num < end_account:
            input("\nPress Enter to continue to next account (or Ctrl+C to stop)...")

    # Summary
    print("\n" + "="*80)
    print("BATCH AUTHENTICATION COMPLETE")
    print("="*80)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"📊 Total Accounts: {start_account} - {end_account}")
    print(f"\n💡 Daily Upload Capacity: {success_count * 6}-{success_count * 10} videos")
    print("="*80 + "\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Batch authenticate YouTube accounts')
    parser.add_argument('--start', type=int, default=5, help='First account number (default: 5)')
    parser.add_argument('--end', type=int, default=15, help='Last account number (default: 15)')
    parser.add_argument('--credentials-dir', default='/root/youtube_credentials', help='Credentials directory')
    parser.add_argument('--token-dir', default='/root/youtube_tokens', help='Token directory')

    args = parser.parse_args()

    batch_authenticate(
        credentials_dir=args.credentials_dir,
        token_dir=args.token_dir,
        start_account=args.start,
        end_account=args.end
    )
