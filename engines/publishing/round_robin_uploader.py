"""
Round-Robin YouTube Uploader

Cycles through multiple authenticated Google Cloud Projects to maximize daily uploads.
All projects upload to the SAME WiseVirgin channel.

Strategy:
- Tries account 1, if quota exceeded → tries account 2
- If all accounts exhausted → waits until tomorrow
- Tracks which accounts have quota available
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from engines.publishing.youtube_uploader import YouTubeUploader
from utils.logging_utils import setup_logger, get_daily_log_file
import json
from datetime import datetime

logger = setup_logger("round_robin_uploader", get_daily_log_file())

class RoundRobinYouTubeUploader:
    def __init__(self, credentials_dir='/root/youtube_credentials', token_dir='/root/youtube_tokens'):
        """
        Initialize round-robin uploader

        Args:
            credentials_dir: Directory with OAuth credentials
            token_dir: Directory with authentication tokens
        """
        self.credentials_dir = credentials_dir
        self.token_dir = token_dir
        self.quota_tracking_file = "data/youtube_quota_tracking.json"

        # Find all available authenticated accounts
        self.available_accounts = self._discover_accounts()

        logger.info(f"Round-robin uploader initialized with {len(self.available_accounts)} accounts")

    def _discover_accounts(self):
        """
        Discover all authenticated YouTube accounts

        Returns:
            list: Available account numbers
        """
        if not os.path.exists(self.token_dir):
            logger.warning(f"Token directory not found: {self.token_dir}")
            return []

        accounts = []
        for filename in os.listdir(self.token_dir):
            if filename.startswith('credentials_') and filename.endswith('_token.pickle'):
                # Extract account number from filename
                # Format: credentials_3_token.pickle → 3
                try:
                    account_num = int(filename.split('_')[1])
                    accounts.append(account_num)
                except (IndexError, ValueError):
                    continue

        accounts.sort()
        logger.info(f"Discovered {len(accounts)} authenticated accounts: {accounts}")

        return accounts

    def _load_quota_tracking(self):
        """
        Load quota tracking data

        Returns:
            dict: Quota tracking data by date and account
        """
        if not os.path.exists(self.quota_tracking_file):
            return {}

        try:
            with open(self.quota_tracking_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading quota tracking: {e}")
            return {}

    def _save_quota_tracking(self, data):
        """
        Save quota tracking data

        Args:
            data: Quota tracking data to save
        """
        try:
            os.makedirs(os.path.dirname(self.quota_tracking_file), exist_ok=True)
            with open(self.quota_tracking_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving quota tracking: {e}")

    def _mark_account_exhausted(self, account_number):
        """
        Mark an account as quota exhausted for today

        Args:
            account_number: Account to mark as exhausted
        """
        today = datetime.now().strftime('%Y-%m-%d')
        tracking = self._load_quota_tracking()

        if today not in tracking:
            tracking[today] = {}

        tracking[today][str(account_number)] = {
            "exhausted": True,
            "exhausted_at": datetime.now().isoformat()
        }

        self._save_quota_tracking(tracking)
        logger.warning(f"Account {account_number} marked as quota exhausted for {today}")

    def _is_account_available(self, account_number):
        """
        Check if account has quota available today

        Args:
            account_number: Account to check

        Returns:
            bool: True if account has quota available
        """
        today = datetime.now().strftime('%Y-%m-%d')
        tracking = self._load_quota_tracking()

        if today not in tracking:
            return True

        if str(account_number) not in tracking[today]:
            return True

        return not tracking[today][str(account_number)].get("exhausted", False)

    def upload_video(self, video_file, metadata, max_retries=None):
        """
        Upload video using round-robin account selection

        Args:
            video_file: Path to video file
            metadata: Video metadata (title, description, tags, etc.)
            max_retries: Maximum accounts to try (default: all available)

        Returns:
            str: Video ID if successful, None if all accounts exhausted
        """
        if max_retries is None:
            max_retries = len(self.available_accounts)

        if not self.available_accounts:
            logger.error("No authenticated accounts available")
            return None

        logger.info(f"Attempting upload with {len(self.available_accounts)} accounts available")

        attempts = 0
        for account_num in self.available_accounts:
            # Skip if already exhausted today
            if not self._is_account_available(account_num):
                logger.info(f"Account {account_num} already exhausted today, skipping")
                continue

            attempts += 1
            if attempts > max_retries:
                logger.warning(f"Max retries ({max_retries}) reached")
                break

            logger.info(f"Attempting upload with account {account_num} (attempt {attempts}/{max_retries})")

            try:
                uploader = YouTubeUploader(
                    credentials_dir=self.credentials_dir,
                    token_dir=self.token_dir
                )

                result = uploader.upload_video(
                    video_file=video_file,
                    metadata=metadata,
                    account_number=account_num
                )

                # Extract video_id from dict response
                video_id = result.get('video_id') if isinstance(result, dict) else result

                if video_id:
                    logger.info(f"✅ Upload successful with account {account_num}")
                    logger.info(f"   Video ID: {video_id}")
                    logger.info(f"   URL: https://www.youtube.com/watch?v={video_id}")
                    return video_id
                else:
                    logger.warning(f"Upload returned no video ID for account {account_num}")

            except Exception as e:
                error_message = str(e)

                # Check if it's a quota error
                if "uploadLimitExceeded" in error_message or "quota" in error_message.lower():
                    logger.warning(f"Account {account_num} quota exhausted: {error_message}")
                    self._mark_account_exhausted(account_num)
                    # Continue to next account
                    continue
                else:
                    logger.error(f"Upload error with account {account_num}: {error_message}")
                    # For non-quota errors, might want to retry same account or move to next
                    # For now, continue to next account
                    continue

        # All accounts exhausted
        logger.error("❌ All accounts exhausted. No more quota available today.")
        logger.info("💡 Quotas reset at midnight PST. Try again tomorrow.")

        return None

    def get_available_quota_estimate(self):
        """
        Estimate how many more videos can be uploaded today

        Returns:
            dict: Quota estimates
        """
        available_count = sum(1 for acc in self.available_accounts if self._is_account_available(acc))

        return {
            "total_accounts": len(self.available_accounts),
            "available_accounts": available_count,
            "exhausted_accounts": len(self.available_accounts) - available_count,
            "estimated_min_capacity": available_count * 6,  # Conservative estimate
            "estimated_max_capacity": available_count * 10,  # Optimistic estimate
            "accounts_status": {
                acc: "available" if self._is_account_available(acc) else "exhausted"
                for acc in self.available_accounts
            }
        }

if __name__ == "__main__":
    # Test round-robin uploader
    uploader = RoundRobinYouTubeUploader()

    quota_info = uploader.get_available_quota_estimate()

    print("\n" + "="*80)
    print("ROUND-ROBIN UPLOADER STATUS")
    print("="*80)
    print(f"Total Accounts: {quota_info['total_accounts']}")
    print(f"Available Today: {quota_info['available_accounts']}")
    print(f"Exhausted Today: {quota_info['exhausted_accounts']}")
    print(f"\nEstimated Capacity Today: {quota_info['estimated_min_capacity']}-{quota_info['estimated_max_capacity']} videos")
    print(f"\nAccount Status:")
    for acc, status in quota_info['accounts_status'].items():
        status_emoji = "✅" if status == "available" else "❌"
        print(f"  {status_emoji} Account {acc}: {status}")
    print("="*80 + "\n")
