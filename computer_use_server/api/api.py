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
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InputRequest(BaseModel):
    text: Optional[str] = None
    coordinate: Optional[List[int]] = None

class EditRequest(BaseModel):
    command: Literal["view", "create", "str_replace", "insert", "undo_edit"]
    path: str
    file_text: Optional[str] = None
    view_range: Optional[List[int]] = None
    old_str: Optional[str] = None
    new_str: Optional[str] = None
    insert_line: Optional[int] = None

class BashRequest(BaseModel):
    command: Optional[str] = None
    restart: bool = False

app = FastAPI()

# Constants
DISPLAY_NUM = os.getenv("DISPLAY_NUM", "99")
XDOTOOL = "xdotool"
DISPLAY_ENV = {"DISPLAY": f":{DISPLAY_NUM}"}
OUTPUT_DIR = "/tmp/outputs"
TYPING_DELAY_MS = 12
TYPING_GROUP_SIZE = 50

# Global file history for edit tool
file_history = defaultdict(list)

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
        # Log incoming request
        logger.info(f"Received {action} request with params: {request}")
        
        if action == Action.CURSOR_POSITION:
            cmd = f"{XDOTOOL} getmouselocation --shell"
            result = subprocess.run(
                shlex.split(cmd),
                check=True,
                env=DISPLAY_ENV,
                capture_output=True,
                text=True
            )
            # Parse the output which is in format: X=123\nY=456\n...
            location_data = dict(line.split('=') for line in result.stdout.strip().split('\n'))
            return {"x": int(location_data['X']), "y": int(location_data['Y'])}

        elif action in [Action.MOUSE_MOVE, Action.LEFT_CLICK_DRAG]:
            if not request.coordinate or len(request.coordinate) != 2:
                raise HTTPException(status_code=400, detail="Coordinate required")
            x, y = request.coordinate
            if action == Action.MOUSE_MOVE:
                cmd = f"{XDOTOOL} mousemove --sync {x} {y}"
            else:
                cmd = f"{XDOTOOL} mousedown 1 mousemove --sync {x} {y} mouseup 1"
            
            # Log command being executed
            logger.info(f"Executing command: {cmd}")
            result = subprocess.run(
                shlex.split(cmd), 
                check=True, 
                env=DISPLAY_ENV,
                capture_output=True,
                text=True
            )
            logger.info(f"Command output: {result.stdout}")
            if result.stderr:
                logger.warning(f"Command stderr: {result.stderr}")

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

    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed: {e.cmd}\nReturn code: {e.returncode}\nOutput: {e.output}\nError: {e.stderr}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Error handling {action}: {str(e)}\nType: {type(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/edit")
async def handle_edit(request: EditRequest):
    try:
        path = Path(request.path)
        
        if request.command == "view":
            if not path.exists():
                raise HTTPException(status_code=404, detail=f"Path {path} does not exist")
            
            if path.is_dir():
                result = subprocess.run(
                    ["find", path, "-maxdepth", "2", "-not", "-path", "*/\\.*"],
                    capture_output=True,
                    text=True
                )
                return {"output": result.stdout, "error": result.stderr}
            
            content = path.read_text()
            if request.view_range:
                lines = content.split("\n")
                start, end = request.view_range
                content = "\n".join(lines[start-1:end])
            return {"output": content}

        elif request.command == "create":
            if path.exists():
                raise HTTPException(status_code=400, detail=f"File already exists at {path}")
            if not request.file_text:
                raise HTTPException(status_code=400, detail="file_text is required")
            path.write_text(request.file_text)
            return {"output": f"File created successfully at: {path}"}

        elif request.command == "str_replace":
            if not request.old_str:
                raise HTTPException(status_code=400, detail="old_str is required")
            content = path.read_text()
            occurrences = content.count(request.old_str)
            if occurrences == 0:
                raise HTTPException(status_code=400, detail=f"old_str not found in file")
            if occurrences > 1:
                raise HTTPException(status_code=400, detail=f"Multiple occurrences of old_str found")
            
            new_content = content.replace(request.old_str, request.new_str or "")
            file_history[str(path)].append(content)
            path.write_text(new_content)
            return {"output": "File edited successfully"}

        elif request.command == "insert":
            if request.insert_line is None or request.new_str is None:
                raise HTTPException(status_code=400, detail="insert_line and new_str are required")
            
            content = path.read_text()
            lines = content.split("\n")
            if request.insert_line < 0 or request.insert_line > len(lines):
                raise HTTPException(status_code=400, detail="Invalid insert_line")
            
            new_lines = lines[:request.insert_line] + request.new_str.split("\n") + lines[request.insert_line:]
            new_content = "\n".join(new_lines)
            file_history[str(path)].append(content)
            path.write_text(new_content)
            return {"output": "File edited successfully"}

        elif request.command == "undo_edit":
            if not file_history[str(path)]:
                raise HTTPException(status_code=400, detail="No edit history found")
            
            old_content = file_history[str(path)].pop()
            path.write_text(old_content)
            return {"output": "Last edit undone successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bash")
async def handle_bash(request: BashRequest):
    try:
        if request.restart:
            # Kill existing bash processes
            subprocess.run(["pkill", "bash"], check=False)
            return {"system": "tool has been restarted"}

        if not request.command:
            raise HTTPException(status_code=400, detail="command is required")

        # Change to root directory before executing command
        process = await asyncio.create_subprocess_shell(
            request.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/"  # Set working directory to root
        )
        stdout, stderr = await process.communicate()
        
        return {
            "output": stdout.decode() if stdout else None,
            "error": stderr.decode() if stderr else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
