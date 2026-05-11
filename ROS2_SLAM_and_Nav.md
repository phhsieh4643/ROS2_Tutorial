# 《進階專題：機器人的空間記憶與大腦 —— SLAM 與 Nav2 自動導航》

## 1. 核心觀念：建圖 (SLAM) 與導航 (Navigation) 為何要分開？

在初學階段，很多人會問：「為什麼不讓機器人一邊開、一邊建圖、一邊自己導航避障就好？」

這牽涉到**運算資源**與**系統穩定度**的考量。在 ROS 2 中，我們通常將自動駕駛拆成兩個完全獨立的階段：
* **階段一：建圖 (SLAM)。** 機器人在完全陌生的環境中，靠著輪子轉速 (`/odom`) 與光達 (`/scan`)，像拼圖一樣慢慢把地圖畫出來。這極度消耗 CPU 計算能力。
* **階段二：導航 (Navigation 2)。** 地圖存檔後，環境的大致輪廓就被視為「已知」。此時機器人只需要專心做兩件事：**「確認自己在哪」**(定位) 與 **「規劃怎麼走」**(路徑規劃)。這樣做不僅省電、穩定，而且地圖可以重複使用。

---

## 2. 📥 環境準備：下載大腦與記憶套件

在正式開始前，我們必須先將龐大且複雜的 AI 演算法安裝到系統中。請開啟終端機，執行以下指令：

```bash
sudo apt update

# 一次安裝 Cartographer(建圖)、Nav2(導航框架) 以及 TB3 專屬的設定檔
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-turtlebot3-cartographer ros-humble-turtlebot3-navigation2 -y
```

---

## 3. 🗺️ 階段一：探索未知，使用 Cartographer 繪製地圖

我們將使用 Google 開源的 **Cartographer** 演算法來幫機器人建立「長期記憶」。請依序開啟四個終端機：

**1. 啟動 Gazebo 虛擬世界 (終端機 1)**
將機器人放入充滿障礙物的房間中：
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**2. 啟動 SLAM 建圖節點 (終端機 2)**
呼叫官方寫好的 SLAM 腳本。加上 `use_sim_time:=True` 非常重要，它會強迫演算法使用 Gazebo 的虛擬時間，確保 TF 樹不會崩潰（這會自動幫你開啟 Rviz2）：
```bash
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

**3. 遙控探索與建圖 (終端機 3)**
啟動鍵盤控制：
```bash
ros2 run turtlebot3_teleop teleop_keyboard
```
> **👁️ Rviz2 觀察重點：** 慢慢遙控機器人走遍每個角落。你會看到原本灰色的「未知領域」，被光達掃描後會變成白色的「可通行區」與黑色的「實體牆壁」。務必讓機器人走完一整圈，確保地圖邊界閉合。

**4. 儲存地圖檔 (終端機 4)**
當地圖看起來完整後，**請不要關閉任何終端機**。使用 `map_server` 將地圖存檔到你的家目錄（命名為 `my_map`）：
```bash
ros2 run nav2_map_server map_saver_cli -f ~/my_map
```
*(執行後，你的家目錄會產生 `my_map.pgm` 圖片與 `my_map.yaml` 設定檔。)*

---

## 4. 🧠 解剖 Nav2 大腦：代價地圖與雙層規劃器

在把畫好的地圖餵給機器人之前，我們先透視 Nav2 大腦的三個核心模組：

1. **代價地圖 (Costmap)：** 如果機器人緊貼著牆壁走，現實中一定會撞車。Nav2 會在地圖障礙物周圍畫上一圈淺藍色或紫色的「膨脹層」。越靠近牆壁，代價 (Cost) 越高，機器人會盡量走在代價為 0 的安全區。
2. **全局規劃器 (Global Planner)：** 像 Google Maps。當你給定終點，它會在靜態地圖上用 A* 演算法，瞬間計算出一條從 A 點到 B 點的最短路徑（在 Rviz2 顯示為**紅線**）。
3. **局部規劃器 (Local Planner)：** 像人類駕駛。它只關注機器人前方 1~2 公尺的雷達數據，負責動態閃避突然衝出來的障礙物，並實際控制油門與轉向（在 Rviz2 顯示為**藍線**）。

---

## 5. 🚀 階段二：喚醒大腦，啟動 Nav2 自動導航

請將剛才開啟的四個終端機**全部關閉 (`Ctrl+C`)**，我們要進入真正的自動駕駛階段。

**1. 啟動世界與 Nav2 大腦 (終端機 1 & 2)**
開啟第一個終端機啟動 Gazebo：
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```
開啟第二個終端機啟動 Nav2，並明確指定剛才存好的地圖路徑：
```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=$HOME/my_map.yaml
```

