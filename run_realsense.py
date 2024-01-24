import pyrealsense2 as rs
import rerun as rr
import numpy as np

rr.init("realsense")
# connect to my macbook on tailscale
# rr.connect("100.79.94.136:9876")
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
profile = pipeline.start(config)

for i in range(10):
    frames = pipeline.wait_for_frames()
    rr.log("realsense color", rr.Image(np.asanyarray(frames.get_color_frame().get_data())))
# save for later analysis, can do an scp
rr.save("realsense.rrd")
