# ROS 2 Humble 初階程式設計 (Client Libraries) 完整講義

本講義涵蓋 ROS 2 官方初階客戶端函式庫教學的完整流程。我們將先從巨觀的角度了解專案架構，接著動手建立工作空間、撰寫套件，並實作**發布/訂閱**、**服務/客戶端**與**參數**。

資料來源: [ROS 2 Humble Beginner Client Libraries](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries.html)

## 1. 核心觀念：ROS 2 工作空間 (Workspace) 檔案架構總覽

在 ROS 2 中，所有的開發都發生在一個稱為 **「工作空間 (Workspace)」** 的資料夾中（通常命名為 `ros2_ws`）。當你使用 `colcon build` 編譯過後，這個工作空間會長出特定的骨架。了解這些檔案的位置，是開發 ROS 2 的第一步。

### 📂 完整目錄結構樹狀圖
```text
ros2_ws/                       <-- 工作空間根目錄 (Workspace Root)
│
├── build/                     <-- [系統生成] 編譯過程的暫存檔
├── install/                   <-- [系統生成] 編譯完成的可執行檔與環境設定
├── log/                       <-- [系統生成] 編譯與執行的日誌檔 (報錯都在這找)
│
└── src/                       <-- ⭐ [開發者專區] 你寫的所有程式碼都在這裡！
    │
    ├── my_cpp_pkg/            <-- 📦 1. C++ 專案套件 (ament_cmake)
    │   ├── CMakeLists.txt     <-- [設定檔] 告訴系統如何編譯 C++ 程式碼 (包含 Launch 檔安裝規則)
    │   ├── package.xml        <-- [設定檔] 宣告套件資訊與依賴的函式庫
    │   ├── include/           <-- [資料夾] 存放 C++ 標頭檔 (.h / .hpp)
    │   │   └── my_cpp_pkg/
    │   │       └── my_node.hpp
    │   ├── src/               <-- [資料夾] 存放 C++ 原始碼 (.cpp)
    │   │   └── my_node.cpp
    │   └── launch/            <-- [資料夾] ⭐ 存放 Launch 啟動腳本 (如 parameters_launch.py)
    │       └── my_launch.py
    │
    ├── my_python_pkg/         <-- 📦 2. Python 專案套件 (ament_python)
    │   ├── package.xml        <-- [設定檔] 宣告套件資訊與依賴的函式庫
    │   ├── setup.py           <-- [設定檔] 註冊 Python 執行檔進入點，與 Launch 檔安裝規則
    │   ├── setup.cfg          <-- [設定檔] 告訴系統把執行檔安裝到 install 的哪裡
    │   ├── my_python_pkg/     <-- [資料夾] 存放 Python 程式碼 (必須與套件同名)
    │   │   ├── __init__.py    <-- [程式碼] 讓 Python 認得這是一個模組
    │   │   └── my_node.py     <-- [程式碼] 你的 ROS 2 Python 節點程式
    │   └── launch/            <-- [資料夾] ⭐ 存放 Launch 啟動腳本 (如 parameters_launch.py)
    │       └── my_launch.py
    │
    ├── tutorial_interfaces/   <-- 📦 3. 獨立的自訂通訊格式套件 (第 6 章)
    │   ├── CMakeLists.txt     
    │   ├── package.xml        
    │   ├── msg/               <-- [資料夾] 自訂主題 (Topic) 訊息格式 (.msg)
    │   └── srv/               <-- [資料夾] 自訂服務 (Service) 格式 (.srv)
    │
    └── more_interfaces/       <-- 📦 4. 混合套件：同時包含 C++ 節點與自訂格式 (第 7 章)
        ├── CMakeLists.txt     
        ├── package.xml        
        ├── msg/               <-- 在同一個套件定義格式
        │   └── AddressBook.msg 
        └── src/               <-- 在同一個套件寫 C++ 節點去引用它
            └── publish_address_book.cpp
```

### 💡 架構重點與目錄功能解說

1. **手動開發區 vs. 系統生成區**
   * **`src/`**：這是**唯一**需要你手動建立、操作與寫程式的地方。
   * **`build/`、`install/`、`log/`**：都是系統執行 `colcon build` 後自動生成的，若編譯出現嚴重異常，可以直接刪除這三個資料夾重新編譯，不會影響你的程式碼。

2. **套件的「身分證」與「說明書」**
   * **`package.xml`**：負責宣告套件的相依性（Dependencies），讓系統知道需要安裝哪些外部函式庫。
   * **`CMakeLists.txt` 或 `setup.py`**：負責告訴系統如何編譯這個套件、以及執行檔要安裝到哪裡。

3. **實體程式邏輯區 (`src/` vs `include/` vs Python 同名資料夾)**
   * **C++ 套件**：具體的實作檔案（`.cpp`）放在套件內的 `src/`，而標頭檔（`.h` / `.hpp`）放在 `include/` 內。
   * **Python 套件**：所有的程式碼（`.py`）全部集中放在與套件名稱「完全同名」的子資料夾內。

4. **啟動腳本區 (`launch/`)**
   * 這是存放 **啟動腳本 (Launch files)** 的地方。當你需要一次啟動多個節點，或是**在啟動時動態注入參數 (Parameters)**，就會在這裡撰寫 `.py` 的腳本。
   * ⚠️ **極度重要**：寫完 launch 檔後，必須在 `setup.py` 的 `data_files` 或 `CMakeLists.txt` 的 `install(DIRECTORY...)` 中設定安裝規則，否則 `ros2 launch` 會找不到檔案！（詳見講義第 8 章實作）。

