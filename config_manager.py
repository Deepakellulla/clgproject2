"""
Advanced Configuration Manager
Handles complex settings and feature flags
"""

import json
import logging
from typing import Any, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manage advanced configuration options"""
    
    DEFAULT_CONFIG = {
        "features": {
            "enable_logging": True,
            "enable_state_persistence": True,
            "enable_statistics": True,
            "enable_user_feedback": False,
            "enable_scheduled_broadcasts": False
        },
        "message_templates": {
            "default": "👋 Hey! Check out my business 🚀",
            "followup": "Just wanted to follow up! 😊",
            "special_offer": "🎉 Special offer just for you!",
            "custom": ""
        },
        "broadcast_settings": {
            "max_retries": 3,
            "retry_delay": 2,
            "timeout_seconds": 30,
            "batch_size": 50,
            "batch_delay": 60
        },
        "safety_features": {
            "skip_new_accounts": False,
            "new_account_days": 30,
            "skip_inactive_users": False,
            "inactive_days": 90,
            "max_dms_per_user": 10,
            "min_interval_between_dms": 300,
            "auto_unblock_days": 7,
            "enable_captcha_detection": True
        },
        "filters": {
            "skip_bots": True,
            "skip_admins": True,
            "skip_verified": False,
            "skip_no_profile_pic": False,
            "min_username_length": 3,
            "include_only_usernames": []
        },
        "scheduling": {
            "enabled": False,
            "broadcast_times": ["09:00", "14:00", "20:00"],
            "timezone": "UTC",
            "days_of_week": [0, 1, 2, 3, 4, 5, 6]
        },
        "notifications": {
            "webhook_enabled": False,
            "webhook_url": "",
            "notify_on_error": True,
            "notify_on_success": False,
            "summary_interval": 3600
        },
        "analytics": {
            "track_open_rates": False,
            "track_responses": False,
            "export_interval": 86400,
            "export_format": "json"
        }
    }

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
                # Merge with defaults to ensure all keys exist
                return self._merge_configs(self.DEFAULT_CONFIG, config)
            else:
                logger.info("Using default configuration")
                return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"Error loading config: {e}. Using defaults.")
            return self.DEFAULT_CONFIG.copy()

    def _merge_configs(self, defaults: Dict, custom: Dict) -> Dict:
        """Recursively merge custom config with defaults"""
        result = defaults.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get config value using dot notation (e.g., 'features.enable_logging')"""
        keys = key_path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any):
        """Set config value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        logger.info(f"Configuration updated: {key_path} = {value}")

    def get_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self.get(f"features.{feature}", False)

    def get_message_template(self, template_name: str) -> str:
        """Get a message template"""
        return self.get(f"message_templates.{template_name}", "")

    def get_safety_setting(self, setting: str) -> Any:
        """Get a safety setting"""
        return self.get(f"safety_features.{setting}")

    def get_filters(self) -> Dict[str, Any]:
        """Get all active filters"""
        return self.get("filters", {})

    def export_summary(self) -> Dict[str, Any]:
        """Export a summary of important settings"""
        return {
            "enabled_features": [k for k, v in self.get("features", {}).items() if v],
            "safety_settings": self.get("safety_features", {}),
            "broadcast_settings": self.get("broadcast_settings", {}),
            "filters": self.get("filters", {})
        }


# Create example config file template
def create_example_config():
    """Create an example config.json file"""
    config = ConfigManager.DEFAULT_CONFIG
    try:
        with open("config.example.json", 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Created config.example.json")
    except Exception as e:
        print(f"❌ Error creating example config: {e}")


if __name__ == "__main__":
    # Create example config
    create_example_config()
    
    # Test configuration
    config = ConfigManager()
    print("\n📋 Current Configuration:")
    print(json.dumps(config.export_summary(), indent=2))
