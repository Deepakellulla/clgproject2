# Railway Deployment Guide 🚀

This guide will help you deploy your Telegram userbot to Railway.

## Prerequisites

1. GitHub account with your bot code pushed
2. Railway account (https://railway.app)
3. All environment variables ready

## Step-by-Step Deployment

### 1. Push Code to GitHub

```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial bot setup"

# Add remote and push
git remote add origin https://github.com/yourusername/telegram-userbot.git
git branch -M main
git push -u origin main
```

**Important:** Make sure `.env` is in `.gitignore` to prevent leaking credentials!

### 2. Create Railway Account

1. Go to https://railway.app
2. Sign up (can use GitHub for easy login)
3. Create a new project

### 3. Connect GitHub Repository

1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Authenticate with GitHub
4. Select your `telegram-userbot` repository
5. Railway will automatically detect the Dockerfile and deploy

### 4. Add Environment Variables

In Railway dashboard:

1. Go to "Settings" tab of your project
2. Click "Variables"
3. Add each variable from your `.env`:
   - `API_ID`
   - `API_HASH`
   - `PHONE_NUMBER`
   - `GROUP_ID`
   - `DM_INTERVAL` (optional)
   - `RATE_LIMIT_DELAY` (optional)
   - `MAX_RETRIES` (optional)

### 5. Configure Deployment

Railway should auto-detect from `Dockerfile` and `railway.toml`.

For manual configuration:
1. Go to "Deployment" settings
2. Set start command: `python telegram_userbot.py`
3. Set restart policy to "always"

### 6. Handle Authentication

**Important:** The first run requires Telegram authentication!

On first deployment:
1. Go to "Logs" tab
2. Look for authentication prompt
3. Click the Telegram link in logs
4. Complete authentication
5. The bot will continue running

### 7. Monitor and Manage

#### View Logs
- Railway Dashboard → Logs tab
- Real-time monitoring of bot activity
- Check for errors and warnings

#### Check Status
- Railway Dashboard shows deployment status
- Green = Running, Red = Failed
- Check health check status

#### Restart the Bot
1. Go to Settings
2. Click "Restart" to restart the service

#### Update Code
1. Push changes to GitHub
2. Railway automatically redeploys
3. Check Deployment tab for progress

## Advanced Configuration

### Enable Persistent Storage

For `bot_state.json` to persist across restarts:

1. In Railway project settings
2. Add Volume:
   - Mount path: `/app`
   - Name: `bot-storage`

This prevents losing user blacklist/whitelist data.

### Set Resource Limits

1. Go to Project Settings
2. Adjust resources:
   - CPU: 0.25-0.5 vCPU is enough
   - RAM: 256-512 MB is sufficient
   - These keep costs low

### Set Up Email Alerts

1. Project Settings → Alerts
2. Enable notifications for:
   - Deployment failures
   - Service crashes
   - Unusual activity

## Troubleshooting

### Bot Starts But Does Nothing

**Problem:** Bot is running but not sending DMs

**Solutions:**
1. Check GROUP_ID is correct (should be negative)
2. Check logs for errors: `tail -f userbot.log`
3. Verify bot has access to the group
4. Check if account is restricted

### "Flood Wait" Errors

**Problem:** Getting rate-limited frequently

**Solution:**
1. Increase `RATE_LIMIT_DELAY` to 3-5
2. Increase `DM_INTERVAL` to 600+ seconds
3. Reduce broadcast frequency
4. Wait 24-48 hours before retrying

### Authentication Fails

**Problem:** Can't authenticate Telegram

**Solutions:**
1. Delete session file and restart
2. Check PHONE_NUMBER format (+1234567890)
3. Try 2FA if enabled on account
4. Check for account restrictions

### Out of Memory

**Problem:** Bot crashes with OOM error

**Solution:**
1. Increase RAM allocation in Railway
2. Reduce batch size in config
3. Restart bot regularly

## Cost Estimation

**Free tier includes:**
- $5 usage credit per month
- Enough for continuous light usage

**Estimated costs:**
- Minimal CPU usage: < $0.50/month
- 256 MB RAM: < $1/month
- Storage: < $0.10/month

**Total:** Usually within free tier

## Security Checklist

- [ ] `.env` is in `.gitignore`
- [ ] No API credentials in source code
- [ ] All secrets in Railway variables only
- [ ] Regular monitoring of logs
- [ ] Change API credentials if exposed
- [ ] Use strong Telegram account password
- [ ] Enable 2FA on Telegram if possible

## Useful Railway CLI Commands

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Deploy changes
railway up

# Set environment variable
railway variables set API_ID=your_value

# Get variable value
railway variables get API_ID

# Status
railway status
```

## Health Monitoring

Railway includes automatic health checks. The bot includes:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('bot_state.json') else 1)"
```

This checks if the bot is running correctly. If health checks fail:
1. Railway automatically logs it
2. You receive notifications
3. Bot restarts if configured

## Performance Optimization

### Reduce Bandwidth
- Optimize message size (keep under 5KB)
- Use text-only messages (no media)
- Minimize logging

### Reduce Memory
- Use `memory_profiler` to identify leaks
- Clear old logs periodically
- Limit state file size

### Improve Speed
- Cache user info when possible
- Use connection pooling
- Implement request batching

## Scaling Considerations

For larger deployments (1000+ members):

1. **Increase DM_INTERVAL** - Spread load over time
2. **Optimize RATE_LIMIT_DELAY** - Find sweet spot
3. **Use multiple instances** - Railway supports scaling
4. **Monitor resource usage** - Check Railway dashboard

## Backup and Recovery

### Backup State

```bash
# Download bot_state.json from Railway
railway run cat bot_state.json > backup_state.json
```

### Restore State

```bash
# Upload state file
railway run cp /tmp/backup_state.json bot_state.json
```

## Getting Help

- **Railway Support:** https://discord.gg/railway
- **Telethon Docs:** https://docs.telethon.dev
- **This Repository Issues:** Open an issue on GitHub

---

**Happy Deployment! 🚀**
