import discord
from discord import app_commands
from discord.ext import commands
import io
import logging
import asyncio
from typing import Optional

from comfyui_client import ComfyUIClient
import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord_bot')

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize ComfyUI client
comfy_client = ComfyUIClient(config.COMFYUI_URL)


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        logger.info(f'Synced {len(synced)} command(s)')
    except Exception as e:
        logger.error(f'Failed to sync commands: {e}')


@bot.tree.command(name="generate", description="Generate an image using ComfyUI")
@app_commands.describe(
    prompt="The text prompt describing what you want to generate",
    negative_prompt="What you don't want in the image (optional)",
    image="Input image for img2img (optional)",
    steps="Number of sampling steps (default: 20)",
    cfg="CFG scale - how closely to follow the prompt (default: 7.0)",
    sampler="Sampling method (default: euler)",
    scheduler="Scheduler type (default: normal)",
    denoise="Denoising strength for img2img (default: 0.75, 1.0 for txt2img)",
    width="Image width (default: 512, only for text2img)",
    height="Image height (default: 512, only for text2img)",
    seed="Random seed for reproducibility (optional)"
)
@app_commands.choices(sampler=[
    app_commands.Choice(name="euler", value="euler"),
    app_commands.Choice(name="euler_ancestral", value="euler_ancestral"),
    app_commands.Choice(name="heun", value="heun"),
    app_commands.Choice(name="dpm_2", value="dpm_2"),
    app_commands.Choice(name="dpm_2_ancestral", value="dpm_2_ancestral"),
    app_commands.Choice(name="lms", value="lms"),
    app_commands.Choice(name="dpm_fast", value="dpm_fast"),
    app_commands.Choice(name="dpm_adaptive", value="dpm_adaptive"),
    app_commands.Choice(name="dpmpp_2s_ancestral", value="dpmpp_2s_ancestral"),
    app_commands.Choice(name="dpmpp_sde", value="dpmpp_sde"),
    app_commands.Choice(name="dpmpp_2m", value="dpmpp_2m"),
    app_commands.Choice(name="ddim", value="ddim"),
    app_commands.Choice(name="uni_pc", value="uni_pc"),
])
@app_commands.choices(scheduler=[
    app_commands.Choice(name="normal", value="normal"),
    app_commands.Choice(name="karras", value="karras"),
    app_commands.Choice(name="exponential", value="exponential"),
    app_commands.Choice(name="sgm_uniform", value="sgm_uniform"),
    app_commands.Choice(name="simple", value="simple"),
    app_commands.Choice(name="ddim_uniform", value="ddim_uniform"),
])
async def generate(
    interaction: discord.Interaction,
    prompt: str,
    negative_prompt: Optional[str] = "",
    image: Optional[discord.Attachment] = None,
    steps: Optional[int] = None,
    cfg: Optional[float] = None,
    sampler: Optional[str] = None,
    scheduler: Optional[str] = None,
    denoise: Optional[float] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    seed: Optional[int] = None
):
    """Generate an image using ComfyUI."""

    # Check if command is used in allowed channel (if configured)
    if config.ALLOWED_CHANNEL_ID and str(interaction.channel_id) != config.ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(
            "❌ This command can only be used in the designated channel.",
            ephemeral=True
        )
        return

    # Defer response since generation takes time
    await interaction.response.defer()

    try:
        # Use default values from config if not provided
        steps = steps or config.DEFAULT_KSAMPLER['steps']
        cfg = cfg or config.DEFAULT_KSAMPLER['cfg']
        sampler = sampler or config.DEFAULT_KSAMPLER['sampler_name']
        scheduler = scheduler or config.DEFAULT_KSAMPLER['scheduler']

        # Set default dimensions for text2img
        width = width or 512
        height = height or 512

        # Determine if this is img2img or text2img
        is_img2img = image is not None

        if is_img2img:
            # Image-to-image generation
            denoise = denoise or 0.75

            # Download and upload the input image
            await interaction.followup.send("📤 Uploading input image to ComfyUI...")
            image_data = await image.read()

            # Upload image to ComfyUI
            uploaded_filename = await comfy_client.upload_image(image_data, image.filename)
            logger.info(f"Uploaded image: {uploaded_filename}")

            # Create img2img workflow
            workflow = comfy_client.create_img2img_workflow(
                image_filename=uploaded_filename,
                prompt=prompt,
                negative_prompt=negative_prompt,
                steps=steps,
                cfg=cfg,
                sampler_name=sampler,
                scheduler=scheduler,
                denoise=denoise,
                seed=seed
            )
        else:
            # Text-to-image generation
            denoise = denoise or 1.0

            # Create text2img workflow
            workflow = comfy_client.create_text2img_workflow(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=steps,
                cfg=cfg,
                sampler_name=sampler,
                scheduler=scheduler,
                denoise=denoise,
                seed=seed
            )

        # Queue the workflow
        await interaction.followup.send("⚙️ Generating image with ComfyUI...")
        prompt_id = await comfy_client.queue_prompt(workflow)
        logger.info(f"Queued prompt: {prompt_id}")

        # Wait for completion
        history = await comfy_client.wait_for_completion(prompt_id)

        # Get output images
        output_images = await comfy_client.get_output_images(history)

        if not output_images:
            await interaction.followup.send("❌ No images were generated.")
            return

        # Send the generated images
        files = []
        for idx, img_data in enumerate(output_images):
            files.append(discord.File(io.BytesIO(img_data), filename=f"generated_{idx}.png"))

        # Create embed with generation info
        embed = discord.Embed(
            title="✨ Image Generated Successfully",
            color=discord.Color.green()
        )
        embed.add_field(name="Prompt", value=prompt[:1024], inline=False)
        if negative_prompt:
            embed.add_field(name="Negative Prompt", value=negative_prompt[:1024], inline=False)

        settings = f"**Steps:** {steps} | **CFG:** {cfg} | **Sampler:** {sampler}\n"
        settings += f"**Scheduler:** {scheduler} | **Denoise:** {denoise}"
        if not is_img2img:
            settings += f"\n**Size:** {width}x{height}"
        if seed is not None:
            settings += f"\n**Seed:** {seed}"

        embed.add_field(name="Settings", value=settings, inline=False)
        embed.set_footer(text=f"Generated by {interaction.user.display_name}")

        await interaction.followup.send(embed=embed, files=files)
        logger.info(f"Successfully generated {len(output_images)} image(s) for user {interaction.user}")

    except Exception as e:
        logger.error(f"Error generating image: {e}", exc_info=True)
        await interaction.followup.send(f"❌ Error generating image: {str(e)}")


