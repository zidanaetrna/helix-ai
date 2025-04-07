```markdown
# Synthelix AI Auto-bot 🤖

An automated bot for the Synthelix AI airdrop program that handles node operations, daily point claims, and wallet management.

## ✨ Features

- ✅ Automatic node submission every 24 hours
- 🏆 Daily point claiming automation
- 💼 Wallet connection management
- 📊 Points tracking and monitoring
- ⏰ Smart timing for optimal reward collection
- 🚀 24/7 operation with automatic retries
```
## 🛠 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/zidanaetrna/helix-ai.git
   cd helix-ai
   ```

2. **Install dependencies:**
   ```bash
   apt install python3 python3.12-env & python -m venv venv & source venv/bin/activate
   ```

## 🚀 Usage

Run the bot with:
```bash
python bot.py
```
The bot will:
1. Display an ASCII art interface
2. Check your current points balance
3. Automatically claim daily rewards when available
4. Manage node operations
5. Run continuously with 5-minute checks

3. **Set up your environment:**
   - Run the bot once and it will guide you through the `.env` file setup
     ```
     SESSION_TOKEN=your_session_token_here
     PROJECT_ID=your_project_id_here
     WALLET_ADDRESS=your_wallet_address_here
     ```

## ⚙️ Configuration

Edit the `.env` file to change settings:
- `SESSION_TOKEN`: Your session/bearer token from Synthelix
- `PROJECT_ID`: Your project ID from the dashboard
- `WALLET_ADDRESS`: Your connected wallet address

## 📅 Daily Reward System

The bot automatically tracks:
- Last daily claim time
- Next eligible claim time
- Referral bonus status

## 📊 Points Tracking

The bot monitors your points balance through the Synthelix API and displays:
- Current points
- Recent changes
- Claim history

## 🤖 Bot Commands

While running, the bot provides real-time information about:
- Node status (🟢 Online/🔴 Offline)
- Next submission time
- Points accumulation
- Error states and retries

## ⚠️ Disclaimer

- This bot is for educational purposes only
- Use at your own risk
- Not affiliated with Synthelix AI
- Always comply with the platform's terms of service

## 🌟 Credits

Created by [aetrna](https://github.com/zidanaetrna)  
Project: Synthelix AI Auto-bot



