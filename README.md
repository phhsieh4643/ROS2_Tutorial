# 🤖 ROS 2 Humble 機器人開發完整教學指南

這個項目是一套針對 **ROS 2 Humble** 初學者的完整學習資源。內容涵蓋了從 Windows WSL 環境配置、核心命令列工具 (CLI) 的使用，到使用 C++ 與 Python 進行客戶端函式庫 (Client Libraries) 程式設計的實戰演練。

---

## 📁 核心講義說明

| 講義檔案 | 核心學習目標 | 適合階段 |
| :--- | :--- | :--- |
| 🛠️ [**ROS2_Install.md**](ROS2_Install.md) | WSL 系統配置與 ROS 2 Humble 環境安裝 | 環境整備期 |
| 🔍 [**ROS2_CLI_Tools.md**](ROS2_Humble_Beginner_CLI_Tools.md) | 掌握 Node, Topic, Service, Action 等命令列操作 | 觀念建立期 |
| 💻 [**ROS2_Client_Libs.md**](ROS2_Humble_Beginner_Client_Libraries.md) | 實戰 C++/Python 節點、自訂介面與參數管理 | 應用開發期 |

---

## 📂 專案目錄結構 (Repository Structure)

為了方便學習與管理，本專案將不同的功能模組拆分為獨立的工作空間 (Workspace)：

```text
ROS2_Tutorial/
├── 📄 README.md             <-- 你現在的位置
├── 📄 .gitignore            <-- (建議加入) 排除編譯產生的巨量檔案
├── 📄 ROS2_*.md             <-- 核心教學講義檔案
│
└── 📁 ros2_ws/              <-- 實作原始碼目錄
    ├── 📁 pub_sub/          <-- 1. 主題發布與訂閱實作區
    ├── 📁 ser_cli/          <-- 2. 服務與客戶端實作區
    ├── 📁 cus_msg_srv/      <-- 3. 自訂通訊格式 (msg/srv) 實作區
    └── 📁 parms/            <-- 4. 參數管理 (Parameters) 實作區
```
> ⚠️ **注意**：每個子資料夾（如 `pub_sub/`）內皆包含獨立的 `src/`，請進入各別資料夾後再執行編譯。

---

## 🚀 快速開始 (Quick Start)

### 1. 必備環境
* **作業系統**：Windows 11 (WSL 2) 或 Ubuntu 22.04 LTS
* **ROS 版本**：ROS 2 Humble Desktop

### 2. 下載專案
```bash
git clone https://github.com/YourUsername/ROS2_Tutorial.git
cd ROS2_Tutorial
```

### 3. 編譯工作空間 (推薦指令)
進入特定功能目錄進行編譯（以 `pub_sub` 為例）：
```bash
cd ros2_ws/pub_sub
colcon build --symlink-install --merge-install
source install/setup.bash
```
> 💡 **為什麼使用 `--symlink-install`？**
> 這樣修改 Python 原始碼或 Launch 檔後，「不需重新編譯」即可立刻看到修改效果！

---

## 🛠️ Git 專案管理建議

如果你計畫將本專案上傳至 GitHub，請務必建立 `.gitignore` 檔案以節省空間並避免版本衝突。

**應排除的資料夾：**
* `build/` (暫存檔)
* `install/` (安裝檔)
* `log/` (日誌檔)
* `**/__pycache__/` (Python 快取)

---

## 📚 學習路徑建議

1.  **環境安裝**：跟隨 `ROS2_Install.md` 完成 WSL 與 ROS 2 的安裝。
2.  **互動演練**：打開 `ROS2_CLI_Tools.md`，使用 `turtlesim` 熟悉節點與主題的概念。
3.  **核心開發**：按照 `ROS2_Client_Libs.md` 的節點順序，手動在 `ros2_ws/` 下建立並編寫程式碼。
4.  **自主除錯**：學會使用 `ros2 node info` 與 `ros2 topic echo` 來排除通訊問題。

---

## 💡 常用命令速查

| 功能 | 指令 | 範例 (結合本專案) |
| :--- | :--- | :--- |
| **載入環境** | `source /opt/ros/humble/setup.bash` | (每次開啟新視窗皆必須執行) |
| **啟動節點** | `ros2 run <pkg> <node>` | `ros2 run py_battery_monitor sensor` |
| **列出節點** | `ros2 node list` | (查看目前活躍的節點名稱) |
| **查看主題資料** | `ros2 topic echo /topic` | `ros2 topic echo /battery_status` |
| **查看介面定義** | `ros2 interface show <type>`| `ros2 interface show robot_interfaces/msg/DeliveryStatus` |
| **呼叫服務** | `ros2 service call /name <type> <args>` | `ros2 service call /place_order example_interfaces/srv/AddTwoInts "{a: 10, b: 5}"` |
| **動態修改參數** | `ros2 param set <node> <key> <val>` | `ros2 param set /speed_limiter max_speed 0.5` |


---

## 🎓 自學資源與參考
* [ROS 2 Humble 官方文件](https://docs.ros.org/en/humble/index.html)
* [TurtleBot3(ROS2)-Humble 線上手冊](https://idminer.com.tw/docs-category/emanual-tb3-humble/)
* [ROS 2 Humble 影片教學清單](https://www.youtube.com/playlist?list=PLLSegLrePWgJudpPUof4-nVFHGkB62Izy)

---

祝你在 ROS 2 的世界中探索愉快！ 🤖🚀
