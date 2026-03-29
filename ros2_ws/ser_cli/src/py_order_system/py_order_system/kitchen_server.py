import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts # 借用內建格式：傳入 a, b，回傳 sum

class KitchenServer(Node):
    def __init__(self):
        super().__init__('kitchen_node')
        # 建立服務伺服器：(服務型態, '服務名稱', 回呼函式)
        self.srv = self.create_service(AddTwoInts, 'place_order', self.order_callback)
        self.get_logger().info('👨‍🍳 廚房已開工，等待點餐...')

    def order_callback(self, request, response):
        # 讀取 Client 傳來的 request (a=漢堡數量, b=薯條數量)
        burgers = request.a
        fries = request.b
        
        # 計算總數後賦值給 response.sum
        response.sum = burgers + fries
        
        # 在終端機印出收到什麼訂單
        self.get_logger().info(f'🔔 收到新訂單: 漢堡 {burgers} 份, 薯條 {fries} 份')
        
        return response # 必須將 response 物件回傳給 Client

def main():
    rclpy.init()
    node = KitchenServer()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()