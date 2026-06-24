# Pre-Deployment Checklist & Troubleshooting

## ✅ Pre-Deployment Checklist

### Telegram Setup
- [ ] Created Telegram API app at https://my.telegram.org
- [ ] Have API_ID and API_HASH
- [ ] Phone number ready (+XXXXXXXXXXX format)
- [ ] Target group identified
- [ ] Have negative GROUP_ID (e.g., -1001234567890)

### Environment Configuration
- [ ] Created `.env` file with all required variables
- [ ] `.env` is in `.gitignore`
- [ ] All variables have correct values
- [ ] Tested .env locally with `python telegram_userbot.py`

### Code Preparation
- [ ] Customized `message.txt` with your promotion text
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Ran bot locally without errors
- [ ] Authenticated with Telegram (first-run prompt)

### GitHub Setup
- [ ] Initialized git repository
- [ ] All files committed except `.env` and session files
- [ ] Pushed to GitHub
- [ ] Verified no credentials in public code

### Railway Setup
- [ ] Created Railway account
- [ ] Connected GitHub repository
- [ ] Added all environment variables to Railway
- [ ] Configured deployment settings

### Safety Verification
- [ ] DM_INTERVAL ≥ 300 seconds (5 minutes)
- [ ] RATE_LIMIT_DELAY ≥ 2 seconds
- [ ] MAX_RETRIES ≤ 5
- [ ] Message is professional and non-spammy
- [ ] Not targeting users without consent

---

## 🐛 Troubleshooting Guide

### Issue: Bot starts but doesn't send DMs

**Symptoms:**
- Bot logs show running but no DM activity
- No errors in logs

**Checklist:**
1. Verify GROUP_ID is correct
   ```bash
   # Forward a message from group to @userinfobot
   # Check the returned ID matches your GROUP_ID
   ```

2. Check bot access to group
   ```bash
   # Make sure bot account is member of group
   # Check if account has DM permission
   ```

3. Verify custom message loads
   ```bash
   # Check if message.txt exists
   ls -la message.txt
   # Check message format
   cat message.txt
   ```

4. Enable debug logging
   - Change log level to DEBUG
   - Check detailed error messages

5. Test manually
   ```python
   # Add to telegram_userbot.py temporarily
   import asyncio
   async def test():
       members = await userbot.get_group_members()
       print(f"Found {len(members)} members")
       # Try sending to first member
       if members:
           await userbot.send_dm_with_retry(members[0], "Test")
   
   asyncio.run(test())
   ```

---

### Issue: "Flood wait" or "Too many requests"

**Symptoms:**
- Logs show "FloodWaitError"
- DMing slows down significantly
- Numbers: "Flood wait: 30s", "Flood wait: 300s"

**Solutions (in order of preference):**

1. **Increase intervals immediately**
   ```env
   DM_INTERVAL=600           # 10 minutes instead of 5
   RATE_LIMIT_DELAY=3        # 3 seconds instead of 2
   ```

2. **Stop the bot**
   - Restart: `railway restart` or kill process
   - Wait 1-2 hours before restarting

3. **Reduce batch size**
   - Don't try to DM large groups frequently
   - Spread over longer periods

4. **Account-level action**
   - Telegram has flagged your account
   - Wait 24-48 hours minimum
   - Consider backing off from this account

**Prevention:**
- Never go below 2-second delays
- Monitor flood error count
- Increase delays when you see any flood errors

---

### Issue: "Account restricted" or "Peer flood error"

**Symptoms:**
- Continuous PeerFloodError exceptions
- Account can't send DMs to specific users
- Message: "Peer flood detected"

**This means:**
- Your account is being rate-limited by Telegram
- Or specific users have privacy restrictions
- Or your behavior appears spammy to Telegram

**Recovery (48-72 hours):**
1. Stop the bot immediately
2. Don't use account for 24-48 hours
3. Only use web/official apps when resuming
4. When resuming, use very conservative settings:
   ```env
   DM_INTERVAL=1800          # 30 minutes
   RATE_LIMIT_DELAY=5        # 5 seconds
   ```

**Prevention:**
- Test with small groups first
- Monitor blacklist growth
- If > 10% of users blacklisted, adjust strategy
- Watch for consecutive PeerFloodError messages

---

### Issue: "Invalid peer ID" or user not found

**Symptoms:**
- Logs: "PeerIdInvalidError" or "peer doesn't exist"
- Some users never receive DMs

**Causes:**
- User deleted their account
- User's ID changed (rare)
- User privacy settings block DMs from non-contacts
- User has been restricted

**Solution:**
- This is normal for some users
- Bot automatically blacklists these
- This is included in "skipped" count
- Monitor: if > 5% users have this, something's wrong

---

### Issue: Bot authentication fails

**Symptoms:**
- First run asks for phone number but doesn't proceed
- Error: "Invalid phone format"
- Error: "Phone not registered"

**Solutions:**

1. **Check phone format**
   ```
   Correct: +1234567890
   Wrong:   1234567890
   Wrong:   +1 234 567 890
   ```