5. **通訊定義區 (`msg/`, `srv/`, `action/`)**
   * 這些資料夾只存放「純文字定義檔」，用來定義節點之間資料傳遞的格式。
   * ROS 2 的編譯系統 (`rosidl`) 會在編譯時讀取這些檔案，並自動幫你生成對應的 C++ 標頭檔和 Python 模組。

---

## 2. 建立工作空間與編譯 (Workspace & `colcon`)

了解架構後，我們實際來建立最外層的空殼。

**實作指令：**
```bash
# 1. 建立工作空間與 src 資料夾
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws

# 2. 使用 colcon 編譯整個工作空間 (目前是空的，但會生成基礎目錄)
colcon build

# 3. 載入編譯好的環境 (每次開新終端機執行程式前都要做)
source install/setup.bash
```

---

## 3. 建立套件 (Creating a Package)

**觀念解說：**
套件 (Package) 是 ROS 2 程式碼的整理單位。如果你想要編譯程式碼或與他人分享，就必須將它們組織在套件中。在同一個工作空間內，你可以擁有多個不同編譯類型的套件（C++ 或 Python），但**不能將套件巢狀建立**（套件裡面不能有套件）。

一個標準的 ROS 2 套件必須包含：
* **`package.xml`**：包含套件的描述、維護者、授權與依賴資訊。
* **C++ (`ament_cmake`) 專屬**：`CMakeLists.txt` (編譯規則)。
* **Python (`ament_python`) 專屬**：`setup.py` (安裝規則)、`setup.cfg` 與同名原始碼資料夾。

### 3.1 使用指令建立套件與預設節點
我們進入 `src/` 資料夾，建立負責存放程式碼的套件。這次我們加上 `--node-name` 參數，讓系統自動幫我們生成一個印出 "Hello World" 的簡單節點程式碼。

**實作指令：**
```bash
cd ~/ros2_ws/src

# 建立 Python 套件並自動生成一個名為 my_node 的節點
ros2 pkg create --build-type ament_python --license Apache-2.0 --node-name my_node py_test_pkg

# 建立 C++ 套件並自動生成一個名為 my_node 的節點
ros2 pkg create --build-type ament_cmake --license Apache-2.0 --node-name my_node cpp_test_pkg
```

### 3.2 自訂套件資訊 (Customize package.xml & setup.py)
建立套件後，裡面的設定檔會有許多預設的 `TODO`。為了保持專案完整性，強烈建議進行修改。

1. **修改 `package.xml` (C++ 與 Python 皆需)：**
   打開 `ros2_ws/src/py_test_pkg/package.xml`，修改以下標籤：
   ```xml
   <description>Beginner client libraries tutorials practice package</description>
   <maintainer email="your_email@example.com">Your Name</maintainer>
   <license>Apache License 2.0</license>
   ```

2. **修改 `setup.py` (僅 Python 需)：**
   打開 `ros2_ws/src/py_test_pkg/setup.py`，確保 `maintainer`、`maintainer_email`、`description` 與 `license` 的內容與 `package.xml` **完全一致**。

### 3.3 指定編譯與執行
當工作空間內的套件越來越多，全部重新編譯會非常耗時。你可以指定只編譯特定的套件。

**實作指令：**
```bash
cd ~/ros2_ws
# 只編譯 py_test_pkg 與 cpp_test_pkg
colcon build --packages-select py_test_pkg cpp_test_pkg

# 載入環境設定
source install/setup.bash

# 執行剛剛自動生成的 Hello World 節點
ros2 run py_test_pkg my_node
```
*(終端機將會印出 `Hi from py_test_pkg.`)*

### 3.4 深入解析設定檔：組成要素與撰寫指南

在 ROS 2 中，這三個檔案定義了套件的「身分」與「行為」。了解它們的細節，才能應付更複雜的開發情境。

#### 3.4.1 `package.xml`：套件的「身分證」
不論是 Python 還是 C++ 套件，都必須包含此檔案。它是基於 XML 格式，用來宣告套件資訊與依賴關係。

*   **基礎資訊標籤：**
    *   `<name>`: 套件名稱（必須與資料夾同名）。
    *   `<version>`: 套件版本（通常為 `0.0.0`）。
    *   `<description>`: 簡短描述套件的功能。
    *   `<maintainer>`: 維護者姓名與 Email。
    *   `<license>`: 軟體授權名稱（如 `Apache-2.0`）。
*   **依賴宣告標籤：**
    *   `<buildtool_depend>`: 編譯工具依賴（C++ 通常為 `ament_cmake`，Python 為 `ament_python`）。
    *   `<depend>`: 同時包含編譯、匯出與執行時的依賴。
    *   `<build_depend>`: 僅在編譯期間需要的依賴。
    *   `<exec_depend>`: 僅在執行期間需要的依賴。
    *   `<test_depend>`: 單元測試時才需要的依賴。

#### 3.4.2 `setup.py` (Python)：套件的「安裝指南」
這是 Python 套件專有的，決定了 Python 模組如何被安裝，以及「執行檔」的對應關係。

*   **`packages`**: 告知系統哪些資料夾包含 Python 原始碼（通常是與套件同名的資料夾）。
*   **`data_files`**: 告知系統哪些非程式碼檔案（如 `package.xml`、Launch 檔）需要被安裝到 `install/` 目錄。
*   **`setup.cfg`**: 這是一個輔助檔，用來告知 `colcon` 應該將生成的執行檔安裝到 `install/lib/<package_name>` 的哪個位置。通常由 `ros2 pkg create` 自動生成，不需手動修改。
*   **`entry_points`**: **最核心的部分**。在 `console_scripts` 中定義：
    `'執行檔名稱 = 套件名.程式檔名:函式名'`
    例如：`'talker = py_test_pkg.publisher_member_function:main'`

#### 3.4.3 `CMakeLists.txt` (C++)：套件的「編譯藍圖」
這是 C++ 套件專有的，負責引導 CMake 如何將原始碼轉化為執行檔。

