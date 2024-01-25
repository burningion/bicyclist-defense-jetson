# Bicyclist Defense with NVIDIA Jetson Orin Nano (WIP)

Defending Bicyclists from Erratic Drivers with Computer Vision and mmWave Radar

![Bicyclist Safety Architecture Diagram](/images/bicyclist-safety/.png)

## Networking Setup

I've installed Tailscale on my iPhone and my Jetson Orin Nano. 

Once I've done that, I can set up my Jetson Orin Nano to run a webserver for configuration on my phone. My Jetson Orin Nano just needs to tether from my iPhone.

For some reason, I wasn't able to discover the Wifi hotspot from my iPhone until _after_ my laptop connected to it. 

So, in order to have this work:

Enable Wifi hotspot on iPhone -> Connect with laptop -> Scan for Wifi -> Find the right mac address -> connect w/ password

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

## AWR1443 mmWave 

You _must_ use Jetpack 6. Otherwise, there's a bug in the UART controller for the Jetson Orin Nano. 

Once you've done that, install the requirements for the [pymmwave](https://github.com/m6c7l/pymmw) project.

From there, you can edit the `source/mss/14_mmw-xWR14xx.cfg` file to just run the resources you need, and extract running features from the `source/app/` directory.
