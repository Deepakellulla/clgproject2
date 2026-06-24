# Telegram Group DM Userbot 🚀

A powerful Telegram userbot for automated direct messaging to group members with advanced features for business promotion.

## ⚠️ Important Disclaimer

- **This tool must be used responsibly and in accordance with Telegram's Terms of Service**
- Telegram prohibits spam and unsolicited bulk messaging
- Aggressive use can result in account restrictions or permanent bans
- Always ensure you have proper consent from recipients
- I recommend starting with longer intervals and monitoring account health

## Features ✨

- ✅ Automatic DM to group members
- ✅ Skip bots and admins automatically
- ✅ Configurable DM intervals (default: 5 minutes)
- ✅ Rate limiting and anti-flood protection
- ✅ Persistent state management
- ✅ Custom HTML-formatted messages
- ✅ Comprehensive logging
- ✅ User blacklist/whitelist system
- ✅ Retry logic with exponential backoff
- ✅ Easy Railway deployment
- ✅ Docker support

## Prerequisites

- Python 3.9+
- Telegram account (not a bot account - must be a real user account)
- API credentials from https://my.telegram.org

## Setup Instructions

### 1. Get Telegram API Credentials

1. Go to https://my.telegram.org/
2. Log in with your phone number
3. Click "API development tools"
4. Create an application and get your `API_ID` and `API_HASH`

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/telegram-userbot.git
cd telegram-userbot
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit the .env file with your credentials
nano .env
```

**Required variables in `.env`:**
```
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+your_phone_number
GROUP_ID=-1001234567890  # Negative ID for groups
```

### 5. Customize Your Message

Edit `message.txt` with your promotional message. Supports HTML formatting:
- `<b>Bold</b>`
- `<i>Italic</i>`
- `<u>Underline</u>`
- `<code>Code</code>`

### 6. Run Locally

```bash
python telegram_userbot.py
```

The first run will ask you to authenticate via Telegram.

## Configuration Options

### .env Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_ID` | - | Your Telegram API ID |
| `API_HASH` | - | Your Telegram API Hash |
| `PHONE_NUMBER` | - | Your phone number with country code |
| `GROUP_ID` | - | Group ID to target (use negative: -1001234567890) |
| `DM_INTERVAL` | 300 | Seconds between DM rounds |
| `RATE_LIMIT_DELAY` | 2 | Seconds between individual DMs |
| `MAX_RETRIES` | 3 | Retry attempts per failed DM |

### Advanced Settings

#### Finding Your Group ID

1. Forward a message from the target group to the bot: https://t.me/userinfobot
2. The bot will show you the group ID
3. For private groups, add a `-100` prefix if not already present

#### Recommended Settings for Safety

```env
DM_INTERVAL=600        # 10 minutes
RATE_LIMIT_DELAY=3     # 3 seconds between DMs
MAX_RETRIES=2          # Fewer retries
```

## Deployment on Railway

### Method 1: Connect GitHub (Recommended)

1. Push your code to GitHub
2. Go to https://railway.app
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your telegram-userbot repository
5. Add environment variables:
   - Go to Variables tab
   - Add all variables from `.env`
6. Railway will automatically deploy using the Dockerfile

### Method 2: Deploy Using Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Create project
railway init

# Add environment variables
railway variables set API_ID=your_id
railway variables set API_HASH=your_hash
railway variables set PHONE_NUMBER=+1234567890
railway variables set GROUP_ID=-1001234567890

# Deploy
railway up
```

## Advanced Features

### User Blacklist/Whitelist

The bot maintains a `bot_state.json` file that tracks:
- Blacklisted users (failed DMs, flood errors)
- Whitelisted users (force include)
- DM history

```json
{
  "blacklist": [123456, 789012],
  "whitelist": [345678],
  "last_updated": "2024-01-01T12:00:00"
}
```

### Monitoring & Logs

Logs are saved to `userbot.log`. Monitor key events:

```bash
# Watch logs in real-time
tail -f userbot.log

# Check for errors
grep "ERROR" userbot.log

# Check for flood warnings
grep "Flood" userbot.log
```

### Statistics API

Check bot statistics:

```python
stats = await userbot.get_stats()
print(stats)
# {
#   'is_running': True,
#   'total_dmed': 450,
#   'blacklisted_users': 12,
#   'whitelisted_users': 5,
#   'last_error': ''
# }
```

## Troubleshooting

### "Flood wait detected"
- Increase `RATE_LIMIT_DELAY`
- Increase `DM_INTERVAL`
- This means Telegram is rate-limiting you - wait longer

### "Account restricted"
- Your account may be flagged for spam
- Wait 24-48 hours before trying again
- Use more conservative intervals

### "Session expired"
- Delete `.session` files
- Re-authenticate by running the bot again

### Bot only DMs some members
- Check `userbot.log` for blacklisted users
- Check if some users have privacy settings blocking DMs
- Verify group member list hasn't changed

## Best Practices

1. **Start Conservative**
   - Begin with longer intervals (10+ minutes)
   - Monitor for 24 hours before increasing frequency

2. **Personalization**
   - Mention group name or shared interest
   - Use clear, professional language

3. **Monitoring**
   - Check logs regularly
   - Watch for "Flood" warnings
   - Monitor account status

4. **Rate Limiting**
   - Never set `RATE_LIMIT_DELAY` below 1 second
   - Never set `DM_INTERVAL` below 60 seconds
   - Add longer delays during testing

5. **Consent**
   - Ensure users in group are aware
   - Provide opt-out information in message
   - Respect user privacy

## Architecture

```
telegram-userbot/
├── telegram_userbot.py      # Main bot logic
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── Procfile               # Railway process file
├── railway.toml           # Railway configuration
├── .env.example           # Environment template
├── message.txt            # Custom DM message
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── bot_state.json        # Persistent state (generated)
└── userbot.log          # Log file (generated)
```

## Security Notes

- **Never commit `.env` or `.session` files to GitHub**
- Use `.gitignore` to prevent accidental commits
- Store sensitive data only in Railway environment variables
- Regularly rotate API credentials if compromised
- Monitor your Telegram account for unauthorized access

## Performance Metrics

- **Throughput**: ~30-50 DMs per minute (with safety delays)
- **Memory**: ~50-100 MB typical usage
- **CPU**: Minimal when idle, spikes during broadcasts
- **Network**: ~1 KB per DM

For 500 members at 5-minute intervals:
- 100 DMs per 5 minutes = 20 DMs/minute
- 2 second delay = within safe limits

## Contributing

Found a bug? Have suggestions? Open an issue on GitHub!

## License

MIT License - Use freely but responsibly

## Disclaimer

This tool is provided for legitimate business use only. Users are responsible for:
- Complying with Telegram's Terms of Service
- Respecting user privacy
- Following local laws and regulations
- Not using for spam or harassment

The author is not liable for account restrictions, bans, or other consequences resulting from misuse.

---

**Need Help?**
- Check logs: `tail -f userbot.log`
- Review .env settings
- Verify API credentials
- Check Telegram account status
