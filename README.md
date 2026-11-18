# Robot SLAM & Nav2 Simulation Workspace

ROS 2 Humble workspace for simulating a differential-drive robot (`diff_bot`) equipped with a 360° 2D LiDAR and RGB-D camera in **Gazebo Fortress**, supporting 2D mapping with **SLAM Toolbox** and autonomous navigation with **Nav2**.

## Packages

| Package | Description |
| --- | --- |
| `slam_sim` | Robot URDF/Xacro (`diff_bot`), 4-room Gazebo Fortress world (`rooms.sdf`), `ros_gz_bridge`, and SLAM Toolbox mapping bringup. |
| `nav_sim` | Nav2 configuration (AMCL + Regulated Pure Pursuit / DWB controllers), saved occupancy map (`rooms_map`), RViz config (`nav.rviz`), and programmatic goal sender (`send_goals`). |

## Workspace Structure

```text
robot_slam_nav_ws/
├── src/
│   ├── slam_sim/
│   │   ├── config/slam_toolbox.yaml
│   │   ├── launch/{sim,bridge,slam,bringup}.launch.py
│   │   ├── rviz/slam.rviz
│   │   ├── urdf/robot.urdf.xacro
│   │   └── worlds/rooms.sdf
│   └── nav_sim/
│       ├── config/{nav2_params,nav2_params_dwb}.yaml
│       ├── launch/nav2_sim.launch.py
│       ├── maps/rooms_map.{yaml,pgm}
│       ├── nav_sim/send_goals.py
│       └── rviz/nav.rviz
├── .gitignore
└── README.md
```

## Prerequisites

- **ROS 2 Humble**
- **Gazebo Fortress** (`ignition-fortress`) with `ros_gz_sim` and `ros_gz_bridge`
- **SLAM Toolbox** (`ros-humble-slam-toolbox`)
- **Nav2** (`ros-humble-navigation2`, `ros-humble-nav2-bringup`, `ros-humble-nav2-simple-commander`)
- **Teleop** (optional, for manual mapping): `ros-humble-teleop-twist-keyboard`

## Build

```bash
cd ~/robot_slam_nav_ws
colcon build --symlink-install
source install/setup.bash
```

To rebuild a single package:

```bash
colcon build --packages-select nav_sim --symlink-install
source install/setup.bash
```

---

## 1. SLAM Mapping (`slam_sim`)

Launch Gazebo Fortress, the ROS-Gazebo bridge, RViz, and SLAM Toolbox:

```bash
source ~/robot_slam_nav_ws/install/setup.bash
ros2 launch slam_sim bringup.launch.py
```

Drive the robot around the rooms in a second terminal:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Save the generated map into `nav_sim/maps/`:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/robot_slam_nav_ws/src/nav_sim/maps/rooms_map
```

---

## 2. Autonomous Navigation (`nav_sim`)

Launch Gazebo Fortress, Nav2 (in a composed `nav2_container`), and RViz:

```bash
source ~/robot_slam_nav_ws/install/setup.bash

# Default: AMCL localisation on rooms_map + Regulated Pure Pursuit (rpp)
ros2 launch nav_sim nav2_sim.launch.py
```

### Launch Arguments

| Argument | Default | Description |
| --- | --- | --- |
| `controller` | `rpp` | Local controller: `rpp` (Regulated Pure Pursuit) or `dwb` (DWB Local Planner). |
| `slam` | `false` | Set `true` to localise with live SLAM Toolbox instead of AMCL + saved map. |
| `map` | `<nav_sim>/maps/rooms_map.yaml` | Path to occupancy map YAML (used when `slam:=false`). |
| `rviz` | `true` | Launch RViz with `nav.rviz`. |
| `gui` | `true` | Launch Gazebo Fortress GUI (`false` runs headless). |
| `use_composition` | `True` | Run Nav2 nodes inside `component_container_isolated`. |
| `startup_delay` | `12.0` | Seconds to wait for Gazebo and robot spawn before starting Nav2. |

Examples:

```bash
# Use DWB local planner
ros2 launch nav_sim nav2_sim.launch.py controller:=dwb

# Navigate while mapping with SLAM Toolbox
ros2 launch nav_sim nav2_sim.launch.py slam:=true

# Headless simulation (no Gazebo GUI or RViz)
ros2 launch nav_sim nav2_sim.launch.py gui:=false rviz:=false
```

### Sending Navigation Goals

Wait ~12–15 seconds after launch until the Navigation 2 panel in RViz reports **Navigation: active** and **Localization: active**.

#### Option A — Interactive (RViz)
1. Click **Nav2 Goal** in the RViz toolbar.
2. Click and drag on the map to set the target position and heading.

#### Option B — Command Line (`send_goals`)

```bash
source ~/robot_slam_nav_ws/install/setup.bash

# Navigate to a named room waypoint (sw, center, nw, ne, se)
ros2 run nav_sim send_goals --room ne

# Patrol all rooms (center -> nw -> ne -> se -> sw)
ros2 run nav_sim send_goals --patrol

# Send a custom goal in the map frame
ros2 run nav_sim send_goals --x 4.0 --y 1.5 --yaw 0.0

# Add --slam when Nav2 was launched with slam:=true
ros2 run nav_sim send_goals --room center --slam
```

### Map & Coordinate Reference

The robot spawns in Gazebo (`rooms.sdf`) at `(-4.0, -1.5, yaw=0.0)`, which corresponds to `(0.0, 0.0, yaw=0.0)` in the `rooms_map` frame (`map = gazebo + (4.0, 1.5)`). AMCL initializes automatically at `(0.0, 0.0, 0.0)` via `set_initial_pose: true`.

| Waypoint | `map` Frame `(x, y, yaw)` | Gazebo World `(x, y)` |
| --- | --- | --- |
| `sw` (spawn) | `(0.0, 0.0, 0.0)` | `(-4.0, -1.5)` |
| `center` | `(4.0, 1.5, 0.0)` | `(0.0, 0.0)` |
| `nw` | `(1.5, 4.0, 1.57)` | `(-2.5, 2.5)` |
| `ne` | `(6.5, 3.5, 0.0)` | `(2.5, 2.0)` |
| `se` | `(6.5, -0.5, -1.57)` | `(2.5, -2.0)` |

## License

Apache-2.0

