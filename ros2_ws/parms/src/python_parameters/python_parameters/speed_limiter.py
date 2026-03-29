import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor

class SpeedLimiterNode(Node):
    def __init__(self):
        super().__init__('speed_limiter')
        
        # 1. 建立參數描述 (選用，但推薦)
        # 讓其他使用者知道這個參數的用途
        my_desc = ParameterDescriptor(description='機器人的最高移動速限 (m/s)')
        
        # 2. 宣告參數：(參數名稱, 預設值, 描述)
        # 系統會從預設值 '1.0' 自動推斷出這個參數是浮點數 (Double) 型態
        self.declare_parameter('max_speed', 1.0, my_desc)

        # 3. 建立計時器，每 1 秒讀取並印出當前限速
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        # 4. 取得參數的當前值 (加上 .double_value 確保型態正確)
        current_speed_limit = self.get_parameter('max_speed').get_parameter_value().double_value
        
        # 印出狀態
        self.get_logger().info('目前最高限速設定為: %.2f m/s' % current_speed_limit)

def main():
    rclpy.init()
    node = SpeedLimiterNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()