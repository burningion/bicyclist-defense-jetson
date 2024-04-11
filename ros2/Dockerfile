FROM nvcr.io/nvidia/isaac/ros:aarch64-ros2_humble_b7e1ed6c02a6fa3c1c7392479291c035
RUN pip install pillow --upgrade 
RUN apt-get update && apt-get install -y sudo apt-utils
RUN apt-get install -y libpthread-stubs0-dev ros-humble-perception-pcl ros-humble-composition 
RUN git clone https://github.com/kimsooyoung/mmwave_ti_ros.git /mmwave_ti_ros
RUN source /opt/ros/humble/setup.bash && colcon build --packages-select gtest_vendor gmock_vendor
RUN source /opt/ros/humble/setup.bash && colcon build --symlink-install --packages-select serial && source install/local_setup.bash
RUN source /opt/ros/humble/setup.bash && colcon build --symlink-install --packages-select ti_mmwave_ros2_interfaces && source install/local_setup.bash
RUN source /opt/ros/humble/setup.bash && colcon build --symlink-install --packages-select ti_mmwave_ros2_pkg && source install/local_setup.bash
RUN source /opt/ros/humble/setup.bash && colcon build --symlink-install --packages-select ti_mmwave_ros2_examples && source install/local_setup.bash