*   **`find_package(<lib> REQUIRED)`**: 尋找並載入必要的依賴庫。
*   **`add_executable(<name> src/path.cpp)`**: 宣告要生成的執行檔名稱及其對應的源碼。
*   **`ament_target_dependencies(<name> <libs>)`**: 將 ROS 2 的相依庫（如 `rclcpp`）連結到指定的執行檔。
*   **`install(TARGETS <names> DESTINATION lib/${PROJECT_NAME})`**: 設定安裝路徑，讓 `ros2 run` 找得到編譯好的執行檔。
*   **`ament_package()`**: **必須放在最後一行**，代表結尾並將套件資訊導出。

### 3.5 套件標準開發流程與 `colcon` 編譯指令

為了讓開發更有條理，建議養成以下的標準流程。同時，學會 `colcon build` 的進階參數能大幅縮短等待編譯的時間。

#### 3.5.1 ROS 2 程式開發的黃金六步驟
不論你是使用 Python 還是 C++，開發流程通常如下：

1.  **建立套件殼層**：使用 `ros2 pkg create` 在 `src/` 下建立新套件。
2.  **撰寫源碼**：在原始碼資料夾中編寫 `.py` 或 `.cpp` 檔案。
3.  **配置依賴 (`package.xml`)**：加入程式中用到的所有 ROS 2 套件依賴。
4.  **配置編譯與執行檔 (`setup.py` / `CMakeLists.txt`)**：定義執行檔名稱與進入點。
5.  **編譯工作空間**：在根目錄執行 `colcon build`。
6.  **載入環境並執行**：`source install/setup.bash` 之後使用 `ros2 run` 啟動節點。

#### 3.5.2 `colcon build` 常用指令詳解
在大型專案中，你不需要每次都編譯所有套件。以下是常用的指令選項：

*   **全域編譯** (最基礎)：
    ```bash
    colcon build
    ```
*   **指定編譯特定套件**：(節省時間首選)
    ```bash
    colcon build --packages-select <your_package_name>
    ```
*   **軟連結安裝 (Symlink Install)**：(開發 Python 與 Launch 檔時強烈建議)
    ```bash
    colcon build --symlink-install
    ```
    *💡 提示：使用此參數後，當你修改 Python 程式碼或 Launch 檔時，不需重新編譯即可生效（C++ 仍需重新編譯）。*
    
*   **編譯單個套件及其所有依賴**：
    ```bash
    colcon build --packages-up-to <your_package_name>
    ```
*   **編譯失敗時跳過後續並繼續**：
    ```bash
    colcon build --continue-on-error
    ```

---

## 4. 撰寫發布者與訂閱者 (Publisher & Subscriber)

這個單元展示節點之間如何透過「主題 (Topic)」進行連續性的資料廣播。

### 🐍 4.1 Python 實作
**發布者 (Publisher)：** 放於 `py_test_pkg/py_test_pkg/` 下的 `publisher_member_function.py`。
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String # 引入內建的字串訊息格式

class MinimalPublisher(Node):
    def __init__(self):
        # 初始化節點並命名為 'minimal_publisher'
        super().__init__('minimal_publisher')
        
        # 建立發布者：(訊息型態, 主題名稱, Queue Size(佇列大小))
        # Queue Size 設為 10 代表若網路塞車，最多暫存 10 筆訊息
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        
        # 建立計時器：每 0.5 秒自動呼叫一次 timer_callback
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.i = 0 # 用來計算發布次數的變數

    def timer_callback(self):
        msg = String()                 # 實例化一個 String 訊息物件
        msg.data = 'Hello World: %d' % self.i # 將資料塞入 msg 的 data 欄位
        self.publisher_.publish(msg)   # 實際將訊息發布到主題上
        self.get_logger().info('Publishing: "%s"' % msg.data) # 在終端機印出 Log
        self.i += 1

def main(args=None):
    rclpy.init(args=args) # 初始化 ROS 2 Python 函式庫
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher) # 讓節點保持活著，持續監聽事件(如計時器)
    minimal_publisher.destroy_node()
    rclpy.shutdown() # 關閉 ROS 2

if __name__ == '__main__':
    main()
```

#### ✍️ 隨堂練習：撰寫 Python 訂閱者 (Subscriber)
看完發布者的寫法，請嘗試根據下方的註解提示，在同個目錄下建立 `subscriber_member_function.py` 並練習實作出完整的訂閱者程式碼。

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        # 1. 初始化父類別，節點命名為 'minimal_subscriber'
        # 2. 使用 create_subscription 建立訂閱者 (型態為 String, 主題為 'topic', 回呼函式為 listener_callback, Queue Size 為 10)
        pass

    # 3. 實作 listener_callback，功能是印出收到的 msg.data 內容
    def listener_callback(self, msg):
        pass

def main(args=None):
    # 4. 初始化 rclpy
    # 5. 建立 MinimalSubscriber 節點物件
    # 6. 使用 rclpy.spin 讓節點開始運作
    # 7. 結束後銷毀節點、關閉 rclpy
    pass

if __name__ == '__main__':
    main()
```
<details>
<summary>👉 點擊展開：Python 訂閱者解答</summary>

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        # 解答 1 & 2
        self.subscription = self.create_subscription(String, 'topic', self.listener_callback, 10)
        self.subscription  # 防止 unused variable 警告

    # 解答 3
    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)

def main(args=None):
    # 解答 4 & 5
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    # 解答 6
    rclpy.spin(minimal_subscriber)
    # 解答 7
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

#### 💡 補充：為什麼要多寫一行 `self.subscription`？

