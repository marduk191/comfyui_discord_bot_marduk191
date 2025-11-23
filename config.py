import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ALLOWED_CHANNEL_ID = os.getenv('ALLOWED_CHANNEL_ID')

# ComfyUI Configuration
COMFYUI_URL = os.getenv('COMFYUI_URL', 'http://127.0.0.1:8188')

# Validate required settings
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN must be set in .env file")

# Default KSampler settings
DEFAULT_KSAMPLER = {
    'steps': 20,
    'cfg': 7.0,
    'sampler_name': 'euler',
    'scheduler': 'normal',
    'denoise': 1.0
}
