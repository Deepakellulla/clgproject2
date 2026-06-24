#!/usr/bin/env python3
"""
Interactive Setup Script for Telegram Userbot
Helps users configure their bot easily
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}")
    print(f"{text.center(60)}")
    print(f"{'=' * 60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print_header("Checking Prerequisites")
    
    prerequisites = {
        'Python 3.9+': sys.version_info >= (3, 9),
        'pip': check_command('pip --version'),
        'git': check_command('git --version'),
    }
    
    all_good = True
    for req, installed in prerequisites.items():
        if installed:
            print_success(f"{req} is installed")
        else:
            print_error(f"{req} is NOT installed")
            all_good = False
    
    return all_good

def check_command(cmd):
    """Check if a command is available"""
    return os.system(f"{cmd} > /dev/null 2>&1") == 0

def setup_env_file():
    """Setup .env file"""
    print_header("Setting up Environment Variables")
    
    env_file = '.env'
    
    # Check if .env already exists
    if Path(env_file).exists():
        response = input(f"{Colors.WARNING}.env file already exists. Overwrite? (y/n): {Colors.ENDC}").lower()
        if response != 'y':
            print_info("Skipping .env setup")
            return
    
    print_info("Get your Telegram API credentials from https://my.telegram.org/")
    print()
    
    api_id = input(f"{Colors.OKCYAN}Enter your API_ID: {Colors.ENDC}").strip()
    api_hash = input(f"{Colors.OKCYAN}Enter your API_HASH: {Colors.ENDC}").strip()
    phone = input(f"{Colors.OKCYAN}Enter your phone number (with country code, e.g., +1234567890): {Colors.ENDC}").strip()
    
    print_info("Enter your target group ID")
    print_info("Tip: Forward a message from the group to @userinfobot to get the ID")
    group_id = input(f"{Colors.OKCYAN}Enter GROUP_ID (negative, e.g., -1001234567890): {Colors.ENDC}").strip()
    
    # Optional settings
    print()
    print_info("Optional Settings (press Enter to use defaults):")
    dm_interval = input(f"{Colors.OKCYAN}DM Interval in seconds (default 300): {Colors.ENDC}").strip() or "300"
    rate_limit = input(f"{Colors.OKCYAN}Rate limit delay in seconds (default 2): {Colors.ENDC}").strip() or "2"
    
    # Create .env file
    env_content = f"""# Telegram API Credentials
API_ID={api_id}
API_HASH={api_hash}
PHONE_NUMBER={phone}

# Group Configuration
GROUP_ID={group_id}

# Timing Settings
DM_INTERVAL={dm_interval}
RATE_LIMIT_DELAY={rate_limit}
MAX_RETRIES=3

# Optional Features
DB_ENABLED=false
WEBHOOK_ENABLED=false
STATS_ENABLED=true
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print_success(f"✓ Created {env_file}")
        print_info(f"Saved: API_ID, API_HASH, PHONE_NUMBER, GROUP_ID")
    except Exception as e:
        print_error(f"Failed to create {env_file}: {e}")
        return False
    
    return True

def setup_message():
    """Setup custom message"""
    print_header("Setting up Custom DM Message")
    
    msg_file = 'message.txt'
    
    if Path(msg_file).exists():
        response = input(f"{Colors.WARNING}{msg_file} already exists. Edit it? (y/n): {Colors.ENDC}").lower()
        if response != 'y':
            print_info("Keeping existing message")
            return
    
    print_info("Create your custom DM message (HTML formatting supported)")
    print_info("Formatting: <b>bold</b>, <i>italic</i>, <u>underline</u>, <code>code</code>")
    print_info("Type 'END' on a new line when done:")
    print()
    
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    
    message = '\n'.join(lines)
    
    if not message.strip():
        print_warning("Empty message, using default")
        message = "👋 Hey! Check out my business 🚀\nWould love to connect with you!"
    
    try:
        with open(msg_file, 'w', encoding='utf-8') as f:
            f.write(message)
        print_success(f"✓ Saved message to {msg_file}")
        print(f"\n{Colors.OKCYAN}Message preview:{Colors.ENDC}")
        print(message)
    except Exception as e:
        print_error(f"Failed to save message: {e}")

