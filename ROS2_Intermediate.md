# 《ROS 2 Humble 中階實戰：TurtleBot3 模擬、進階 Launch 與 TF2 空間轉換》

## 動作 (Action) 

在前面的講義中，我們已經學會了 Topic（連續廣播）與 Service（單次的一問一答）。但想像一下真實的機器人情境：**「請走到辦公室的盡頭」**。
這是一個需要耗費數十秒甚至幾分鐘的任務。如果使用 Service，你的主程式會卡死在那邊乾等；而且如果走到一半前方突然出現障礙物，Service 是無法「中途取消」或「回報進度」的。

這就是 **動作 (Action)** 登場的時刻！

### 💡 核心觀念：Action 就像叫 Uber Eats
你可以把 Action 想像成叫外送的完整流程，它由三個部分組成：
1. **目標 (Goal)**：你送出訂單（例如：請倒數 10 秒）。
2. **回饋 (Feedback)**：等待期間，APP 不斷跳出通知（例如：剩下 9 秒、8 秒...）。
3. **結果 (Result)**：餐點送達（例如：倒數完成，任務成功）。
最重要的是：在任務執行期間，你隨時可以按下**取消 (Cancel)**。

---

### 1.1 定義 Action 通訊介面

在開始寫程式前，我們需要先定義 Action 的資料格式。因為這牽涉到自訂介面，所以我們必須先建立一個專屬的 C++ 套件來存放這些定義檔。

**步驟 1：建立存放介面的套件**
開啟終端機，進入工作空間的 `src` 目錄，建立名為 `my_interfaces` 的套件，並在其中建立 `action` 資料夾：

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake --license Apache-2.0 my_interfaces
cd my_interfaces
mkdir action
```

**步驟 2：撰寫 `.action` 定義檔**
在 `my_interfaces/action/` 目錄下建立一個名為 `Countdown.action` 的檔案，用來定義倒數計時任務的格式。Action 檔案分為三個區塊，以 `---` 隔開：

```text
# 1. Goal (目標)：Client 要求 Server 倒數幾秒？
int32 starting_count
---
# 2. Result (結果)：任務結束後，Server 回傳的最終狀態
string message
---
# 3. Feedback (回饋)：執行期間，Server 不斷回報的進度
int32 current_count
```

*(提醒：定義好 `.action` 後，記得修改 `package.xml` 並在 `CMakeLists.txt` 中使用 `rosidl_generate_interfaces` 進行編譯，這在之前的講義已經學過了！編譯完成後，我們才能在 Python 或 C++ 程式中使用這個 `Countdown` 格式。)*

---

### 📦 1.2 建立 Action 程式專屬套件
有了 `Countdown.action` 介面後，我們需要建立新的套件，用來存放接下來要寫的 Python 與 C++ 程式碼。

開啟終端機，進入 `src` 目錄並建立套件（我們將利用 `--dependencies` 參數，讓系統自動幫我們把依賴寫進設定檔中，省去手動新增的麻煩）：

建立 Python Action 套件：

```Bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python --license Apache-2.0 my_action_py_pkg --dependencies rclpy my_interfaces
```

建立 C++ Action 套件：

```Bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake --license Apache-2.0 my_action_cpp_pkg --dependencies rclcpp rclcpp_action my_interfaces
```

### 🐍 1.3 Python 實作 Action
Python 實作 Action 相當直觀，我們將使用 `rclpy.action` 模組。

#### 撰寫 Action Server (動作伺服器)
在 `my_action_py_pkg/my_action_py_pkg/` 下建立 `countdown_server.py`。Action Server 最重要的就是 `execute_callback`，這是實際執行耗時任務的地方。

```python
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
```

#### 撰寫 Action Client (動作用戶端)
在 `my_action_py_pkg/my_action_py_pkg/` 下建立 `countdown_client.py`。Client 的邏輯稍微複雜一點，因為它包含了大量的**非同步 (Async)** 操作，也就是把任務丟出去後不卡死，而是設定好「收到進度時要呼叫哪個函式」。

為了展示 Action 最強大的「可取消性」，我們在此範例中加入了一個 2 秒的計時器：當倒數到一半時，Client 會故意失去耐心並發送取消請求。

```python
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
```

---

### ⚙️ 1.4 C++ 實作 Action

C++ 處理 Action 比較嚴謹，必須引入 `rclcpp_action` 函式庫。
特別注意：C++ 的 Action Server 為了避免耗時任務卡死 ROS 2 的通訊機制（Spin），**必須開啟一個獨立的執行緒 (`std::thread`) 來跑耗時的 `execute` 邏輯**。

#### 撰寫 Action Server (動作伺服器)
這段程式碼展示了 C++ Action Server 必須實作的三個核心 Callback：`handle_goal` (是否接受目標)、`handle_cancel` (是否允許取消)、以及 `handle_accepted` (開始執行)。
在 `my_action_cpp_pkg/src/` 下建立 `countdown_server.cpp`：

```cpp
#include <functional>
#include <memory>
#include <thread>
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "my_interfaces/action/countdown.hpp"

