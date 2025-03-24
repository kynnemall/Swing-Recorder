# Swing-Recorder

## Why?
I enjoy playing golf but my swing is terrible and I want to get instant feedback so I can see where I'm making mistakes.

## How?
To achieve this, I made a portable recording rig consisting of:
* A Raspberry Pi 4b
* A [3.5 inch TFT display and metal case](https://thepihut.com/products/raspberry-pi-4-metal-case-with-3-5-tft-touchscreen-480x320)
* A [USB camera](https://www.webcamerausb.com/elp-global-shutter-monochrome-hd-webcam-640fps-120p-420fps-240p-210fps-480p-120fps-800p-high-speed-camera-usb20-manual-focus-with-optical-zoom-lens-p-512.html) capable of up to 640 FPS
* And a tripod

With this setup I developed a Python GUI to record using the camera presets. If I happen to have hit a shot, I can log the resulting shot shape and distance (carry and total) with Trackman.

## To-do list
- [X] Develop a working Python GUI
- [ ] Investigate power banks for maximum portability
- [ ] Add option for snapshot to check camera position with 5 second delay
- [ ] Add playback option after recording
