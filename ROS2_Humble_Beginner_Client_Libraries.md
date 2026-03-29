# ROS 2 Humble 初階程式設計 (Client Libraries) 完整講義

本講義涵蓋 ROS 2 官方初階客戶端函式庫教學的完整流程。我們將先從巨觀的角度了解專案架構，接著動手建立工作空間、撰寫套件，並實作**發布/訂閱**、**服務/客戶端**與**參數**。

資料來源: [ROS 2 Humble Beginner Client Libraries](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries.html)

## 1. 核心觀念：ROS 2 工作空間 (Workspace) 檔案架構總覽

在 ROS 2 中，所有的開發都發生在一個稱為 **「工作空間 (Workspace)」** 的資料夾中（通常命名為 `ros2_ws`）。這就像是你的專屬虛擬桌面。當你使用 `colcon build` 指令編譯後，這個工作空間會長出特定的骨架。

了解這些檔案的位置與作用，是你在 ROS 2 開發中「不迷路」的第一步。


```text
ros2_ws/                       <-- 工作空間根目錄 (Workspace Root)，colcon build 只能在這裡執行
│
├── build/                     <-- 🚫 [系統生成] 編譯過程的暫存檔 (出錯可直接刪除)
├── install/                   <-- 🚫 [系統生成] 編譯完成的可執行檔與環境設定 (source 的目標)
├── log/                       <-- 🚫 [系統生成] 編譯與執行的日誌檔 (尋找底層報錯)
│
└── src/                       <-- ⭐ [開發者專區] 所有的套件 (Packages) 都建立在這裡
    │
    ├── my_cpp_pkg/            <-- 📦 類型 A：純 C++ 專案套件 (ament_cmake)
    │   ├── CMakeLists.txt     <-- [設定檔] 編譯藍圖、宣告依賴與安裝規則
    │   ├── package.xml        <-- [設定檔] 套件身分證、宣告 ROS 2 依賴函式庫
    │   ├── include/           <-- [資料夾] 存放 C++ 標頭檔 (.h / .hpp)
    │   │   └── my_cpp_pkg/    <-- (慣例上會再包一層與套件同名的資料夾)
    │   │       └── my_node.hpp
    │   ├── src/               <-- [資料夾] 存放 C++ 原始碼 (.cpp)
    │   │   └── my_node.cpp
    │   └── launch/            <-- [資料夾] 存放 Launch 啟動腳本 (.py)
    │       └── my_launch.py
    │
    ├── my_python_pkg/         <-- 📦 類型 B：純 Python 專案套件 (ament_python)
    │   ├── package.xml        <-- [設定檔] 套件身分證、宣告 ROS 2 依賴函式庫
    │   ├── setup.py           <-- [設定檔] 註冊執行檔進入點、宣告 Launch 安裝規則
    │   ├── setup.cfg          <-- [設定檔] 系統生成，指示執行檔的安裝路徑
    │   ├── my_python_pkg/     <-- [資料夾] 存放 Python 程式碼 (⚠️ 必須與套件完全同名)
    │   │   ├── __init__.py    <-- [程式碼] 讓 Python 認得這是一個模組 (不可刪)
    │   │   └── my_node.py     <-- [程式碼] 你的 ROS 2 節點主程式
    │   └── launch/            <-- [資料夾] 存放 Launch 啟動腳本 (.py)
    │       └── my_launch.py
    │
    ├── tutorial_interfaces/   <-- 📦 類型 C：獨立通訊格式套件 (必須是 ament_cmake)
    │   ├── CMakeLists.txt     <-- [設定檔] 呼叫 rosidl_generate_interfaces 生成程式碼
    │   ├── package.xml        <-- [設定檔] 宣告 msg/srv 生成器的依賴
    │   ├── msg/               <-- [資料夾] 存放自訂主題格式
    │   │   ├── Num.msg
    │   │   └── Sphere.msg
    │   └── srv/               <-- [資料夾] 存放自訂服務格式
    │       └── AddThreeInts.srv
    │
    └── more_interfaces/       <-- 📦 類型 D：混合套件 (同時包含 C++ 節點與自訂格式)
        ├── CMakeLists.txt     <-- [設定檔] 寫法最複雜，需手動連結 msg 目標與 cpp 執行檔
        ├── package.xml        <-- [設定檔] 需同時宣告 C++ 與介面生成器的依賴
        ├── msg/               <-- [資料夾] 在同一個套件內定義格式
        │   └── AddressBook.msg 
        └── src/               <-- [資料夾] 在同一個套件內寫 C++ 節點去引用它
            └── publish_address_book.cpp
```

---

### 💡 核心架構解析與開發守則

#### 1. 系統生成區 vs. 手動開發區 (開發黃金守則)
* **`src/` (絕對重點)**：這是整個工作空間中，**唯一**需要你手動建立、操作與寫程式的地方。
* **`build/`、`install/`、`log/`**：這三個資料夾是 `colcon build` 後系統自動吐出來的。
  > ⚠️ **避坑指南**：如果你覺得系統環境卡住了、或是編譯出現無法解釋的嚴重錯誤，**請直接大膽把這三個資料夾刪除 (`rm -rf build install log`)**，然後重新 `colcon build`。這就像是幫 ROS 2 進行「恢復原廠設定」，完全不會傷害到你寫在 `src/` 裡的程式碼！

#### 2. C++ 與 Python 套件架構對比
初學者最常犯的錯，就是在錯誤的資料夾裡寫程式，或是改錯設定檔。請牢記以下對比：

| 功能定位 | ⚙️ C++ 套件 (`ament_cmake`) | 🐍 Python 套件 (`ament_python`) |
| :--- | :--- | :--- |
| **套件身分證 (必備)** | `package.xml` | `package.xml` |
| **編譯/安裝藍圖** | `CMakeLists.txt` | `setup.py` (與 `setup.cfg`) |
| **主程式碼放在哪？** | 套件內的 `src/` 資料夾 | 與套件**「完全同名」**的子資料夾內 |
| **標頭檔/模組宣告** | `include/<pkg_name>/` | 同名資料夾內的 `__init__.py` |

