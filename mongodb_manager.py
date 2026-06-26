"""
MongoDB Manager for Telegram Userbot
Handles all database operations for:
- Global user tracking (never re-DM across all groups/accounts)
- Multiple account management
- DM history and analytics
- User engagement tracking
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime, timedelta
import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MongoDBManager:
    """Handle all MongoDB operations"""
    
    def __init__(self, mongo_url: str):
        """
        Initialize MongoDB connection
        
        Args:
            mongo_url: MongoDB connection string
                       e.g., "mongodb+srv://user:pass@cluster.mongodb.net/telegrambot"
        """
        try:
            self.client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client['telegrambot']
            logger.info("✅ Connected to MongoDB")
            self._create_indexes()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise

    def _create_indexes(self):
        """Create database indexes for faster queries"""
        try:
            # Users collection indexes
            self.db.users.create_index('user_id', unique=False)
            self.db.users.create_index('email', sparse=True)
            self.db.users.create_index('phone', sparse=True)
            
            # DM history indexes
            self.db.dm_history.create_index([('user_id', 1), ('account_id', 1)])
            self.db.dm_history.create_index('timestamp')
            self.db.dm_history.create_index('group_id')
            
            # Accounts indexes
            self.db.accounts.create_index('account_id', unique=True)
            self.db.accounts.create_index('phone_number', unique=True)
            
            # Analytics indexes
            self.db.analytics.create_index('date')
            self.db.analytics.create_index('account_id')
            
            logger.info("✅ Database indexes created")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    # ==================== USER MANAGEMENT ====================
    
    def check_user_exists(self, user_id: int) -> bool:
        """Check if user was ever DMed (across ALL accounts and groups)"""
        result = self.db.users.find_one({'user_id': user_id})
        return result is not None

    def add_user(self, user_id: int, username: str = None, first_name: str = None) -> bool:
        """Add user to global database (one time only)"""
        try:
            existing = self.db.users.find_one({'user_id': user_id})
            
            if existing:
                logger.debug(f"User {user_id} already exists in database")
                return False
            
            user_doc = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'created_at': datetime.now(),
                'total_dms_received': 0,
                'replied': False,
                'last_dm_from_account': None,
                'interest_level': 'unknown'
            }
            
            self.db.users.insert_one(user_doc)
            logger.info(f"✅ Added user {user_id} to global database")
            return True
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data from database"""
        try:
            return self.db.users.find_one({'user_id': user_id})
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None

    def update_user_engagement(self, user_id: int, replied: bool = False, 
                               interest_level: str = 'unknown'):
        """Update user engagement status"""
        try:
            self.db.users.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'replied': replied,
                        'interest_level': interest_level,
                        'last_updated': datetime.now()
                    }
                }
            )
            logger.info(f"Updated user {user_id} engagement")
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")

    # ==================== DM HISTORY ====================
    
    def save_dm(self, user_id: int, account_id: str, group_id: int, 
                message: str, status: str = 'sent'):
        """Save DM to history (global tracking)"""
        try:
            dm_doc = {
                'user_id': user_id,
                'account_id': account_id,
                'group_id': group_id,
                'message': message,
                'status': status,  # sent, failed, bounced
                'timestamp': datetime.now()
            }
            
            result = self.db.dm_history.insert_one(dm_doc)
            
            # Update user's total DM count
            self.db.users.update_one(
                {'user_id': user_id},
                {'$inc': {'total_dms_received': 1}}
            )
            
            logger.debug(f"Saved DM to user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving DM: {e}")
            return False

    def get_user_dm_count(self, user_id: int) -> int:
        """Get how many times user was DMed (across all accounts)"""
        try:
            count = self.db.dm_history.count_documents({'user_id': user_id})
            return count
        except Exception as e:
            logger.error(f"Error getting DM count: {e}")
            return 0

    def get_user_dm_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get all DMs sent to this user"""
        try:
            return list(self.db.dm_history.find({'user_id': user_id})
                       .sort('timestamp', -1).limit(limit))
        except Exception as e:
            logger.error(f"Error getting DM history: {e}")
            return []

    # ==================== ACCOUNT MANAGEMENT ====================
    
    def register_account(self, account_id: str, phone_number: str, 
                        group_ids: List[int] = None) -> bool:
        """Register a new bot account"""
        try:
            existing = self.db.accounts.find_one({'account_id': account_id})
            if existing:
                logger.warning(f"Account {account_id} already registered")
                return False
            
            account_doc = {
                'account_id': account_id,
                'phone_number': phone_number,
                'group_ids': group_ids or [],
                'created_at': datetime.now(),
                'total_dms_sent': 0,
                'is_active': True,
                'last_broadcast': None
            }
            
            self.db.accounts.insert_one(account_doc)
            logger.info(f"✅ Registered account {account_id}")
            return True
        except Exception as e:
            logger.error(f"Error registering account: {e}")
            return False

    def get_account(self, account_id: str) -> Optional[Dict]:
        """Get account details"""
        try:
            return self.db.accounts.find_one({'account_id': account_id})
        except Exception as e:
            logger.error(f"Error getting account: {e}")
            return None

    def get_all_accounts(self) -> List[Dict]:
        """Get all registered accounts"""
        try:
            return list(self.db.accounts.find({'is_active': True}))
        except Exception as e:
            logger.error(f"Error getting accounts: {e}")
            return []

    def update_account_stats(self, account_id: str, dms_sent: int = 0):
        """Update account broadcast statistics"""
        try:
            self.db.accounts.update_one(
                {'account_id': account_id},
                {
                    '$inc': {'total_dms_sent': dms_sent},
                    '$set': {'last_broadcast': datetime.now()}
                }
            )
        except Exception as e:
            logger.error(f"Error updating account stats: {e}")

    # ==================== ANALYTICS ====================
    
    def save_broadcast_analytics(self, account_id: str, group_id: int, 
                                  sent: int, failed: int, skipped: int):
        """Save broadcast statistics"""
        try:
            analytics_doc = {
                'account_id': account_id,
                'group_id': group_id,
                'date': datetime.now().date().isoformat(),
                'sent': sent,
                'failed': failed,
                'skipped': skipped,
                'success_rate': (sent / (sent + failed) * 100) if (sent + failed) > 0 else 0,
                'timestamp': datetime.now()
            }
            
            self.db.analytics.insert_one(analytics_doc)
            logger.info(f"✅ Saved analytics for account {account_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")
            return False

    def get_daily_analytics(self, account_id: str, days: int = 7) -> List[Dict]:
        """Get last N days analytics"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            return list(self.db.analytics.find({
                'account_id': account_id,
                'date': {'$gte': start_date}
            }).sort('date', -1))
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return []

    def get_global_stats(self) -> Dict:
        """Get global statistics across all accounts"""
        try:
            total_users = self.db.users.count_documents({})
            total_dms = self.db.dm_history.count_documents({})
            total_accounts = self.db.accounts.count_documents({'is_active': True})
            
            failed_dms = self.db.dm_history.count_documents({'status': 'failed'})
            success_rate = ((total_dms - failed_dms) / total_dms * 100) if total_dms > 0 else 0
            
            return {
                'total_users_in_database': total_users,
                'total_dms_sent': total_dms,
                'total_accounts': total_accounts,
                'failed_dms': failed_dms,
                'success_rate': f"{success_rate:.1f}%",
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting global stats: {e}")
            return {}

    # ==================== REPORTING ====================
    
    def get_top_users_by_engagement(self, limit: int = 10) -> List[Dict]:
        """Get users who replied or engaged"""
        try:
            return list(self.db.users.find({'replied': True})
                       .sort('last_updated', -1).limit(limit))
        except Exception as e:
            logger.error(f"Error getting engaged users: {e}")
            return []

    def export_all_users(self) -> List[Dict]:
        """Export all users for external analysis"""
        try:
            return list(self.db.users.find({}))
        except Exception as e:
            logger.error(f"Error exporting users: {e}")
            return []

    def cleanup_old_data(self, days: int = 90):
        """Delete DM history older than N days (for storage optimization)"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            result = self.db.dm_history.delete_many({'timestamp': {'$lt': cutoff_date}})
            logger.info(f"Deleted {result.deleted_count} old DM records")
        except Exception as e:
            logger.error(f"Error cleaning up data: {e}")

    def get_health_status(self) -> Dict:
        """Check database health"""
        try:
            self.client.admin.command('ping')
            collections_count = len(self.db.list_collection_names())
            
            return {
                'status': 'healthy',
                'collections': collections_count,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


if __name__ == "__main__":
    # Test MongoDB connection
    mongo_url = os.getenv('MONGODB_URL')
    if mongo_url:
        db = MongoDBManager(mongo_url)
        print("✅ MongoDB connection successful!")
        print(db.get_health_status())
    else:
        print("❌ MONGODB_URL environment variable not set")
