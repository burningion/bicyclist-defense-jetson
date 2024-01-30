from __future__ import annotations

import argparse
from ublox_gps import UbloxGps
import serial
import numpy as np
import pyrealsense2 as rs
import rerun as rr  # pip install rerun-sdk
import imufusion

# sorry, replace the id with your own:
port = serial.Serial('/dev/serial/by-id/usb-u-blox_AG_-_www.u-blox.com_u-blox_GNSS_receiver-if00', baudrate=38400, timeout=1)
gps = UbloxGps(port)

# need to keep track of our orientation
ahrs = imufusion.Ahrs()

# coords = gps.geo_coords()
# coords.lat, coords.lon

def run_realsense(num_frames: int | None) -> None:
    # Visualize the data as RDF
    rr.log("realsense", rr.ViewCoordinates.RDF, timeless=True)

    # Open the pipe
    pipe = rs.pipeline()
    profile = pipe.start()

    # We don't log the depth exstrinsics. We treat the "realsense" space as being at
    # the origin of the depth sensor so that "realsense/depth" = Identity

    # Get and log depth intrinsics
    depth_profile = profile.get_stream(rs.stream.depth)
    depth_intr = depth_profile.as_video_stream_profile().get_intrinsics()
    # This approach is wrong, we need frames to calculate orientation
    #accel_profile = profile.get_stream(rs.stream.accel)
    # accel_intr = accel_profile.as_motion_stream_profile().get_motion_intrinsics()
    #  Accel(0) @ 63fps MOTION_XYZ32F on the D455 by default
    #  accessed via: accel_intr.data 
    #gyro_profile = profile.get_stream(rs.stream.gyro)
    #gyro_intr = accel_profile.as_motion_stream_profile().get_motion_intrinsics()
    # Gyro(0) @ 200fps MOTION_XYZ32F on the D455 by default
    # accessed via: gyro_intr.data

    rr.log(
        "realsense/depth/image",
        rr.Pinhole(
            resolution=[depth_intr.width, depth_intr.height],
            focal_length=[depth_intr.fx, depth_intr.fy],
            principal_point=[depth_intr.ppx, depth_intr.ppy],
        ),
        timeless=True,
    )

    # Get and log color extrinsics
    rgb_profile = profile.get_stream(rs.stream.color)

    rgb_from_depth = depth_profile.get_extrinsics_to(rgb_profile)
    rr.log(
        "realsense/rgb",
        rr.Transform3D(
            translation=rgb_from_depth.translation,
            mat3x3=np.reshape(rgb_from_depth.rotation, (3, 3)),
            from_parent=True,
        ),
        timeless=True,
    )

    # Get and log color intrinsics
    rgb_intr = rgb_profile.as_video_stream_profile().get_intrinsics()

    rr.log(
        "realsense/rgb/image",
        rr.Pinhole(
            resolution=[rgb_intr.width, rgb_intr.height],
            focal_length=[rgb_intr.fx, rgb_intr.fy],
            principal_point=[rgb_intr.ppx, rgb_intr.ppy],
        ),
        timeless=True,
    )

    # Read frames in a loop
    frame_nr = 0
    try:
        while True:
            if num_frames and frame_nr >= num_frames:
                break

            rr.set_time_sequence("frame_nr", frame_nr)
            frame_nr += 1

            frames = pipe.wait_for_frames()
            for f in frames:
                # log accel first @ 63fps
                accel = frames[2].as_motion_frame().get_motion_data()
                gyro = frames[3].as_motion_frame().get_motion_data()
                gyro_np = np.array([gyro.x, gyro.y, gyro.z])
                accel_np = np.array([accel.x, accel.y, accel.z])
                ahrs.update_no_magnetometer(gyro_np, accel_np, 1 / 63) # :/
                quaternion_xyzw = np.roll(np.array(ahrs.quaternion.wxyz), -1)

                rr.log("realsense", rr.Transform3D(rotation=rr.Quaternion(xyzw=quaternion_xyzw)))
                # Log the depth frame
                depth_frame = frames.get_depth_frame()
                depth_units = depth_frame.get_units()
                depth_image = np.asanyarray(depth_frame.get_data())

                rr.log("realsense/depth/image", rr.DepthImage(depth_image, meter=1.0 / depth_units))

                # Log the color frame
                color_frame = frames.get_color_frame()
                color_image = np.asanyarray(color_frame.get_data())
                rr.log("realsense/rgb/image", rr.Image(color_image))
    finally:
        pipe.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Streams frames from a connected realsense depth sensor.")
    parser.add_argument("--num-frames", type=int, default=None, help="The number of frames to log")
    rr.init("realsense example")
    args = parser.parse_args()

    
    run_realsense(args.num_frames)

    rr.save("realsense.rrd")


if __name__ == "__main__":
    main()