#### 3. 專屬功能資料夾：`launch/` 與 `msg/`、`srv/`
除了寫主程式（Node）之外，你還會常在套件內建立這兩種資料夾：

* **`launch/` (啟動腳本區)**：
   * 這是存放 **啟動腳本 (Launch files)** 的地方。當你需要一次啟動多個節點，或是**在啟動時動態注入參數 (Parameters)**，就會在這裡撰寫 `.py` 的腳本。
   * ⚠️ **極度重要**：寫完 launch 檔後，必須在 `setup.py` 的 `data_files` 或 `CMakeLists.txt` 的 `install(DIRECTORY...)` 中設定安裝規則，否則 `ros2 launch` 會找不到檔案！（詳見講義第 8 章實作）。
   
* **`msg/`, `srv/`, `action/` (通訊定義區)**：
   * 這些資料夾只存放「純文字定義檔」，用來定義節點之間資料傳遞的格式。
   * ROS 2 的編譯系統 (`rosidl`) 會在編譯時讀取這些檔案，並自動幫你生成對應的 C++ 標頭檔和 Python 模組。

#### 4. 細節提醒

1.  **C++ 的 `include` 資料夾層級**：
    在標準的 C++ 套件中，`include/` 底下通常會再建立一個 **與套件同名的子資料夾**（例如 `include/my_cpp_pkg/`），然後才把 `.hpp` 標頭檔放進去。這樣做是為了避免當專案變大、套件變多時，不同套件的標頭檔名稱發生衝突。
2.  **Python 的 `__init__.py`**：
    這個檔案通常是空的，但它**絕對不能刪掉**。沒有它，`colcon build` 和 Python 直譯器就不會把這個資料夾當作一個合法的模組，你的 `ros2 run` 就會報錯說找不到節點。
3.  **介面套件 (類型 C 與 D) 的底層邏輯**：
    只要你的套件裡面有 `.msg` 或 `.srv` 檔案，這個套件的編譯類型就**必須是 C++ (`ament_cmake`)**。因為 ROS 2 需要呼叫 CMake 底層的產生器，把這些純文字檔編譯成 Python 和 C++ 都能呼叫的底層記憶體結構。
---

## 2. 建立工作空間與編譯 (Workspace & `colcon`)

**觀念解說：**
在 ROS 2 中，所有的開發都必須在一個名為 **工作空間 (Workspace)** 的大資料夾內進行。你不能在桌面上隨便建一個檔案就開始寫 ROS 2。通常我們會將這個核心資料夾命名為 `ros2_ws`。

### ⚠️ 核心防呆守則：指令要在哪裡下？
在 ROS 2 的開發日常中，你必須牢記兩個最重要的目錄位置：
1. **開發區 (`~/ros2_ws/src`)**：所有「建立套件 (create)」、「寫程式」的動作，都在這裡進行。
2. **工作空間根目錄 (`~/ros2_ws`)**：所有「編譯 (colcon build)」的動作，**絕對只能在這裡進行**。如果在 `src` 裡面按編譯，系統會大亂！

---

### 實作步驟與指令

**Step 1: 建立工作空間與 src 資料夾**
* **所在位置**：任何地方皆可 (通常在 Home 目錄 `~`)
```bash
mkdir -p ~/ros2_ws/src
```

**Step 2: 首次編譯生成系統架構**
* **所在位置**：必須在工作空間根目錄 (`~/ros2_ws`)
```bash
cd ~/ros2_ws
# ⭐ 建議使用以下進階指令進行編譯
colcon build --symlink-install --merge-install
```
> 💡 **為什麼建議這樣下指令？** (詳見 3.5.2 章節)
> * `--symlink-install`: 讓 Python 程式碼與 Launch 檔修改後即刻生效。
> * `--merge-install`: 將所有套件安裝在同一個層級，讓路徑更簡潔。

*(執行後，系統會自動在 `ros2_ws` 內生成 `build/`、`install/`、`log/` 三個資料夾)*

**Step 3: 載入環境設定 (Source)**
* **所在位置**：任何地方皆可 (但路徑要指對)
* **注意事項**：編譯完畢後，系統會把能執行的東西放在 `install` 資料夾中。**每次你開啟一個新的終端機視窗**，在執行你自己寫的程式前，都必須執行以下指令：
```bash
# 如果你剛好在 ~/ros2_ws 目錄下：
source install/setup.bash

# 為了防呆，建議直接打絕對路徑 (不管在哪個目錄都能載入)：
source ~/ros2_ws/install/setup.bash
```

---

## 3. 建立套件 (Creating a Package)

**觀念解說：**
套件 (Package) 是 ROS 2 程式碼的整理單位。一個套件裡面可以包含多個節點 (Node)。
在同一個 `src` 資料夾內，你可以建立無數個套件（有些用 Python 寫，有些用 C++ 寫），但**不能將套件巢狀建立**（套件裡面不能包著另一個套件）。

### 3.1 建立套件與預設節點

* **所在位置**：必須在 `~/ros2_ws/src` 下！
* **指令模板**：
  `ros2 pkg create --build-type <編譯類型> --license Apache-2.0 --node-name <預設節點名稱> <套件名稱>`

**指令參數解說：**
* `<編譯類型>`：Python 請填 `ament_python`；C++ 請填 `ament_cmake`。
* `<預設節點名稱>`：系統會順便幫你生成一隻印著 Hello World 的程式碼，請給這支程式一個名字。
* `<套件名稱>`：這個專案資料夾的名字（通常用底線命名法）。