在 Python 的 `__init__` 中，你會看到最後一行寫了 `self.subscription`（變數名稱直接寫在一行）。這是官方推薦的作法，主要有兩個原因：
1.  **防止 Linter (靜態代碼檢查) 警告**：如果你使用 VS Code 的 Pylance、Ruff 或 Flake8，它們會檢查變數是否「被定義但未被讀取」。雖然訂閱者在後台運行，但在 `__init__` 中沒有其他地方會讀取這個變數，報錯器會噴出黃色警告。寫這一行能明確告訴系統：「我正在使用這個變數」。
2.  **與 C++ 實作範例對齊**：在 C++ 版本中，為了避免 GCC 編譯器報錯 (Unused Variable)，官方範例會使用 `(void)subscription_;`。Python 的教程為了保持結構上的一致性，也保留了這個習慣。

事實上，只要你有將其宣告為 `self.subscription`（類別屬性），物件就不會被回收。即使刪掉這一行，訂閱功能依然能正常運作。

</details>


#### ⚠️ 重點：Python 設定檔更新 (`package.xml` & `setup.py`)
寫完程式後，系統還不知道你的程式需要哪些依賴，也不知道如何執行它們。

1. **更新 `package.xml`**：加入程式中 import 的函式庫。
   在 `<license>` 標籤下方加入：
   ```xml
   <exec_depend>rclpy</exec_depend>
   <exec_depend>std_msgs</exec_depend>
   ```

2. **更新 `setup.py`**：註冊你寫好的節點，讓 `ros2 run` 找得到。
   在 `entry_points` 的 `console_scripts` 陣列中加入：
   ```python
   entry_points={
       'console_scripts': [
           'talker = py_test_pkg.publisher_member_function:main',
           'listener = py_test_pkg.subscriber_member_function:main',
       ],
   },
   ```
*(修改完畢後，記得回到工作空間根目錄執行 `colcon build`！)*

---

### ⚙️ 4.2 C++ 實作
**發布者 (Publisher)：** 放於 `cpp_test_pkg/src/` 下的 `publisher_member_function.cpp`。

```cpp
#include <chrono>
#include <functional>
#include <memory>
#include <string>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

class MinimalPublisher : public rclcpp::Node
{
  public:
    MinimalPublisher() : Node("minimal_publisher"), count_(0)
    {
      publisher_ = this->create_publisher<std_msgs::msg::String>("topic", 10);
      timer_ = this->create_wall_timer(500ms, std::bind(&MinimalPublisher::timer_callback, this));
    }

  private:
    void timer_callback()
    {
      auto message = std_msgs::msg::String();
      message.data = "Hello, world! " + std::to_string(count_++);
      RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
      publisher_->publish(message);
    }
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    size_t count_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MinimalPublisher>());
  rclcpp::shutdown();
  return 0;
}
```

#### ✍️ 隨堂練習：撰寫 C++ 訂閱者 (Subscriber)
了解 C++ 發布者結構後，請在同個目錄下建立 `subscriber_member_function.cpp`，並嘗試根據註解提示，實作出完整的訂閱者節點！

```cpp
#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using std::placeholders::_1;

class MinimalSubscriber : public rclcpp::Node
{
  public:
    MinimalSubscriber() : Node("minimal_subscriber")
    {
      // 1. 建立訂閱者：<訊息型態>("主題名稱", Queue Size, 綁定 topic_callback 函式與佔位符)
    }

  private:
    // 2. 實作 topic_callback 回呼函式：參數為常數指標 (const std_msgs::msg::String & msg) const
    // 3. 在函式內使用 RCLCPP_INFO 印出收到的資料內容

    // 4. 宣告訂閱者的指標變數
};

int main(int argc, char * argv[])
{
  // 5. 初始化 rclcpp
  // 6. 使用 std::make_shared 建立並啟動 MinimalSubscriber 節點 (spin)
  // 7. 關閉 rclcpp
  return 0;
}
```
<details>
<summary>👉 點擊展開：C++ 訂閱者解答</summary>

```cpp
#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using std::placeholders::_1;

class MinimalSubscriber : public rclcpp::Node
{
  public:
    MinimalSubscriber() : Node("minimal_subscriber")
    {
      // 解答 1
      subscription_ = this->create_subscription<std_msgs::msg::String>(
        "topic", 10, std::bind(&MinimalSubscriber::topic_callback, this, _1));
    }

  private:
    // 解答 2 & 3
    void topic_callback(const std_msgs::msg::String & msg) const
    {
      RCLCPP_INFO(this->get_logger(), "I heard: '%s'", msg.data.c_str());
    }
    
    // 解答 4
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  // 解答 5
  rclcpp::init(argc, argv);
  // 解答 6
  rclcpp::spin(std::make_shared<MinimalSubscriber>());
  // 解答 7
  rclcpp::shutdown();
  return 0;
}
```
</details>

#### ⚠️ 重點：C++ 設定檔更新 (`package.xml` & `CMakeLists.txt`)
與 Python 類似，C++ 專案也必須設定依賴與編譯規則。

1. **更新 `package.xml`**：
   在 `<buildtool_depend>ament_cmake</buildtool_depend>` 下方加入：
   ```xml
   <depend>rclcpp</depend>
   <depend>std_msgs</depend>
   ```

2. **更新 `CMakeLists.txt`**：告訴 CMake 如何編譯這兩個 `.cpp` 檔案並安裝它們。
   在 `find_package(ament_cmake REQUIRED)` 下方加入以下規則：
   ```cmake
   find_package(rclcpp REQUIRED)
   find_package(std_msgs REQUIRED)

   # 告訴編譯器要編譯的執行檔，並命名為 talker 與 listener
   add_executable(talker src/publisher_member_function.cpp)
   ament_target_dependencies(talker rclcpp std_msgs)

   add_executable(listener src/subscriber_member_function.cpp)
   ament_target_dependencies(listener rclcpp std_msgs)

   # 告訴系統要把編譯好的檔案安裝到 install/lib/<pkg_name> 下，ros2 run 才找得到
   install(TARGETS
     talker
     listener
     DESTINATION lib/${PROJECT_NAME})
   ```
