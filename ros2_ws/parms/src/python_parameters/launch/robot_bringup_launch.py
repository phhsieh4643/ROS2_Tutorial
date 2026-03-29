from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='python_parameters',  # 替換成你的套件名稱 (C++ 則是 cpp_parameters)
            executable='speed_limiter',   # 你的執行檔名稱
            name='custom_speed_limiter',
            output='screen',
            emulate_tty=True,
            
            # 👇 在這裡注入參數值！(例如將預設的 1.0 改為 0.3)
            parameters=[
                {'max_speed': 0.3}
            ]
        )
    ])