**實作指令 (以 Python 和 C++ 為例)：**
```bash
cd ~/ros2_ws/src

# 範例 A：建立 Python 套件
# 建立一個名為 py_test_pkg 的套件，並在裡面產生一支名為 my_node 的 Python 程式
ros2 pkg create --build-type ament_python --license Apache-2.0 --node-name my_node py_test_pkg

# 範例 B：建立 C++ 套件
# 建立一個名為 cpp_test_pkg 的套件，並在裡面產生一支名為 my_node 的 C++ 程式
ros2 pkg create --build-type ament_cmake --license Apache-2.0 --node-name my_node cpp_test_pkg
```

### 3.2 自訂套件資訊 (Customize package.xml & setup.py)
*(此部分為設定檔修改，請直接使用文字編輯器如 VS Code 打開檔案修改)*

1. **修改 `package.xml` (C++ 與 Python 皆需)：**
   打開 `ros2_ws/src/py_test_pkg/package.xml`，修改描述與維護者資訊：
   ```xml
   <description>Beginner client libraries tutorials practice package</description>
   <maintainer email="your_email@example.com">Your Name</maintainer>
   <license>Apache License 2.0</license>
   ```
2. **修改 `setup.py` (僅 Python 需)：**
   打開 `ros2_ws/src/py_test_pkg/setup.py`，確保內容與 `package.xml` 完全一致。

### 3.3 編譯與執行 (Build & Run)

當你寫好程式後，必須經過「編譯 ➔ 載入環境 ➔ 執行」三個步驟。

* **指令模板**：
  `ros2 run <套件名稱> <執行檔/節點名稱>`

**實作指令：**
```bash
# 步驟 1：編譯 (⚠️ 必須回到根目錄)
cd ~/ros2_ws
colcon build --packages-select py_test_pkg cpp_test_pkg

# 步驟 2：載入環境 (⚠️ 每次開新終端機都要做)
source install/setup.bash

# 步驟 3：執行程式 (只要有 source 過，在哪個目錄執行都沒關係)
ros2 run py_test_pkg my_node
```
*(成功的話，終端機將會印出 `Hi from py_test_pkg.`)*

---

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

1. **[目錄: `~/ros2_ws/src`] 建立套件殼層**：使用 `ros2 pkg create ...` 指令。
2. **[目錄: 編輯器] 撰寫源碼**：在原始碼資料夾中編寫 `.py` 或 `.cpp` 檔案。
3. **[目錄: 編輯器] 配置依賴**：在 `package.xml` 加入用到的函式庫。
4. **[目錄: 編輯器] 配置編譯與執行檔**：在 `setup.py` 或 `CMakeLists.txt` 中定義程式的進入點。
5. **[目錄: `~/ros2_ws`] 編譯工作空間**：執行 `colcon build`。
6. **[目錄: 任意處] 載入環境並執行**：執行 `source ~/ros2_ws/install/setup.bash`，接著 `ros2 run <套件> <節點>`。

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
*   **專業開發者黃金指令** (強烈建議啟動)：
    ```bash
    colcon build --symlink-install --merge-install
    ```
    *💡 **參數詳細原因解說：***
    *   **`--symlink-install` (軟連結安裝)**：
        在預設情況下，`colcon` 會將你的 Python 檔、Launch 檔「複製」一份到 `install/` 資料夾。如果你改了程式碼，就必須重新編譯。加上這個參數後，系統會改用「捷徑 (Symlink)」指向你的原始碼路徑。因此，**修改 Python 或 Launch 檔後，不需重新編譯即可生效**（注意：C++ 仍需重新編譯，因為機器碼必須重新產生）。
    *   **`--merge-install` (合併安裝)**：
        ROS 2 預設會為每個套件在 `install/` 下建立獨立資料夾。當套件變多時，環境變數 (PATH) 會變得非常冗長。此參數會將所有套件的執行檔、資源檔合併放在同一個 `lib`、`share` 資料夾下，讓系統搜尋檔案更有效率，也能避免某些環境下的路徑長度限制問題。

    
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

**情境引入 (Why)：**
在送餐機器人中，有些數據是需要「連續不斷」回報的。例如：機器人身上的**電池感測器 (Publisher)** 需要每秒鐘向外廣播一次目前的剩餘電量；而機器人的**主控台儀表板 (Subscriber)** 只要一收到數據，就會更新螢幕顯示。

這就是「主題 (Topic)」發布與訂閱的經典場景。在這個實作中，我們將使用內建的字串格式 (`String`)，來模擬這個電池監控廣播系統。

---

### 🐍 4.1 Python 實作流程：電池監控系統

