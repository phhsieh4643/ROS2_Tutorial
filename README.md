# ROS 2 Humble 完整教學指南

這個項目包含 ROS 2 Humble 初學者系列教學的完整講義與實踐指南，涵蓋從環境安裝、命令列工具使用，到客戶端函式庫程式設計的全面內容。

## 📁 檔案說明

### 1. [ROS2_Install.md](ROS2_Install.md)
**ROS 2 Humble 安裝與 WSL 基礎操作講義**

涵蓋內容：
- **Windows 環境準備 (WSL 系統)**
  - WSL 工具介紹與常用指令
  - WSL 系統管理、備份與匯入
  - 實用技巧與疑難排解
  
- **ROS 2 Humble 安裝步驟 (Ubuntu 22.04)**
  - 語系設定 (Set Locale)
  - 軟體源配置 (Setup Sources)
  - ROS 2 套件安裝 (Desktop Install)

**適合對象**：初次在 Windows 上安裝 ROS 2 的使用者

---

### 2. [ROS2_Humble_Beginner_CLI_Tools.md](ROS2_Humble_Beginner_CLI_Tools.md)
**ROS 2 Humble 基礎觀念與命令列工具總整理**

涵蓋內容：
- **環境設定** (Configuring Environment)
  - ROS 2 環境變數載入
  - Domain ID 隔離設定
  
- **基礎模擬工具**
  - turtlesim 海龜模擬器
  - rqt 圖形化介面工具
  
- **核心概念**
  - 節點 (Nodes)：系統工作單元
  - 主題 (Topics)：連續性資料傳遞機制
  
- **實用命令列工具**
  - 節點、主題、服務、參數查詢指令
  - 即時資料監測與手動發布工具

**適合對象**：想理解 ROS 2 基本架構的初學者

---

### 3. [ROS2_Humble_Beginner_Client_Libraries.md](ROS2_Humble_Beginner_Client_Libraries.md)
**ROS 2 Humble 初階程式設計 (Client Libraries) 完整講義**

涵蓋內容：
- **工作空間架構**
  - Workspace 檔案結構深度解析
  - 不同套件類型 (C++、Python、自訂通訊格式)
  
- **編譯與建置**
  - 使用 colcon 進行專案編譯
  - 套件建立與配置
  
- **ROS 2 程式設計**
  - 發布/訂閱機制實作
  - 服務/客戶端模式
  - 參數設定與管理
  - Launch 啟動腳本編寫

**適合對象**：想開發 ROS 2 應用程式的開發者

---

## 🚀 快速開始

### 必備環境
- Windows 11 (建議)
- WSL 2 已啟用
- Ubuntu 22.04 LTS

### 安裝步驟
1. 參照 **ROS2_Install.md** 設定 WSL 與安裝 ROS 2
2. 依照 **ROS2_Humble_Beginner_CLI_Tools.md** 學習基本概念
3. 閱讀 **ROS2_Humble_Beginner_Client_Libraries.md** 進行實際開發

### 常用命令參考
```bash
# 載入 ROS 2 環境
source /opt/ros/humble/setup.bash

# 啟動海龜模擬器進行基礎練習
ros2 run turtlesim turtlesim_node

# 查看系統中的節點
ros2 node list

# 查看活躍的主題
ros2 topic list -t

# 編譯工作空間
colcon build
```

---

## 📚 學習路徑建議

1. **第一階段 - 環境準備** (2-3 小時)
   - 閱讀 ROS2_Install.md 的 Part 1 與 Part 2
   - 完成 ROS 2 Humble 安裝

2. **第二階段 - 基礎觀念** (3-4 小時)
   - 讀完 ROS2_Humble_Beginner_CLI_Tools.md
   - 使用 turtlesim 進行互動式學習
   - 熟悉 ros2 命令列工具

3. **第三階段 - 程式設計** (5-7 小時)
   - 逐章閱讀 ROS2_Humble_Beginner_Client_Libraries.md
   - 動手建立工作空間與套件
   - 實作 Publisher、Subscriber、Service 等模式

---

## 💡 核心概念速查表

| 概念 | 說明 | 檔案位置 |
|------|------|--------|
| **節點 (Nodes)** | ROS 2 中獨立執行的程式單元 | CLI Tools |
| **主題 (Topics)** | 單向廣播的連續資料流 | CLI Tools |
| **服務 (Services)** | 同步的請求-回應通訊 | Client Libraries |
| **工作空間** | 所有 ROS 2 開發的容器 | Client Libraries |
| **套件 (Packages)** | 代碼、設定與資源的組織單位 | Client Libraries |
| **Launch 檔** | 批量啟動多個節點的腳本 | Client Libraries |

---

## 📖 資料來源

本教學內容參考以下官方資源：
- [ROS 2 Humble 官方文件](https://docs.ros.org/en/humble/index.html)
- Beginner: CLI Tools 系列教學
- Beginner: Client Libraries 系列教學
- [ROS 2 Humble 影片教學播放清單](https://www.youtube.com/playlist?list=PLLSegLrePWgJudpPUof4-nVFHGkB62Izy)
- [TurtleBot3(ROS2)-Humble 線上手冊 Archives - 採智科技網站v2](https://idminer.com.tw/docs-category/emanual-tb3-humble/)

---

## 🎓 學習建議

- **動手實踐**：邊讀邊練，不要只看理論
- **多用工具**：充分利用 `ros2` 命列工具與 `rqt` 來觀察系統
- **從簡到繁**：先掌握單節點通訊，再進階到複雜系統架構
- **保持耐心**：ROS 2 學習曲線陡峭，但理解後能開發強大的機器人系統

---

## 📝 筆記

此教學講義適合在 Linux 環境（或 WSL）中進行實作。建議配合實際的機器人開發環境使用。

祝您學習愉快！ 🤖
