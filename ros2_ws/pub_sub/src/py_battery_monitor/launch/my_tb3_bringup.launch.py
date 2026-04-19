import os

# 1. 引入模組：尋找套件路徑
# 這個模組用來尋找 ROS 2 套件在系統中的實際「安裝」路徑 (通常在 install/ 目錄下)
from ament_index_python.packages import get_package_share_directory

# 2. 引入模組：Launch 核心系統
# LaunchDescription 是一個容器，用來打包所有你想執行的啟動指令
from launch import LaunchDescription
# IncludeLaunchDescription 允許我們把別人的 Launch 檔「包」進來，當作自己的一部分
from launch.actions import IncludeLaunchDescription
# 告訴系統我們要 Include 的檔案是一個 Python 格式的 Launch 檔
from launch.launch_description_sources import PythonLaunchDescriptionSource

# 3. 引入模組：節點操作
# Node 用來定義要啟動的單一 ROS 2 節點及其各項參數與設定
from launch_ros.actions import Node

def generate_launch_description():
    """
    這個函式是 ROS 2 Launch 系統的標準進入點。
    系統啟動時會尋找這個函式，並且它必須回傳一個 LaunchDescription 物件。
    """

    # =====================================================================
    # 動作 1：尋找並載入 TB3 的虛擬世界 (Gazebo)
    # =====================================================================
    # 這裡不能寫死絕對路徑，因為每個人的電腦安裝位置不同。
    # get_package_share_directory 會自動幫我們找到 'turtlebot3_gazebo' 裝在哪裡
    tb3_gazebo_pkg_dir = get_package_share_directory('turtlebot3_gazebo')
    
    # 利用 os.path.join 將路徑組合起來，指向目標：turtlebot3_world.launch.py
    tb3_world_launch_path = os.path.join(
        tb3_gazebo_pkg_dir, 
        'launch', 
        'turtlebot3_world.launch.py'
    )

    # 把剛剛找到的官方 Launch 檔，包裝成一個可以被執行的動作 (Action)
    gazebo_launch_action = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(tb3_world_launch_path)
    )

    # =====================================================================
    # 動作 2：啟動 Rviz2 監控畫面
    # =====================================================================
    rviz_node = Node(
        package='rviz2',          # Rviz2 所在的套件名稱
        executable='rviz2',       # 實際執行的程式名稱
        name='rviz2_monitor',     # 在目前的 ROS 2 系統中，幫這個節點取的新名字
        output='screen'           # 'screen' 代表將此節點的 print/Log 直接輸出到目前的終端機畫面上
        # 實務上我們會加上 arguments=['-d', rviz設定檔路徑] 來免除手動設定畫面
    )

    # =====================================================================
    # 動作 3：啟動我們自訂的控制節點 (並示範 Remappings 轉接)
    # =====================================================================
    # 假設我們寫好的節點原本會發布速度到 '/my_custom_speed' 這個主題上，
    # 但 TB3 機器人硬體只聽得懂 '/cmd_vel'。我們可以用 remappings 幫它重新導向。
    custom_control_node = Node(
        package='py_battery_monitor',    # 替換成你自己的開發套件名稱
        executable='sensor',      # 替換成你的執行檔名稱 (用之前的發布者 talker 做示範)
        name='my_auto_driver',    # 幫這個控制節點取個響亮的名字
        remappings=[
            # 格式為 tuple：('/你程式碼裡寫的主題名稱', '/系統實際上要對接的主題名稱')
            ('/battery_status', '/cmd_vel') 
        ]
    )

    # =====================================================================
    # 最終打包：將所有動作交給 ROS 2 執行
    # =====================================================================
    # 將上述定義好的 3 個動作放進陣列中，一鍵啟動！
    return LaunchDescription([
        gazebo_launch_action,
        rviz_node,
        custom_control_node
    ])