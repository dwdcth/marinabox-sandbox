# MarinaBox Sandbox

<p>
    <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/marinabox/marinabox-sandbox?style=flat-square&logo=github">
    <img alt="GitHub forks" src="https://img.shields.io/github/forks/marinabox/marinabox-sandbox?style=flat-square&logo=github">
    <img alt="GitHub issues" src="https://img.shields.io/github/issues/marinabox/marinabox-sandbox?style=flat-square&logo=github">
    <img alt="GitHub license" src="https://img.shields.io/github/license/marinabox/marinabox-sandbox?style=flat-square&logo=github">
</p>

This repository contains the Docker configurations and build files for MarinaBox's sandbox environments. It provides two main sandbox types:
- Browser Sandbox: A containerized Chrome browser environment
- Desktop Sandbox: A containerized Linux desktop environment

## Overview

MarinaBox sandboxes are isolated environments that can be controlled remotely. Each sandbox includes:
- VNC server for remote viewing
- Video recording capabilities
- Secure isolation from host system
- Computer Use command support

## Sandbox Types

### Browser Sandbox
- Chromium-based browser environment
- Remote debugging support
- Ideal for web automation and testing
- Minimal footprint

### Desktop Sandbox
- Full Linux desktop environment
- Support for multiple applications
- Suitable for complex workflows
- Complete desktop interaction capabilities

## Building Images

### Browser Sandbox
```
docker build -f Dockerfile.chromium -t marinabox/marinabox-browser .
```

### Desktop Sandbox
```
docker build -f Dockerfile.desktop -t marinabox/marinabox-desktop .
```

## License

MarinaBox Sandbox is released under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project makes significant use of:
- [noVNC](https://github.com/novnc/noVNC), an open source VNC client using HTML5 (WebSockets, Canvas). noVNC is licensed under the MPL-2.0 License.
- [Anthropic Quickstarts](https://github.com/anthropics/anthropic-quickstarts), specifically the Computer Use Demo which provided inspiration for the sandbox implementation. Licensed under the MIT License.
