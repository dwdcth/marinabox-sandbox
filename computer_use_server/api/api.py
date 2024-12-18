from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Literal
import subprocess
import base64
import os
import shlex
import asyncio
from enum import Enum
from pathlib import Path
from uuid import uuid4
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InputRequest(BaseModel):
    text: Optional[str] = None
    coordinate: Optional[List[int]] = None

app = FastAPI()

# Constants
DISPLAY_NUM = os.getenv("DISPLAY_NUM", "99")
XDOTOOL = "xdotool"
DISPLAY_ENV = {"DISPLAY": f":{DISPLAY_NUM}"}
OUTPUT_DIR = "/tmp/outputs"
TYPING_DELAY_MS = 12
TYPING_GROUP_SIZE = 50

class Action(str, Enum):
    KEY = "key"
    TYPE = "type"
    MOUSE_MOVE = "mouse_move"
    LEFT_CLICK = "left_click"
    LEFT_CLICK_DRAG = "left_click_drag"
    RIGHT_CLICK = "right_click"
    MIDDLE_CLICK = "middle_click"
    DOUBLE_CLICK = "double_click"
    SCREENSHOT = "screenshot"
    CURSOR_POSITION = "cursor_position"

@app.get("/screenshot")
async def take_screenshot():
    try:
        # Take screenshot using ffmpeg
        screenshot_path = "/tmp/screenshot.png"
        cmd = [
            "ffmpeg", "-f", "x11grab", "-video_size", "1280x800",
            "-i", f":{DISPLAY_NUM}", "-frames:v", "1", "-y", screenshot_path
        ]
        subprocess.run(cmd, check=True, env=DISPLAY_ENV)

        # Read the screenshot and convert to base64
        with open(screenshot_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Clean up
        os.remove(screenshot_path)
        
        return {"status": "success", "image": encoded_string}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/input/{action}")
async def handle_input(
    action: Action,
    request: InputRequest
):
    try:
        if action in [Action.MOUSE_MOVE, Action.LEFT_CLICK_DRAG]:
            if not request.coordinate or len(request.coordinate) != 2:
                raise HTTPException(status_code=400, detail="Coordinate required")
            x, y = request.coordinate
            if action == Action.MOUSE_MOVE:
                cmd = f"{XDOTOOL} mousemove --sync {x} {y}"
            else:
                cmd = f"{XDOTOOL} mousedown 1 mousemove --sync {x} {y} mouseup 1"
            
            subprocess.run(shlex.split(cmd), check=True, env=DISPLAY_ENV)

        elif action in [Action.KEY, Action.TYPE]:
            if not request.text:
                raise HTTPException(status_code=400, detail="Text required")
            
            if action == Action.KEY:
                cmd = f"{XDOTOOL} key -- {request.text}"
                subprocess.run(shlex.split(cmd), check=True, env=DISPLAY_ENV)
            else:
                for chunk in [request.text[i:i+TYPING_GROUP_SIZE] for i in range(0, len(request.text), TYPING_GROUP_SIZE)]:
                    cmd = f"{XDOTOOL} type --delay {TYPING_DELAY_MS} -- {shlex.quote(chunk)}"
                    subprocess.run(shlex.split(cmd), check=True, env=DISPLAY_ENV)

        elif action in [Action.LEFT_CLICK, Action.RIGHT_CLICK, Action.MIDDLE_CLICK, Action.DOUBLE_CLICK]:
            click_arg = {
                Action.LEFT_CLICK: "1",
                Action.RIGHT_CLICK: "3",
                Action.MIDDLE_CLICK: "2",
                Action.DOUBLE_CLICK: "--repeat 2 --delay 500 1"
            }[action]
            cmd = f"{XDOTOOL} click {click_arg}"
            subprocess.run(shlex.split(cmd), check=True, env=DISPLAY_ENV)

        # Take a screenshot after any action (except cursor_position)
        if action != Action.CURSOR_POSITION:
            screenshot_result = await take_screenshot()
            return {"status": "success", "screenshot": screenshot_result["image"]}
        
        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error handling input: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
