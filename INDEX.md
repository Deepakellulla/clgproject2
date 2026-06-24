# 📦 Project Files & Directory Overview

## 🎯 Complete Telegram Userbot Package

This is a production-ready Telegram group DM bot with advanced features, Railway deployment support, and comprehensive documentation.

---

## 📁 File Structure

### 🤖 Core Application Files

| File | Purpose | Size | Importance |
|------|---------|------|-----------|
| `telegram_userbot.py` | Main bot logic | ~400 lines | ⭐⭐⭐⭐⭐ |
| `config_manager.py` | Advanced configuration | ~300 lines | ⭐⭐⭐ |
| `analytics.py` | Performance tracking | ~350 lines | ⭐⭐⭐ |
| `setup.py` | Interactive setup wizard | ~350 lines | ⭐⭐⭐⭐ |

### 📋 Configuration Files

| File | Purpose |
|------|---------|
| `.env.example` | Environment variables template |
| `.env` | Your actual credentials (local only, DON'T COMMIT) |
| `message.txt` | Custom DM message (editable) |
| `.gitignore` | Prevent secrets from GitHub |
| `config.json` | Advanced features config (optional) |

### 🚀 Deployment Files

| File | Purpose | Platform |
|------|---------|----------|
| `Dockerfile` | Container definition | Docker/Railway |
| `docker-compose.yml` | Local dev environment | Docker |
| `Procfile` | Process file | Railway |
| `railway.toml` | Railway configuration | Railway |
| `requirements.txt` | Python dependencies | All |

### 📚 Documentation Files

| File | Best For | Read Time |
|------|----------|-----------|
| `README.md` | Complete documentation | 20 min |
| `QUICKSTART.md` | Fast setup & deployment | 10 min |
| `RAILWAY_GUIDE.md` | Railway-specific guide | 15 min |
| `TROUBLESHOOTING.md` | Fixing problems | 10 min |
| `GITHUB_README.md` | GitHub repo page | 5 min |

### 📊 Generated Files (Created at Runtime)

| File | Purpose | Created By |
|------|---------|-----------|
| `bot_state.json` | User blacklist/whitelist | telegram_userbot.py |
| `userbot.log` | Activity logs | telegram_userbot.py |
| `analytics.json` | Performance metrics | analytics.py |
| `session.*` | Telegram auth session | telegram_userbot.py |
| `.session-journal` | Session journal | telethon |

---

## 🚀 Getting Started Roadmap

### Phase 1: Setup (5-10 minutes)
1. Read: `QUICKSTART.md`
2. Run: `python setup.py`
3. Answer configuration questions
4. Bot created locally ✅

### Phase 2: Local Testing (3-5 minutes)
1. Run: `python telegram_userbot.py`
2. Authenticate with Telegram
3. Watch it broadcast to your group
4. Monitor: `tail -f userbot.log`

### Phase 3: Push to GitHub (2 minutes)
1. `git init`
2. `git add .`
3. `git commit -m "Initial setup"`
4. `git push origin main`

### Phase 4: Deploy to Railway (3-5 minutes)
1. Create Railway account
2. Connect GitHub repo
3. Add environment variables
4. Railway auto-deploys ✅

### Phase 5: Monitor (Ongoing)
1. Check Railway logs
2. Review `analytics.json`
3. Adjust settings if needed
4. Scale up safely

---

## 📖 Which Document Should I Read?

```
I want to...                          Read this...
────────────────────────────────────────────────────
Get started FAST                  → QUICKSTART.md
Full documentation                → README.md
Deploy to Railway                 → RAILWAY_GUIDE.md
Fix an error                       → TROUBLESHOOTING.md
Understand the architecture        → This file + README.md
Deploy using Docker               → README.md + docker-compose.yml
Set up GitHub repo                → QUICKSTART.md + .gitignore
Monitor performance               → analytics.py + README.md
```

---

## 🔑 Key Concepts

### Required Environment Variables
```
API_ID          - From https://my.telegram.org
API_HASH        - From https://my.telegram.org
PHONE_NUMBER    - Your Telegram account (+XXXXXXXXXXX)
GROUP_ID        - Target group (negative, e.g., -1001234567890)
```

### Safe Default Settings
```
DM_INTERVAL          = 300 seconds (5 minutes)
RATE_LIMIT_DELAY     = 2 seconds (between DMs)
MAX_RETRIES          = 3 attempts
```

### Auto-Skip Features
```
✅ Bots        - Automatically skipped
✅ Admins      - Automatically skipped
✅ Blacklist   - Users with failed DMs skipped
❌ No skipping privacy or content filtering
```

---

## 📊 File Dependencies

```
telegram_userbot.py (Main)
    ├── imports: telethon, asyncio, logging
    ├── uses: .env file for config
    ├── reads: message.txt for custom message
    ├── writes: bot_state.json, userbot.log
    └── calls: telegram API

config_manager.py
    ├── loads: config.json (optional)
    └── used by: telegram_userbot.py (optional)

analytics.py
    ├── reads: bot_state.json
    ├── writes: analytics.json
    └── used by: monitoring/reporting

setup.py
    ├── creates: .env file
    ├── creates: message.txt
    ├── updates: .gitignore
    └── initializes: git repo

Dockerfile
    ├── installs: Python 3.11
    ├── installs: requirements.txt
    ├── copies: all source files
    └── runs: telegram_userbot.py

docker-compose.yml
    ├── builds: Dockerfile
    └── mounts: volumes for persistence
```

---

## 🎯 Common Use Cases

### Use Case 1: Simple Business Promotion
```
Files you need:
  - telegram_userbot.py
  - .env (with credentials)
  - message.txt (your promo)
  - requirements.txt
  
Commands:
  pip install -r requirements.txt
  python telegram_userbot.py
```

### Use Case 2: Production Deployment (Railway)
```
Files you need:
  - Everything above +
  - Dockerfile
  - railway.toml
  - Procfile
  - GitHub repo
  
Steps:
  1. Push to GitHub
  2. Connect to Railway
  3. Deploy automatically
```

### Use Case 3: Advanced Monitoring
```
Files you need:
  - Everything +
  - analytics.py
  - config_manager.py
  
Commands:
  python analytics.py --export
  python -c "from config_manager import ConfigManager; c = ConfigManager(); print(c.export_summary())"
```

### Use Case 4: Docker/Local Development
```
Files you need:
  - docker-compose.yml
  - Dockerfile
  - All source files
  
Commands:
  docker-compose up -d
  docker-compose logs -f
```

---

## 🔒 Security Checklist

### Files to Keep Secret
- [ ] `.env` - Never commit, never share
- [ ] `*.session` files - Session tokens
- [ ] `*.session-journal` - Session data
- [ ] `bot_state.json` - Contains user IDs

### Files to Share Safely
- [ ] All `.md` files - Documentation
- [ ] `.py` files - Source code
- [ ] `.gitignore` - Git rules
- [ ] `.env.example` - Template only
- [ ] `requirements.txt` - Dependencies

### GitHub Safety
```
✅ DO commit:
  - .py source files
  - .md documentation
  - Dockerfile
  - requirements.txt
  - .gitignore
  - .env.example (template)

❌ DON'T commit:
  - .env (actual secrets)
  - *.session files
  - *.log files
  - bot_state.json
  - analytics.json (optional)
```

---

## 💾 Data & State Management

### State Persistence
```
bot_state.json          - User blacklist/whitelist
  ├─ survived bot restarts
  ├─ grows as users blacklisted
  └─ can be backed up

userbot.log            - Activity log
  ├─ helps debug issues
  ├─ shows all errors
  └─ can be trimmed safely

analytics.json         - Performance metrics
  ├─ success rates
  ├─ error counts
  └─ can be exported to CSV
```

### Backup Strategy
```
Important to backup:    Optional to backup:
  - bot_state.json        - userbot.log
  - .env file             - analytics.json
  - message.txt
  - config.json
```

---

## 📈 Scaling Guide

### For Small Groups (50-100 members)
```
DM_INTERVAL = 300        (5 minutes)
RATE_LIMIT_DELAY = 2     (safe)
Expected time = 2-5 minutes per cycle
```

### For Medium Groups (100-500 members)
```
DM_INTERVAL = 600        (10 minutes)
RATE_LIMIT_DELAY = 2     (safe)
Expected time = 5-25 minutes per cycle
```

### For Large Groups (500+ members)
```
DM_INTERVAL = 900-1200   (15-20 minutes)
RATE_LIMIT_DELAY = 3-5   (safer)
Expected time = 30+ minutes per cycle
Monitor closely for flood errors
```

---

## 🔄 Update Workflow

### Update Message Only
```bash
1. Edit message.txt locally
2. python telegram_userbot.py  # Auto-loads new message
3. Check logs for confirmation
```

### Update Code
```bash
1. Edit telegram_userbot.py
2. Test locally: python telegram_userbot.py
3. git add telegram_userbot.py
4. git commit -m "Fix bug"
5. git push  # Railway auto-redeploys
```

### Update Config
```bash
1. Edit .env locally
2. Commit to Railway Variables tab
3. Railway restarts with new config
```

---

## 🎓 Learning Path

### Beginner
1. Read: QUICKSTART.md
2. Run: setup.py
3. Test: python telegram_userbot.py
4. Deploy: RAILWAY_GUIDE.md

### Intermediate
1. Read: README.md (full)
2. Customize: message.txt, config
3. Monitor: analytics.py output
4. Debug: TROUBLESHOOTING.md

### Advanced
1. Understand: telegram_userbot.py code
2. Extend: config_manager.py
3. Analyze: analytics.py
4. Optimize: performance tuning

---

## 🆘 Quick Help

**Bot won't start?**
→ Check requirements.txt installed
→ Check .env file exists with all variables

**Bot runs but doesn't send?**
→ Check GROUP_ID is negative
→ Check GROUP_ID correct
→ Check logs: tail -f userbot.log

**Deployment failed?**
→ Check RAILWAY_GUIDE.md
→ Check all env vars in Railway
→ Check Dockerfile exists

**Getting flooded?**
→ Check TROUBLESHOOTING.md
→ Increase DM_INTERVAL
→ Increase RATE_LIMIT_DELAY

**Need more help?**
→ Read TROUBLESHOOTING.md (10 min)
→ Open GitHub issue
→ Check Railway Discord

---

## 📦 Dependencies Explained

```
telethon==1.34.0
  └─ Telegram client library
     (does the actual messaging)

python-dotenv==1.0.0
  └─ Loads .env file
     (keeps secrets out of code)

aiofiles==23.2.1
  └─ Async file operations
     (reads/writes efficiently)
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] .env file exists (locally)
- [ ] message.txt has your content
- [ ] Python 3.9+ installed
- [ ] Dependencies installed: `pip list`
- [ ] Bot runs locally without errors
- [ ] Bot authenticates with Telegram
- [ ] Bot sends test DM successfully
- [ ] Logs show activity
- [ ] Code pushed to GitHub
- [ ] GitHub .gitignore prevents secret commits
- [ ] Railway connected to GitHub
- [ ] Railway has all env variables
- [ ] Railway deployment succeeds
- [ ] Railway logs show bot activity

---

## 🎯 Next Actions

1. **Right now:** Read `QUICKSTART.md` (10 min)
2. **Next:** Run `python setup.py` (5 min)
3. **Then:** Test locally with `python telegram_userbot.py` (5 min)
4. **Finally:** Deploy to Railway using `RAILWAY_GUIDE.md` (5 min)

**Total time: ~25 minutes from start to production! 🚀**

---

**For detailed help on any file, open that file directly!**
