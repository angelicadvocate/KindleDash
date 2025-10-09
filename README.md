# ⚠️ WARNING! ⚠️

**This project is in active development and is not yet ready for production use.**  

- Features may be incomplete or unstable.  
- Breaking changes may occur at any time.  
- Use at your own risk.  
- Intended for testing, experimentation, and development only.  

---

**Version:** 0.1.0-alpha

# KindleDash
**Wireless dashboard for non-touch Kindles: weather, metrics, and custom slides. Compatible with most Linux-based devices, including Nook, Kobo, and custom setups.**

KindleDash turns your non-touch Kindle (or similar Linux-based device) into a customizable wireless dashboard, capable of displaying weather, metrics, and rotating slides.

---

## Table of Contents

1. [Device Setup](#device-setup)  
2. [Install KindleDash Docker Service](#install-kindledash-docker-service)  
3. [Configuration](#configuration)  
4. [Running the Dashboard](#running-the-dashboard)  
5. [Contributing](#contributing)  

---

## Device Setup

> **Note:** These instructions focus on non-touch Kindles. Other devices may require different steps. See [MobileRead](https://www.mobileread.com/) for detailed jailbreak/root instructions for your specific device.

1. Connect your device to a computer and **enable USBNet on your Kindle**.
2. **Enable wireless SSH access** to the device.
3. Determine the root password for your device and SSH into the device.
   (This may vary by model/serial number; refer to guides or root password generators.)
4. Create a script to fetch and display the dashboard image:  
```bash
nano /mnt/us/screenfetch.sh
```
5. Add the following contents:
```bash
curl HOST_IP_ADDRESS:PORT/slides -o currentimage.png
eips -c
eips -c
eips -g currentimage.png
```
6. Make the script executable:
```bash
chmod +x /mnt/us/screenfetch.sh
```
7. Create a cron job to run the script at the desired frequency (e.g., once a minute):
```bash
* * * * * /mnt/us/screenfetch.sh
```
8. Restart the Kindle to activate the cron job.

## Install KindleDash Docker Service

Placeholder: Instructions to pull and run the Docker service from KindleDash GitHub
 will go here.

## Configuration

Placeholder: Details about slide setup, URLs, rotation intervals, inversion, overlays, etc., will be added as the project evolves.

## Running the Dashboard

Placeholder: Steps for monitoring, logs, or troubleshooting.

## Contributing

Contributions, issues, and feature requests are welcome!




































