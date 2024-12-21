# MarinaBox Sandbox

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
```bash
cd browser
docker build -t marinabox-browser .
```

### Desktop Sandbox
```bash
cd desktop
docker build -t marinabox-desktop .
```
