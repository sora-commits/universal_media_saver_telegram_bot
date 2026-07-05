# Universal Media Saver Bot

**Automatically saves all media from Telegram to your Google Drive — quietly and cleanly.**

This bot receives photos, videos, voice messages, video circles, documents, stickers, and more, saves them to your Google Drive, and cleans up the chat.

---

## Features

- Supports **all media types**
- Quiet mode — deletes original messages and notifications
- Automatic temporary file cleanup
- Easy one-time authorization
- 24/7 operation after deployment

---

## Quick Start

### Step 1: Create a Telegram Bot

1. Open [@BotFather](https://t.me/BotFather) in Telegram
2. Send `/newbot`
3. Choose a name and username
4. Copy your **BOT_TOKEN**

### Step 2: Prepare Google Drive Folder

1. Create a new folder in your Google Drive (e.g. `Telegram Media`)
2. Open the folder and copy the **Folder ID** from the URL  
   (Example: `1AbCdEfGhIjKlMnOpQrStUvWxYz1234567890`)

### Step 3: Configure Environment Variables

1. Copy `.env.example` to `.env`
2. Open `.env` and fill in your data:

BOT_TOKEN=your_bot_token_here
DRIVE_FOLDER_ID=your_folder_id_here

### Step 4: Google OAuth Setup (One-time)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Drive API**
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
6. Select **Desktop app** → Create
7. Download the JSON file and rename it to `client_secret.json`

### Step 5: First Authorization (Local)

1. Run the bot (main.py)   
2. A browser window will open — log in with your Google account and grant access
3. After success, a token.pickle file will be created
4. Then you can run the bot locally or use third-party services (I used Railway for testing)