#### Step 1: 建立 Python 套件
開啟終端機，進入你的工作空間並建立名為 `py_battery_monitor` 的套件：
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python --license Apache-2.0 py_battery_monitor
```

#### Step 2: 撰寫發布者 (電池感測器節點)
在 `~/ros2_ws/src/py_battery_monitor/py_battery_monitor/` 目錄下，建立 `sensor.py`：

```python
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
```

#### ✍️ Step 3: 隨堂練習 - 撰寫訂閱者 (儀表板節點)
看完發布者的寫法，請嘗試根據下方的註解提示，在同個目錄下建立 `dashboard.py`，並練習實作出接收電量數據的儀表板。

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class BatteryDashboard(Node):
    def __init__(self):
        # 1. 初始化父類別，節點命名為 'battery_dashboard'
        # 2. 使用 create_subscription 建立訂閱者 (型態為 String, 主題為 'battery_status', 回呼函式為 listener_callback, Queue Size 為 10)
        pass

    # 3. 實作 listener_callback，功能是用 get_logger().info 印出收到的 msg.data 內容
    def listener_callback(self, msg):
        pass

def main(args=None):
    # 4. 初始化 rclpy、建立 BatteryDashboard 節點物件、啟動 spin、最後關閉
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

class BatteryDashboard(Node):
    def __init__(self):
        super().__init__('battery_dashboard')
        # 解答 1 & 2
        self.subscription = self.create_subscription(String, 'battery_status', self.listener_callback, 10)
        self.subscription  # 防止 unused variable 警告

    # 解答 3
    def listener_callback(self, msg):
        self.get_logger().info(f'🖥️ 儀表板接收到: "{msg.data}"')

def main(args=None):
    # 解答 4
    rclpy.init(args=args)
    battery_dashboard = BatteryDashboard()
    rclpy.spin(battery_dashboard)
    battery_dashboard.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

#### 💡 補充：為什麼要多寫一行 `self.subscription`？
在 Python 的 `__init__` 中，你會看到最後一行單獨寫了 `self.subscription`。這是防禦性程式碼：一方面可以防止 Linter (如 Flake8) 報出「變數未使用」的警告，另一方面能明確標示這個訂閱者物件必須存在，避免被 Python 的垃圾回收機制意外清除。

</details>


#### Step 4: 更新設定檔 (`package.xml` & `setup.py`)
寫完程式後，必須註冊執行檔。打開 `py_battery_monitor` 資料夾：

1. **更新 `package.xml`**：加入依賴。
   ```xml
   <exec_depend>rclpy</exec_depend>
   <exec_depend>std_msgs</exec_depend>
   ```

2. **更新 `setup.py`**：在 `console_scripts` 陣列中加入：
   ```python
   entry_points={
       'console_scripts': [
           'sensor = py_battery_monitor.sensor:main',
           'dashboard = py_battery_monitor.dashboard:main',
       ],
   },
   ```

---

### ⚙️ 4.2 C++ 實作流程：電池監控系統

#### Step 1: 建立 C++ 套件
開啟終端機執行以下指令：
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake --license Apache-2.0 cpp_battery_monitor
```

#### Step 2: 撰寫發布者 (電池感測器節點)
在 `~/ros2_ws/src/cpp_battery_monitor/src/` 下建立 `sensor.cpp`：

```cpp
#include <chrono>       // 處理時間單位 (如 1000ms)
#include <functional>   // 提供 std::bind
#include <memory>       // 提供智慧指標
#include <string>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

class BatterySensor : public rclcpp::Node
{
  public:
    BatterySensor() : Node("battery_sensor"), battery_level_(100)
    {
      // 1. 建立發布者
      publisher_ = this->create_publisher<std_msgs::msg::String>("battery_status", 10);
      // 2. 建立定時器 (每秒執行一次 timer_callback)
      timer_ = this->create_wall_timer(1000ms, std::bind(&BatterySensor::timer_callback, this));
    }

  private:
    void timer_callback()
    {
      auto message = std_msgs::msg::String();
      message.data = "目前電量: " + std::to_string(battery_level_) + "%";
      
      RCLCPP_INFO(this->get_logger(), "🔋 發布: '%s'", message.data.c_str());
      publisher_->publish(message);
      
      if (battery_level_ > 0) battery_level_--;
    }

    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    int battery_level_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<BatterySensor>());
  rclcpp::shutdown();
  return 0;
}
```

#### ✍️ Step 3: 隨堂練習 - 撰寫訂閱者 (儀表板節點)
請在同目錄下建立 `dashboard.cpp`，並嘗試實作出 C++ 版本的訂閱者！

```cpp
#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using std::placeholders::_1;

class BatteryDashboard : public rclcpp::Node
{
  public:
    BatteryDashboard() : Node("battery_dashboard")
    {
      // 1. 建立訂閱者：綁定 'battery_status' 主題與 topic_callback
    }

  private:
    // 2. 實作 topic_callback (參數為 const std_msgs::msg::String & msg)
    // 3. 在函式內印出收到的數據

    // 4. 宣告訂閱者的智慧指標變數
};

int main(int argc, char * argv[])
{
  // 5. 初始化、啟動 spin、關閉 rclcpp
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

class BatteryDashboard : public rclcpp::Node
{
  public:
    BatteryDashboard() : Node("battery_dashboard")
    {
      // 解答 1
      subscription_ = this->create_subscription<std_msgs::msg::String>(
        "battery_status", 10, std::bind(&BatteryDashboard::topic_callback, this, _1));
    }

  private:
    // 解答 2 & 3
    void topic_callback(const std_msgs::msg::String & msg) const
    {
      RCLCPP_INFO(this->get_logger(), "🖥️ 儀表板接收到: '%s'", msg.data.c_str());
    }
    
    // 解答 4
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  // 解答 5
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<BatteryDashboard>());
  rclcpp::shutdown();
  return 0;
}
```
</details>

#### Step 4: 更新設定檔 (`package.xml` & `CMakeLists.txt`)
打開 `cpp_battery_monitor` 目錄下的設定檔：

1. **更新 `package.xml`**：
   ```xml
   <depend>rclcpp</depend>
   <depend>std_msgs</depend>
   ```

2. **更新 `CMakeLists.txt`**：加入編譯與安裝規則。
   ```cmake
   find_package(rclcpp REQUIRED)
   find_package(std_msgs REQUIRED)

   # 編譯 sensor
   add_executable(sensor src/sensor.cpp)
   ament_target_dependencies(sensor rclcpp std_msgs)

   # 編譯 dashboard
   add_executable(dashboard src/dashboard.cpp)
   ament_target_dependencies(dashboard rclcpp std_msgs)

   # 安裝執行檔
   install(TARGETS sensor dashboard DESTINATION lib/${PROJECT_NAME})
   ```

---

### 🔨 4.3 編譯與執行測試 (Build & Run)

在完成程式碼撰寫與設定檔修改後，請回到工作空間根目錄進行編譯。建議使用 `--packages-select` 來指定只編譯我們剛剛建好的套件：

```bash
cd ~/ros2_ws
colcon build --packages-select py_battery_monitor cpp_battery_monitor
```

編譯完成後，我們需要 **兩個終端機** 來測試。請確保每次開啟新終端機時，都已經執行了 `source install/setup.bash` 來載入環境。

**測試 Python 版本：**
* **終端機 1 (Talker)**: `ros2 run py_battery_monitor sensor`
* **終端機 2 (Listener)**: `ros2 run py_battery_monitor dashboard`

