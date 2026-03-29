import rclpy
from rclpy.node import Node
from std_msgs.msg import String # 引入內建的字串訊息格式

class BatterySensor(Node):
    def __init__(self):
        # 初始化節點並命名為 'battery_sensor'
        super().__init__('battery_sensor')
        
        # 建立發布者：(訊息型態, '主題名稱', Queue Size)
        # Queue Size 設為 10 代表若網路塞車，最多暫存 10 筆訊息
        self.publisher_ = self.create_publisher(String, 'battery_status', 10)
        
        # 建立計時器：每 1.0 秒自動呼叫一次 timer_callback
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.battery_level = 100 # 初始電量 100%

    def timer_callback(self):
        msg = String()                 # 實例化一個 String 訊息物件
        msg.data = f'目前電量: {self.battery_level}%' # 將資料塞入 msg 的 data 欄位
        
        self.publisher_.publish(msg)   # 實際將訊息發布到主題上
        self.get_logger().info(f'🔋 發布: "{msg.data}"') # 在終端機印出 Log
        
        # 模擬電量消耗，每次發布後扣 1%
        if self.battery_level > 0:
            self.battery_level -= 1

def main(args=None):
    rclpy.init(args=args) # 初始化 ROS 2 Python 函式庫
    battery_sensor = BatterySensor()
    rclpy.spin(battery_sensor) # 讓節點保持活著，持續監聽事件(如計時器)
    battery_sensor.destroy_node()
    rclpy.shutdown() # 關閉 ROS 2

if __name__ == '__main__':
    main()