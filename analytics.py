"""
Analytics and Monitoring Module
Track bot performance, DM success rates, and user engagement
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)


class BotAnalytics:
    """Track and analyze bot performance"""
    
    def __init__(self, analytics_file: str = "analytics.json"):
        self.analytics_file = analytics_file
        self.data = self.load_analytics()

    def load_analytics(self) -> Dict:
        """Load analytics from file"""
        try:
            if Path(self.analytics_file).exists():
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading analytics: {e}")
        
        return self._get_default_analytics()

    def _get_default_analytics(self) -> Dict:
        """Get default analytics structure"""
        return {
            "start_time": datetime.now().isoformat(),
            "total_broadcasts": 0,
            "total_dms_sent": 0,
            "total_dms_failed": 0,
            "active_users": 0,
            "blacklisted_users": 0,
            "flood_errors": 0,
            "last_broadcast": None,
            "success_rate": 0.0,
            "hourly_stats": {},
            "daily_stats": {},
            "user_responses": []
        }

    def save_analytics(self):
        """Save analytics to file"""
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")

    def record_broadcast(self, sent: int, failed: int, skipped: int):
        """Record a broadcast event"""
        self.data["total_broadcasts"] += 1
        self.data["total_dms_sent"] += sent
        self.data["total_dms_failed"] += failed
        self.data["active_users"] = sent + skipped
        self.data["last_broadcast"] = datetime.now().isoformat()
        
        # Calculate success rate
        total = sent + failed
        if total > 0:
            self.data["success_rate"] = (sent / total) * 100
        
        # Record hourly stats
        hour = datetime.now().strftime("%Y-%m-%d %H:00")
        if hour not in self.data["hourly_stats"]:
            self.data["hourly_stats"][hour] = {
                "sent": 0,
                "failed": 0,
                "skipped": 0
            }
        
        self.data["hourly_stats"][hour]["sent"] += sent
        self.data["hourly_stats"][hour]["failed"] += failed
        self.data["hourly_stats"][hour]["skipped"] += skipped
        
        self.save_analytics()

    def record_flood_error(self):
        """Record a flood error"""
        self.data["flood_errors"] += 1
        self.save_analytics()

    def record_blacklist(self, count: int):
        """Update blacklisted user count"""
        self.data["blacklisted_users"] = count
        self.save_analytics()

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        stats = {
            "uptime": self._calculate_uptime(),
            "total_broadcasts": self.data["total_broadcasts"],
            "total_dms_sent": self.data["total_dms_sent"],
            "total_dms_failed": self.data["total_dms_failed"],
            "success_rate": f"{self.data['success_rate']:.1f}%",
            "average_dms_per_broadcast": self._calculate_average_dms(),
            "blacklisted_users": self.data["blacklisted_users"],
            "flood_errors": self.data["flood_errors"],
            "last_broadcast": self.data["last_broadcast"],
            "daily_summary": self._get_daily_summary()
        }
        return stats

    def _calculate_uptime(self) -> str:
        """Calculate bot uptime"""
        try:
            start = datetime.fromisoformat(self.data["start_time"])
            uptime = datetime.now() - start
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            return f"{days}d {hours}h {minutes}m"
        except Exception:
            return "N/A"

    def _calculate_average_dms(self) -> int:
        """Calculate average DMs per broadcast"""
        if self.data["total_broadcasts"] == 0:
            return 0
        return int(self.data["total_dms_sent"] / self.data["total_broadcasts"])

    def _get_daily_summary(self) -> Dict:
        """Get summary for today"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_stats = {
            "sent": 0,
            "failed": 0,
            "skipped": 0
        }
        
        for hour, stats in self.data["hourly_stats"].items():
            if hour.startswith(today):
                today_stats["sent"] += stats.get("sent", 0)
                today_stats["failed"] += stats.get("failed", 0)
                today_stats["skipped"] += stats.get("skipped", 0)
        
        return today_stats

    def get_performance_report(self) -> str:
        """Get a formatted performance report"""
        stats = self.get_statistics()
        
        report = f"""
╔════════════════════════════════════════════════════╗
║           BOT PERFORMANCE REPORT                    ║
╚════════════════════════════════════════════════════╝

📊 STATISTICS:
  Uptime: {stats['uptime']}
  Total Broadcasts: {stats['total_broadcasts']}
  Total DMs Sent: {stats['total_dms_sent']}
  Total DMs Failed: {stats['total_dms_failed']}
  Success Rate: {stats['success_rate']}
  Avg DMs/Broadcast: {stats['average_dms_per_broadcast']}

⚠️  ISSUES:
  Flood Errors: {stats['flood_errors']}
  Blacklisted Users: {stats['blacklisted_users']}

📅 TODAY'S SUMMARY:
  Sent: {stats['daily_summary']['sent']}
  Failed: {stats['daily_summary']['failed']}
  Skipped: {stats['daily_summary']['skipped']}

🕐 Last Broadcast: {stats['last_broadcast']}

════════════════════════════════════════════════════
"""
        return report

    def export_csv(self, filename: str = "analytics_export.csv"):
        """Export analytics to CSV"""
        try:
            with open(filename, 'w') as f:
                f.write("Timestamp,Type,Sent,Failed,Skipped,SuccessRate\n")
                
                for hour, stats in sorted(self.data["hourly_stats"].items()):
                    sent = stats.get("sent", 0)
                    failed = stats.get("failed", 0)
                    skipped = stats.get("skipped", 0)
                    total = sent + failed
                    rate = (sent / total * 100) if total > 0 else 0
                    
                    f.write(f"{hour},broadcast,{sent},{failed},{skipped},{rate:.1f}%\n")
            
            logger.info(f"Analytics exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting analytics: {e}")
            return False

    def get_trend_analysis(self) -> Dict:
        """Analyze trends over time"""
        if not self.data["hourly_stats"]:
            return {}
        
        hourly_rates = []
        for stats in self.data["hourly_stats"].values():
            sent = stats.get("sent", 0)
            failed = stats.get("failed", 0)
            total = sent + failed
            if total > 0:
                rate = (sent / total) * 100
                hourly_rates.append(rate)
        
        if not hourly_rates:
            return {}
        
        return {
            "average_success_rate": f"{statistics.mean(hourly_rates):.1f}%",
            "peak_success_rate": f"{max(hourly_rates):.1f}%",
            "lowest_success_rate": f"{min(hourly_rates):.1f}%",
            "consistency": self._calculate_consistency(hourly_rates)
        }

    def _calculate_consistency(self, rates: List[float]) -> str:
        """Calculate consistency of success rates"""
        if len(rates) < 2:
            return "N/A"
        
        std_dev = statistics.stdev(rates)
        if std_dev < 5:
            return "Very Consistent"
        elif std_dev < 10:
            return "Consistent"
        elif std_dev < 20:
            return "Somewhat Variable"
        else:
            return "Highly Variable"


