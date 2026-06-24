"""
Telegram Group DM Userbot
Automatically sends DMs to group members for business promotion
Features:
- Skip bots and admins
- Custom message templates
- Rate limiting and delays
- Logging and error handling
- Persistent state management
"""
from telethon.sessions import StringSession
import asyncio
import logging
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Set
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import UserStatusOnline, UserStatusOffline
from telethon.errors import PeerFloodError, FloodWaitError, PeerIdInvalidError
import aiofiles

# Load environment variables
load_dotenv()

# Configuration
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
GROUP_ID = int(os.getenv('GROUP_ID'))
DM_INTERVAL = int(os.getenv('DM_INTERVAL', 300))  # 5 minutes default
RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', 2))  # seconds between DMs
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))

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

class TelegramUserbot:
    def __init__(self):
        SESSION_STRING = os.getenv("SESSION_STRING")

        self.client = TelegramClient(
            StringSession(SESSION_STRING),
            API_ID,
            API_HASH
        )
        self.group_id = GROUP_ID
        self.dm_interval = DM_INTERVAL
        self.rate_limit_delay = RATE_LIMIT_DELAY
        self.max_retries = MAX_RETRIES
        
        # State management
        self.dm_history: Dict[int, datetime] = {}
        self.user_blacklist: Set[int] = set()
        self.user_whitelist: Set[int] = set()
        self.is_running = False
        self.last_error_message = ""
        
        # Load persistent state
        self.state_file = 'bot_state.json'
        self.load_state()

    def load_state(self):
        """Load persistent state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.user_blacklist = set(state.get('blacklist', []))
                    self.user_whitelist = set(state.get('whitelist', []))
                    logger.info(f"Loaded state: {len(self.user_blacklist)} blacklisted users")
        except Exception as e:
            logger.error(f"Error loading state: {e}")

    def save_state(self):
        """Save persistent state to file"""
        try:
            state = {
                'blacklist': list(self.user_blacklist),
                'whitelist': list(self.user_whitelist),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info("State saved successfully")
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    async def start(self):
        """Start the userbot"""
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                logger.error("Invalid session string")
                return
            logger.info("✅ Userbot started successfully")
            me = await self.client.get_me()
            logger.info(f"Logged in as: {me.first_name} (@{me.username})")
            
            # Register event handlers
            self.client.on(events.NewMessage(chats=GROUP_ID))(self.handle_group_message)
            
            self.is_running = True
            await self.main_loop()
        except Exception as e:
            logger.error(f"❌ Failed to start userbot: {e}")
            self.last_error_message = str(e)

    async def stop(self):
        """Stop the userbot gracefully"""
        self.is_running = False
        self.save_state()
        await self.client.disconnect()
        logger.info("✅ Userbot stopped")

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
        if user_id in self.user_blacklist:
            return True
        if user_id in self.user_whitelist:
            return False
        
        # Check bot status
        if await self.is_bot(user_id):
            logger.debug(f"Skipping bot: {user_id}")
            return True
        
        # Check admin status
        if await self.is_admin(user_id):
            logger.debug(f"Skipping admin: {user_id}")
            return True
        
        return False

    async def send_dm_with_retry(self, user_id: int, message: str) -> bool:
        """Send DM to user with retry logic"""
        for attempt in range(self.max_retries):
            try:
                await self.client.send_message(user_id, message, parse_mode='html')
                logger.info(f"✅ DM sent to {user_id}")
                self.dm_history[user_id] = datetime.now()
                return True
            except FloodWaitError as e:
                logger.warning(f"⚠️ Flood wait: {e.seconds}s - waiting...")
                await asyncio.sleep(e.seconds)
            except PeerFloodError:
                logger.warning(f"❌ Peer flood error for {user_id} - adding to blacklist")
                self.user_blacklist.add(user_id)
                self.save_state()
                return False
            except PeerIdInvalidError:
                logger.warning(f"❌ Invalid peer ID: {user_id}")
                self.user_blacklist.add(user_id)
                return False
            except Exception as e:
                logger.error(f"Error sending DM to {user_id} (attempt {attempt+1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False

    async def broadcast_dm(self, message: str, include_list: List[int] = None):
        """Send DM to members who haven't received one recently"""
        try:
            members = include_list or await self.get_group_members()
            successful = 0
            failed = 0
            skipped = 0
            
            logger.info(f"🚀 Starting broadcast to {len(members)} members")
            
            for user_id in members:
                # Check if we should skip this user
                if await self.should_skip_user(user_id):
                    skipped += 1
                    continue
                
                # Check if already DMed recently
                if user_id in self.dm_history:
                    last_dm = self.dm_history[user_id]
                    if datetime.now() - last_dm < timedelta(seconds=self.dm_interval):
                        continue
                
                # Send DM
                # Send DM
                if await self.send_dm_with_retry(user_id, message):
                    successful += 1
                else:
                    failed += 1
                
                # Rate limiting - KEEP THIS!
                await asyncio.sleep(self.rate_limit_delay)
                
                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)
            
            logger.info(f"📊 Broadcast completed - Sent: {successful}, Failed: {failed}, Skipped: {skipped}")
            
        except Exception as e:
            logger.error(f"Error during broadcast: {e}")

    async def main_loop(self):
        """Main bot loop"""
        logger.info("🔄 Starting main loop")
        
        # Load custom message from file if exists
        custom_message = self.load_custom_message()
        
        while self.is_running:
            try:
                await self.broadcast_dm(custom_message)
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
        
        # Default message
        return "👋 Hey! Check out my business 🚀\nWould love to connect with you!"

    async def handle_group_message(self, event):
        """Handle messages in the group"""
        try:
            # You can add handlers for group commands here
            if event.message.text.startswith('!reload'):
                logger.info("Reloading custom message...")
                message = self.load_custom_message()
                await event.reply("✅ Message reloaded!")
        except Exception as e:
            logger.error(f"Error handling group message: {e}")

    async def get_stats(self) -> Dict:
        """Get bot statistics"""
        return {
            'is_running': self.is_running,
            'total_dmed': len(self.dm_history),
            'blacklisted_users': len(self.user_blacklist),
            'whitelisted_users': len(self.user_whitelist),
            'last_error': self.last_error_message
        }


async def main():
    """Main entry point"""
    userbot = TelegramUserbot()
    
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
