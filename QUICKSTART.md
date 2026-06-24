# Quick Start Guide ⚡

Get your bot running in 15 minutes!

## 1️⃣ Get API Credentials (2 min)

1. Go to https://my.telegram.org/
2. Login with your phone
3. Click "API development tools"
4. Create app and copy `API_ID` and `API_HASH`

## 2️⃣ Setup Locally (5 min)

```bash
# Clone/create project
git clone <your-repo> && cd telegram-userbot

# Install dependencies
pip install -r requirements.txt

# Run setup wizard
python setup.py

# Follow prompts to enter:
# - API_ID, API_HASH
# - Phone number (+1234567890)
# - Group ID (-1001234567890)
# - Custom message
```

## 3️⃣ Test Locally (3 min)

```bash
# Run the bot
python telegram_userbot.py

# On first run, it will ask for authentication
# Click the Telegram link it provides
# Complete the login

# Check logs - should show:
# ✅ Userbot started successfully
# 🚀 Starting broadcast to X members
# ✅ Broadcast completed
```

## 4️⃣ Deploy to Railway (5 min)

### Option A: GitHub → Railway (Easiest)

1. Push code to GitHub
   ```bash
   git add .
   git commit -m "Bot setup"
   git push origin main
   ```

2. Go to https://railway.app
3. Click "New Project" → "Deploy from GitHub"
4. Select your telegram-userbot repo
5. Click Variables tab
6. Add environment variables:
   - `API_ID` = your_id
   - `API_HASH` = your_hash
   - `PHONE_NUMBER` = +1234567890
   - `GROUP_ID` = -1001234567890
7. Railway auto-deploys! ✅

### Option B: Railway CLI

```bash
npm install -g @railway/cli
railway login
railway init
railway variables set API_ID=your_value
railway variables set API_HASH=your_value
railway variables set PHONE_NUMBER=+1234567890
railway variables set GROUP_ID=-1001234567890
railway up
```

## ⚙️ Important Settings

**Safe defaults already in `.env`:**
- `DM_INTERVAL=300` (5 minutes)
- `RATE_LIMIT_DELAY=2` (2 seconds between DMs)
- `MAX_RETRIES=3`

**These prevent Telegram from banning you.**

## 📊 Monitor Your Bot

### Local Monitoring
```bash
tail -f userbot.log
```

### Railway Monitoring
1. Railway Dashboard → Your Project
2. Click "Logs" tab
3. Watch real-time activity

### Check Bot Stats
- File: `bot_state.json` - Shows blacklisted users
- File: `userbot.log` - Shows all activity

## 🆘 Quick Fixes

| Problem | Fix |
|---------|-----|
| Bot doesn't send DMs | Check GROUP_ID is negative |
| "Flood wait" errors | Increase `DM_INTERVAL` and `RATE_LIMIT_DELAY` |
| Auth fails | Delete `.session` files, restart |
| Railway keeps restarting | Check all env variables are set |
| Account restricted | Stop bot, wait 48 hours |

## ✅ Verify It's Working

```bash
# In logs, look for:
✅ Userbot started successfully
🚀 Starting broadcast to 50 members
✅ DM sent to 12345
```

## 🚀 Next Steps

1. **Monitor for 24 hours**
   - Check logs regularly
   - Look for any flood errors
   - Adjust delays if needed

2. **Customize message**
   - Edit `message.txt` with your promo
   - Uses HTML: `<b>bold</b>`, `<i>italic</i>`
   - Push to GitHub → auto-redeploys

3. **Track performance**
   - Check `analytics.json` after broadcasts
   - Review success rates
   - Adjust if needed

## ⚠️ Critical Rules

1. **NEVER go below:**
   - `DM_INTERVAL=300` (5 min)
   - `RATE_LIMIT_DELAY=2` (2 sec)

2. **DO skip:**
   - Bots ✅ (auto-skipped)
   - Admins ✅ (auto-skipped)
   - Sensitive accounts (add to blacklist manually)

3. **DON'T:**
   - Run multiple bots on same account
   - DM outside your target group
   - Use offensive/spammy messages
   - Ignore "Flood wait" errors

## 📞 Need Help?

1. Check `TROUBLESHOOTING.md`
2. Review logs: `tail -f userbot.log`
3. Read `README.md` for detailed docs
4. Railway Discord: https://discord.gg/railway

---

## 🎯 Performance Expectations

**With default settings (5-min interval, 2-sec delays):**
- 50 members: ~10 DMs per 5 minutes
- 500 members: ~100 DMs per 5 minutes
- 1000 members: ~200 DMs per 5 minutes

**Estimated monthly cost on Railway:**
- Free tier usually sufficient
- ~$1-2 if going over free tier

**Success rate:**
- 80-95% on healthy accounts
- Drops if account gets restricted

---

## 🔄 Update Bot Later

```bash
# Make changes to message.txt
nano message.txt

# Push to GitHub
git add message.txt
git commit -m "Update message"
git push

# Railway auto-redeploys!
# Or manually restart: Railway Dashboard → Restart
```

---

**You're all set! Good luck with your bot! 🚀**

Need detailed help? See:
- Setup issues → `TROUBLESHOOTING.md`
- Deployment questions → `RAILWAY_GUIDE.md`
- Full documentation → `README.md`