@bot.tree.command(name="ping", description="Check if the bot is responsive")
async def ping(interaction: discord.Interaction):
    """Simple ping command to check if bot is working."""
    await interaction.response.send_message(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")


@bot.tree.command(name="comfyui_status", description="Check ComfyUI connection status")
async def comfyui_status(interaction: discord.Interaction):
    """Check if ComfyUI server is accessible."""
    await interaction.response.defer(ephemeral=True)

    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{config.COMFYUI_URL}/system_stats") as response:
                if response.status == 200:
                    stats = await response.json()
                    embed = discord.Embed(
                        title="✅ ComfyUI Status",
                        description="ComfyUI server is online and accessible",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="Server URL", value=config.COMFYUI_URL, inline=False)

                    # Add system stats if available
                    if 'system' in stats:
                        system = stats['system']
                        if 'os' in system:
                            embed.add_field(name="OS", value=system['os'], inline=True)
                        if 'python_version' in system:
                            embed.add_field(name="Python", value=system['python_version'], inline=True)

                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.followup.send(
                        f"⚠️ ComfyUI server returned status code: {response.status}",
                        ephemeral=True
                    )
    except Exception as e:
        logger.error(f"Error checking ComfyUI status: {e}")
        await interaction.followup.send(
            f"❌ Cannot connect to ComfyUI server at {config.COMFYUI_URL}\nError: {str(e)}",
            ephemeral=True
        )


def main():
    """Main function to run the bot."""
    if not config.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN is not set in .env file")
        return

    logger.info(f"Starting bot with ComfyUI at {config.COMFYUI_URL}")
    bot.run(config.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