*(修改完畢後，記得回到工作空間根目錄執行 `colcon build`！)*

---

## 5. 撰寫服務與客戶端 (Service & Client)

服務採用「請求 (Request) / 回應 (Response)」機制，適合單次觸發的任務（例如：計算兩個數字的總和）。

### 🐍 5.1 Python 實作 
**服務端 (Service Server)：**
```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts # 引入相加兩個整數的服務格式

class MinimalService(Node):
    def __init__(self):
        super().__init__('minimal_service')
        # 建立服務伺服器：(服務型態, '服務名稱', 回呼函式)
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        # 讀取 Client 傳來的 request，計算結果後賦值給 response
        response.sum = request.a + request.b
        self.get_logger().info('收到請求: a=%d, b=%d' % (request.a, request.b))
        
        return response # 必須回傳 response 物件給 Client
```

#### ✍️ 隨堂練習：撰寫 Python 客戶端 (Service Client)
換你試試看！請根據註解提示，建立一個會主動向 Server 發送請求的 Client 節點。

```python
import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class MinimalClientAsync(Node):
    def __init__(self):
        super().__init__('minimal_client_async')
        # 1. 使用 create_client 建立客戶端 (服務型態 AddTwoInts, 服務名稱 'add_two_ints')
        
        # 2. 等待 Server 上線 (wait_for_service)，若沒上線則持續印出「等待中...」
        
        # 3. 實例化 Request 物件 (AddTwoInts.Request())
        pass

    def send_request(self, a, b):
        # 4. 將參數 a, b 填入 request 並發送 (call_async)
        # 5. 使用 rclpy.spin_until_future_complete 等待結果
        # 6. 回傳 future 的 result()
        pass

def main(args=None):
    # 7. 初始化、建立 Client 節點、發送請求 (41, 1)、印出結果、關閉
    pass

if __name__ == '__main__':
    main()
```
<details>
<summary>👉 點擊展開：Python 客戶端解答</summary>

```python
import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class MinimalClientAsync(Node):
    def __init__(self):
        super().__init__('minimal_client_async')
        # 解答 1
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        
        # 解答 2
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待服務端上線中...')
            
        # 解答 3
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        # 解答 4
        self.future = self.cli.call_async(self.req)
        # 解答 5
        rclpy.spin_until_future_complete(self, self.future)
        
        # 解答 6
        return self.future.result()

def main(args=None):
    rclpy.init(args=args)
    minimal_client = MinimalClientAsync()
    # 解答 7
    response = minimal_client.send_request(41, 1)
    minimal_client.get_logger().info('結果: %d' % response.sum)
    minimal_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```
</details>

#### ⚠️ 重點：Python 設定檔更新 (服務)
別忘了更新設定檔，讓系統認識新的服務與客戶端：
1. **`package.xml`**: 加入 `example_interfaces` 依賴。
   ```xml
   <exec_depend>example_interfaces</exec_depend>
   ```
2. **`setup.py`**: 在 `console_scripts` 陣列加入新節點資料。
   ```python
   'server = py_test_pkg.service_member_function:main',
   'client = py_test_pkg.client_member_function:main',
   ```

---

### ⚙️ 5.2 C++ 實作
**客戶端 (Service Client)：**
```cpp
#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

using namespace std::chrono_literals;

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("minimal_client");
  
  // 建立客戶端，指定與 Server 相同的服務型態與名稱
  auto client = node->create_client<example_interfaces::srv::AddTwoInts>("add_two_ints");

  // 準備請求資料 (Request)
  auto request = std::make_shared<example_interfaces::srv::AddTwoInts::Request>();
  request->a = 41;
  request->b = 1;

  // 使用 while 迴圈等待 Server 上線，每秒檢查一次
  while (!client->wait_for_service(1s)) {
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "等待服務端上線中...");
  }

  // 非同步發送請求 (async_send_request 不會卡死主程式)
  auto result = client->async_send_request(request);
  
  // 等待 Server 回傳結果，若成功則印出
  if (rclcpp::spin_until_future_complete(node, result) == rclcpp::FutureReturnCode::SUCCESS) {
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "計算結果: %ld", result.get()->sum);
  } else {
    RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "呼叫服務失敗");
  }

  rclcpp::shutdown();
  return 0;
}
```

#### ✍️ 隨堂練習：撰寫 C++ 服務端 (Service Server)
Client 需要有人接聽電話，請根據註解提示實作出 C++ 的 Service Server！

```cpp
#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"
#include <memory>

// 1. 實作 add 回呼函式，參數為 Request 與 Response 的 shared_ptr
void add(const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request,
         std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response)
{
    // 2. 計算 request 內的 a+b 並填入 response->sum
    // 3. 印出收到的請求內容 (RCLCPP_INFO)
}

int main(int argc, char **argv)
{
  // 4. 初始化 rclcpp
  // 5. 建立節點 "minimal_service"
  // 6. 建立服務端 (create_service)，綁定上述的 add 函式
  // 7. 啟動節點 (spin)、關閉 rclcpp
  return 0;
}
```
<details>
<summary>👉 點擊展開：C++ 服務端解答</summary>

