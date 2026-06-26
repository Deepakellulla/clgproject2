"""
Advanced Telegram Group DM Userbot with:
- Activity-based filtering (only DM active users)
- Auto-restriction detection via @Spambot
- Multi-account support
- MongoDB integration
- Auto-pause/resume on restrictions
"""

from telethon.sessions import StringSession
from mongodb_manager import MongoDBManager
import asyncio
import logging
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import PeerFloodError, FloodWaitError, PeerIdInvalidError
import re

# Load environment variables
load_dotenv()

# Configuration
ACCOUNT_ID = os.getenv('ACCOUNT_ID', 'default_account')
ACCOUNT_NUMBER = os.getenv('ACCOUNT_NUMBER', '1')
GROUP_ID = int(os.getenv('GROUP_ID'))
MONGODB_URL = os.getenv('MONGODB_URL')
SESSION_STRING = os.getenv('SESSION_STRING')
DM_INTERVAL = int(os.getenv('DM_INTERVAL', 300))
RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', 300))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
MIN_ACTIVITY = int(os.getenv('MIN_ACTIVITY', 1))  # Minimum messages in group

# Get API credentials based on ACCOUNT_NUMBER
API_ID_KEY = f'API_ID_{ACCOUNT_NUMBER}'
API_HASH_KEY = f'API_HASH_{ACCOUNT_NUMBER}'

API_ID = os.getenv(API_ID_KEY) or os.getenv('API_ID')
API_HASH = os.getenv(API_HASH_KEY) or os.getenv('API_HASH')

