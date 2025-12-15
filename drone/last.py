#!/usr/bin/env python3
"""
Simple outdoor GPS takeoff script.

- Connects to Pixhawk on /dev/serial0 @ 57600
- Waits for GPS + EKF to be ready
- Arms
- Takes off to 1.0 m AGL
- Holds that altitude in GUIDED mode
- On Ctrl+C or error: switches to LAND and exits

!!! FLY SAFELY !!!
- Use outside, in a wide open area
- Make sure RC is ready so you can take over (e.g. STABILIZE on a switch)
"""

import time
import sys
import threading
from dronekit import connect, VehicleMode
from pymavlink import mavutil
from crop_inspection import crop_inspection

# === CONFIG ===
CONNECTION_STRING = "/dev/serial0"
BAUD = 57600
TARGET_ALTITUDE_M = 0.6

# === SHARED GPS DATA ===
# Global variable to expose GPS coordinates to other modules
current_gps_position = None  # Will be tuple: (lat, lon, alt)
vehicle_instance = None  # Shared vehicle instance


def get_current_gps():
    """
    Returns the current GPS position as (lat, lon, alt).
    Returns None if not available yet.
    Can be called from other modules that import this file.
    """
    if vehicle_instance is not None:
        gps_loc = vehicle_instance.location.global_frame
        alt = vehicle_instance.location.global_relative_frame.alt
        if gps_loc.lat is not None and gps_loc.lon is not None:
            return (gps_loc.lat, gps_loc.lon, alt if alt is not None else 0.0)
    return current_gps_position


def safe_land(vehicle, reason=""):
    """Switch to LAND mode safely."""
    try:
        print(f"[EMERGENCY] Initiating LAND. Reason: {reason}")
        if vehicle.mode.name != "LAND":
            vehicle.mode = VehicleMode("LAND")
            # Wait for mode change confirmation
            for _ in range(20):
                if vehicle.mode.name == "LAND":
                    break
                time.sleep(0.1)
        # Optional: wait until almost on ground before disarming
        for _ in range(200):  # up to ~20s
            alt = vehicle.location.global_relative_frame.alt
            print(f"[LANDING] Altitude: {alt:.2f} m")
            if alt is not None and alt < 0.15:
                break
            time.sleep(0.1)

        # Disarm if still armed
        if vehicle.armed:
            print("[INFO] Disarming...")
            vehicle.armed = False
            for _ in range(30):
                if not vehicle.armed:
                    break
                time.sleep(0.2)
        print("[INFO] Land sequence complete.")
    except Exception as e:
        print(f"[ERROR] Exception during safe_land: {e}")


def wait_for_gps_and_ekf(vehicle):
    """Wait for GPS fix and EKF readiness."""
    print("[CHECK] Waiting for GPS fix (>= 3D) ...")
    while True:
        gps = vehicle.gps_0
        fix = gps.fix_type
        sats = gps.satellites_visible
        print(f"[GPS] fix_type={fix}, sats={sats}")
        if fix >= 3 and sats is not None and sats >= 6:
            break
        time.sleep(1.0)

    print("[CHECK] Waiting for vehicle.is_armable ...")
    while not vehicle.is_armable:
        print("[STATUS] Vehicle not armable yet. "
              f"Mode={vehicle.mode.name}, EKF OK?={vehicle.ekf_ok}")
        time.sleep(1.0)
    print("[CHECK] GPS + EKF ready.")


def arm_and_takeoff(vehicle, target_alt):
    """
    Arms vehicle and fly to target_alt (meters) using simple_takeoff.
    """
    print("[MISSION] arm_and_takeoff start")

    # Make sure we're in GUIDED
    if vehicle.mode.name != "GUIDED":
        print(f"[INFO] Current mode: {vehicle.mode.name} → requesting GUIDED")
        vehicle.mode = VehicleMode("GUIDED")
        for _ in range(50):  # up to ~5 sec
            if vehicle.mode.name == "GUIDED":
                break
            time.sleep(0.1)
        if vehicle.mode.name != "GUIDED":
            raise RuntimeError("Failed to enter GUIDED mode")

    # Arm
    print("[INFO] Arming motors...")
    vehicle.armed = True

    t0 = time.time()
    while not vehicle.armed:
        print(f"[INFO] Waiting for arm... mode={vehicle.mode.name}, armed={vehicle.armed}")
        time.sleep(0.5)
        if time.time() - t0 > 15:
            raise RuntimeError("Timeout while waiting for arming")

    print("[INFO] Armed. Taking off...")
    vehicle.simple_takeoff(target_alt)

    # Wait until we reach target altitude (or timeout)
    t0 = time.time()
    while True:
        alt = vehicle.location.global_relative_frame.alt
        if alt is None:
            print("[ALT] Altitude unknown yet...")
        else:
            print(f"[ALT] Current: {alt:.2f} m / Target: {target_alt:.2f} m")

        # Basic check: if mode changed away from GUIDED during takeoff, bail
        if vehicle.mode.name != "GUIDED":
            raise RuntimeError(f"Mode changed during takeoff: {vehicle.mode.name}")

        # Consider reached when >= 95% of target
        if alt is not None and alt >= target_alt * 0.95:
            print("[MISSION] Target altitude reached")
            break

        if time.time() - t0 > 30:
            raise RuntimeError("Timeout while climbing to target altitude")

        time.sleep(0.5)