**測試 C++ 版本：**
* **終端機 1 (Talker)**: `ros2 run cpp_battery_monitor sensor`
* **終端機 2 (Listener)**: `ros2 run cpp_battery_monitor dashboard`

執行後，你將會看到終端機 1 的電池感測器每秒扣 1% 並發布訊息，而終端機 2 的儀表板會立刻接收到並印出最新的電量狀態！
---

## 5. 撰寫服務與客戶端 (Service & Client)

**情境引入 (Why)：**
在送餐機器人的餐廳裡，有些動作是「連續不斷」的（例如發布攝影機畫面），這適合用上一章的 Topic。但有些動作是「單次觸發、一問一答」的。
例如：**服務生 (Client)** 向 **廚房 (Server)** 送出點餐單：「我要 2 份漢堡和 3 份薯條」。廚房收到後，會回傳一個確認結果：「收到！總共 5 份餐點準備中」。

這時候，我們就會使用 **Service (服務)**。它採用「請求 (Request) / 回應 (Response)」的雙向同步機制。在這個實作中，我們將借用 ROS 2 內建的 `AddTwoInts` (兩個整數相加) 格式，來模擬這個「點餐與計算總餐點數」的過程。

---

### 🐍 5.1 Python 實作流程：點餐系統

#### Step 1: 建立 Python 套件
開啟終端機，進入你的工作空間並建立名為 `py_order_system` 的套件：
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python --license Apache-2.0 py_order_system
```

#### Step 2: 撰寫服務端 (廚房節點)
在 `~/ros2_ws/src/py_order_system/py_order_system/` 目錄下，建立 `kitchen_server.py`：

```python
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
```

#### ✍️ Step 3: 隨堂練習 - 撰寫客戶端 (服務生節點)
換你試試看！在同一個目錄下建立 `waiter_client.py`。請根據註解提示，建立一個會主動向廚房發送點餐請求的 Client 節點。

```python
import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class WaiterClientAsync(Node):
    def __init__(self):
        super().__init__('waiter_node')
        # 1. 使用 create_client 建立客戶端 (服務型態 AddTwoInts, 服務名稱 'place_order')
        
        # 2. 寫一個 while 迴圈，等待廚房上線 (wait_for_service)，若沒上線則持續印出「呼叫廚房中...」
        
        # 3. 實例化 Request 物件 (AddTwoInts.Request())
        pass

    def send_order(self, burgers, fries):
        # 4. 將參數 burgers, fries 填入 request 的 a 與 b
        # 5. 使用 call_async 發送請求，並將結果存入 self.future
        # 6. 使用 rclpy.spin_until_future_complete 等待廚房回應
        # 7. 回傳 self.future.result()
        pass

def main(args=None):
    # 8. 初始化 rclpy、建立 WaiterClientAsync 節點
    # 9. 呼叫 send_order 送出 (2份漢堡, 3份薯條) 的請求
    # 10. 印出結果 (response.sum)，然後銷毀節點與關閉系統
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

class WaiterClientAsync(Node):
    def __init__(self):
        super().__init__('waiter_node')
        # 解答 1
        self.cli = self.create_client(AddTwoInts, 'place_order')
        
        # 解答 2
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('☎️ 呼叫廚房中，請稍後...')
            
        # 解答 3
        self.req = AddTwoInts.Request()

    def send_order(self, burgers, fries):
        # 解答 4
        self.req.a = burgers
        self.req.b = fries
        # 解答 5
        self.future = self.cli.call_async(self.req)
        # 解答 6
        rclpy.spin_until_future_complete(self, self.future)
        # 解答 7
        return self.future.result()

def main(args=None):
    # 解答 8
    rclpy.init(args=args)
    waiter_client = WaiterClientAsync()
    
    # 解答 9
    burgers_qty = 2
    fries_qty = 3
    waiter_client.get_logger().info(f'💁‍♂️ 服務生送出訂單：{burgers_qty} 漢堡, {fries_qty} 薯條...')
    response = waiter_client.send_order(burgers_qty, fries_qty)
    
    # 解答 10
    waiter_client.get_logger().info(f'✅ 廚房回報：總共 {response.sum} 份餐點準備中！')
    waiter_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```
</details>

#### Step 4: 更新設定檔
為了讓系統認識你的新程式，請修改 `py_order_system` 資料夾下的設定檔：
1. **`package.xml`**: 加入介面依賴。
   ```xml
   <exec_depend>example_interfaces</exec_depend>
   ```
2. **`setup.py`**: 在 `console_scripts` 陣列加入執行檔對應。
   ```python
   entry_points={
       'console_scripts': [
           'kitchen = py_order_system.kitchen_server:main',
           'waiter = py_order_system.waiter_client:main',
       ],
   },
   ```

---

### ⚙️ 5.2 C++ 實作流程：點餐系統

#### Step 1: 建立 C++ 套件
開啟終端機執行以下指令建立套件：
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake --license Apache-2.0 cpp_order_system
```

#### Step 2: 撰寫客戶端 (服務生節點)
在 `~/ros2_ws/src/cpp_order_system/src/` 目錄下建立 `waiter_client.cpp`：
```cpp
#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

using namespace std::chrono_literals;

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("waiter_node");
  
  // 建立客戶端，指定與 Server 相同的服務型態與名稱 ('place_order')
  auto client = node->create_client<example_interfaces::srv::AddTwoInts>("place_order");

  // 準備請求資料 (2份漢堡，3份薯條)
  auto request = std::make_shared<example_interfaces::srv::AddTwoInts::Request>();
  request->a = 2;
  request->b = 3;

  // 使用 while 迴圈等待廚房上線，每秒檢查一次
  while (!client->wait_for_service(1s)) {
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "☎️ 呼叫廚房中，請稍後...");
  }

  RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "💁‍♂️ 服務生送出訂單：2 漢堡, 3 薯條...");
  
  // 非同步發送請求 (async_send_request 不會卡死主程式)
  auto result = client->async_send_request(request);
  
  // 等待 Server 回傳結果，若成功則印出
  if (rclcpp::spin_until_future_complete(node, result) == rclcpp::FutureReturnCode::SUCCESS) {
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "✅ 廚房回報：總共 %ld 份餐點準備中！", result.get()->sum);
  } else {
    RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "❌ 點餐失敗，廚房無回應");
  }

  rclcpp::shutdown();
  return 0;
}
```

