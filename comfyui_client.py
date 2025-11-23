import aiohttp
import json
import uuid
import websockets
import io
from typing import Optional, Dict, Any
from PIL import Image
import logging

logger = logging.getLogger('comfyui_client')


class ComfyUIClient:
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        self.client_id = str(uuid.uuid4())

    async def upload_image(self, image_data: bytes, filename: str) -> str:
        """Upload an image to ComfyUI and return the filename."""
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('image', image_data, filename=filename, content_type='image/png')
            data.add_field('overwrite', 'true')

            async with session.post(f'{self.server_url}/upload/image', data=data) as response:
                if response.status != 200:
                    raise Exception(f"Failed to upload image: {response.status}")
                result = await response.json()
                return result['name']

    async def queue_prompt(self, workflow: Dict[str, Any]) -> str:
        """Queue a workflow and return the prompt ID."""
        payload = {
            'prompt': workflow,
            'client_id': self.client_id
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.server_url}/prompt', json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to queue prompt: {response.status} - {error_text}")
                result = await response.json()
                return result['prompt_id']

    async def get_image(self, filename: str, subfolder: str = '', folder_type: str = 'output') -> bytes:
        """Download a generated image from ComfyUI."""
        params = {'filename': filename, 'subfolder': subfolder, 'type': folder_type}

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.server_url}/view', params=params) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get image: {response.status}")
                return await response.read()

    async def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for a workflow to complete via WebSocket and return the results."""
        ws_url = f"{self.server_url.replace('http', 'ws')}/ws?clientId={self.client_id}"

        try:
            async with websockets.connect(ws_url) as websocket:
                async for message in websocket:
                    data = json.loads(message)

                    if data['type'] == 'executing':
                        executing_data = data['data']
                        if executing_data['node'] is None and executing_data.get('prompt_id') == prompt_id:
                            # Execution finished
                            return await self._get_history(prompt_id)

                    elif data['type'] == 'execution_error':
                        if data['data'].get('prompt_id') == prompt_id:
                            raise Exception(f"Execution error: {data['data']}")

        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            raise

    async def _get_history(self, prompt_id: str) -> Dict[str, Any]:
        """Get the execution history for a prompt."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.server_url}/history/{prompt_id}') as response:
                if response.status != 200:
                    raise Exception(f"Failed to get history: {response.status}")
                history = await response.json()
                return history.get(prompt_id, {})

    def create_text2img_workflow(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        cfg: float = 7.0,
        sampler_name: str = "euler",
        scheduler: str = "normal",
        denoise: float = 1.0,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a basic text-to-image workflow."""
        if seed is None:
            seed = int(uuid.uuid4().int % (2**32))

        workflow = {
            "3": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": sampler_name,
                    "scheduler": scheduler,
                    "denoise": denoise,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "discord_bot",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }

        return workflow

    def create_img2img_workflow(
        self,
        image_filename: str,
        prompt: str,
        negative_prompt: str = "",
        steps: int = 20,
        cfg: float = 7.0,
        sampler_name: str = "euler",
        scheduler: str = "normal",
        denoise: float = 0.75,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create an image-to-image workflow."""
        if seed is None:
            seed = int(uuid.uuid4().int % (2**32))

        workflow = {
            "3": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": sampler_name,
                    "scheduler": scheduler,
                    "denoise": denoise,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["10", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "discord_bot",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            },
            "10": {
                "inputs": {
                    "pixels": ["11", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEEncode"
            },
            "11": {
                "inputs": {
                    "image": image_filename,
                    "upload": "image"
                },
                "class_type": "LoadImage"
            }
        }

        return workflow

    async def get_output_images(self, history: Dict[str, Any]) -> list[bytes]:
        """Extract and download output images from execution history."""
        images = []

        if 'outputs' not in history:
            return images

        for node_id, node_output in history['outputs'].items():
            if 'images' in node_output:
                for image_info in node_output['images']:
                    image_data = await self.get_image(
                        image_info['filename'],
                        image_info.get('subfolder', ''),
                        image_info.get('type', 'output')
                    )
                    images.append(image_data)

        return images