2. **Clear session**
   ```bash
   # Delete session file
   rm session.session*
   rm *.session*
   
   # Restart bot
   python telegram_userbot.py
   ```

3. **Use app password (if 2FA enabled)**
   - If account has 2FA, you might need app-specific password
   - Check: https://my.telegram.org/apps
   - Contact Telegram support if issues persist

4. **Verify phone is on account**
   - Make sure phone number is the one registered on Telegram
   - Not a forwarded number or voIP number (may not work)

---

### Issue: Railway deployment keeps restarting

**Symptoms:**
- Deployment status shows cycling restarts
- Logs in Railway show crashes
- Restart pattern: every 10-30 seconds

**Diagnostic steps:**

1. **Check Railway logs**
   - Railway dashboard → Logs tab
   - Look for error messages
   - Note exact error

2. **Common causes:**

   **A) Authentication timeout**
   ```
   Solution: Bot needs initial auth on first Railway run
   - Railway isn't interactive, so auth fails
   - Must auth locally first, then push session files (carefully!)
   - Or implement non-interactive auth
   ```

   **B) Missing environment variables**
   ```
   - Check all 4 required vars are set
   - Typos in variable names?
   - Double-check values for typos
   ```

   **C) Python crash**
   ```
   - Check Python syntax: python -m py_compile telegram_userbot.py
   - Check missing imports: python -c "import telethon"
   - Review recent code changes
   ```

3. **Fix authentication on Railway:**
   ```python
   # Option 1: Pre-authenticate locally, upload session
   # (Use with caution, encrypt session files!)
   
   # Option 2: Use phone-number-based auth library
   # See Telethon docs for alternatives
   
   # Option 3: Keep restarting until auth prompt appears and complete it
   # Railway logs will show link to click
   ```

---

### Issue: Out of Memory (OOM) errors

**Symptoms:**
- Logs show memory exhaustion
- Bot crashes: "Killed (OOM)"
- Railway shows Memory Limit Exceeded

**Solutions:**

1. **Increase RAM on Railway**
   - Settings → Resources → RAM
   - Increase to 512MB or 1GB
   - Check costs

2. **Optimize bot**
   ```python
   # Reduce state caching
   # Clear old logs
   # Reduce batch sizes
   ```

3. **Monitor memory**
   ```bash
   # On Railway, run:
   railway exec python -m memory_profiler telegram_userbot.py
   ```

---

### Issue: DMs sent but all marked as "Seen"

**This is normal.** Telegram always shows delivery status, but seeing the message doesn't mean they read it.

**Verification:**
- Message shows checkmark (sent) ✓
- Then second checkmark (delivered) ✓✓
- Then blue checkmarks if they open Telegram app ✓✓ (blue)

---

## 📊 Common Error Messages

| Error | Meaning | Fix |
|-------|---------|-----|
| `FloodWaitError: Waiting 120s` | Rate limited | Increase delays, restart bot |
| `PeerFloodError` | Account is spamming too much | Stop bot, wait 48 hours |
| `PeerIdInvalidError` | User doesn't exist | Normal, user likely deleted account |
| `ChatNotFoundError` | Group doesn't exist | Check GROUP_ID |
| `AuthorizationError` | Not authenticated | Re-authenticate with phone |
| `InvalidSessionError` | Session expired | Delete session file, restart |
| `DocumentNotFoundError` | User removed | Bot auto-blacklists |

---

## 🔍 Debugging Steps

### Enable Debug Logging

```python
# In telegram_userbot.py, change:
logging.basicConfig(level=logging.DEBUG)  # instead of INFO
```

### Check Specific User

```python
# Add to main loop temporarily:
async def debug_user(user_id):
    is_bot = await userbot.is_bot(user_id)
    is_admin = await userbot.is_admin(user_id)
    print(f"User {user_id}: bot={is_bot}, admin={is_admin}")

await debug_user(123456789)
```

### Test DM to One User

```bash
# Create test_dm.py:
import asyncio
from telegram_userbot import TelegramUserbot

async def test():
    bot = TelegramUserbot()
    await bot.start()
    await bot.send_dm_with_retry(123456789, "Test message")
    await bot.stop()

asyncio.run(test())
```

---

## 📞 Getting Help

**Before asking for help, provide:**
1. Last 50 lines of `userbot.log`
2. Your `.env` settings (WITHOUT secrets)
3. Error message (full)
4. What you've already tried

**Where to get help:**
- Railway Discord: https://discord.gg/railway
- Telethon Issues: https://github.com/LonamiWebs/Telethon/issues
- This repo Issues: Open on GitHub

---

## ✅ Final Pre-Launch Checklist

- [ ] Bot runs 10 minutes locally without errors
- [ ] Message is professional and appropriate
- [ ] DM_INTERVAL is ≥ 300 seconds
- [ ] RATE_LIMIT_DELAY is ≥ 2 seconds
- [ ] Deployment on Railway is successful
- [ ] Logs show bot activity
- [ ] First broadcast succeeded
- [ ] No flood/peer errors in logs
- [ ] Plan to monitor for 24 hours
- [ ] Know how to stop bot if issues arise

**You're ready to launch! 🚀**
