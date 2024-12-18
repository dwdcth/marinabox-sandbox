docker build --no-cache -t marinabox .

docker run -d -p 4002:9222 -p 5002:6081 -e RESOLUTION=1920x1080x24 xvfb-desktop

How to get an iframe to host on my website:

```html
<iframe src="http://localhost:6081/vnc.html?autoconnect=true&resize=scale" allow="clipboard-read; clipboard-write"></iframe>
```


           curl http://127.0.0.1:4002/json/version                            
{
   "Browser": "Chrome/124.0.6367.78",
   "Protocol-Version": "1.3",
   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
   "V8-Version": "12.4.254.14",
   "WebKit-Version": "537.36 (@a087f2dd364ddd58b9c016ef1bf563d2bc138711)",
   "webSocketDebuggerUrl": "ws://127.0.0.1:4002/devtools/browser/aaf9878c-46a3-42bb-bed6-4d5734495de8"
}

After adding desktop environment:

# Build the images
docker build -f Dockerfile.chromium -t marinabox-browser .
docker build -f Dockerfile.desktop -t marinabox-desktop .

# Run Chromium browser container
docker run -d -p 9222:9222 -e RESOLUTION=1920x1080x24 chromium-browser

# Run Alpine desktop container
docker run -d -p 5900:5900 -p 6081:6081 -p 8000:8000 -e RESOLUTION=1280x800x24 marinabox-desktop