class HealthMonitor:
    """Monitor bot health and alert on issues"""
    
    def __init__(self, analytics: BotAnalytics):
        self.analytics = analytics
        self.alerts = []

    def check_health(self) -> Dict:
        """Perform comprehensive health check"""
        health = {
            "status": "healthy",
            "checks": {},
            "warnings": [],
            "alerts": []
        }
        
        stats = self.analytics.get_statistics()
        
        # Check success rate
        try:
            success_rate = float(stats['success_rate'].rstrip('%'))
            if success_rate < 50:
                health["alerts"].append("⚠️  Success rate below 50%")
                health["status"] = "critical"
            elif success_rate < 80:
                health["warnings"].append("⚠️  Success rate below 80%")
                health["status"] = "warning"
        except:
            pass
        
        # Check flood errors
        if stats['flood_errors'] > 10:
            health["alerts"].append(f"⚠️  High flood errors: {stats['flood_errors']}")
            health["status"] = "critical"
        elif stats['flood_errors'] > 5:
            health["warnings"].append(f"⚠️  Elevated flood errors: {stats['flood_errors']}")
        
        # Check blacklist growth
        if stats['blacklisted_users'] > stats['total_dms_sent'] * 0.1:
            health["warnings"].append("⚠️  High blacklist ratio")
        
        health["checks"] = {
            "success_rate": stats['success_rate'],
            "total_dms": stats['total_dms_sent'],
            "failed_dms": stats['total_dms_failed'],
            "flood_errors": stats['flood_errors'],
            "blacklisted": stats['blacklisted_users']
        }
        
        return health

    def get_health_summary(self) -> str:
        """Get formatted health summary"""
        health = self.check_health()
        
        status_icon = "✅" if health["status"] == "healthy" else ("⚠️ " if health["status"] == "warning" else "❌")
        
        summary = f"\n{status_icon} Health Status: {health['status'].upper()}\n"
        
        if health["checks"]:
            summary += "\n📊 Health Checks:\n"
            for check, value in health["checks"].items():
                summary += f"  • {check}: {value}\n"
        
        if health["warnings"]:
            summary += "\n⚠️  Warnings:\n"
            for warning in health["warnings"]:
                summary += f"  • {warning}\n"
        
        if health["alerts"]:
            summary += "\n❌ Alerts:\n"
            for alert in health["alerts"]:
                summary += f"  • {alert}\n"
        
        return summary


if __name__ == "__main__":
    # Example usage
    analytics = BotAnalytics()
    
    # Simulate some data
    analytics.record_broadcast(sent=45, failed=5, skipped=10)
    
    # Print report
    print(analytics.get_performance_report())
    
    # Health check
    monitor = HealthMonitor(analytics)
    print(monitor.get_health_summary())
    
    # Trend analysis
    trends = analytics.get_trend_analysis()
    if trends:
        print("\n📈 Trend Analysis:")
        for key, value in trends.items():
            print(f"  {key}: {value}")
