FROM nvcr.io/nvidia/isaac/ros:aarch64-ros2_humble_b7e1ed6c02a6fa3c1c7392479291c035
RUN pip install pillow --upgrade 
RUN apt-get update && apt-get install -y sudo apt-utils
RUN apt-get install -y libpthread-stubs0-dev ros-humble-perception-pcl ros-humble-composition 
RUN git clone https://github.com/kimsooyoung/mmwave_ti_ros.git /mmwave_ti_ros
RUN cd /mmwave_ti_ros && colcon build --symlink-install --packages-select serial
