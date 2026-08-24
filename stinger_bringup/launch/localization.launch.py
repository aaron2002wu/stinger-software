'''
This launches the robot localization package
This fuses the IMU and GPS data
This publishes topic /odometry/filtered and TF
'''

from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
import os
import xacro

def generate_launch_description():

    pkg_share = get_package_share_directory('stinger_bringup')

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )
    use_sim_time = LaunchConfiguration('use_sim_time')

    ekf_config_path = PythonExpression([
        f"'{pkg_share}/config/ekf_sim.yaml' if '", use_sim_time, "' == 'true' else '{pkg_share}/config/ekf.yaml'"
    ])
    navsat_transform_file_path = os.path.join(pkg_share, 'config', 'navsat_transform.yaml')

    # URDF File Path
    xacro_file = os.path.join(
        get_package_share_directory('stinger_description'),
        'urdf',
        'stinger_tug.urdf.xacro'
    )
    
    # Get URDF from xacro
    robot_description = xacro.process(xacro_file)

    return LaunchDescription([
        use_sim_time_arg,

        # Robot description publisher
        Node(
            name = 'robot_state_publisher',
            package = 'robot_state_publisher',
            executable = 'robot_state_publisher',
            output = 'screen',
            parameters = [{
                'robot_description': robot_description,
                'use_sim_time': use_sim_time
            }]
        ),
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            parameters=[ekf_config_path, {'use_sim_time': use_sim_time}],
        ),    
        Node(
            package='robot_localization',
            executable='navsat_transform_node',
            name='navsat_transform_node',
            parameters=[navsat_transform_file_path, {'use_sim_time': use_sim_time}],
            respawn=True,
            remappings=[
                ('/imu', '/stinger/imu/relative'),
                ('/gps/fix', '/stinger/gps/fix')
            ],
        ),
        Node(
            package='stinger_bringup',
            executable='imu_republisher',
            name='imu_republisher',
            output='screen'
        )
    ])
