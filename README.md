# ComfyUI Discord Bot

A Discord bot that integrates with your local ComfyUI installation to generate AI images directly from Discord. Users can send text prompts, upload input images, and configure KSampler settings for customized image generation.

## Features

- **Text-to-Image Generation**: Generate images from text prompts
- **Image-to-Image Generation**: Transform existing images with AI
- **Customizable KSampler Settings**: Control steps, CFG, sampler type, scheduler, and more
- **Discord Slash Commands**: Easy-to-use `/generate` command with autocomplete
- **Real-time Progress**: Get updates while your image is being generated
- **Multiple Sampler Options**: Support for euler, dpm++, ddim, and many more samplers
- **Seed Control**: Reproducible results with seed specification

## Prerequisites

- Python 3.8 or higher
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) installed and running locally
- A Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- A checkpoint model (e.g., `sd_xl_base_1.0.safetensors`) in your ComfyUI models folder

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/comfyui_discord_bot_marduk191.git
   cd comfyui_discord_bot_marduk191
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Discord bot token:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   COMFYUI_URL=http://127.0.0.1:8188
   ```

## Setting Up Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section and click "Add Bot"
4. Under the "Token" section, click "Reset Token" and copy it to your `.env` file
5. Enable "MESSAGE CONTENT INTENT" in the Bot settings
6. Go to "OAuth2" → "URL Generator"
7. Select scopes: `bot` and `applications.commands`
8. Select permissions: `Send Messages`, `Attach Files`, `Embed Links`, `Use Slash Commands`
9. Copy the generated URL and open it in your browser to invite the bot to your server

## Running ComfyUI

Make sure ComfyUI is running before starting the bot:

```bash
# In your ComfyUI directory
python main.py
```

ComfyUI should be accessible at `http://127.0.0.1:8188` by default.

## Running the Bot

```bash
python bot.py
```

The bot will:
1. Connect to Discord
2. Sync slash commands
3. Be ready to generate images!

## Usage

### Basic Text-to-Image Generation

```
/generate prompt: a beautiful sunset over mountains
```

### Advanced Generation with Custom Settings

```
/generate
  prompt: a futuristic city at night
  negative_prompt: blurry, low quality
  steps: 30
  cfg: 8.5
  sampler: dpmpp_2m
  scheduler: karras
  width: 768
  height: 768
```

### Image-to-Image Generation

1. Use the `/generate` command
2. Attach an image to the `image` parameter
3. Add your prompt describing how you want to transform the image
4. Optionally adjust the `denoise` parameter (0.0-1.0, default: 0.75)
   - Lower values keep more of the original image
   - Higher values give the AI more creative freedom

```
/generate
  prompt: turn this into a cyberpunk scene
  image: [attach your image]
  denoise: 0.6
  steps: 25
```

### KSampler Settings

| Parameter | Description | Default | Range/Options |
|-----------|-------------|---------|---------------|
| `steps` | Number of denoising steps | 20 | 1-150 |
| `cfg` | Classifier-Free Guidance scale | 7.0 | 1.0-20.0 |
| `sampler` | Sampling algorithm | euler | See list below |
| `scheduler` | Noise schedule | normal | normal, karras, exponential, etc. |
| `denoise` | Denoising strength (img2img) | 0.75 | 0.0-1.0 |
| `seed` | Random seed for reproducibility | Random | Any integer |
| `width` | Image width (text2img only) | 512 | Multiple of 8 |
| `height` | Image height (text2img only) | 512 | Multiple of 8 |

### Available Samplers

- `euler` - Fast and reliable (recommended for beginners)
- `euler_ancestral` - More varied results
- `dpmpp_2m` - High quality, good detail
- `dpmpp_sde` - Slower but very high quality
- `ddim` - Classic sampler
- And many more!

### Utility Commands

- `/ping` - Check if the bot is responsive
- `/comfyui_status` - Check ComfyUI connection status

## Configuration

### config.py

Edit `config.py` to change default settings:

```python
DEFAULT_KSAMPLER = {
    'steps': 20,
    'cfg': 7.0,
    'sampler_name': 'euler',
    'scheduler': 'normal',
    'denoise': 1.0
}
```

### Checkpoint Model

The bot uses `sd_xl_base_1.0.safetensors` by default. To use a different model, edit the checkpoint name in `comfyui_client.py`:

```python
"ckpt_name": "your_model_name.safetensors"
```

## Troubleshooting

### Bot doesn't respond to commands

1. Make sure the bot has been invited with proper permissions
2. Wait a few minutes for Discord to sync slash commands
3. Try kicking and re-inviting the bot

### "Cannot connect to ComfyUI server"

1. Verify ComfyUI is running: visit http://127.0.0.1:8188 in your browser
2. Check the `COMFYUI_URL` in your `.env` file
3. Make sure no firewall is blocking the connection

### "Failed to upload image"

1. Ensure the image format is supported (PNG, JPG, WebP)
2. Check that the image isn't too large (Discord limit: 25MB)

### Workflow fails or produces errors

1. Make sure you have the required checkpoint model in ComfyUI
2. Check ComfyUI logs for specific errors
3. Verify your ComfyUI installation has all required custom nodes

## Project Structure

```
comfyui_discord_bot_marduk191/
├── bot.py              # Main Discord bot with slash commands
├── comfyui_client.py   # ComfyUI API client
├── config.py           # Configuration and settings
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## License

MIT License - feel free to modify and use as needed!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - The powerful UI and backend for Stable Diffusion
- [discord.py](https://github.com/Rapptz/discord.py) - Python Discord API wrapper