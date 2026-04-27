import time
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor # ⭐ 新增：引入多執行緒執行器
from rclpy.action import ActionServer, CancelResponse
from my_interfaces.action import Countdown # 引入我們剛剛定義的 Action

class CountdownActionServer(Node):
    def __init__(self):
        super().__init__('countdown_server')
        # 建立 Action Server：(節點本身, 介面型態, 'Action名稱', 執行任務的回呼函式)
        self._action_server = ActionServer(
            self,
            Countdown,
            'countdown',
            execute_callback=self.execute_callback,
            cancel_callback=self.cancel_callback) # ⭐ 新增：掛載取消回呼函式
        self.get_logger().info('倒數計時 Action Server 已啟動！')

    def cancel_callback(self, goal_handle):
        # 決定是否接受取消請求。這裡我們直接同意 (CancelResponse.ACCEPT)。
        # 若不同意則回傳 CancelResponse.REJECT。
        self.get_logger().info('收到取消請求，已同意。')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        self.get_logger().info(f'收到任務：開始倒數 {goal_handle.request.starting_count} 秒')
        
        # 準備 Feedback 與 Result 的物件
        feedback_msg = Countdown.Feedback()
        result = Countdown.Result()

        # 開始執行耗時任務 (倒數迴圈)
        for i in range(goal_handle.request.starting_count, 0, -1):
            # 檢查 Client 是否發送了「取消任務」的要求
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('任務已取消！')
                result.message = "任務中途被取消"
                return result

            # 填入並發送 Feedback
            feedback_msg.current_count = i
            self.get_logger().info(f'回饋進度: 剩下 {i} 秒')
            goal_handle.publish_feedback(feedback_msg)
            
            time.sleep(1.0) # 模擬耗時的物理動作

        # 迴圈順利結束，標記任務成功
        goal_handle.succeed()
        result.message = "倒數完成，任務成功！"
        self.get_logger().info(result.message)
        
        return result # 回傳最終結果

def main(args=None):
    rclpy.init(args=args)
    server = CountdownActionServer()
    
    # ⭐ 修改：使用 MultiThreadedExecutor，讓 Server 能在執行任務時同時處理「取消請求」
    executor = MultiThreadedExecutor()
    executor.add_node(server)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
        
    rclpy.shutdown()

if __name__ == '__main__':
    main()