#### ✍️ Step 3: 隨堂練習 - 撰寫服務端 (廚房節點)
Client 送出訂單了，廚房不能沒有人接單！在同目錄下建立 `kitchen_server.cpp`，請根據註解實作出 C++ 的 Service Server。

```cpp
#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"
#include <memory>

// 1. 實作 take_order 回呼函式，參數為 Request 與 Response 的 shared_ptr
void take_order(const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request,
          std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response)
{
    // 2. 計算 request 內的 a(漢堡) + b(薯條) 並填入 response->sum
    // 3. 印出收到的訂單內容 (RCLCPP_INFO)
}

int main(int argc, char **argv)
{
  // 4. 初始化 rclcpp
  // 5. 建立節點 "kitchen_node"
  // 6. 建立服務端 (create_service)，名稱取為 "place_order"，並綁定上述的 take_order 函式
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
void take_order(const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request,
          std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response)
{
  // 解答 2
  response->sum = request->a + request->b;
  // 解答 3
  RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "🔔 收到新訂單: 漢堡 %ld 份, 薯條 %ld 份", request->a, request->b);
}

int main(int argc, char **argv)
{
  // 解答 4
  rclcpp::init(argc, argv);
  // 解答 5
  auto node = rclcpp::Node::make_shared("kitchen_node");
  
  // 解答 6
  auto service = node->create_service<example_interfaces::srv::AddTwoInts>("place_order", &take_order);
  
  RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "👨‍🍳 廚房已開工，等待點餐...");
  
  // 解答 7
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```
</details>

#### Step 4: 更新設定檔
打開 `cpp_order_system` 下的 `CMakeLists.txt` 與 `package.xml`：
1. **`package.xml`**: 加入依賴。
   ```xml
   <depend>example_interfaces</depend>
   ```
2. **`CMakeLists.txt`**: 宣告執行檔並連結依賴。
   ```cmake
   find_package(rclcpp REQUIRED)
   find_package(example_interfaces REQUIRED)

   # 增加 server(廚房) 端執行檔
   add_executable(kitchen src/kitchen_server.cpp)
   ament_target_dependencies(kitchen rclcpp example_interfaces)

   # 增加 client(服務生) 端執行檔
   add_executable(waiter src/waiter_client.cpp)
   ament_target_dependencies(waiter rclcpp example_interfaces)

   install(TARGETS kitchen waiter DESTINATION lib/${PROJECT_NAME})
   ```

---

### 🔨 5.3 編譯與實戰驗證 (Build & Test)

回到工作空間根目錄進行編譯：
```bash
cd ~/ros2_ws
colcon build --packages-select py_order_system cpp_order_system
```

編譯完成後，我們需要 **兩個終端機** 來測試這個點餐系統。請確保每次開啟新終端機時，都已經執行了 `source install/setup.bash` 來載入環境。

**測試 Python 版本：**
* **終端機 1 (廚房 Server)**: `ros2 run py_order_system kitchen`
* **終端機 2 (服務生 Client)**: `ros2 run py_order_system waiter`

**測試 C++ 版本：**
* **終端機 1 (廚房 Server)**: `ros2 run cpp_order_system kitchen`
* **終端機 2 (服務生 Client)**: `ros2 run cpp_order_system waiter`

執行後，你將會看到這段精彩的跨節點對話：
* **終端機 2 (Waiter)** 印出：「💁‍♂️ 服務生送出訂單：2 漢堡, 3 薯條...」
* **終端機 1 (Kitchen)** 瞬間印出：「🔔 收到新訂單: 漢堡 2 份, 薯條 3 份」
* **終端機 2 (Waiter)** 收到回傳：「✅ 廚房回報：總共 5 份餐點準備中！」並且自動結束程式。

#### 💡 進階技巧：手動呼叫服務 (CLI 工具)
當廚房 (Server) 還在運行時，你不一定要寫一隻 Client 程式才能點餐。你可以直接透過終端機指令（CLI）當作客人手動送出請求：

在全新的終端機輸入：
```bash
ros2 service call /place_order example_interfaces/srv/AddTwoInts "{a: 10, b: 5}"
```
你會看到終端機 1 的廚房馬上接單，並在你當前的終端機回傳計算結果 `sum: 15`！這在開發除錯時非常實用。

---

## 6. 自訂資料格式 (Custom msg and srv files)

**情境引入 (Why)：**
在前面的單元中，我們使用了系統內建的資料格式（例如用 `String` 傳字串，用 `Int32` 傳數字）。
但在真實的機器人專案中，這遠遠不夠。想像一下，送餐機器人需要回報它的當前狀態，如果只傳一個字串太難解析了。我們希望能**把多個數據包裝成一個專屬的資料包**，例如同時傳送：`訂單編號 (整數)`、`配送狀態 (字串)` 以及 `當前座標 (X,Y,Z 位置)`。

在 ROS 2 中，我們透過建立 `.msg` (主題格式) 與 `.srv` (服務格式) 檔案來定義這些自訂結構。
> ⚠️ **核心守則**：官方強烈建議，將所有自訂格式**獨立放在一個專屬的 C++ (`ament_cmake`) 套件中**。即使你未來只打算用 Python 寫程式，這個「定義格式的套件」也必須是 CMake 類型，因為底層需要透過 CMake 來將純文字轉換為各種語言的原始碼。

---

### 📦 6.1 實作流程：建立專屬介面套件

