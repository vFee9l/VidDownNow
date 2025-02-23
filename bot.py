from pyrogram import Client, filters
import yt_dlp
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API credentials from environment variables
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# Initialize bot
app = Client("video_downloader_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Files for storing activation data
ACTIVATION_KEYS_FILE = "activationkeys.txt"
ACTIVATED_USERS_FILE = "activated_users.txt"

# Function to check if a user is activated
def is_user_activated(user_id):
    if not os.path.exists(ACTIVATED_USERS_FILE):
        return False
    with open(ACTIVATED_USERS_FILE, "r") as f:
        activated_users = f.read().splitlines()
    return str(user_id) in activated_users

# Function to activate a user
def activate_user(user_id):
    with open(ACTIVATED_USERS_FILE, "a") as f:
        f.write(f"{user_id}\n")

# Function to validate activation key
def is_valid_key(key):
    if not os.path.exists(ACTIVATION_KEYS_FILE):
        return False
    with open(ACTIVATION_KEYS_FILE, "r") as f:
        keys = f.read().splitlines()
    return key in keys

# Function to remove used activation key
def remove_activation_key(key):
    with open(ACTIVATION_KEYS_FILE, "r") as f:
        keys = f.read().splitlines()
    keys.remove(key)
    with open(ACTIVATION_KEYS_FILE, "w") as f:
        f.write("\n".join(keys) + "\n")

# Function to download video
def download_video(url):
    options = {'format': 'best', 'outtmpl': 'downloads/%(title)s.%(ext)s', 'quiet': True}
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# 🔹 Handle /start command (Request Activation)
@app.on_message(filters.command("start"))
def start_command(client, message):
    user_id = message.from_user.id

    if is_user_activated(user_id):
        message.reply_text("✅ You are already activated! Send a video link to download.")
        return
    
    message.reply_text("🔑 Please enter your activation key to use this bot.")

# 🔹 Handle activation key entry
@app.on_message(filters.private & filters.text)
def handle_activation_or_links(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    # If the user is not activated, check activation key
    if not is_user_activated(user_id):
        if is_valid_key(text):
            activate_user(user_id)
            remove_activation_key(text)
            message.reply_text("✅ Activation successful! Now you can send video links to download.")
        else:
            message.reply_text("❌ Invalid activation key. Please enter a valid key.")
        return

    # Process video link if user is activated
    platforms = {
        "youtube.com": "YouTube",
        "youtu.be": "YouTube",
        "tiktok.com": "TikTok",
        "instagram.com": "Instagram",
        "twitter.com": "Twitter",
        "x.com": "Twitter"
    }
    platform = next((p for k, p in platforms.items() if k in text), None)

    if not platform:
        return message.reply_text("❌ Unsupported link. Please send a valid video link.")

    message.reply_text(f"🔄 Downloading from {platform}...")

    try:
        file_path = download_video(text)
        message.reply_text("✅ Download complete! Uploading...")
        message.reply_video(file_path)
        os.remove(file_path)
    except Exception as e:
        message.reply_text(f"❌ Download failed: {e}")

# Run bot
app.run()
