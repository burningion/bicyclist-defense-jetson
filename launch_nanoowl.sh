docker build . -t nanoowl
docker run --runtime nvidia -it --rm --network host --volume /tmp/argus_socket:/tmp/argus_socket --volume /etc/enctune.conf:/etc/enctune.conf --volume /etc/nv_tegra_release:/etc/nv_tegra_release --volume /tmp/nv_jetson_model:/tmp/nv_jetson_model --volume /home/stankley/Development/jetson-containers/data:/data --device /dev/snd --device /dev/bus/usb --device /dev/video0 --device /dev/video1 --device /dev/video2 --device /dev/video3 --device /dev/video4 --device /dev/video5 --device /dev/video6 --device /dev/video7 -p 7860:7860 nanoowl /bin/bash