#### Step 1: 建立介面套件與資料夾
開啟終端機，我們來建立一個專門存放格式的套件，命名為 `robot_interfaces`。

* **所在位置**：必須在 `~/ros2_ws/src` 下
```bash
cd ~/ros2_ws/src

# 建立一個 CMake 類型的介面套件
ros2 pkg create --build-type ament_cmake --license Apache-2.0 robot_interfaces

# 進入套件並建立 msg 與 srv 專屬資料夾
cd robot_interfaces
mkdir msg srv
```

#### Step 2: 建立自訂 Message (`.msg` 主題格式)
我們要建立一個名為 `DeliveryStatus.msg` 的檔案。

* **所在位置**：編輯器打開 `~/ros2_ws/src/robot_interfaces/msg/DeliveryStatus.msg`
* **內容撰寫**：
```text
# 這是送餐機器人的狀態回報格式
int32 order_id
string delivery_status

# 我們也可以直接引用 ROS 2 內建的其他複雜格式 (例如 geometry_msgs 裡的 Point 座標)
geometry_msgs/Point current_location
```

#### Step 3: 建立自訂 Service (`.srv` 服務格式)
我們要建立一個名為 `AssignTask.srv` 的檔案。這是一個用來「指派送餐任務」的服務，使用 `---` 來分隔 Client 的請求 (Request) 與 Server 的回應 (Response)。

* **所在位置**：編輯器打開 `~/ros2_ws/src/robot_interfaces/srv/AssignTask.srv`
* **內容撰寫**：
```text
# Request (經理送出的任務請求)
int32 table_number
string food_name
---
# Response (機器人回傳的接單結果)
bool success
string estimated_time
```

---

### ⚙️ 6.2 更新設定檔以生成程式碼

寫完這兩個純文字檔後，我們必須修改設定檔，讓 ROS 2 的底層編譯器 (`rosidl`) 知道要把它們翻譯成 C++ 與 Python 程式碼。

#### Step 4: 修改 CMakeLists.txt
* **所在位置**：打開 `~/ros2_ws/src/robot_interfaces/CMakeLists.txt`
請找到 `find_package(ament_cmake REQUIRED)`，並在它**下方**加入以下這段程式碼：

```cmake
# 1. 尋找我們在 msg 裡用到的外部依賴 (geometry_msgs)
find_package(geometry_msgs REQUIRED)

# 2. 尋找 ROS 2 的介面程式碼產生器
find_package(rosidl_default_generators REQUIRED)

# 3. 告訴產生器，我們寫了哪些 .msg 和 .srv 檔案
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/DeliveryStatus.msg"
  "srv/AssignTask.srv"
  DEPENDENCIES geometry_msgs # 宣告我們的格式依賴了這個外部套件
)
```

#### Step 5: 修改 package.xml
* **所在位置**：打開 `~/ros2_ws/src/robot_interfaces/package.xml`
請在 `<buildtool_depend>ament_cmake</buildtool_depend>` 的**下方**，加入以下四行標籤：

```xml
  <depend>geometry_msgs</depend>
  
  <buildtool_depend>rosidl_default_generators</buildtool_depend>
  <exec_depend>rosidl_default_runtime</exec_depend>
  
  <member_of_group>rosidl_interface_packages</member_of_group>
```

---

### 🔨 6.3 編譯與實戰驗證 (Build & Verify)

現在我們回到工作空間根目錄進行編譯。這個步驟會把純文字檔轉化為系統底層的 `.hpp` 和 `.py` 檔案。

**編譯指令：**
```bash
cd ~/ros2_ws

# 為了節省時間，我們指定只編譯這個介面套件
colcon build --packages-select robot_interfaces

# 載入最新環境，讓系統認得剛編譯好的新格式
source install/setup.bash
```

**驗證指令：**
編譯完成後，我們不需要寫任何 Node，可以直接使用 ROS 2 的 CLI 工具來檢查系統是否成功註冊了我們的專屬格式。

在終端機輸入：
```bash
# 檢查我們自訂的 Message 格式
ros2 interface show robot_interfaces/msg/DeliveryStatus
```
*終端機應成功印出：*
```text
int32 order_id
string delivery_status
geometry_msgs/Point current_location
        float64 x
        float64 y
        float64 z
```
*(你會發現，系統非常聰明地把 `geometry_msgs/Point` 裡面的 `x, y, z` 結構也一起展開給你看！)*

接著檢查 Service 格式：
```bash
ros2 interface show robot_interfaces/srv/AssignTask
```
*終端機應成功印出：*
```text
int32 table_number
string food_name
---
bool success
string estimated_time
```

現在你已經擁有了送餐機器人專屬的通訊格式。未來在撰寫 Python 或 C++ 節點時，你只需要像之前一樣，加入 `from robot_interfaces.msg import DeliveryStatus` 就能直接在程式中使用這個超級資料包了！

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

**情境引入 (Why)：**
想像你正在開發一台送餐機器人。在空曠的走廊，最高時速可以跑 `1.0 m/s`；但如果進入人多的用餐區，經理希望能在**不修改程式碼、不重新啟動機器人**的情況下，直接把最高速限降到 `0.5 m/s`。
這時候，我們就會把「最高速限 (`max_speed`)」設計成一個 **參數 (Parameter)**。

這個單元將帶你從零建立套件，在程式中宣告參數，並透過指令或 Launch 檔動態「覆寫」它。

---

### 🐍 8.1 Python 實作流程：限速器節點