def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Dependencies")
    
    req_file = 'requirements.txt'
    if not Path(req_file).exists():
        print_error(f"{req_file} not found!")
        return False
    
    print_info("Installing packages from requirements.txt...")
    result = os.system(f"pip install -r {req_file}")
    
    if result == 0:
        print_success("✓ Dependencies installed successfully")
        return True
    else:
        print_error("Failed to install dependencies")
        return False

def setup_git_repo():
    """Initialize git repository"""
    print_header("Setting up Git Repository")
    
    if Path('.git').exists():
        print_warning("Git repository already initialized")
        return
    
    response = input(f"{Colors.OKCYAN}Initialize git repository? (y/n): {Colors.ENDC}").lower()
    if response != 'y':
        return
    
    os.system("git init")
    os.system("git config user.name 'Telegram Bot'")
    os.system("git config user.email 'bot@telegram.local'")
    
    # Create initial commit
    os.system("git add .")
    os.system("git commit -m 'Initial bot setup'")
    
    print_success("✓ Git repository initialized")
    print_info("Next: Add remote and push to GitHub")
    print_info("Commands:")
    print("  git remote add origin <your-github-url>")
    print("  git branch -M main")
    print("  git push -u origin main")

def test_configuration():
    """Test if configuration is valid"""
    print_header("Testing Configuration")
    
    load_dotenv()
    
    checks = {
        'API_ID': os.getenv('API_ID'),
        'API_HASH': os.getenv('API_HASH'),
        'PHONE_NUMBER': os.getenv('PHONE_NUMBER'),
        'GROUP_ID': os.getenv('GROUP_ID'),
        'Requirements.txt exists': Path('requirements.txt').exists(),
        'Message file exists': Path('message.txt').exists(),
    }
    
    all_good = True
    for check, result in checks.items():
        if result:
            print_success(f"{check}: ✓")
        else:
            print_error(f"{check}: ✗")
            all_good = False
    
    return all_good

def show_next_steps():
    """Show next steps for the user"""
    print_header("Next Steps")
    
    print(f"{Colors.OKGREEN}✅ Setup Complete!{Colors.ENDC}\n")
    
    steps = [
        ("1", "Test locally", "python telegram_userbot.py"),
        ("2", "Push to GitHub", "git push origin main"),
        ("3", "Deploy on Railway", "https://railway.app"),
        ("4", "Monitor logs", "tail -f userbot.log"),
        ("5", "Check status", "Check Railway dashboard"),
    ]
    
    for num, desc, cmd in steps:
        print(f"{Colors.BOLD}{num}. {desc}{Colors.ENDC}")
        print(f"   {Colors.OKCYAN}$ {cmd}{Colors.ENDC}")
        print()

def main():
    """Main setup flow"""
    print_header("Telegram Userbot Setup Wizard")
    
    print(f"{Colors.WARNING}⚠️  IMPORTANT DISCLAIMER:{Colors.ENDC}")
    print("This tool must be used responsibly and in accordance with Telegram ToS.")
    print("Aggressive use can result in account restrictions or bans.")
    print()
    
    # Run setup steps
    steps = [
        ("Checking Prerequisites", check_prerequisites),
        ("Setting up Environment", setup_env_file),
        ("Setting up Message", setup_message),
        ("Installing Dependencies", install_dependencies),
        ("Testing Configuration", test_configuration),
        ("Setting up Git", setup_git_repo),
    ]
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                print_warning(f"Skipped: {step_name}")
            print()
        except KeyboardInterrupt:
            print_error("\n\nSetup cancelled by user")
            sys.exit(1)
        except Exception as e:
            print_error(f"Error during {step_name}: {e}")
    
    show_next_steps()
    
    print(f"{Colors.OKGREEN}Happy botting! 🚀{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nSetup cancelled")
        sys.exit(1)