class CountdownServer : public rclcpp::Node
{
public:
  using Countdown = my_interfaces::action::Countdown;
  using GoalHandleCountdown = rclcpp_action::ServerGoalHandle<Countdown>;

  CountdownServer() : Node("countdown_server")
  {
    using namespace std::placeholders;
    // 建立 Action Server 並綁定三個核心 Callback
    this->action_server_ = rclcpp_action::create_server<Countdown>(
      this, "countdown",
      std::bind(&CountdownServer::handle_goal, this, _1, _2),
      std::bind(&CountdownServer::handle_cancel, this, _1),
      std::bind(&CountdownServer::handle_accepted, this, _1));
  }

private:
  rclcpp_action::Server<Countdown>::SharedPtr action_server_;

  // 1. 處理目標：決定是否接受這個任務
  rclcpp_action::GoalResponse handle_goal(
    const rclcpp_action::GoalUUID & uuid, std::shared_ptr<const Countdown::Goal> goal)
  {
    RCLCPP_INFO(this->get_logger(), "收到目標要求倒數 %d 秒", goal->starting_count);
    return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
  }

  // 2. 處理取消：當 Client 要求中斷任務時
  rclcpp_action::CancelResponse handle_cancel(const std::shared_ptr<GoalHandleCountdown> goal_handle)
  {
    RCLCPP_INFO(this->get_logger(), "收到取消任務請求");
    return rclcpp_action::CancelResponse::ACCEPT;
  }

  // 3. 處理接受：任務被接受後，開啟新執行緒 (Thread) 去跑長時間運算
  void handle_accepted(const std::shared_ptr<GoalHandleCountdown> goal_handle)
  {
    std::thread{std::bind(&CountdownServer::execute, this, std::placeholders::_1), goal_handle}.detach();
  }

  // 實際執行耗時任務的邏輯
  void execute(const std::shared_ptr<GoalHandleCountdown> goal_handle)
  {
    const auto goal = goal_handle->get_goal();
    auto feedback = std::make_shared<Countdown::Feedback>();
    auto result = std::make_shared<Countdown::Result>();
    rclcpp::Rate loop_rate(1); // 1Hz (每秒執行一次)

    for (int i = goal->starting_count; (i > 0) && rclcpp::ok(); --i) {
      // 檢查是否收到取消請求
      if (goal_handle->is_canceling()) {
        result->message = "任務中途被取消";
        goal_handle->canceled(result);
        return;
      }
      // 更新並發布 Feedback
      feedback->current_count = i;
      goal_handle->publish_feedback(feedback);
      RCLCPP_INFO(this->get_logger(), "回饋進度: 剩下 %d 秒", i);
      
      loop_rate.sleep(); // 模擬耗時
    }

    // 完成任務
    if (rclcpp::ok()) {
      result->message = "倒數完成，任務成功！";
      goal_handle->succeed(result);
      RCLCPP_INFO(this->get_logger(), "任務完成！");
    }
  }
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CountdownServer>());
  rclcpp::shutdown();
  return 0;
}
```

#### ✍️ 隨堂練習：撰寫 C++ Action Client
在 `my_action_cpp_pkg/src/` 下建立 `countdown_client.cpp`。請嘗試根據註解提示，實作出對應的 C++ Action Client，並且加入「2 秒後自動取消」的功能！

```cpp
#include <functional>
#include <memory>
#include <chrono>
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "my_interfaces/action/countdown.hpp"

class CountdownClient : public rclcpp::Node
{
public:
  using Countdown = my_interfaces::action::Countdown;
  using GoalHandleCountdown = rclcpp_action::ClientGoalHandle<Countdown>;

  CountdownClient() : Node("countdown_client")
  {
    // 提示 1: 使用 rclcpp_action::create_client 建立 client_ptr_
    this->client_ptr_ = ________________________<Countdown>(this, "countdown");
  }

