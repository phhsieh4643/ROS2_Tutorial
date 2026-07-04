# ROS 2 Humble 教學指南

本儲存庫包含一套完整的 ROS 2 Humble 學習與開發教學文件。請依照學習階段與需求，參考以下對應的文件。

## 文件索引

### 1. 環境建置與安裝

*   **[ROS2_Install.md](ROS2_Install.md)**
    在 Windows Subsystem for Linux (WSL) 上配置與安裝 ROS 2 Humble 環境的詳細步驟指南。
*   **[ROS2 安裝.pptx](ROS2%20%E5%AE%89%E8%A3%9D.pptx)**
    提供 ROS 2 安裝流程總覽與詳細步驟的簡報檔。
*   **[樹莓派連線注意事項.md](樹莓派連線注意事項.md)**
    說明如何在 ROS 2 網路環境下連線與設定 Raspberry Pi 的重要注意事項。
*   **[WSL_Turtlebot_通訊問題解決.md](WSL_Turtlebot_通訊問題解決.md)**
    提供 WSL 與 TurtleBot 之間 ROS 2 訊息傳輸與網路通訊問題（如防火牆或網段設定）的標準排解流程。

### 2. 初階教學

*   **[ROS2_Humble_Beginner_CLI_Tools.md](ROS2_Humble_Beginner_CLI_Tools.md)**
    核心命令列介面 (CLI) 工具介紹。涵蓋系統基本操作與概念，包含節點 (Nodes)、主題 (Topics)、服務 (Services) 與動作 (Actions)。
*   **[ROS2_Humble_Beginner_Client_Libraries.md](ROS2_Humble_Beginner_Client_Libraries.md)**
    ROS 2 應用程式開發實作指南。著重於使用 C++ 與 Python 客戶端函式庫 (Client Libraries) 撰寫節點、管理參數以及定義自訂介面。

### 3. 中高階主題

*   **[ROS2_Intermediate.md](ROS2_Intermediate.md)**
    深入探討 ROS 2 應用程式開發的中階概念與進階技術。
*   **[ROS2_SLAM_and_Nav.md](ROS2_SLAM_and_Nav.md)**
    使用 ROS 2 實作同步定位與建圖 (SLAM) 及自主系統導航的完整指南。

---

## 工作空間結構

`ros2_ws/` 目錄包含與教學文件相輔相成的程式碼實作範例，依據功能性分類如下：

*   **pub_sub/**: 發布者 (Publisher) 與訂閱者 (Subscriber) 通訊範例。
*   **ser_cli/**: 服務 (Service) 與客戶端 (Client) 通訊範例。
*   **cus_msg_srv/**: 自訂訊息 (Message) 與服務 (Service) 介面定義範例。
*   **parms/**: 參數 (Parameters) 管理實作範例。

### 編譯指示

編譯工作空間時，建議進入特定功能的子目錄，並使用以下指令進行編譯，以利開發順利進行：

```bash
cd ros2_ws/<目標目錄>
colcon build --symlink-install --merge-install
source install/setup.bash
```

**備註：** 使用 `--symlink-install` 參數，即可在修改 Python 程式碼或 Launch 檔案後直接套用變更，無需重新編譯。

---

## 參考資料

*   [TurtleBot3 Overview - ROBOTIS e-Manual](https://docs.robotis.com/docs/systems/turtlebot3/overview/)
