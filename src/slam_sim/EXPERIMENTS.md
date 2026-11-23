# LiDAR and odometry SLAM experiments

The robot remains a differential-drive configuration for every test.

## Recommended comparison

Experiment A is the baseline:

```bash
source install/setup.bash
ros2 launch slam_sim bringup.launch.py \
  lidar_update_rate:=10 lidar_noise_stddev:=0.0
```

Experiment B reduces the LiDAR update rate:

```bash
source install/setup.bash
ros2 launch slam_sim bringup.launch.py \
  lidar_update_rate:=5 lidar_noise_stddev:=0.0
```

Experiment C adds Gaussian range noise at 5 Hz:

```bash
source install/setup.bash
ros2 launch slam_sim bringup.launch.py \
  lidar_update_rate:=5 lidar_noise_stddev:=0.01
```

The launch logs from `scan_monitor` report the measured `/scan` rate. Move
the robot with the same teleoperation commands and route in every run.

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Save each result in the workspace's `slam_experiment_results` folder before
starting the next experiment. Run these commands from the workspace root:

```bash
mkdir -p slam_experiment_results
ros2 run nav2_map_server map_saver_cli \
  -f slam_experiment_results/experiment_a
```

Change the output filename for Experiments B and C.

## Odometry drift controls

These arguments make odometry differences explicit:

```text
wheel_mu               Wheel-ground friction coefficient
wheel_radius           Physical wheel radius
drive_wheel_radius     Wheel radius assumed by the odometry plugin
wheel_separation       Physical wheel separation
drive_wheel_separation Wheel separation assumed by the odometry plugin
```

Start with a small calibrated-geometry mismatch:

```bash
ros2 launch slam_sim bringup.launch.py \
  wheel_radius:=0.05 drive_wheel_radius:=0.047 \
  wheel_separation:=0.34 drive_wheel_separation:=0.31 \
  lidar_update_rate:=10 lidar_noise_stddev:=0.0
```

Test low traction or wheel slip by reducing `wheel_mu`, for example:

```bash
ros2 launch slam_sim bringup.launch.py \
  wheel_mu:=0.4 lidar_update_rate:=10 lidar_noise_stddev:=0.0
```

`odometry_monitor` reports planar displacement and incremental odometry path.
Compare it with the expected route and the RViz map in repeated runs.

## Experiment G: odometry noise

The odometry noise filter adds seeded Gaussian noise to forward translation
and yaw changes for each moving odometry update. It publishes the same noisy
pose on `/odom` and the `odom` to `base_footprint` transform, so SLAM receives
the perturbed odometry. Stationary updates do not accumulate noise.

Run from the workspace root with the same route as the baseline:

```bash
ros2 launch slam_sim bringup.launch.py \
  lidar_update_rate:=10 lidar_noise_stddev:=0.0 \
  odom_translation_noise_stddev:=0.001 \
  odom_yaw_noise_stddev:=0.001 odom_noise_seed:=42
```

The standard deviations apply per moving odometry update (metres and radians,
respectively); the fixed seed makes repeated runs reproducible. Save the map
as `slam_experiment_results/experiment_g` and compare it with A.

If G looks similar to A, repeat with a stronger but still controlled
odometry-noise level to test sensitivity:

```bash
ros2 launch slam_sim bringup.launch.py \
  lidar_update_rate:=10 lidar_noise_stddev:=0.0 \
  odom_translation_noise_stddev:=0.003 \
  odom_yaw_noise_stddev:=0.003 odom_noise_seed:=42
```

Keep the route and driving pattern unchanged, then save as
`slam_experiment_results/experiment_h`.

If H remains clean, repeat the same settings and route with a different seed
to check whether the result holds across noise realizations:

```bash
ros2 launch slam_sim bringup.launch.py \
  lidar_update_rate:=10 lidar_noise_stddev:=0.0 \
  odom_translation_noise_stddev:=0.003 \
  odom_yaw_noise_stddev:=0.003 odom_noise_seed:=7
```

Save this repeat as `slam_experiment_results/experiment_i` and compare it with
H.

## Experiment J: observe loop closure

A saved final map cannot show when or whether loop closure corrected drift.
Run the clean baseline, drive a route that returns to previously mapped walls,
and watch RViz while closing the loop:

```bash
ros2 launch slam_sim bringup.launch.py \
  lidar_update_rate:=10 lidar_noise_stddev:=0.0
```

Note whether duplicate wall segments align or the map visibly shifts when the
robot revisits the area. Save the final map as
`slam_experiment_results/experiment_j` and record the before/after observation
in `slam_experiment_results/comparison.md`.

## Comparison checklist

Record the following for A, B, and C:

- measured `/scan` rate;
- map distortion and wall alignment;
- obstacle and corner consistency;
- whether repeated walls merge cleanly;
- whether loop closure changes the complete map;
- `/odom` travel versus the physical route.
