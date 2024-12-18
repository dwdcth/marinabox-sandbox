import requests
import base64

def get_screenshot(api_url="http://localhost:8000"):
    try:
        # Make request to the screenshot endpoint
        response = requests.get(f"{api_url}/screenshot")
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Get the base64 image data
        image_data = response.json()["image"]
        
        # Decode base64 and save to file
        image_bytes = base64.b64decode(image_data)
        
        # Save to local file
        with open("screenshot.png", "wb") as f:
            f.write(image_bytes)
            
        print("Screenshot saved successfully as 'screenshot.png'")
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as e:
        print(f"Error: {e}")

def get_cursor_position(api_url="http://localhost:8000"):
    try:
        response = requests.post(f"{api_url}/input/cursor_position")
        response.raise_for_status()
        
        position = response.json()
        print(f"Cursor position - X: {position['x']}, Y: {position['y']}")
        return position
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_screenshot()
    get_cursor_position()