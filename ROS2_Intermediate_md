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
ros2 pkg create --build-type ament_cmake --license Apache-2.0 my_action_cpp_pkg --de
```

### 🐍 1.3 Python 實作 Action
Python 實作 Action 相當直觀，我們將使用 `rclpy.action` 模組。

#### 撰寫 Action Server (動作伺服器)
在 `my_action_py_pkg/my_action_py_pkg/` 下建立 `countdown_server.py`。Action Server 最重要的就是 `execute_callback`，這是實際執行耗時任務的地方。

```python
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from my_interfaces.action import Countdown # 引入我們剛剛定義的 Action

class CountdownActionServer(Node):
    def __init__(self):
        super().__init__('countdown_server')
        # 建立 Action Server：(節點本身, 介面型態, 'Action名稱', 執行任務的回呼函式)
        self._action_server = ActionServer(
            self, Countdown, 'countdown', self.execute_callback)
        self.get_logger().info('倒數計時 Action Server 已啟動！')

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
    rclpy.spin(server)
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

# ⭐ 新增：引入 GoalStatus 來判斷最終任務狀態碼 (成功/失敗/取消)
from action_msgs.msg import GoalStatus 

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
        
        # ⭐ 設定一個 2 秒後觸發的計時器，模擬使用者中途反悔
        self._cancel_timer = self.create_timer(2.0, self.timer_cancel_callback)

        # 核心 3：任務被接受後，再次發起非同步請求，索取「最終結果 (Result)」
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    # ⭐ 實作：發送取消任務請求
    def timer_cancel_callback(self):
        self.get_logger().info('等太久了，發送取消任務請求！')
        self._cancel_timer.cancel() # 停止計時器，避免重複發送
        
        # 呼叫 cancel_goal_async()，並設定 Callback 來聽取 Server 是否同意取消
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
            
        rclpy.shutdown() # 任務結束，關閉節點

def main(args=None):
    rclpy.init(args=args)
    action_client = CountdownActionClient()
    action_client.send_goal(5) # 要求倒數 5 秒
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

