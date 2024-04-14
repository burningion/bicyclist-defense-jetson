# Bicyclist Defense with NVIDIA Jetson Orin Nano 

Defending Bicyclists from Erratic Drivers with Computer Vision and mmWave Radar

![Bicyclist Safety Architecture Diagram](./assets/bicyclist-safety.png)

This project attempts to build a bicyclist warning system for erratic drivers. It aims to use computer vision along with radar to track cars which may present a threat to the bicyclist, and warn them before a potential collision occurs.

It currently runs Owl-ViT via [NanoOWL](https://github.com/NVIDIA-AI-IOT/nanoowl) to track and highlight cars, trucks, and pedestrians in real time from an attached camera, viewable on a person's iPhone mounted on their bicycle. 

There are two buttons in the app, one to record mmWave sensor data and images for training a model, and another to record videos of your trips. This is useful to build help build a dataset for distillation (improving the framerate of the inference model), keep recordings of dangerous drivers, or just record and visualize your rides. 

I've added a radar sensor to allow for sensor fusion, aiming to have more robust results than computer vision alone, with better tracking of vehicles and their speed / trajectory.

## Hardware Setup

![hardware setup](./assets/hardware.png)

I run the device off a [DeWalt 20v](https://amzn.to/3SxmQk0) battery, plugged in to an adapter. I added a second line, going through a [5v BEC](https://amzn.to/4b7muI5) and a [second male plug](https://amzn.to/4b8xjtA) for allowing me to run off my [power supply](https://amzn.to/3S5dIl6) when doing development on my workbench.

## Starting the Server and Recording a Bicycle Trip

![live webcam feed](./assets/recording.gif)

The main application is a NextJS and FastAPI server running off the Owl-ViT model. For data collection via h264 video recordings, you'll need to have the ffmpeg libraries installed:

```
$ sudo apt-get install -y libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev
```

To install the Python dependencies you just need to:

```
$ cd bicyclist-defense-jetson/bicycle-app
$ npm i
$ npm run dev
```

Or, use the `launch_bicycle.sh` script to build and run a container with the app set up. You'll still need to start the application manually, via `cd /bicyclist/bicycle-app`, followed by a `npm i`.

> **NOTE:** You may have jittery video if running the application via `npm run dev` in your web browser. This is because _some_ browsers will open two websocket connections due to the way React manages it's state in development in the page load `useEffect`. If you instead do a `npm run build`, followed by an `npm run start`, you should see the completely optimized experience without jitter.

This will spin up a FastAPI server, along with the NextJS server. If you're using Tailscale, you'll be able to see your app from the iPhone if you have the Tailscale app installed and the Jetson is on your Tailnet.

From there, you can click "Record 30s" and have 30s of raw sensor data recorded for analysis later. 

Alternatively, you can click "Record Video", and record as much video of your trip as you like, saved with a timestamp of the beginning of the recording in MP4 format.

> Note: trtexec is in the container at: /usr/src/tensorrt/bin/trtexec

## Replaying in Rerun

![rerun gui](./assets/rerun.png)

You have two ways of using Rerun.

I currently use and run the webapp here to control recording from my iPhone. This lets me hit record when I'm out, and allows the Jetson to record to the SSD I've added to it.

But when I'm developing or adding new sensors, I use an iPython session, and connect to my desktop version of Rerun.

To do this I:

```python
import rerun as rr
import numpy as np

rr.init("realsense")
# connect to my macbook on tailscale
rr.connect("100.79.94.136:9876")

rr.log("any value name", rr.Image(...)) # log your datastructure here
```

The big point is the IP address of my laptop or desktop in the `rr.connect` line. This let's me just stream values over the Tailscale network and see if I've got my data structures right.

## Networking Setup

![networking setup](./assets/network-bicyclist.png)

I've installed Tailscale on my iPhone and my Jetson Orin Nano. 

Once I've done that, I can set up my Jetson Orin Nano to run a webserver accessible from my phone. My Jetson Orin Nano just needs to tether the hotspot from my iPhone while on bicycle rides.

For some reason, I wasn't able to discover the Wifi hotspot from my iPhone until _after_ my laptop connected to it. 

So, in order to have this work:
```
Enable Wifi hotspot on iPhone -> Connect with laptop -> Scan for Wifi -> Find the right mac address -> connect w/ password
```

These commands will scan for the wifi:

```bash
$ sudo nmcli dev wifi rescan
$ sudo nmcli dev wifi
```

And then once you see the address of your Wifi hotspot name you can:

```
$ sudo nmcli d wifi connect AS:0D:20:20:92 password theactualpassword
```

From there, each time you bring up the Jetson, it will autoconnect to the Wifi hotspot.

## Running the Server via Container

I've included a `Dockerfile` to run the container on your Jetson Orin Nano.

To run it, you should be able to do a:

```bash
$ ./launch_bicycle.sh
```

From the repository's directory. This will build the container image, and then drop you into a shell inside of the container.

From there, you can cd `/bicyclist/bicycle-app`, and then run a `npm i`, followed by `npm run dev` to enable live reloading for development.

Once you're ready to deploy (and get better framerates), you can do a:

```bash
$ npm run build
$ npm run start
```

This will run a more optimized version of the application, allowing for the maximum fps on the system.

## Running the Server on Startup

![JTOP](./assets/jtop.png)

If you want to have the webserver start when your Jetson is turned on automatically, I've included an example service for systemd, `bicyclist-protection.service`. Copy this to `/etc/systemd/system/`.

You'll need to replace my username with your username, and the location of this repository's installation there too.

I use [nvm](https://github.com/nvm-sh/nvm) to manage my Node version, so the script loads and does that, as set in `bicycle-app/launch.sh`. Double check that your username and path are set here, replace my values with the ones that match your setup. Then you can reload systemctl and start the service:

```bash
$ sudo systemctl daemon-reload
$ sudo systemctl start bicyclist-protection.service
```

You can check to see if the service started successfully by running a:

```bash
$ journalctl -u  bicyclist-protection
```

If everything went well, you should see something like:

```bash
ubuntu launch.sh[45933]: > concurrently "python3 -m uvicorn api.index:app --host 0.0.0.0" "next start"
ubuntu launch.sh[45949]: [1]    ▲ Next.js 14.1.0
ubuntu launch.sh[45949]: [1]    - Local:        http://localhost:3000
ubuntu launch.sh[45949]: [1]
ubuntu launch.sh[45949]: [1]  ✓ Ready in 676ms
```

And then you should be able to visit the service at port 3000.

If you'd like to monitor your application, I recommmend using the [jetson_stats](https://github.com/rbonghi/jetson_stats) project. Install it with pip:

```bash
$ sudo pip3 install -U jetson-stats
```

Reboot the Jetson, and run it with a `jtop` to monitor usage.

## Realsense Installation on Jetson Orin Nano

The default installation doesn't seem to work. Here's what I did in order to build:

```bash
$ cd librealsense
$ mkdir build
$ cd build
$ cmake ../ -DBUILD_PYTHON_BINDINGS:bool=true -DPYTHON_EXECUTABLE=/home/stankley/.pyenv/shims/python3 -DBUILD_WITH_CUDA=true -DCMAKE_BUILD_TYPE=release -DBUILD_EXAMPLES=true -DCMAKE_CUDA_ARCHITECTURES=75 -DFORCE_RSUSB_BACKEND=TRUE
$ sudo make install
$ cp /usr/local/OFF/*.so ~/.local/lib/python3.10/site-packages/
```

You'll need to replace `python3.10` with your Python version as appropriate. A `which python3` should start steering you in the right direction.

## Realsense IMU to Orientation Quaternion

I use the [imufusion library](https://github.com/xioTechnologies/Fusion) to do sensor fusion across the accelerometer and gyroscope on the Realsense.

I've also added a [GPS device](https://www.sparkfun.com/products/17285) to (eventually) do correction via heading, which imufusion supports.

## AWR1443 mmWave Radar Data Collection

You _must_ use Jetpack 6. Otherwise, there's a bug in the UART controller for the Jetson Orin Nano on Jetpack 5 that prevents the AWR1443 from running. 

Once you've done that, install the requirements for the [pymmwave](https://github.com/m6c7l/pymmw) project.

From there, you can edit the `source/mss/14_mmw-xWR14xx.cfg` file to just run the resources you need, and extract running features from the `source/app/` directory.

I plan on using the point cloud to do DBSCAN as outlined in the paper [here](https://ieeexplore.ieee.org/document/9916096).

## Discovering Video Devices for Inference, in Containers

Because computer vision research tends to move quickly, it can be tricky to install the correct dependencies to run multiple projects in the same repository. 

To cope with this, and to make your work reproducible, you can use containers. But using containers in embedded systems is a bit trickier than normal container development, as you have to deal with displays, GPUs, volumes, and USB devices all in one go.

It also makes debugging more difficult. For example, if you want to expose a webcam to your container, you have to know which one you want, _before_ you run the container.

So it's not just working from within the container itself. It involves bouncing back and forth between environments, and keeping track of them.

For example, here's how we check and see which devices we have: (make sure you've installed `v4l-utils`)

```
$ v4l2-ctl --list-devices
NVIDIA Tegra Video Input Device (platform:tegra-camrtc-ca):
	/dev/media0

Intel(R) RealSense(TM) Depth Ca (usb-3610000.usb-1.1):
	/dev/video0
	/dev/video1
	/dev/video2
	/dev/video3
	/dev/video4
	/dev/video5
	/dev/media1
	/dev/media2

HD Pro Webcam C920 (usb-3610000.usb-2.2):
	/dev/video6
	/dev/video7
	/dev/media3
```

With this, we can then add a parameter to mount these devices in the container:

```
$ docker run --device /dev/bus/usb --device /dev/video0 --device /dev/video1 --device /dev/video2 --device /dev/video3 --device /dev/video4 --device /dev/video5 --device /dev/video6 --device /dev/video7 <containername> /bin/bash
```

