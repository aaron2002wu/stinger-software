"""Launch the robot localization package (EKF + NavSat + Robot State Publisher).

Fuses IMU and GPS into a filtered state estimate on /odometry/filtered and broadcasts TF.
"""

import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('stinger_bringup')
    desc_share = get_package_share_directory('stinger_description')

    # ------ Launch Arguments ------
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )
    sim_time_param = {'use_sim_time': LaunchConfiguration('use_sim_time')}

    # ------ Config & URDF Paths ------
    ekf_config = os.path.join(pkg_share, 'config', 'ekf.yaml')
    navsat_config = os.path.join(pkg_share, 'config', 'navsat_transform.yaml')
    xacro_file = os.path.join(desc_share, 'urdf', 'stinger_tug.urdf.xacro')
    robot_description = xacro.process(xacro_file)

    # ------ Nodes ------
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }]
    )

    ekf_filter_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        parameters=[ekf_config, sim_time_param],
        output='screen'
    )

    navsat_transform_node = Node(
        package='robot_localization',
        executable='navsat_transform_node',
        name='navsat_transform_node',
        parameters=[navsat_config, sim_time_param],
        respawn=True,
        remappings=[
            ('/imu', '/stinger/imu/relative'),
            ('/gps/fix', '/stinger/gps/fix')
        ],
        output='screen'
    )

    imu_republisher = Node(
        package='stinger_bringup',
        executable='imu_republisher',
        name='imu_republisher',
        parameters=[sim_time_param],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time_arg,
        robot_state_publisher,
        ekf_filter_node,
        navsat_transform_node,
        imu_republisher
    ])
