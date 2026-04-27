import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from my_interfaces.action import Countdown

# ⭐ 新增：引入 GoalStatus 與執行相關函式
from action_msgs.msg import GoalStatus 
import threading
import sys
import termios
import tty
import select

class CountdownActionClient(Node):
    def __init__(self):
        super().__init__('countdown_client')
        # 建立 Action Client：(綁定此節點, 介面型態, Action 名稱)
        self._action_client = ActionClient(self, Countdown, 'countdown')
        self._goal_handle = None # ⭐ 新增：用來儲存目標控制代碼，發送取消請求時會用到

    # send_goal_async 把目標發送出去後，會立刻回傳一個 Future 物件，程式會繼續往下走。
    # feedback_callback：設定當 Server 傳送過程進度過來時，去執行該函式。
    # add_done_callback：設定當 Server 回覆「是否接下任務」時，去執行 goal_response_callback。
    def send_goal(self, starting_count):
        self.get_logger().info('等待 Action Server 上線...')
        self._action_client.wait_for_server()

        goal_msg = Countdown.Goal()
        goal_msg.starting_count = starting_count

        self.get_logger().info('發送目標...')
        # 核心 1：非同步發送 Goal
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        
        # 核心 2：綁定 Server 是否接受任務的回呼函式
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result() 
        if not goal_handle.accepted:
            self.get_logger().info('任務被 Server 拒絕 :(')
            return

        self.get_logger().info('任務被接受，開始執行！')
        
        # ⭐ 將 goal_handle 保存下來，取消時需要用到它
        self._goal_handle = goal_handle 
        
        # ⭐ 修改：不再使用計時器，改為啟動一個執行緒來監聽鍵盤
        self.keyboard_thread = threading.Thread(target=self.wait_for_keyboard)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()

        # 核心 3：任務被接受後，再次發起非同步請求，索取「最終結果 (Result)」
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    # ⭐ 實作：監聽鍵盤輸入 (空白鍵)
    def wait_for_keyboard(self):
        self.get_logger().info('=== 在此視窗按下「空白鍵 (Space)」可取消任務 ===')
        
        while rclpy.ok():
            # 設定終端機為 Raw Mode 以便抓取單一按鍵
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                # 使用 select 監控 stdin，避免無限阻塞
                rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                if rlist:
                    key = sys.stdin.read(1)
                    if key == ' ': # 如果按下的是空白鍵
                        break
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
            # 若任務已經結束 (例如順利倒數完)，就退出執行緒
            if self._goal_handle is None:
                return

        if rclpy.ok() and self._goal_handle:
            self.get_logger().info('偵測到按下空白鍵，正在發送取消任務請求...')
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self.cancel_done_callback)

    # ⭐ 實作：確認 Server 對取消請求的回覆
    def cancel_done_callback(self, future):
        cancel_response = future.result()
        # 若陣列長度大於 0，代表 Server 成功攔截並準備取消
        if len(cancel_response.goals_canceling) > 0:
            self.get_logger().info('Server 已收到並同意取消任務！')
        else:
            self.get_logger().info('Server 拒絕取消 (可能剛好執行完了)')

    def feedback_callback(self, feedback_msg):
        # 處理不斷送來的 Feedback
        self.get_logger().info(f'收到進度：剩下 {feedback_msg.feedback.current_count} 秒')

    def get_result_callback(self, future):
        result_wrap = future.result()
        status = result_wrap.status        # 取得狀態碼
        result_msg = result_wrap.result.message # 取得回傳訊息
        
        # ⭐ 判斷任務最終的狀態碼
        if status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info(f'任務最終狀態：已成功取消 ({result_msg})')
        elif status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f'任務最終狀態：順利完成 ({result_msg})')
        else:
            self.get_logger().info(f'任務異常結束，狀態碼：{status}')
        
        self._goal_handle = None # 清除目標控制代碼，讓鍵盤執行緒知道可以結束了
        rclpy.shutdown() # 任務結束，關閉節點

def main(args=None):
    rclpy.init(args=args)
    action_client = CountdownActionClient()
    action_client.send_goal(10) # 要求倒數 5 秒
    rclpy.spin(action_client)  # 讓程式進入無限迴圈，保持活著監聽封包

if __name__ == '__main__':
    main()