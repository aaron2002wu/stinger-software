"""Launch the Gazebo simulation, spawn the Stinger Tugboat, and start localization with sim time."""

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


def generate_launch_description():
    stinger_sim_share = get_package_share_directory('stinger_sim')
    stinger_desc_share = get_package_share_directory('stinger_description')
    stinger_bringup_share = get_package_share_directory('stinger_bringup')

    # 1. World Argument
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='default.world',
        description='World file to load in Gazebo'
    )
    world = LaunchConfiguration('world')

    # 2. Launch Gazebo Simulation & ROS-GZ Bridge
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([stinger_sim_share, 'launch', 'sim.launch.py'])
        ),
        launch_arguments={'world': world}.items()
    )

    # 3. Spawn the Stinger Tugboat in Gazebo
    spawn_vehicle = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([stinger_desc_share, 'launch', 'spawn.launch.py'])
        )
    )

    # 4. Launch Localization with use_sim_time:=true (Delayed 5s like gt-bbx)
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([stinger_bringup_share, 'launch', 'localization.launch.py'])
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )
    delayed_localization = TimerAction(period=5.0, actions=[localization])

    return LaunchDescription([
        world_arg,
        gz_sim,
        spawn_vehicle,
        delayed_localization
    ])