if API_ID:
    API_ID = int(API_ID)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('userbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AdvancedTelegramUserbot:
    """Advanced userbot with activity filtering and restriction detection"""
    
    def __init__(self):
        """Initialize userbot"""
        
        # Validate credentials
        if not API_ID or not API_HASH or not SESSION_STRING:
            logger.error("❌ Missing API_ID, API_HASH, or SESSION_STRING!")
            raise ValueError("Missing required credentials")
        
        if not MONGODB_URL:
            logger.error("❌ MONGODB_URL not set!")
            raise ValueError("MONGODB_URL required")
        
        # Initialize Telegram client
        self.client = TelegramClient(
            StringSession(SESSION_STRING),
            API_ID,
            API_HASH
        )
        
        # Initialize MongoDB
        self.db = MongoDBManager(MONGODB_URL)
        
        # Configuration
        self.account_id = ACCOUNT_ID
        self.account_number = ACCOUNT_NUMBER
        self.group_id = GROUP_ID
        self.dm_interval = DM_INTERVAL
        self.rate_limit_delay = RATE_LIMIT_DELAY
        self.max_retries = MAX_RETRIES
        self.min_activity = MIN_ACTIVITY
        
        # State
        self.is_running = False
        self.is_restricted = False
        self.restriction_until = None
        self.dms_sent_this_session = 0
        self.active_users_cache = {}
        
        # Register account
        self._register_account()

    def _register_account(self):
        """Register account in MongoDB"""
        try:
            self.db.register_account(
                account_id=self.account_id,
                phone_number=f"Account {self.account_number}",
                group_ids=[self.group_id]
            )
            logger.info(f"✅ Account '{self.account_id}' (#{self.account_number}) registered")
        except Exception as e:
            logger.warning(f"Account registration: {e}")

    async def start(self):
        """Start the userbot"""
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                logger.error("❌ Invalid SESSION_STRING")
                return
            
            logger.info("✅ Userbot started successfully")
            me = await self.client.get_me()
            logger.info(f"Logged in as: {me.first_name} (@{me.username})")
            logger.info(f"Account #{self.account_number} | ACCOUNT_ID: {self.account_id}")
            
            self.is_running = True
            await self.main_loop()
        except Exception as e:
            logger.error(f"❌ Failed to start userbot: {e}")

    async def stop(self):
        """Stop the userbot gracefully"""
        self.is_running = False
        await self.client.disconnect()
        logger.info("✅ Userbot stopped")

    async def check_account_restriction(self) -> Tuple[bool, Optional[datetime]]:
        """
        Check if account is restricted using @Spambot
        1. Send /start command to @Spambot
        2. Wait for Spambot reply
        3. Parse reply to check if restricted
        4. Extract restriction date and time
        Returns: (is_restricted, restriction_until_datetime)
        """
        try:
            logger.info("=" * 70)
            logger.info("🔍 CHECKING ACCOUNT RESTRICTION STATUS WITH @SPAMBOT")
            logger.info("=" * 70)
            
            # Step 1: Send /start command to Spambot
            logger.info("📤 Sending /start command to @Spambot...")
            await self.client.send_message('@Spambot', '/start')
            
            # Step 2: Wait for Spambot to reply
            logger.info("⏳ Waiting for @Spambot response (waiting 4 seconds)...")
            await asyncio.sleep(4)
            
            # Step 3: Get Spambot's response
            logger.info("📥 Fetching @Spambot messages...")
            messages = await self.client.get_messages('@Spambot', limit=10)
            
            if not messages:
                logger.warning("⚠️ No messages from @Spambot")
                logger.info("✅ Account is NOT RESTRICTED (or Spambot didn't reply)")
                logger.info("=" * 70)
                return False, None
            
            # Get the most recent message from Spambot
            latest_message = messages[0]
            message_text = latest_message.text or ""
            
            logger.info("=" * 70)
            logger.info("📋 SPAMBOT RESPONSE:")
            logger.info("=" * 70)
            logger.info(message_text)
            logger.info("=" * 70)
            
            # Step 4: Analyze the response
            message_lower = message_text.lower()
            
            # Check for RESTRICTED keywords
            restricted_keywords = ["restricted", "banned", "limited", "suspension", "blocked"]
            is_restricted_detected = any(keyword in message_lower for keyword in restricted_keywords)
            
            # Check for NOT RESTRICTED keywords
            not_restricted_keywords = ["not restricted", "no restrictions", "clean", "ok", "green"]
            is_not_restricted_detected = any(keyword in message_lower for keyword in not_restricted_keywords)
            
            if is_restricted_detected and not is_not_restricted_detected:
                logger.warning("=" * 70)
                logger.warning("⚠️  ACCOUNT IS RESTRICTED!")
                logger.warning("=" * 70)
                
                # Try to extract restriction date and time from Spambot's message
                restriction_until = self._parse_restriction_date(message_text)
                
                if restriction_until:
                    wait_seconds = (restriction_until - datetime.utcnow()).total_seconds()
                    wait_hours = wait_seconds / 3600
                    wait_days = wait_hours / 24
                    
                    logger.warning(f"📅 Restriction END DATE & TIME (UTC): {restriction_until}")
                    logger.warning(f"⏱️  WAIT TIME: {wait_days:.1f} days, {wait_hours:.1f} hours, {wait_seconds:.0f} seconds")
                    logger.warning("=" * 70)
                    return True, restriction_until
                else:
                    logger.warning("⏰ Could not extract exact restriction date/time from Spambot message")
                    logger.warning("=" * 70)
                    return True, None
            
            else:
                logger.info("=" * 70)
                logger.info("✅ ACCOUNT IS CLEAN - NOT RESTRICTED")
                logger.info("=" * 70)
                return False, None
            
        except Exception as e:
            logger.error("=" * 70)
            logger.error(f"❌ ERROR checking restriction: {e}")
            logger.error("=" * 70)
            logger.warning("Assuming account is NOT restricted and proceeding...")
            return False, None

    def _parse_restriction_date(self, message_text: str) -> Optional[datetime]:
        """
        Parse restriction date and time from Spambot's message in UTC format
        Tries multiple date formats and handles UTC timezone
        Returns: datetime in UTC (naive datetime object treating it as UTC)
        """
        logger.info("🔎 Parsing restriction date/time from Spambot response (UTC format)...")
        logger.info("📝 @Spambot message content:")
        for line in message_text.split('\n'):
            if line.strip():
                logger.info(f"   {line}")
        
        # Pattern 1: YYYY-MM-DD HH:MM:SS UTC/GMT
        pattern1 = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*(?:UTC|GMT)?'
        match = re.search(pattern1, message_text)
        if match:
            time_str = match.group(1)
            try:
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                logger.info(f"✅ Parsed date (format 1 - UTC): {dt} UTC")
                return dt
            except Exception as e:
                logger.debug(f"Format 1 failed: {e}")
        
        # Pattern 2: YYYY-MM-DD HH:MM UTC/GMT
        pattern2 = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s*(?:UTC|GMT)?'
        match = re.search(pattern2, message_text)
        if match:
            time_str = match.group(1)
            try:
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                logger.info(f"✅ Parsed date (format 2 - UTC): {dt} UTC")
                return dt
            except Exception as e:
                logger.debug(f"Format 2 failed: {e}")
        
        # Pattern 3: DD.MM.YYYY HH:MM:SS UTC/GMT (European format)
        pattern3 = r'(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})\s*(?:UTC|GMT)?'
        match = re.search(pattern3, message_text)
        if match:
            time_str = match.group(1)
            try:
                dt = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S")
                logger.info(f"✅ Parsed date (format 3 - UTC): {dt} UTC")
                return dt
            except Exception as e:
                logger.debug(f"Format 3 failed: {e}")
        
        # Pattern 4: DD.MM.YYYY HH:MM UTC/GMT (European format, no seconds)
        pattern4 = r'(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2})\s*(?:UTC|GMT)?'
        match = re.search(pattern4, message_text)
        if match:
            time_str = match.group(1)
            try:
                dt = datetime.strptime(time_str, "%d.%m.%Y %H:%M")
                logger.info(f"✅ Parsed date (format 4 - UTC): {dt} UTC")
                return dt
            except Exception as e:
                logger.debug(f"Format 4 failed: {e}")
        
        # Pattern 5: January 15, 2024 14:30 UTC or similar (Month Name format)
        pattern5 = r'([A-Za-z]+\s+\d{1,2},?\s+\d{4}\s+\d{1,2}:\d{2})\s*(?:UTC|GMT)?'
        match = re.search(pattern5, message_text)
        if match:
            time_str = match.group(1)
            try:
                dt = datetime.strptime(time_str, "%B %d, %Y %H:%M")
                logger.info(f"✅ Parsed date (format 5 - UTC): {dt} UTC")
                return dt
            except Exception as e:
                logger.debug(f"Format 5a failed: {e}")
                try:
                    dt = datetime.strptime(time_str, "%B %d %Y %H:%M")
                    logger.info(f"✅ Parsed date (format 5b - UTC): {dt} UTC")
                    return dt
                except Exception as e2:
                    logger.debug(f"Format 5b failed: {e2}")
        
        # Pattern 6: 2024-01-15T14:30:00Z (ISO format with Z for UTC)
        pattern6 = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z'
        match = re.search(pattern6, message_text)
        if match:
            time_str = match.group(1)
            try:
                dt = datetime.fromisoformat(time_str)
                logger.info(f"✅ Parsed date (format 6 - ISO UTC Z): {dt} UTC")
                return dt
            except Exception as e:
                logger.debug(f"Format 6 failed: {e}")
        
        # Pattern 7: 2024-01-15T14:30:00 UTC (ISO format)
        pattern7 = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s*(?:UTC|GMT)?'
        match = re.search(pattern7, message_text)
        if match:
            time_str = match.group(1)
            try:
                dt = datetime.fromisoformat(time_str)
                logger.info(f"✅ Parsed date (format 7 - ISO UTC): {dt} UTC")
                return dt
            except Exception as e:
                logger.debug(f"Format 7 failed: {e}")
        
        logger.warning("❌ Could not extract restriction date/time - no recognized pattern found")
        logger.warning(f"📝 Full message: {message_text}")
        return None

    async def handle_restriction(self):
        """Handle account restriction - pause until restriction ends (UTC time)"""
        self.is_restricted = True
        
        if self.restriction_until:
            # Use UTC time for comparison since Spambot gives UTC times
            wait_time = (self.restriction_until - datetime.utcnow()).total_seconds()
            if wait_time > 0:
                hours = wait_time / 3600
                days = hours / 24
                logger.warning("=" * 70)
                logger.warning("⏸️  ACCOUNT IS RESTRICTED")
                logger.warning(f"📅 Restriction END (UTC): {self.restriction_until}")
                logger.warning(f"⏱️  WAIT TIME: {days:.1f} days, {hours:.1f} hours, {wait_time:.0f} seconds")
                logger.warning("🤖 Bot is PAUSED - Will resume automatically when restriction ends")
                logger.warning("=" * 70)
                
                # Wait until restriction ends
                await asyncio.sleep(wait_time + 60)  # +1 min buffer for safety
                
                logger.warning("=" * 70)
                logger.info("✅ RESTRICTION PERIOD ENDED - RESUMING BOT NOW")
                logger.warning("=" * 70)
                self.is_restricted = False
                self.restriction_until = None
            else:
                logger.info("✅ Restriction time already passed, resuming immediately...")
                self.is_restricted = False
                self.restriction_until = None
        else:
            # If we can't extract exact time, pause for 24 hours and check again
            logger.warning("=" * 70)
            logger.warning("⏸️  ACCOUNT IS RESTRICTED (END TIME NOT FOUND)")
            logger.warning("⏸️  Pausing bot for 24 hours, will check again...")
            logger.warning("=" * 70)
            
            await asyncio.sleep(86400)  # Wait 24 hours
            
            logger.info("⏱️  24 hours passed. Checking restriction status again...")
            self.is_restricted = False

    async def get_group_members(self) -> List[int]:
        """Get all members from the group"""
        try:
            members = []
            async for member in self.client.iter_participants(self.group_id):
                members.append(member.id)
            logger.info(f"Found {len(members)} total members in group")
            return members
        except Exception as e:
            logger.error(f"Error getting group members: {e}")
            return []

    async def get_active_users(self) -> Dict[int, int]:
        """
        Get users who have messaged in the group
        Returns: {user_id: message_count}
        """
        try:
            logger.info("📊 Fetching active users (who posted in group)...")
            
            active_users = {}
            
            # Get all messages in group (last 1000)
            async for message in self.client.iter_messages(self.group_id, limit=1000):
                if message.sender_id:
                    active_users[message.sender_id] = active_users.get(message.sender_id, 0) + 1
            
            logger.info(f"📊 Found {len(active_users)} active users in group")
            
            # Cache for later use
            self.active_users_cache = active_users
            
            return active_users
            
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return {}

    async def is_user_active(self, user_id: int) -> bool:
        """Check if user has posted in group (at least MIN_ACTIVITY times)"""
        if not self.active_users_cache:
            await self.get_active_users()
        
        message_count = self.active_users_cache.get(user_id, 0)
        is_active = message_count >= self.min_activity
        
        if not is_active:
            logger.debug(f"User {user_id} not active (posted {message_count} times)")
        
        return is_active

    async def is_bot(self, user_id: int) -> bool:
        """Check if user is a bot"""
        try:
            user = await self.client.get_entity(user_id)
            return user.bot
        except Exception as e:
            logger.debug(f"Error checking if user {user_id} is bot: {e}")
            return False

    async def is_admin(self, user_id: int) -> bool:
        """Check if user is admin in the group"""
        try:
            participant = await self.client.get_permissions(self.group_id, user_id)
            return participant.is_admin or participant.is_creator
        except Exception as e:
            logger.debug(f"Error checking admin status for {user_id}: {e}")
            return False

    async def should_skip_user(self, user_id: int) -> bool:
        """Check if user should be skipped"""
        
        # Check global database
        if self.db.check_user_exists(user_id):
            logger.debug(f"User {user_id} already DMed globally")
            return True
        
        # Check if user is bot
        if await self.is_bot(user_id):
            logger.debug(f"Skipping bot: {user_id}")
            return True
        
        # Check if user is admin
        if await self.is_admin(user_id):
            logger.debug(f"Skipping admin: {user_id}")
            return True
        
        # ✅ NEW: Check if user is active in group
        if not await self.is_user_active(user_id):
            logger.debug(f"Skipping inactive user: {user_id}")
            return True
        
        return False

    async def send_dm_with_retry(self, user_id: int, message: str) -> bool:
        """Send DM to user with retry logic"""
        for attempt in range(self.max_retries):
            try:
                await self.client.send_message(user_id, message, parse_mode='html')
                logger.info(f"✅ DM sent to {user_id}")
                
                # Save to MongoDB
                self.db.save_dm(
                    user_id=user_id,
                    account_id=self.account_id,
                    group_id=self.group_id,
                    message=message,
                    status='sent'
                )
                
                # Add to global database
                user = await self.client.get_entity(user_id)
                self.db.add_user(
                    user_id=user_id,
                    username=user.username,
                    first_name=user.first_name
                )
                
                return True
                
            except FloodWaitError as e:
                logger.warning(f"⚠️ Flood wait: {e.seconds}s")
                await asyncio.sleep(e.seconds)
            except PeerFloodError:
                logger.warning(f"❌ Peer flood error for {user_id}")
                self.db.save_dm(
                    user_id=user_id,
                    account_id=self.account_id,
                    group_id=self.group_id,
                    message=message,
                    status='failed'
                )
                return False
            except PeerIdInvalidError:
                logger.warning(f"❌ Invalid peer ID: {user_id}")
                return False
            except Exception as e:
                logger.error(f"Error sending DM to {user_id}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        return False

    async def broadcast_dm(self, message: str, active_users: Dict[int, int] = None):
        """Send DM only to active users"""
        try:
            # Get all members
            members = await self.get_group_members()
            
            # Get active users if not provided
            if not active_users:
                active_users = await self.get_active_users()
            
            successful = 0
            failed = 0
            skipped = 0
            inactive = 0
            
            logger.info(f"🚀 Starting broadcast (only to {len(active_users)} active users)")
            
            for user_id in members:
                # Skip inactive users
                if user_id not in active_users:
                    inactive += 1
                    continue
                
                # Skip if should skip
                if await self.should_skip_user(user_id):
                    skipped += 1
                    continue
                
                # Send DM
                if await self.send_dm_with_retry(user_id, message):
                    successful += 1
                else:
                    failed += 1
                
                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)
            
            logger.info(f"📊 Broadcast completed:")
            logger.info(f"   Sent: {successful}, Failed: {failed}, Skipped: {skipped}, Inactive: {inactive}")
            
            # Save analytics
            self.db.save_broadcast_analytics(
                account_id=self.account_id,
                group_id=self.group_id,
                sent=successful,
                failed=failed,
                skipped=skipped + inactive
            )
            
            self.dms_sent_this_session += successful
            
        except Exception as e:
            logger.error(f"Error during broadcast: {e}")

    async def main_loop(self):
        """Main bot loop with restriction checking"""
        logger.info("🔄 Starting main loop")
        custom_message = self.load_custom_message()
        
        logger.info("📋 === STARTUP CHECK ===")
        # Check restriction on startup
        is_restricted, restriction_until = await self.check_account_restriction()
        if is_restricted:
            logger.warning(f"⚠️  Account RESTRICTED on startup")
            self.is_restricted = True
            self.restriction_until = restriction_until
            await self.handle_restriction()
        else:
            logger.info("✅ Account is ACTIVE on startup")
        
        # Main broadcast loop
        while self.is_running:
            try:
                # Check for restrictions every cycle
                if not self.is_restricted:
                    logger.info("📋 === RESTRICTION CHECK ===")
                    is_restricted, restriction_until = await self.check_account_restriction()
                    
                    if is_restricted:
                        logger.warning(f"⚠️  Account became RESTRICTED during operation")
                        self.is_restricted = True
                        self.restriction_until = restriction_until
                        await self.handle_restriction()
                        continue
                    else:
                        logger.info("✅ Account is ACTIVE - Proceeding with broadcast")
                
                # Skip if restricted
                if self.is_restricted:
                    logger.warning("⏸️  Account is RESTRICTED - Skipping broadcast")
                    logger.info(f"⏳ Checking again in 5 minutes...")
                    await asyncio.sleep(300)  # Check every 5 minutes
                    continue
                
                # Get active users and broadcast
                active_users = await self.get_active_users()
                await self.broadcast_dm(custom_message, active_users)
                
                logger.info(f"⏰ Next broadcast in {self.dm_interval}s")
                await asyncio.sleep(self.dm_interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(10)

    def load_custom_message(self) -> str:
        """Load custom message from file"""
        try:
            if os.path.exists('message.txt'):
                with open('message.txt', 'r', encoding='utf-8') as f:
                    message = f.read().strip()
                    logger.info(f"Loaded custom message ({len(message)} chars)")
                    return message
        except Exception as e:
            logger.error(f"Error loading message: {e}")
        
        return "👋 Hey! Check out my business 🚀\nWould love to connect with you!"


async def main():
    """Main entry point"""
    userbot = AdvancedTelegramUserbot()
    
    try:
        await userbot.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        await userbot.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await userbot.stop()


if __name__ == "__main__":
    asyncio.run(main())
