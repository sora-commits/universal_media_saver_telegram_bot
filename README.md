# Universal Media Saver Bot

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0)
![License](https://img.shields.io/badge/license-MIT-green)

**Automatically saves all media from Telegram to your Google Drive — quietly and cleanly.**

This bot receives photos, videos, voice messages, video circles, documents, stickers, and more, saves them to your Google Drive, and cleans up the chat.

The bot is **private by design**: it only responds to the Telegram user ID set in `OWNER_ID`. Anyone else messaging the bot is ignored.

---

## Features

- Supports **all media types**
- Quiet mode — deletes original messages and notifications
- Automatic temporary file cleanup
- Private — only responds to its owner
- Deployable locally or on a headless host (Railway, VPS, etc.)
- 24/7 operation after deployment

---

## Quick Start

### Step 1: Create a Telegram Bot

1. Open [@BotFather](https://t.me/BotFather) in Telegram
2. Send `/newbot`
3. Choose a name and username
4. Copy your **BOT_TOKEN**

### Step 2: Get Your Telegram User ID

1. Open [@userinfobot](https://t.me/userinfobot) in Telegram
2. Send it any message
3. Copy your **numeric user ID** — this becomes `OWNER_ID`, so only you can use the bot

### Step 3: Prepare Google Drive Folder

1. Create a new folder in your Google Drive (e.g. `Telegram Media`)
2. Open the folder and copy the **Folder ID** from the URL
   (Example: `1AbCdEfGhIjKlMnOpQrStUvWxYz1234567890`)

### Step 4: Configure Environment Variables

1. Copy `.env.example` to `.env`
2. Open `.env` and fill in your data:

```
BOT_TOKEN=your_bot_token_here
DRIVE_FOLDER_ID=your_folder_id_here
OWNER_ID=your_telegram_user_id_here
```

### Step 5: Google OAuth Setup (One-time)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **Google Drive API**
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Select **Desktop app** → Create
6. Download the JSON file, rename it to `client_secret.json`, and place it next to `main.py`

### Step 6: First Authorization (Local)

1. Install dependencies: `pip install -r requirements.txt`
2. Run the bot: `python main.py`
3. A browser window will open — log in with your Google account and grant access
4. After success, a `token.pickle` file is created automatically next to `main.py`

From this point on the bot reuses `token.pickle` and refreshes it automatically — no more browser logins needed locally.

---

## Deploying to a Headless Host (Railway, VPS, etc.)

A cloud host has no browser, so the one-time login from Step 6 has to happen on your own machine first. Once you have `token.pickle` locally:

1. Encode it to base64:

   **PowerShell:**
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("token.pickle")) | Out-File -Encoding utf8NoBOM token_b64.txt
   ```

   **Linux/macOS:**
   ```bash
   base64 -w 0 token.pickle > token_b64.txt
   ```

2. Open `token_b64.txt` and copy its contents.

3. In your host's environment variables, set:

   | Variable | Value |
   |---|---|
   | `BOT_TOKEN` | your bot token |
   | `DRIVE_FOLDER_ID` | your Drive folder ID |
   | `OWNER_ID` | your Telegram user ID |
   | `GOOGLE_TOKEN_B64` | contents of `token_b64.txt` |

   `client_secret.json` does **not** need to be uploaded — the token already carries what's needed to refresh itself.

4. Deploy the repository. On startup, the bot detects `GOOGLE_TOKEN_B64` and reconstructs `token.pickle` automatically, so no browser is ever needed on the host.

A `Procfile` (`worker: python main.py`) is included for platforms like Railway that use it to detect the start command.

---

## Security Notes

- `client_secret.json` and `token.pickle` grant access to your Google Drive — never commit them. Both are already covered by `.gitignore`.
- The bot only replies to `OWNER_ID`; everyone else is silently ignored.
- Treat `GOOGLE_TOKEN_B64` on your host the same as a password — set it as a secret environment variable, never commit it to the repo.

---

## License

MIT — see [LICENSE](LICENSE).