```cpp
#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"
#include <memory>

// 解答 1
void add(const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request,
         std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response)
{
  // 解答 2
  response->sum = request->a + request->b;
  // 解答 3
  RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "收到請求: a=%ld, b=%ld", request->a, request->b);
}

int main(int argc, char **argv)
{
  // 解答 4
  rclcpp::init(argc, argv);
  // 解答 5
  auto node = rclcpp::Node::make_shared("minimal_service");
  
  // 解答 6
  auto service = node->create_service<example_interfaces::srv::AddTwoInts>("add_two_ints", &add);
  
  RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "準備好執行整數相加服務了。");
  
  // 解答 7
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```
</details>

#### ⚠️ 重點：C++ 設定檔更新 (服務)
C++ 的服務與客戶端同樣需要手動註冊：
1. **`package.xml`**: 加入 `example_interfaces` 依賴。
   ```xml
   <depend>example_interfaces</depend>
   ```
2. **`CMakeLists.txt`**: 宣告執行檔並連結依賴。
   ```cmake
   find_package(example_interfaces REQUIRED)

   # 增加 server 端執行檔與相依
   add_executable(server src/service_member_function.cpp)
   ament_target_dependencies(server rclcpp example_interfaces)

   # 增加 client 端執行檔與相依
   add_executable(client src/client_member_function.cpp)
   ament_target_dependencies(client rclcpp example_interfaces)

   # 確保兩者都被安裝
   install(TARGETS server client DESTINATION lib/${PROJECT_NAME})
   ```

---

## 6. 自訂資料格式 (Custom msg and srv files)

**觀念解說：**
在前面的單元中，我們使用了系統內建的資料格式（例如 `std_msgs/msg/String` 和 `example_interfaces/srv/AddTwoInts`）。但在真實的機器人專案中，你常常會需要定義自己的通訊格式（例如同時傳輸速度與溫度）。

在 ROS 2 中，強烈建議將這些自訂介面獨立成一個專屬的 **`ament_cmake` 套件**（即使你主要使用 Python 開發，介面套件也必須是 CMake）。

### 步驟 1：建立專屬介面套件
請確認你在 `ros2_ws/src` 目錄下，然後執行：
```bash
ros2 pkg create --build-type ament_cmake --license Apache-2.0 tutorial_interfaces
```
**指令詳細拆解**

1. **`ros2 pkg create`**
   * **說明**：這是 ROS 2 命令列工具中，用來「建立新套件 (Package)」的基礎指令。執行後，系統會自動幫你生成資料夾與必要的設定檔（如 `package.xml`）。

2. **`--build-type ament_cmake`**
   * **說明**：指定這個套件的編譯系統為 CMake（通常用於 C++ 專案）。
   * **核心觀念**：在 ROS 2 中，**所有用來定義 `.msg` (訊息)、`.srv` (服務)、`.action` (動作) 的「介面套件」，都強制必須是 CMake 套件**。底層的程式碼產生器 (`rosidl`) 需要透過 CMake 的編譯流程，才能將純文字定義檔，轉換成 C++ 和 Python 都能讀懂的底層程式碼。

3. **`--license Apache-2.0`**
   * **說明**：宣告這個套件的開源授權條款為 Apache 2.0。
   * **好處**：加上這個參數是一個非常好的開發習慣。這會讓系統在自動生成 `package.xml` 時，直接幫你填好授權欄位，避免日後檢查時出現煩人的 `TODO: License declaration` 警告。

4. **`tutorial_interfaces`**
   * **說明**：賦予這個新套件的**名稱**。按照 ROS 2 的命名慣例，專門用來放自訂格式的套件，名稱通常會以 `_interfaces` 結尾，這樣其他人一看就知道這個套件裡面沒有執行檔，只有通訊格式。

接著，進入該套件，並建立 `msg` 和 `srv` 資料夾來存放定義檔：
```bash
cd tutorial_interfaces
mkdir msg srv
```

### 步驟 2：建立自訂 Message (`.msg`)
在 `msg/` 目錄下建立一個 `Num.msg` 檔案。它用來宣告我們自訂的主題資料結構：
```text
# msg/Num.msg
int64 num
```
我們也可以引用其他套件的資料型態。例如建立 `Sphere.msg`：
```text
# msg/Sphere.msg
geometry_msgs/Point center
float64 radius
```

### 步驟 3：建立自訂 Service (`.srv`)
在 `srv/` 目錄下建立 `AddThreeInts.srv` 檔案。使用 `---` 來分隔 Request 和 Response：
```text
# srv/AddThreeInts.srv
int64 a
int64 b
int64 c
---
int64 sum
```

### 步驟 4：修改 `CMakeLists.txt`
為了將我們寫的純文字定義檔轉換為 C++ 與 Python 可用的程式碼，必須修改 `CMakeLists.txt`。請加入以下內容：

```cmake
# 尋找依賴（若 msg 內有使用到其他套件的型態）
find_package(geometry_msgs REQUIRED)

# 尋找產生器
find_package(rosidl_default_generators REQUIRED)

# 宣告要生成的介面檔案
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Num.msg"
  "msg/Sphere.msg"
  "srv/AddThreeInts.srv"
  DEPENDENCIES geometry_msgs # 加入我們依賴的其他套件
)
```

### 步驟 5：修改 `package.xml`
宣告生成介面所需的工具與執行期依賴。請在 `<package>` 標籤內加入：

```xml
<depend>geometry_msgs</depend>
<buildtool_depend>rosidl_default_generators</buildtool_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

### 步驟 6：編譯與驗證
回到工作空間根目錄進行編譯，並指定只編譯這個介面套件：
```bash
cd ~/ros2_ws
colcon build --packages-select tutorial_interfaces
```

編譯完成並 `source install/setup.bash` 載入環境後，你可以使用以下指令來驗證自訂介面是否成功註冊到 ROS 2 系統中：
```bash
# 查看自訂的 Num 格式
ros2 interface show tutorial_interfaces/msg/Num

