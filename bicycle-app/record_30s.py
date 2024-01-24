import pyrealsense2 as rs
import rerun as rr
import numpy as np
import time

rr.init("realsense")
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
profile = pipeline.start(config)
start_time = time.time()  # Get the current time

while True:
    current_time = time.time()  # Update the current time
    elapsed_time = current_time - start_time  # Calculate elapsed time
    frames = pipeline.wait_for_frames()
    rr.log("realsense color", rr.Image(np.asanyarray(frames.get_color_frame().get_data())))
    if elapsed_time > 30:  # Check if 30 seconds have passed
        break  # Exit the loop
pipeline.stop()
rr.save("realsense.rrd")