def send_body_velocity(vehicle, vx, vy, vz, duration_s):
    """
    Move the drone with velocity in BODY_NED frame.

    vx: forward  (m/s, +forward)
    vy: right    (m/s, +right)
    vz: down     (m/s, +down; negative = up)
    duration_s: how long to keep this velocity command
    """
    if not vehicle.armed:
        raise RuntimeError("send_body_velocity called while vehicle is disarmed")

    if vehicle.mode.name != "GUIDED":
        raise RuntimeError(f"send_body_velocity requires GUIDED mode, got {vehicle.mode.name}")

    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,                      # time_boot_ms (ignored)
        0, 0,                   # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_NED,  # frame relative to drone body
        0b0000111111000111,     # type_mask: use only velocity
        0, 0, 0,                # x, y, z positions  (not used)
        vx, vy, vz,             # velocities in m/s
        0, 0, 0,                # accelerations (not used)
        0, 0                    # yaw, yaw_rate (not used)
    )

    t0 = time.time()
    while time.time() - t0 < duration_s:
        # if mode changed mid-move, bail
        if vehicle.mode.name != "GUIDED":
            raise RuntimeError(f"Mode changed during velocity move: {vehicle.mode.name}")

        vehicle.send_mavlink(msg)
        vehicle.flush()
        time.sleep(0.1)

    # send zero velocity to stop
    stop_msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0, 0, 0,
        mavutil.mavlink.MAV_FRAME_BODY_NED,
        0b0000111111000111,
        0, 0, 0,
        0, 0, 0,                # zero velocity
        0, 0, 0,
        0, 0
    )
    vehicle.send_mavlink(stop_msg)
    vehicle.flush()


def main(socket_client=None):
    global current_gps_position, vehicle_instance
    print("[INFO] Connecting to Pixhawk on "
          f"{CONNECTION_STRING} @ {BAUD} ...")
    vehicle = None
    try:

        print("[INFO] Connecting...")
        vehicle = connect("/dev/serial0", baud=57600, wait_ready=False)
        vehicle_instance = vehicle  # Make vehicle accessible globally
        print("[INFO] Connected (low level). Now waiting for attributes...")

        # Wait specifically for some key attributes
        vehicle.wait_ready('gps_0', timeout=30)
        vehicle.wait_ready('attitude', 'location.global_relative_frame', timeout=30)
        vehicle.wait_ready('armed', 'mode', timeout=30)

        print("[INFO] Vehicle attributes ready.")

        wait_for_gps_and_ekf(vehicle)

        # Set GUIDED & arm + takeoff to 1m
        arm_and_takeoff(vehicle, TARGET_ALTITUDE_M)
        time.sleep(.5)
        print("[MOVE] Going forward about 4 m...")
        send_body_velocity(vehicle, vx=0.5, vy=0.0, vz=0.0, duration_s=2.0)
        time.sleep(.5)
        import os

        # Take a picture
        os.system(
            "v4l2-ctl --device=/dev/video0 "
            "--set-fmt-video=width=1920,height=1080,pixelformat=MJPG "
            "--stream-mmap --stream-count=1 --stream-to=capture.jpg"
        )
        
        # Start crop inspection in a separate thread
        inspection_thread = threading.Thread(target=crop_inspection, args=("capture.jpg",get_current_gps() ,socket_client))
        inspection_thread.start()
        print("[INFO] Crop inspection started in background thread")
        
        # Wait for inspection to complete before landing
        inspection_thread.join()
        print("[INFO] Crop inspection completed")

        # take a photo and return - must be async since drifwt
        send_body_velocity(vehicle, vx=-0.5, vy=0.0, vz=0.0, duration_s=2.0)
        # and land
        safe_land(vehicle, reason="Mission  complete")



    except KeyboardInterrupt:
        print("\n[EMERGENCY] Ctrl+C detected – initiating LAND and exit.")
        if vehicle is not None:
            safe_land(vehicle, reason="Ctrl+C")
    except Exception as e:
        print(f"[ERROR] {e}")
        if vehicle is not None:
            safe_land(vehicle, reason=str(e))
    finally:
        if vehicle is not None:
            print("[INFO] Closing vehicle connection...")
            vehicle.close()
        print("[INFO] Program exit.")


if __name__ == "__main__":
    main()