# 終端機應輸出：
# int64 num
```
現在可以像引入 `String` 一樣，在 C++ 或 Python 節點中 `import tutorial_interfaces.msg` 來使用自訂的資料格式了！

---

## 7. 在單一套件中定義與使用自訂介面 (Single-Package Interfaces)

**觀念解說：**
在官方的最佳實踐中，將自訂通訊格式（`.msg`, `.srv`）獨立成一個專屬套件（如上一章的做法）是最乾淨的。但有時候為了方便開發，我們希望**在同一個套件中定義 `.msg`，然後立刻在同一個套件的 C++ 節點中使用它**。

⚠️ **重要限制：** 因為介面定義的底層必須依賴 CMake（`ament_cmake`）來生成程式碼，所以這個混合套件**必須是 C++ 專案套件**。如果你主要寫 Python，官方仍建議將介面獨立成另一個 CMake 套件。

### 步驟 1：建立混合套件與定義檔
首先，建立一個新的 C++ 套件 `more_interfaces`，並在裡面新增一個 `msg` 資料夾：
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake --license Apache-2.0 more_interfaces
mkdir more_interfaces/msg
```
在 `more_interfaces/msg` 下建立 `AddressBook.msg` 通訊錄格式：
```text
uint8 PHONE_TYPE_HOME=0
uint8 PHONE_TYPE_WORK=1
uint8 PHONE_TYPE_MOBILE=2

string first_name
string last_name
string phone_number
uint8 phone_type
```

### 步驟 2：設定套件依賴 (`package.xml`)
打開 `package.xml`，加入產生程式碼必備的三個標籤：
```xml
<buildtool_depend>rosidl_default_generators</buildtool_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

### 步驟 3：撰寫同套件的 C++ 發布者
在 `more_interfaces/src` 建立 `publish_address_book.cpp`：
```cpp
#include <chrono>
#include <memory>
#include "rclcpp/rclcpp.hpp"
// 1. 引入自己套件內剛定義好的格式標頭檔 (即使還沒編譯，先這樣寫)
#include "more_interfaces/msg/address_book.hpp"

using namespace std::chrono_literals;

class AddressBookPublisher : public rclcpp::Node
{
public:
  AddressBookPublisher() : Node("address_book_publisher")
  {
    // 2. 建立發布者
    address_book_publisher_ = this->create_publisher<more_interfaces::msg::AddressBook>("address_book", 10);
    
    // 3. 建立發布內容與計時器
    auto publish_msg = [this]() -> void {
      auto message = more_interfaces::msg::AddressBook();
      message.first_name = "John";
      message.last_name = "Doe";
      message.phone_number = "1234567890";
      message.phone_type = message.PHONE_TYPE_MOBILE;

      std::cout << "發布聯絡人\n名字:" << message.first_name << " 姓氏:" << message.last_name << std::endl;
      this->address_book_publisher_->publish(message);
    };
    timer_ = this->create_wall_timer(1s, publish_msg);
  }

private:
  rclcpp::Publisher<more_interfaces::msg::AddressBook>::SharedPtr address_book_publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<AddressBookPublisher>());
  rclcpp::shutdown();
  return 0;
}
```

### 步驟 4：修改 `CMakeLists.txt` (⚠️ 最關鍵的一步)
要在同一個套件內讓 C++ 節點成功連結到剛剛生成的 `.msg` 程式碼，CMake 需要特殊的寫法。請將以下內容加入你的 `CMakeLists.txt` 中：

```cmake
# --- 1. 生成 Message 程式碼 ---
find_package(rosidl_default_generators REQUIRED)

# 手動列出所有的 .msg 檔案
set(msg_files
  "msg/AddressBook.msg"
)
# 呼叫介面生成器
rosidl_generate_interfaces(${PROJECT_NAME} ${msg_files})
ament_export_dependencies(rosidl_default_runtime)

# --- 2. 編譯 C++ 節點 ---
find_package(rclcpp REQUIRED)
add_executable(publish_address_book src/publish_address_book.cpp)
ament_target_dependencies(publish_address_book rclcpp)

# --- 3. ⚠️ 特殊步驟：連結同套件內的介面 ---
# 取得生成的 C++ 介面目標名稱 (typesupport)
rosidl_get_typesupport_target(cpp_typesupport_target ${PROJECT_NAME} rosidl_typesupport_cpp)
# 強制將你的執行檔與剛剛生成的介面目標進行連結
target_link_libraries(publish_address_book "${cpp_typesupport_target}")

# --- 4. 安裝執行檔 ---
install(TARGETS publish_address_book DESTINATION lib/${PROJECT_NAME})
```
*💡 **解說**：如果介面是放在獨立的套件（如上一章），你只需要 `ament_target_dependencies` 告訴編譯器去找外部套件就可以了。但因為現在介面和節點在**同一個套件同時編譯**，介面還沒真正被「安裝」到系統中，所以必須透過 `rosidl_get_typesupport_target` 和 `target_link_libraries` 手動拉線，告訴編譯器它們之間的依賴關係！*

### 步驟 5：編譯與測試
回到工作空間根目錄進行編譯並執行：
```bash
cd ~/ros2_ws
# --packages-up-to 會編譯這個套件以及它所依賴的其他套件
colcon build --packages-up-to more_interfaces

source install/setup.bash
ros2 run more_interfaces publish_address_book
```
接著你可以開另一個終端機使用 `ros2 topic echo /address_book` 來檢查自訂格式是否成功被你的 C++ 節點廣播出來了！

---

## 8. 在類別中使用參數 (Using Parameters in a class)

**觀念解說：**
參數 (Parameters) 是節點的動態設定值。透過程式碼宣告參數，我們可以讓使用者在啟動節點時去改變程式的行為，而不需要重新編譯原始碼。

這個單元不僅會教你如何「讀取」參數，還會教你如何在程式中動態「覆寫」參數，以及如何透過 Launch 檔來一次設定好所有參數。

### 🐍 8.1 Python 實作
建立一個名為 `python_parameters` 的套件，並撰寫以下節點：

```python
import rclpy
import rclpy.node