  void send_goal()
  {
    using namespace std::placeholders;
    if (!this->client_ptr_->wait_for_action_server(std::chrono::seconds(10))) {
      RCLCPP_ERROR(this->get_logger(), "Action Server 未上線");
      return;
    }

    auto goal_msg = Countdown::Goal();
    goal_msg.starting_count = 5;

    // 設定 Client 端的 Callback Options
    auto send_goal_options = rclcpp_action::Client<Countdown>::SendGoalOptions();
    send_goal_options.goal_response_callback = std::bind(&CountdownClient::goal_response_callback, this, _1);
    send_goal_options.feedback_callback = std::bind(&CountdownClient::feedback_callback, this, _1, _2);
    send_goal_options.result_callback = std::bind(&CountdownClient::result_callback, this, _1);

    // 提示 2: 使用 async_send_goal 非同步發送目標
    this->client_ptr_->________________________(goal_msg, send_goal_options);
  }

private:
  rclcpp_action::Client<Countdown>::SharedPtr client_ptr_;
  rclcpp::TimerBase::SharedPtr timer_;           // 用來倒數觸發取消的計時器
  GoalHandleCountdown::SharedPtr goal_handle_;   // 保存目前的 Goal Handle

  void goal_response_callback(const GoalHandleCountdown::SharedPtr & goal_handle) {
    if (!goal_handle) {
      RCLCPP_ERROR(this->get_logger(), "任務被 Server 拒絕");
    } else {
      RCLCPP_INFO(this->get_logger(), "任務被接受，Server 執行中");
      
      // 提示 3: 將傳入的 goal_handle 保存到類別變數 this->goal_handle_ 中
      this->goal_handle_ = ________________________;
      
      // 設定 2 秒後觸發 timer_cancel_callback 來模擬反悔取消
      this->timer_ = this->create_wall_timer(
        std::chrono::seconds(2), std::bind(&CountdownClient::timer_cancel_callback, this));
    }
  }

  // ⭐ 實作：發送取消任務請求
  void timer_cancel_callback() {
    RCLCPP_INFO(this->get_logger(), "等太久了，發送取消任務請求！");
    this->timer_->cancel(); // 停止計時器避免重複發送
    
    // 提示 4: 呼叫 async_cancel_goal 送出取消請求 (參數為剛剛存下來的 goal_handle_)
    this->client_ptr_->________________________(this->goal_handle_);
  }

  void feedback_callback(
    GoalHandleCountdown::SharedPtr, const std::shared_ptr<const Countdown::Feedback> feedback)
  {
    // 提示 5: 印出 feedback 裡面的 current_count
    RCLCPP_INFO(this->get_logger(), "收到回饋，剩下 %d 秒", feedback->________________);
  }

  void result_callback(const GoalHandleCountdown::WrappedResult & result) {
    // ⭐ 使用 switch 判斷任務的最終狀態碼
    switch (result.code) {
      case rclcpp_action::ResultCode::SUCCEEDED:
        RCLCPP_INFO(this->get_logger(), "順利完成: %s", result.result->message.c_str());
        break;
      // 提示 6: 判斷狀態碼是否為 CANCELED (已被取消)
      case rclcpp_action::ResultCode::________________:
        RCLCPP_INFO(this->get_logger(), "任務最終狀態：已成功取消");
        break;
      default:
        RCLCPP_ERROR(this->get_logger(), "任務異常結束");
        break;
    }
    rclcpp::shutdown();
  }
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  auto client = std::make_shared<CountdownClient>();
  client->send_goal();
  rclcpp::spin(client);
  return 0;
}
```

<details>
<summary>👉 點擊展開：C++ 動作用戶端解答</summary>

```cpp
// 解答 1
this->client_ptr_ = rclcpp_action::create_client<Countdown>(this, "countdown");

// 解答 2
this->client_ptr_->async_send_goal(goal_msg, send_goal_options);

// 解答 3
this->goal_handle_ = goal_handle;

// 解答 4
this->client_ptr_->async_cancel_goal(this->goal_handle_);

// 解答 5
RCLCPP_INFO(this->get_logger(), "收到回饋，剩下 %d 秒", feedback->current_count);

