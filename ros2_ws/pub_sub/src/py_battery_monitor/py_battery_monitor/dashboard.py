import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class BatteryDashboard(Node):
    def __init__(self):
        # 1. 初始化父類別，節點命名為 'battery_dashboard'
        super().__init__('battery_dashboard')
        # 2. 使用 create_subscription 建立訂閱者 (型態為 String, 主題為 'battery_status', 回呼函式為 listener_callback, Queue Size 為 10)
        self.subscription = self.create_subscription(String, 'battery_status', self.listener_callback, 10)
        self.subscription  # prevent unused variable warning

    # 3. 實作 listener_callback，功能是用 get_logger().info 印出收到的 msg.data 內容
    def listener_callback(self, msg):
        self.get_logger().info(f"Dashboard 收到: '{msg.data}'")

def main(args=None):
    # 4. 初始化 rclpy、建立 BatteryDashboard 節點物件、啟動 spin、最後關閉
    rclpy.init(args=args)
    battery_dashboard = BatteryDashboard()
    rclpy.spin(battery_dashboard)
    battery_dashboard.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()