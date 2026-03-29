import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class WaiterClientAsync(Node):
    def __init__(self):
        super().__init__('waiter_node')
        # 1. 使用 create_client 建立客戶端 (服務型態 AddTwoInts, 服務名稱 'place_order')
        self.cli = self.create_client(AddTwoInts, 'place_order')
        
        # 2. 寫一個 while 迴圈，等待廚房上線 (wait_for_service)，若沒上線則持續印出「呼叫廚房中...」
        while not self.cli.wait_for_service(timeout_sec = 1.0):
            self.get_logger.info("呼叫廚房中...")
        
        # 3. 實例化 Request 物件 (AddTwoInts.Request())
        self.req = AddTwoInts.Request()

    def send_order(self, burgers, fries):
        # 4. 將參數 burgers, fries 填入 request 的 a 與 b
        self.req.a = burgers
        self.req.b = fries
        # 5. 使用 call_async 發送請求，並將結果存入 self.future
        self.future = self.cli.call_async(self.req)
        # 6. 使用 rclpy.spin_until_future_complete 等待廚房回應
        rclpy.spin_until_future_complete(self, self.future)
        # 7. 回傳 self.future.result()
        return self.future.result()

def main(args=None):
    # 8. 初始化 rclpy、建立 WaiterClientAsync 節點
    rclpy.init(args=args)
    waiter_client = WaiterClientAsync()
    # 9. 呼叫 send_order 送出 (2份漢堡, 3份薯條) 的請求
    waiter_client.get_logger().info('送出訂單: 漢堡 2 份, 薯條 3 份')
    response = waiter_client.send_order(2, 3)
    # 10. 印出結果 (response.sum)，然後銷毀節點與關閉系統
    waiter_client.get_logger().info(f'總數: {response.sum}')
    waiter_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()