class MinimalParam(rclpy.node.Node):
    def __init__(self):
        super().__init__('minimal_param_node')
        
        # 1. (選用) 加入參數描述 (ParameterDescriptor)
        # 這樣當別人用 ros2 param describe 指令時，就能看到這個參數的用途說明
        from rcl_interfaces.msg import ParameterDescriptor
        my_desc = ParameterDescriptor(description='這是我的專屬字串參數！')
        
        # 2. 宣告參數：(參數名稱, 預設值, 參數描述物件)
        # 系統會從預設值 'world' 自動推斷出這個參數是 String 型態
        self.declare_parameter('my_parameter', 'world', my_desc)

        # 3. 建立計時器，每 1 秒讀取並印出參數值
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        # 4. 取得參數的當前值
        my_param = self.get_parameter('my_parameter').get_parameter_value().string_value
        
        self.get_logger().info('Hello %s!' % my_param)
        
        # 5. 在程式內動態重設(寫入)參數值
        # 這裡我們強制把它設回 'world'。這樣即使使用者從外部用指令修改了參數，下一秒又會被改回來
        my_new_param = rclpy.parameter.Parameter(
            'my_parameter',
            rclpy.Parameter.Type.STRING,
            'world'
        )
        all_new_parameters = [my_new_param]
        self.set_parameters(all_new_parameters)

def main():
    rclpy.init()
    node = MinimalParam()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
```

### ⚙️ 8.2 C++ 實作
建立一個名為 `cpp_parameters` 的套件，並撰寫以下節點：

```cpp
#include <chrono>
#include <functional>
#include <string>
#include <rclcpp/rclcpp.hpp>

using namespace std::chrono_literals;

class MinimalParam : public rclcpp::Node
{
public:
  MinimalParam() : Node("minimal_param_node")
  {
    // 1. (選用) 建立參數描述物件
    auto param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    param_desc.description = "This parameter is mine!";

    // 2. 宣告參數，名稱為 "my_parameter"，預設值為 "world"，並附上描述
    this->declare_parameter("my_parameter", "world", param_desc);

    // 3. 建立計時器
    timer_ = this->create_wall_timer(
      1000ms, std::bind(&MinimalParam::timer_callback, this));
  }

private:
  void timer_callback()
  {
    // 4. 取得參數值，並轉型為字串
    std::string my_param = this->get_parameter("my_parameter").as_string();

    RCLCPP_INFO(this->get_logger(), "Hello %s!", my_param.c_str());

    // 5. 動態重設參數值
    // 建立一個 Parameter 物件陣列，並透過 set_parameters 強制寫入
    std::vector<rclcpp::Parameter> all_new_parameters{rclcpp::Parameter("my_parameter", "world")};
    this->set_parameters(all_new_parameters);
  }
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MinimalParam>());
  rclcpp::shutdown();
  return 0;
}
```

### 🚀 8.3 透過 Launch 檔啟動並注入參數 (進階必學)

每次啟動節點都要手動用 `ros2 param set` 修改參數太麻煩了。在實務上，我們會撰寫一個 Python 的 `Launch` 檔，在啟動節點的同時就把參數「塞」進去。

1. 在你的套件目錄下建立一個 `launch` 資料夾，並在裡面建立 `parameters_launch.py`：

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='你的套件名稱',  # 例如: 'cpp_parameters' 或 'python_parameters'
            executable='你的執行檔名稱', # 例如: 'minimal_param_node'
            name='custom_minimal_param_node',
            output='screen',
            emulate_tty=True,
            # 在這裡注入參數值！
            parameters=[
                {'my_parameter': 'earth'}
            ]
        )
    ])
```

2. **(極度重要) 設定檔更新：讓系統安裝 Launch 檔**
如果你沒有做這一步，系統編譯後會找不到你的 Launch 檔！

* **對於 Python 套件 (`setup.py`)**：
    加入以下 import 語法，並在 `data_files` 陣列中新增一行：
    ```python
    import os
    from glob import glob

    setup(
        # ...
        data_files=[
            # ... 其他預設的行 ...
            # 告訴系統把 launch 資料夾內的所有檔案安裝到 share 目錄下
            (os.path.join('share', package_name, 'launch'), glob('launch/*')),
        ],
    )
    ```

* **對於 C++ 套件 (`CMakeLists.txt`)**：
    在 `install(TARGETS ...)` 的下方加入這段程式碼：
    ```cmake
    # 告訴 CMake 將整個 launch 資料夾安裝到系統的 share 目錄下
    install(
      DIRECTORY launch
      DESTINATION share/${PROJECT_NAME}
    )
    ```

編譯完成後，你就可以用這行指令啟動節點，並看到終端機印出 `Hello earth!`（因為參數被 Launch 檔成功覆寫了）！
```bash
ros2 launch <你的套件名稱> parameters_launch.py
```

---

## 9. 系統診斷與進階工具

* **`ros2doctor`**：當你的 ROS 2 環境出現詭異的問題時（例如節點無法通訊），可以在終端機輸入 `ros2 doctor`。它會幫你檢查網路設定、版本相容性以及環境變數是否設定正確。加入 `--report` 參數可以看更詳細的系統報告。
* **Plugins (C++)**：在 C++ 中，你可以使用 `pluginlib` 來建立外掛程式。這允許節點在執行期間動態載入函式庫，而不需要將所有程式碼靜態連結在一起，這對於大型機器人專案的架構設計非常有用。