// 解答 6
case rclcpp_action::ResultCode::CANCELED:
```
</details>

---

### ⚠️ 1.5 設定檔更新 (CMakeLists.txt & package.xml)

由於我們使用了 `rclcpp_action` (C++) 與 `rclpy.action` (Python)，別忘了更新套件的依賴：

1. **`package.xml`**
   ```xml
   <depend>rclcpp_action</depend>
   <depend>my_interfaces</depend> 
   ```

2. **`CMakeLists.txt` (僅 C++ 專案)**
   必須尋找 `rclcpp_action` 並將它連結到執行檔上：
   ```cmake
   find_package(rclcpp_action REQUIRED)
   find_package(my_interfaces REQUIRED)

   add_executable(action_server src/countdown_server.cpp)
   ament_target_dependencies(action_server rclcpp rclcpp_action my_interfaces)

   add_executable(action_client src/countdown_client.cpp)
   ament_target_dependencies(action_client rclcpp rclcpp_action my_interfaces)
   ```

3. **編譯並執行**：
   設定完依賴後，請回到工作空間根目錄進行編譯。
   ```bash
   cd ~/ros2_ws
   colcon build --packages-select my_interfaces my_action_py_pkg my_action_cpp_pkg
   ```

   編譯完成後，請開啟**兩個**終端機，分別載入環境並執行 Server 與 Client：

   **終端機 1 (啟動 Action Server)**：
   ```bash
    source install/setup.bash
    ros2 run my_action_py_pkg action_server
   ```
   *(此時 Server 會處於待命狀態，並印出「倒數計時 Action Server 已啟動！」)*

   **終端機 2 (啟動 Action Client)**：
   ```bash
    source install/setup.bash
    ros2 run my_action_py_pkg action_client
   ```

   執行後，你就能在終端機中看到優雅的非同步倒數計時、即時回饋的進度，以及中途觸發的「取消任務」測試了！學會了 Action，你就等於拿到了控制真實機器人（如 TurtleBot3）導航系統的鑰匙！

---

## 單元 2：進入機器人世界 —— TurtleBot3 模擬環境建置

在前面的章節中，我們學會了節點之間如何互相傳遞字串與數字。但真實的機器人專案不會只傳遞 "Hello World" —— 系統需要處理雷達點雲 (LiDAR)、輪子轉速 (Odometry) 以及攝影機影像。

為了不因為硬體損壞或電池沒電而阻礙學習，ROS 2 提供了強大的模擬生態系。我們將使用 ROS 官方指定的標準教學機器人 **TurtleBot3 (TB3)**，配合 **Gazebo** 物理模擬器，在你的電腦裡創造一個遵守重力與碰撞法則的真實宇宙。

### 2.1 安裝 TurtleBot3 與 Gazebo 模擬套件

首先，我們需要下載 TB3 的模型檔案以及 Gazebo 模擬器。請開啟終端機，執行以下指令（這會從 Ubuntu 的軟體庫中下載並安裝編譯好的二進位檔）：

```bash
# 確保軟體清單是最新的
sudo apt update

# 安裝 Gazebo 與 ROS 2 的橋接套件
sudo apt install ros-humble-gazebo-* -y

# 安裝 TurtleBot3 的核心訊息與主程式
sudo apt install ros-humble-turtlebot3-msgs ros-humble-turtlebot3 -y

# 安裝 TurtleBot3 的 Gazebo 模擬環境
sudo apt install ros-humble-turtlebot3-gazebo -y
```

> **⚠️ WSL2 用戶特別防坑指南：預先下載 3D 模型避開 Timeout**
> ROS 2 預設只有 30 秒的等待時間將機器人放入虛擬世界，如果網路下載 3D 模型太慢會直接報錯 (`Service /spawn_entity unavailable`)。為了避免卡關，請手動將官方模型包下載到本機：
> ```bash
> mkdir -p ~/.gazebo/models
> git clone https://github.com/osrf/gazebo_models.git ~/.gazebo/models
> ```
> *(若提示資料夾已存在且非空，代表已經下載過，可直接跳過此步驟。)*

### 2.2 設定專屬的環境變數與 WSL 顯示修復

在啟動任何 TB3 相關的 Launch 檔之前，系統必須知道你要召喚哪一台車。TurtleBot3 官方提供了三種不同硬體配置的車型：`burger`（漢堡型，雙層無相機）、`waffle`（鬆餅型，較大且有相機）、以及 `waffle_pi`。

**此外，在 Ubuntu 22.04 環境下載入 ROS 2 時，經常會意外覆蓋掉 Gazebo 原本尋找「3D 渲染資源」的環境變數，導致啟動時引發 `Assertion 'px != 0' failed` 的閃退錯誤 (如下)：**

```bash
[INFO] [spawn_entity.py-4]: process has finished cleanly [pid 10399]
[gzclient-2] gzclient: /usr/include/boost/smart_ptr/shared_ptr.hpp:728: typename boost::detail::sp_member_access<T>::type boost::shared_ptr<T>::operator->() const [with T = gazebo::rendering::Camera; typename boost::detail::sp_member_access<T>::type = gazebo::rendering::Camera*]: Assertion `px != 0' failed.
[ERROR] [gzclient-2]: process has died [pid 10395, exit code -6, cmd 'gzclient --gui-client-plugin=libgazebo_ros_eol_gui.so'].
```