**2. 解決綁架問題，進行初始定位 (Rviz2 介面操作)**
導航啟動後，Rviz2 會打開，但此時演算法不知道機器人一開始被放在哪裡。
* 點擊 Rviz2 頂端的 **2D Pose Estimate**。
* 在地圖上點擊機器人目前實際站在 Gazebo 中的位置，並**按住滑鼠左鍵拖曳**指示車頭朝向。
* *(成功指標：綠色的雷射測距點會完美貼合在黑色的地圖牆壁上！)*

**3. 下達自動駕駛任務 (Rviz2 介面操作)**
點擊 Rviz2 頂部的 **Nav2 Goal** 按鈕。在遠處的走道上點擊並拖曳決定到達時的車頭朝向。放開滑鼠後，Nav2 會立刻算出紅色的全局路徑，機器人就會自己開過去了！

---

## 6. 🛠️ 進階除錯：當機器人卡住時 (Recovery Behaviors)

真實世界充滿意外。當你在 Gazebo 裡臨時丟一個大木桶擋住去路時，Nav2 會自動觸發以下「行為樹 (Behavior Trees)」邏輯來自救：
* **清除代價地圖 (Clear Costmap)：** 重新整理記憶，確認障礙物是否已經移開。
* **原地旋轉 (Spin)：** 原地轉圈圈，用光達重新掃描四周尋找破口。
* **倒車 (Back Up)：** 盲退一小段距離，爭取重新計算路徑的空間。

---

## 7. 💻 寫程式控制大腦：Nav2 Simple Commander API (Python 實作)

在真實的工廠中，機器人必須依靠程式碼來自動巡邏。ROS 2 提供了 API，讓你用 Python 就能發送導航點。

在你的工作空間中建立一個 `patrol_bot.py`，並貼入以下程式碼：

```python
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped

def main():
    rclpy.init()
    
    # 初始化 Nav2 導航器
    navigator = BasicNavigator()
    navigator.get_logger().info('等待 Nav2 系統完全啟動...')
    navigator.waitUntilNav2Active()

    # 設定目標座標點 (PoseStamped 格式)
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'                   # 目標座標是以 map (地圖) 為絕對基準
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    
    # 設定目標的 X, Y 位置 (單位：公尺，請依據你建的地圖修改)
    goal_pose.pose.position.x = 2.0
    goal_pose.pose.position.y = -1.0
    
    # 設定車頭朝向 (四元數，w=1.0 代表不旋轉直行)
    goal_pose.pose.orientation.w = 1.0 

    # 將目標點發送給 Nav2 大腦
    navigator.get_logger().info('收到新座標，自動駕駛出發！')
    navigator.goToPose(goal_pose)

    # 監聽導航進度迴圈
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback:
            print(f'預估剩餘時間: {feedback.estimated_time_remaining.sec} 秒')

    # 任務結束判斷
    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('成功抵達目的地！')
    elif result == TaskResult.CANCELED:
        print('任務被取消！')
    elif result == TaskResult.FAILED:
        print('任務失敗，可能卡在死胡同了！')

    rclpy.shutdown()

if __name__ == '__main__':
    main()
```
*(提示：執行此腳本前，請確保你已經完成了上述的「階段二」並成功給予了 Initial Pose 初始定位。)*

### 🏃 如何執行此腳本

1.  **儲存檔案**：將上述程式碼存為 `patrol_bot.py`。
2.  **開啟新終端機**：確保 Gazebo 與 Nav2 仍在運行中。
3.  **執行路徑**：切換到該檔案所在目錄。
4.  **執行指令**：
    ```bash
    python3 patrol_bot.py
    ```

---