#### Step 1: 建立 Python 套件與預設節點
開啟終端機，進入你的工作空間並建立名為 `python_parameters` 的套件：
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python --license Apache-2.0 --node-name speed_limiter python_parameters
```

#### Step 2: 撰寫程式碼
打開 `~/ros2_ws/src/python_parameters/python_parameters/speed_limiter.py`，將內容替換為以下程式碼：
```python
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
```

#### Step 3: 更新設定檔 (`package.xml` & `setup.py`)
為了讓系統能順利編譯與執行，請確認設定檔：
1. **`package.xml`**：確保有 `<exec_depend>rclpy</exec_depend>`。
2. **`setup.py`**：因為我們剛才使用 `--node-name` 指令，系統應該已經幫你在 `entry_points` 裡寫好 `'speed_limiter = python_parameters.speed_limiter:main'` 了，確認有這行即可。

---

### ⚙️ 8.2 C++ 實作流程：限速器節點

#### Step 1: 建立 C++ 套件與預設節點
如果你想練習 C++，請開終端機執行：
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake --license Apache-2.0 --node-name speed_limiter cpp_parameters
```

#### Step 2: 撰寫程式碼
打開 `~/ros2_ws/src/cpp_parameters/src/speed_limiter.cpp`，替換為以下程式碼：
```cpp
#include <chrono>
#include <string>
#include <rclcpp/rclcpp.hpp>

using namespace std::chrono_literals;

class SpeedLimiterNode : public rclcpp::Node
{
public:
  SpeedLimiterNode() : Node("speed_limiter")
  {
    // 1. 建立參數描述
    auto param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    param_desc.description = "機器人的最高移動速限 (m/s)";

    // 2. 宣告參數，名稱為 "max_speed"，預設值為 1.0
    this->declare_parameter("max_speed", 1.0, param_desc);

    // 3. 建立計時器
    timer_ = this->create_wall_timer(
      1000ms, std::bind(&SpeedLimiterNode::timer_callback, this));
  }

private:
  void timer_callback()
  {
    // 4. 取得參數值，並轉型為 double (浮點數)
    double current_speed_limit = this->get_parameter("max_speed").as_double();

    // 印出狀態
    RCLCPP_INFO(this->get_logger(), "目前最高限速設定為: %.2f m/s", current_speed_limit);
  }
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SpeedLimiterNode>());
  rclcpp::shutdown();
  return 0;
}
```

#### Step 3: 更新設定檔 (`package.xml` & `CMakeLists.txt`)
1. **更新 `package.xml`**：加入依賴。
   ```xml
   <depend>rclcpp</depend>
   ```

2. **更新 `CMakeLists.txt`**：因為 C++ 需要編譯，打開 `CMakeLists.txt`，確保有宣告依賴並連結：
   ```cmake
   find_package(rclcpp REQUIRED)

   # 增加執行檔並連結
   add_executable(speed_limiter src/speed_limiter.cpp)
   ament_target_dependencies(speed_limiter rclcpp)

   install(TARGETS speed_limiter DESTINATION lib/${PROJECT_NAME})
   ```


---

### 🔨 8.3 編譯與載入環境 (Build & Source)

無論你寫了 Python 還是 C++（或兩者都寫了），現在我們回到工作空間根目錄進行編譯：

```bash
cd ~/ros2_ws

# 指定只編譯我們剛剛建好的套件 (節省時間)
colcon build --packages-select python_parameters cpp_parameters

# 載入最新的環境設定 (極度重要！每次編譯完都要執行)
source install/setup.bash
```

---

### 🎮 8.4 終端機實戰驗證 (動態修改參數)

編譯完成後，我們可以來測試參數的威力了！

1. **開啟節點**：
   ```bash
   # 若執行 Python 版：
   ros2 run python_parameters speed_limiter
   ```
   *你會看到終端機不斷印出：「目前最高限速設定為: 1.00 m/s」。*

2. **動態修改參數 (重點！)**：
   **不要關閉**原本的終端機，開啟「第二個終端機」，模擬餐廳經理下達減速指令：
   ```bash
   ros2 param set /speed_limiter max_speed 0.5
   ```
   *這時你切回第一個終端機，會發現它在沒有重新啟動的情況下，印出的訊息直接變成：「目前最高限速設定為: 0.50 m/s」！這就是 Parameter 的強大之處。*

---

### 🚀 8.5 透過 Launch 檔啟動並注入參數 (進階必學)

實務上，我們不可能每次開機都手動去打 `ros2 param set`。我們會撰寫一個 Python 的 `Launch` 檔，在啟動節點的瞬間就把參數「塞」進去。

1. 在你的套件目錄下建立一個 `launch` 資料夾，並在裡面建立 `robot_bringup_launch.py`：

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='python_parameters',  # 替換成你的套件名稱 (C++ 則是 cpp_parameters)
            executable='speed_limiter',   # 你的執行檔名稱
            name='custom_speed_limiter',
            output='screen',
            emulate_tty=True,
            
            # 👇 在這裡注入參數值！(例如將預設的 1.0 改為 0.3)
            parameters=[
                {'max_speed': 0.3}
            ]
        )
    ])
```

2. **(極度重要) 設定檔更新：讓系統安裝 Launch 檔**
如果你沒有做這一步，執行 `colcon build` 後系統會找不到你的 Launch 檔！

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

3. **重新編譯並啟動**：
請再次執行 `colcon build` 與 `source install/setup.bash`。接著使用 Launch 檔啟動：
```bash
ros2 launch python_parameters robot_bringup_launch.py
```
你會發現終端機一啟動，印出來的速度直接就是 `0.30 m/s` 了！未來在控制 TurtleBot3 的 SLAM 演算法時，我們就會大量使用 Launch 檔來載入各種雷達與地圖的參數設定。

---

## 9. 系統診斷與進階工具

* **`ros2doctor`**：當你的 ROS 2 環境出現詭異的問題時（例如節點無法通訊），可以在終端機輸入 `ros2 doctor`。它會幫你檢查網路設定、版本相容性以及環境變數是否設定正確。加入 `--report` 參數可以看更詳細的系統報告。
* **Plugins (C++)**：在 C++ 中，你可以使用 `pluginlib` 來建立外掛程式。這允許節點在執行期間動態載入函式庫，而不需要將所有程式碼靜態連結在一起，這對於大型機器人專案的架構設計非常有用。