為了一次解決這兩個問題，請將以下設定寫入 `~/.bashrc` 中，讓它每次打開終端機都能自動生效：

```bash
# 1. 將預設車型設為 burger (漢堡型)
echo 'export TURTLEBOT3_MODEL=burger' >> ~/.bashrc

# 2. 找回被 ROS 2 意外覆蓋的 Gazebo 原生環境變數 (修復 px != 0 閃退)
echo 'source /usr/share/gazebo/setup.sh' >> ~/.bashrc

# 重新載入環境變數使其立刻生效
source ~/.bashrc
```
*(備註：強制使用 CPU 進行 OpenGL 軟體渲染可能會讓模擬器稍微掉幀，但能保證在 WSL 環境下 100% 穩定運作不出錯。)*

### 2.3 一鍵召喚機器人與虛擬世界

環境準備就緒！我們將使用官方寫好的 Launch 檔，一次啟動 Gazebo 模擬器、載入一個佈滿障礙物的虛擬房間，並把 TB3 放在房間正中央。

請在終端機輸入：
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```
> **⏳ 貼心提醒：** 第一次啟動 Gazebo 時，系統會在背景下載虛擬世界的 3D 模型檔案（如牆壁、木桶等），可能會需要等待 1 到 3 分鐘，畫面才會從黑畫面轉為正常的虛擬房間，請耐心等候！

畫面出現後，你可以使用滑鼠左鍵（平移）、右鍵（縮放）與中鍵（旋轉）來觀察這台帶著 360 度光達 (LiDAR) 的 Burger 機器人。

---

### 2.4 驗證與互動：遙控與雷達數據監聽

機器人已經在虛擬世界中啟動了，接下來我們要像玩遙控車一樣控制它，並看看它「眼中的世界」長什麼樣子。

#### 1. 使用鍵盤遙控機器人 (Teleop)
保持 Gazebo 模擬器開啟，**打開第二個全新的終端機**，輸入以下指令啟動鍵盤控制節點：

```bash
ros2 run turtlebot3_teleop teleop_keyboard
```
此時終端機會顯示操控說明：
* 使用 `w` / `x` 控制前進與後退。
* 使用 `a` / `d` 控制原地左轉與右轉。
* 使用 `s` 煞車停止。

請將滑鼠游標**保持停留在這個終端機視窗內**，按下 `w`，你就會看到 Gazebo 裡的機器人開始往前跑了！

#### 2. 監聽光達 (LiDAR) 數據
機器人頂端的黑色圓盤是 360 度雷射測距儀（光達），它正在以極快的速度旋轉並掃描四周的障礙物距離。這個數據被發布在 `/scan` 這個 Topic 上。

**打開第三個終端機**，我們來偷看這些原始數據：

```bash
ros2 topic echo /scan
```

**數據解析：**
你會看到終端機以極快的速度刷過大量的數字。按 `Ctrl + C` 暫停一下，往上滑觀察：
* `ranges`: 這是一個包含 360 個浮點數的陣列。這 360 個數字分別代表機器人從 0 度到 359 度，每一個角度測量到的障礙物距離（單位為公尺）。
* 如果某個角度沒有障礙物，或者超出掃描範圍，數值通常會顯示為 `inf` (無限大)。

---

### 參考資料
* [ROBOTIS e-Manual: TurtleBot3 Simulation](https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/)

---

## 單元 3：機器人的實體與靈魂 —— Gazebo vs. Rviz2

在進入最高潮的 SLAM (建圖) 與自動導航之前，我們必須先釐清初學者最容易搞混的兩個 3D 介面：**Gazebo** 與 **Rviz2**。

記住一個核心口訣：**「Gazebo 是物理世界，Rviz2 是大腦螢幕。」**

### 🌍 3.1 實體宇宙：Gazebo 模擬器
Gazebo 是一個**物理引擎**。它的任務是欺騙機器人的程式，讓它以為自己活在真實世界中。
* **物理運算：** 它會計算重力 (東西會往下掉)、碰撞體積 (撞到牆會停下來)、以及輪胎與地面的摩擦力。
* **感測器生成：** 當你在 Gazebo 裡面放一面牆，它會計算機器人的「虛擬光達射線」打到牆壁反彈的時間，並把這些數據發布到 `/scan` 主題上。
* **重點：** Gazebo 裡面看到的東西都是「實體」。如果你在這裡刪除一面牆，機器人就可以開過去。

### 🧠 3.2 靈魂視角：Rviz2 數據視覺化
Rviz2 全名是 ROS Visualization，它是一個**純粹的畫圖工具**。
* **沒有物理法則：** Rviz2 裡面沒有重力、沒有碰撞。它只負責「訂閱」資料，然後畫出來。
* **機器人的大腦螢幕：** 它把 `/scan` 裡面無聊的距離數字變成紅色的點；把 `/odom` 的座標變成一條軌跡線。它讓你看到**「機器人眼中的世界長什麼樣子」**。
* **重點：** Rviz2 只是儀表板。你不能在 Rviz2 裡面放一塊石頭來擋住機器人，因為對機器人來說，那只是一張浮在眼前的「幻象貼紙」。

### 🥊 3.3 核心差異對照表

| 功能 | Gazebo (物理模擬器) | Rviz2 (視覺化工具) |
| :--- | :--- | :--- |
| **角色定位** | 上帝視角的真實世界 | 機器人視角的大腦儀表板 |
| **運算內容** | 重力、碰撞、摩擦力、光線反射 | 訂閱 Topic 並將數值轉化為 3D 圖形 |
| **增加障礙物** | 機器人撞到會停下來 | 機器人會直接穿過去 (沒有物理碰撞) |
| **佔用效能** | 很高 (需要大量的 CPU/GPU 運算) | 較低 (單純繪圖) |

---

### 🎮 3.4 實作練習：撞牆測試 (同時觀察實體與數據)

光說不練假把戲，我們現在同時打開它們，讓你親眼看看兩者的連動關係。

**1. 啟動虛擬世界 (Gazebo)**
請開啟第一個終端機，啟動 TB3 的虛擬房間：
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**2. 啟動遙控節點**
打開第二個終端機，啟動鍵盤控制：
```bash
ros2 run turtlebot3_teleop teleop_keyboard
```

**3. 啟動並設定 Rviz2 (大腦螢幕)**
打開第三個終端機，輸入 `rviz2` 啟動。Rviz2 剛開啟時是一片黑畫面，請務必「按照順序」進行以下設定，才能成功讓機器人現身：

1. **設定基準座標 (Fixed Frame)** (左側控制面板上方)
   找到 `Fixed Frame`，把預設的 `map` 改成 **`odom`** (里程計座標)。

   *說明：因為我們還沒跑 SLAM 建圖，系統裡沒有 map 座標，不改的話機器人會無法定位。*

2. **加入 RobotModel 圖層** (點擊左下角 Add)
   點擊 **Add** ➔ 選擇 **By display type** 標籤 ➔ 展開 `rviz_default_plugins` ➔ 點兩下 **RobotModel**。

3. **指定 3D 模型資料來源** (拯救隱形機器人的關鍵)
   在左側面板展開剛剛加入的 `RobotModel`，找到 **Description Topic** 欄位。點擊旁邊的空白處，輸入或選擇 **`/robot_description`**。

   *說明：設定完這步，一台黑色的 Burger 機器人就會瞬間出現在畫面正中央！*

4. **顯示光達點雲 (LaserScan)** (再次點擊左下角 Add)
   點擊 **Add** ➔ 切換到 **By topic** 標籤 ➔ 展開 `/scan` ➔ 點兩下 **LaserScan**。

   *(可選：在左側面板展開 LaserScan，將 Size (m) 改為 0.05 讓紅點更清楚)*

**4. 開始撞牆！**
現在，請將你的螢幕左右分割，左邊放 Gazebo，右邊放 Rviz2。點擊你的「鍵盤遙控終端機」視窗，按下 `w` 讓機器人往前開。

**👁️ 觀察重點：**
* 你會看到 Rviz2 裡面的「紅色點點形狀」完美貼合了 Gazebo 裡面的木桶與牆壁輪廓。
* 故意讓機器人撞上牆壁！你會發現機器人在 Gazebo 裡停下來了（因為物理碰撞），而 Rviz2 裡的紅色點點會緊緊貼在機器人的模型上，這代表感測器回報障礙物距離為 0。

---

## 單元 4：系統總管 —— 進階 Launch 檔撰寫

在剛剛的單元 3 中，為了一邊讓機器人跑、一邊看感測器數據，我們一口氣開了三個終端機。

想像一下，一台真實的自動駕駛車或服務型機器人，身上可能有光達、深度相機、馬達控制器、導航演算法等超過 20 個節點。如果每次開機都要工程師手動開 20 個終端機，那絕對會是一場災難。

為了解決這個問題，ROS 2 提供了強大的 **Launch 檔 (啟動腳本)**，它就像是交響樂團的指揮家，能一鍵精準地喚醒並配置所有節點。

### 🧩 4.1 站在巨人的肩膀上：`IncludeLaunchDescription`
在寫程式時，我們會 `import` 別人的函式庫；在寫 Launch 檔時，我們也可以直接 `Include` (包含) 別人寫好的 Launch 檔。

舉例來說，TB3 官方為了讓機器人在 Gazebo 中生成，背後寫了近百行的設定。我們不需要重寫這一百行，只需要使用 `get_package_share_directory` 這個指令找到官方套件的安裝路徑，然後把它「包」進我們的專案裡即可。

### 🔌 4.2 軟體轉接頭：`Remappings` (主題對接)
這是 ROS 2 模組化設計最精華的功能。

假設你從網路上載了一個超強的 AI 追蹤演算法套件，它會計算速度並發布到 `/ai_velocity` 主題上。但你的 TB3 機器人硬體只聽得懂 `/cmd_vel` 這個主題。怎麼辦？去改 AI 套件的原始碼嗎？

**不用！** 你只需要在 Launch 檔啟動該節點時，加上一行「轉接」指令：
`remappings=[('/ai_velocity', '/cmd_vel')]`
系統就會在底層自動幫你把資料導引過去，完全不需要修改任何一行 C++ 或 Python 程式碼。

---

### 💻 4.3 實作練習：打造專屬的「一鍵啟動」腳本

我們現在要寫一個名為 `my_tb3_bringup.launch.py` 的腳本。它會同時幫我們：啟動虛擬世界、打開 Rviz2，並且啟動你自訂的控制節點。

**1. 建立腳本檔案**
請在之前建好的 `py_test_pkg` (或任何自訂套件) 內部的 `launch` 資料夾中，建立這個檔案。

**2. 撰寫 Launch 邏輯 (附詳細解析)**
請將以下程式碼貼入。這份程式碼包含了 Launch 檔最標準的寫法與詳細的模組解說：

```python
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
        package='py_test_pkg',    # 替換成你自己的開發套件名稱
        executable='talker',      # 替換成你的執行檔名稱 (用之前的發布者 talker 做示範)
        name='my_auto_driver',    # 幫這個控制節點取個響亮的名字
        remappings=[
            # 格式為 tuple：('/你程式碼裡寫的主題名稱', '/系統實際上要對接的主題名稱')
            ('/my_custom_speed', '/cmd_vel') 
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
```

**3. 更新安裝規則 (極度重要！)**
寫完 `.launch.py` 後，如果沒有告訴系統要「安裝」它，`colcon build` 完 ROS 2 還是會找不到檔案。
請打開套件內的 `setup.py`，確保 `data_files` 陣列中有包含 launch 資料夾的安裝規則：
```python
(os.path.join('share', package_name, 'launch'), glob('launch/*')),
```

**4. 編譯與一鍵起飛**
回到工作空間根目錄進行編譯，並載入最新環境：
```bash
cd ~/ros2_ws
colcon build --packages-select py_test_pkg
source install/setup.bash
```

現在你只需要**一個終端機**、**一行指令**：
```bash
ros2 launch py_test_pkg my_tb3_bringup.launch.py
```
按下 Enter 後，Gazebo 模擬器、機器人實體、Rviz2 監控畫面，以及你的自訂節點，將會一口氣全部自動啟動！


> **💡 進階提示：儲存 Rviz2 設定檔 (.rviz)**
> 實務上，我們會在手動設定好 Rviz2 (加入 RobotModel、LaserScan 等) 之後，點擊左上角的 `File` ➔ `Save Config As`，存成一個 `.rviz` 檔案。接著在 Launch 檔的 Rviz 節點中加上 `arguments=['-d', '/絕對路徑/你的設定檔.rviz']`，以後連 Rviz2 的點擊設定都省下來了！

---

## 單元 5：導航與 SLAM 的核心命脈 —— TF2 坐標轉換 (Transform)

### 🌳 5.1 核心觀念：什麼是 TF Tree (坐標樹)？

在 ROS 2 中，所有的坐標系 (Frame) 都是透過「父子關係 (Parent-Child)」連結起來的，形成一棵樹狀結構。真實機器人的標準 TF Tree 通常會長這樣：

```text
map (世界地圖的絕對零點)
 └── odom (里程計的起點)
      └── base_footprint (機器人投影在地面的中心點)
           └── base_link (機器人的實體底盤中心)
                ├── wheel_left_link (左輪)
                ├── wheel_right_link (右輪)
                └── base_scan (光達感測器的位置)
```

**四大核心坐標系解析：**
1. **`map`**：上帝視角。這是 SLAM 建出來的絕對地圖座標。
2. **`odom`**：盲人視角。依靠輪子轉速推算出來的位置。因為輪胎會打滑，所以 `odom` 走久了會產生累積誤差（這時候就需要 SLAM 演算法去計算 `map` 到 `odom` 之間的修正值）。
3. **`base_link`**：機器人本體。所有感測器和零件的安裝位置，都是以它為基準來測量的。
4. **`base_scan`**：光達視角。雷射掃描到的障礙物距離，原點都在這裡。

### 🔄 5.2 靜態轉換 (Static TF) vs. 動態轉換 (Dynamic TF)

這棵坐標樹上的連結線，依照「會不會動」分為兩種：

| 類型 | 定義與特性 | 真實範例 | 負責發布的節點 |
| :--- | :--- | :--- | :--- |
| **靜態轉換 (Static)** | 兩個部位的相對距離**永遠不變**。系統只需廣播一次，就能節省大量網路頻寬。 | `base_link` ➔ `base_scan` (光達是用螺絲鎖在底盤上的，不會亂跑) | `robot_state_publisher` (讀取 URDF 模型檔自動發布) |
| **動態轉換 (Dynamic)** | 兩個部位的相對位置**會隨著時間與動作改變**，必須每秒高頻率發布 (通常 20Hz~50Hz)。 | `odom` ➔ `base_footprint` (機器人在空間中不斷移動) | 馬達控制器、里程計節點、或是 SLAM 演算法 |

> **⚠️ 除錯金律：** TF Tree 是一個嚴格的樹狀圖。**每個子節點「只能有一個」父節點！** 如果你有兩個不同的演算法同時搶著發布 `base_link` 的位置，TF 樹就會發生錯亂，導致機器人在 Rviz2 裡面瘋狂瞬移跳動。

---

### 🛠️ 5.3 實作練習：用 TF2 工具透視機器人骨架

ROS 2 內建了非常強大的命令列工具，讓你可以在不寫程式的情況下，看穿機器人內部的坐標關係。

#### 步驟 1：啟動包含 TF 資訊的機器人
為了有數據可以觀察，我們開啟第一個終端機，啟動 TB3 的 Gazebo 虛擬世界（這會自動啟動發布 TF 的 `robot_state_publisher`）：
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

#### 步驟 2：生成 TF Tree 族譜圖 (PDF)
當你接手一台陌生的機器人，第一件事就是印出它的 TF 族譜。打開第二個終端機，執行：
```bash
ros2 run tf2_tools view_frames
```
*系統會監聽目前的網路 5 秒鐘，並在你的當前目錄下生成一個 `frames.pdf` 檔案。*

打開這張族譜圖！你可以清楚看到誰是父節點、誰是子節點，以及廣播頻率。*

#### 步驟 3：使用 `tf2_echo` 監測即時相對距離
有時候你需要知道「A 點相對於 B 點現在的精確座標」，這時候就可以使用 `tf2_echo` 工具。
在終端機輸入（格式：`ros2 run tf2_ros tf2_echo <父節點> <子節點>`）：

```bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

**數據解析：**
終端機會以 1Hz 的頻率持續印出類似下方的資料：
```text
At time 1775838560.124701359
- Translation: [0.000, 0.000, 0.000]
- Rotation: in Quaternion [0.000, 0.000, 0.000, 1.000]
```
* **Translation (平移)**：這代表機器人目前相對於出發點 (`odom`) 的 X, Y, Z 距離 (公尺)。
* **Rotation (旋轉)**：這代表機器人的朝向。ROS 2 底層使用「四元數 (Quaternion)」來避免萬向鎖問題，雖然人類很難直觀讀懂，但它是導航演算法運算角度的最佳格式。

*(你可以再開一個終端機執行 `teleop_keyboard` 讓機器人移動，你會看到 Translation 的數值跟著即時改變！)*

---

到這裡，你已經掌握了 ROS 2 開發的四大基石：**通訊機制 (Topic/Service/Action)**、**架構設定 (Launch/Params)**、**模擬與視覺化 (Gazebo/Rviz2)**，以及**空間轉換 (TF2)**。