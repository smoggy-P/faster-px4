# FASTER: Fast and Safe Trajectory Planner for Navigation in Unknown Environments #

### This is a repository to make FASTER planner working in PX4-gazebo simulation, forked from https://github.com/mit-acl/faster

## General Setup
FASTER-px4 has been tested with Ubuntu 18.04/ROS Melodic 

1. Install the [simulation for PX4](https://docs.px4.io/master/en/simulation/).

2. Install the [Gurobi Optimizer](https://www.gurobi.com/products/gurobi-optimizer/). You can test your installation typing `gurobi.sh` in the terminal. 

3. Install the following dependencies:
```
sudo apt-get install ros-"${ROS_DISTRO}"-gazebo-ros-pkgs ros-"${ROS_DISTRO}"-mavros-msgs ros-"${ROS_DISTRO}"-tf2-sensor-msgs
```
```
python -m pip install pyquaternion
```

4. Create a workspace, and clone this repo and its dependencies:
```
mkdir ws && cd ws && mkdir src && cd src
git clone https://github.com/mit-acl/faster.git
wstool init
wstool merge ./faster/faster/install/faster_px4.rosinstall

```

In the following, remember (once the workspace is compiled) to add this to your `~/.bashrc`:
```
source PATH_TO_YOUR_WS/devel/setup.bash
``` 

### Instructions to use FASTER with an aerial robot:

1. Compile and run the PX4 simulation:
```
cd /PATH/TO/PX4-Autopilot/
DONT_RUN=1 make px4_sitl_default gazebo
source Tools/setup_gazebo.bash $(pwd) $(pwd)/build/px4_sitl_default
export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:$(pwd)
export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:$(pwd)/Tools/sitl_gazebo
roslaunch px4 posix_sitl.launch
```

2. Set the noise you want to have for localization and depth camera in **odom_and_camera_noise.launch** file in **noise_maker** package and launch the noise maker:
```
roslaunch noise_maker odom_and_camera_noise.launch
```

3. Run the node for control:

```
rosrun pva_tracker tracker_sim_auto_arm_takeoff 
```

5. Compile the planner code and launch the demo:
```
cd /PATH_TO_PLANNER_WS/src
wstool update -j8
cd ..
catkin config -DCMAKE_BUILD_TYPE=Release
catkin build
```

The blue grid shown in Rviz is the unknown space and the orange one is the occupied-known space. Now you can click `Start` in the GUI, and then, in RVIZ, press `G` (or click the option `2D Nav Goal` on the top bar of RVIZ) and click any goal for the drone. 

> **_NOTE (TODO):_**  Right now the radius of the drone plotted in Gazebo (which comes from the `scale` field of `quadrotor_base_urdf.xacro`) does not correspond with the radius specified in `faster.yaml`. 

## Issues when installing Gurobi:

If you find the error:
```
“gurobi_continuous.cpp:(.text.startup+0x74): undefined reference to
`GRBModel::set(GRB_StringAttr, std::__cxx11::basic_string<char,
std::char_traits<char>, std::allocator<char> > const&)'”
```
The solution is:

```bash
cd /opt/gurobi800/linux64/src/build  #Note that the name of the folder gurobi800 changes according to the Gurobi version
sudo make
sudo cp libgurobi_c++.a ../../lib/
```

## Issues with other possible errors:

You can safely ignore these terminal errors:
* `Error in REST request` (when using ROS Melodic)
* `[ERROR] [...]: GazeboRosControlPlugin missing <legacyModeNS> while using DefaultRobotHWSim, defaults to true.` (when using the ground robot)
* `[ERROR] [...]: No p gain specified for pid.  Namespace: /gazebo_ros_control/pid_gains/front_left_wheel.` (when using the ground robot)
