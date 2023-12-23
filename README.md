# Bicyclist Defense with NVIDIA Jetson Orin Nano (WIP)

Defending Bicyclists from Erratic Drivers with Computer Vision

## Networking Setup

I've installed Tailscale on my iPhone and my Jetson Orin Nano. 

Once I've done that, I can set up my Jetson Orin Nano to run a webserver for configuration on my phone. My Jetson Orin Nano just needs to tether from my iPhone:

These commands will scan for the wifi:

```bash
$ sudo nmcli dev wifi rescan
$ sudo nmcli dev wifi
```

And then once I see the WIFI of my phone I can:

```
$ sudo nmcli d wifi connect AS:0D:20:20:92 password actualpassword
```

From there, each time I bring up my Jetson, it will autoconnect to the Wifi.
