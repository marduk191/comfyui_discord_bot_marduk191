# Quick Start Guide

Get your ComfyUI Discord bot up and running in 5 minutes!

## Step 1: Prerequisites Check

Make sure you have:
- ✅ Python 3.8+ installed
- ✅ ComfyUI installed and working
- ✅ A Stable Diffusion model in ComfyUI (e.g., SD XL Base)

## Step 2: Install the Bot

```bash
# Clone and enter directory
git clone https://github.com/yourusername/comfyui_discord_bot_marduk191.git
cd comfyui_discord_bot_marduk191

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Create Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application" → Name it (e.g., "ComfyUI Bot")
3. Go to "Bot" tab → Click "Add Bot"
4. Click "Reset Token" → Copy the token
5. Enable "MESSAGE CONTENT INTENT"
6. Go to OAuth2 → URL Generator
   - Scopes: `bot` + `applications.commands`
   - Permissions: `Send Messages`, `Attach Files`, `Embed Links`
7. Copy the URL and open in browser to invite bot to your server

## Step 4: Configure

```bash
# Copy example config
cp .env.example .env

# Edit .env with your favorite editor
nano .env  # or vim, code, etc.
```

Add your Discord token:
```env
DISCORD_TOKEN=paste_your_token_here
COMFYUI_URL=http://127.0.0.1:8188
```

## Step 5: Start ComfyUI

In your ComfyUI directory:
```bash
python main.py
```

Wait for it to fully load (check http://127.0.0.1:8188 in browser)

## Step 6: Run the Bot

In the bot directory:
```bash
python bot.py
```

You should see:
```
INFO - Logged in as YourBot (ID: ...)
INFO - Synced X command(s)
```

## Step 7: Test It!

In Discord, type:
```
/generate prompt: a cute cat wearing a wizard hat
```

Wait 20-30 seconds and enjoy your generated image!

## Common First-Time Issues

### "Cannot find DISCORD_TOKEN"
- Make sure you created `.env` file (not `.env.example`)
- Check that your token is pasted correctly with no extra spaces

### "Cannot connect to ComfyUI"
- Is ComfyUI running? Check http://127.0.0.1:8188
- Is the port correct in `.env`?

### "Slash commands not showing"
- Wait 5-10 minutes for Discord to sync
- Try kicking and re-inviting the bot

### "Checkpoint not found"
- Edit `comfyui_client.py` line with `ckpt_name` to match your model name
- Check your ComfyUI models folder for the exact filename

## Next Steps

- Read the full [README.md](README.md) for advanced features
- Experiment with different samplers and settings
- Try image-to-image generation by attaching images

## Quick Command Reference

Basic generation:
```
/generate prompt: your prompt here
```

With settings:
```
/generate prompt: your prompt steps: 30 cfg: 8 sampler: dpmpp_2m
```

Image transformation:
```
/generate prompt: cyberpunk style image: [attach file] denoise: 0.7
```

Utility:
```
/ping
/comfyui_status
```

Enjoy generating! 🎨
