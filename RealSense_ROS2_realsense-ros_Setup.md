# ROS2 realsense-ros 安裝與測試指南 (適用 Raspberry Pi & Jetson)

本教學說明如何在已安裝 `librealsense` SDK 的平台上（例如 Raspberry Pi 4 或 NVIDIA Jetson）安裝並測試 ROS2 的 `realsense-ros` wrapper。

---

# Step 1. 下載 ROS2 realsense-ros

回到 workspace：

```bash
cd ~/ros2_ws/src
```

下載 ROS wrapper：

```bash
git clone https://github.com/realsenseai/realsense-ros.git -b ros2-master
```

---

# Step 2. 安裝 ROS dependency

回 workspace：

```bash
cd ~/ros2_ws
```

執行：

```bash
sudo apt-get install python3-rosdep -y
sudo rosdep init # "sudo rosdep init --include-eol-distros" for Foxy and earlier
rosdep update # "sudo rosdep update --include-eol-distros" for Foxy and earlier
```

安裝:
```bash
cd ~/ros2_ws

rosdep install -i --from-path src --rosdistro humble --skip-keys=librealsense2 -y
```

---

# Step 3. Build ROS package

在編譯 `realsense-ros` 前，需要先載入 ROS 2 Humble 環境：

```bash
source /opt/ros/humble/setup.bash
```

進入 ROS 2 workspace：

```bash
cd ~/ros2_ws
```

## Option 1: Standard build (官方文件方式)

官方文件提供最基本的編譯方式：

```bash
colcon build
```

此方式適用於：

- 一般 Ubuntu PC
- 開發測試環境
- 不需要特別最佳化的情境

## Option 2: Recommended build for Raspberry Pi 4 / Jetson

若使用 Raspberry Pi 4 或 Jetson 等開發板，由於資源限制或需要最佳化，建議使用以下設定：
```bash
colcon build \
--symlink-install \
--cmake-args -DCMAKE_BUILD_TYPE=Release \
--parallel-workers 2
```

> **參數說明**：
> 
> `--symlink-install` : 建立 symbolic link，而不是複製檔案至 install 目錄。
> 
> 優點：
> - 修改 ROS package source code 後，不需要重新複製檔案
> - 方便後續修改 realsense-ros 或開發自己的 ROS node
> 
> 適合：
> - ROS 開發環境
> 
> --- 
> `--cmake-args -DCMAKE_BUILD_TYPE=Release` : 指定 CMake 使用 Release 模式編譯。Release 模式會啟用 compiler optimization：
> 
> 優點：
> - 提升執行效率
> - 降低 CPU 負擔
> - 適合即時影像、點雲與 SLAM 應用
> 
> 適合：
> - RealSense camera
> - RGB-D SLAM
> - Navigation
> - Robot application
> 
> 若需要修改或除錯 realsense-ros 原始碼，可以改使用：
> 
> ```bash
> colcon build --cmake-args -DCMAKE_BUILD_TYPE=Debug
> ```
> ---
> Debug 模式提供較完整的除錯資訊，但執行效能較低。
> 
> `--parallel-workers 2` : 限制同時編譯的工作數量。
> 
> 優點：
> - 降低 CPU 使用率
> - 減少記憶體消耗
> 
> 適合：
> - Raspberry Pi 4 或 Jetson 等資源有限的設備
---

編譯完成後載入 workspace：

```bash
source install/local_setup.bash
```
或

```bash
source install/setup.bash
```

# Step 4. 測試 Intel RealSense D435i

## 4.1 啟動 RealSense ROS2 Node

首先載入 ROS2 與 workspace：

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

啟動 RealSense：

```bash
ros2 launch realsense2_camera rs_launch.py
```

正常情況下 terminal 應看到：

```
RealSense ROS v4.58.2
Built with LibRealSense v2.58.2
Device Name: Intel RealSense D435I
Device FW version: 5.17.3.10
Device USB type: 3.2

Starting Sensor: Depth Module
Starting Sensor: RGB Camera

RealSense Node Is Up!
```

代表：

* librealsense 已正確連接 D435i
* ROS2 wrapper 正常啟動
* RGB / Depth sensor 已開啟

---

# 4.2 查看 ROS Topic

開啟另一個 terminal：

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

查看 topic：

```bash
ros2 topic list
```

正常應包含：

### RGB

```
/camera/camera/color/image_raw
/camera/camera/color/camera_info
```

### Depth

```
/camera/camera/depth/image_rect_raw
/camera/camera/depth/camera_info
```

### TF

```
/tf_static
```

此時代表 RGB-D 影像已正常發布。

---

# 4.3 測試 RGB 影像

確認 RGB topic：

```bash
ros2 topic info /camera/camera/color/image_raw
```

預期：

```
Type: sensor_msgs/msg/Image
Publisher count: 1
```

查看影像頻率：

```bash
ros2 topic hz /camera/camera/color/image_raw
```

D435i 預設：

```
average rate: ~30 Hz
```

---

# 4.4 測試 Depth 影像

確認：

```bash
ros2 topic info /camera/camera/depth/image_rect_raw
```

預期：

```
Type: sensor_msgs/msg/Image
Publisher count: 1
```

查看頻率：

```bash
ros2 topic hz /camera/camera/depth/image_rect_raw
```

預期：

```
average rate: ~30 Hz
```

---

# 4.5 啟用 PointCloud

## 方法 1：launch 時啟用（部分平台可用）

官方文件提供：

```bash
ros2 launch realsense2_camera rs_launch.py pointcloud.enable:=true
```

但是在 ARM64 (Raspberry Pi / Jetson) + RealSense ROS v4.58.2 環境中，可能無法正常套用。

---

## 方法 2：Runtime 啟用（推薦）

確認 pointcloud 參數：

```bash
ros2 param list /camera/camera | grep point
```

在 ARM64 平台可能看到：

```
pointcloud__neon_.enable
pointcloud__neon_.ordered_pc
pointcloud__neon_.allow_no_texture_points
```

啟用：

```bash
ros2 param set /camera/camera pointcloud__neon_.enable true
```

成功：

```
Set parameter successful
```

---

# 4.6 確認 PointCloud Topic

查看：

```bash
ros2 topic list | grep points
```

應看到：

```
/camera/camera/depth/color/points
```

確認訊息類型：

```bash
ros2 topic info /camera/camera/depth/color/points
```

預期：

```
Type: sensor_msgs/msg/PointCloud2
Publisher count: 1
```

查看發布頻率：

```bash
ros2 topic hz /camera/camera/depth/color/points
```

預期：

```
average rate: ~30 Hz
```

---

# 4.7 測試 IMU (D435i)

D435i 內建：

* Accelerometer
* Gyroscope

啟動時加入：

```bash
ros2 launch realsense2_camera rs_launch.py \
enable_accel:=true \
enable_gyro:=true
```

查看 topic：

```bash
ros2 topic list | grep imu
```

正常應包含：

```
/camera/camera/imu
```

或：

```
/camera/camera/imu/data
```

查看資料：

```bash
ros2 topic echo /camera/camera/imu
```

應持續輸出：

```yaml
angular_velocity:
  x:
  y:
  z:

linear_acceleration:
  x:
  y:
  z:
```

---

# 4.8 查看影像結果 (Optional)

安裝：

```bash
sudo apt install ros-humble-rqt-image-view
source /opt/ros/humble/setup.bash
```

啟動：

```bash
ros2 run rqt_image_view rqt_image_view
```

選擇：

RGB:

```
/camera/camera/color/image_raw
```

Depth:

```
/camera/camera/depth/image_rect_raw
```

---

# 4.9 最終確認 Checklist

完成後應得到：

| 功能          | Topic                                 | 結果 |
| ----------- | ------------------------------------- | -- |
| RGB         | `/camera/camera/color/image_raw`      | ✅  |
| Depth       | `/camera/camera/depth/image_rect_raw` | ✅  |
| Camera info | `camera_info`                         | ✅  |
| PointCloud  | `/camera/camera/depth/color/points`   | ✅  |
| IMU         | `/camera/camera/imu`                  | ✅  |
| TF          | `/tf_static`                          | ✅  |

完成以上測試後，即代表 ROS2 + RealSense D435i 環境已完成，可以進一步進行：

* RTAB-Map RGB-D SLAM
* ORB-SLAM3 RGB-D
* VINS-Fusion / Visual-Inertial SLAM
* Semantic SLAM pipeline

---

# Step 5. 設定解析度與 FPS

建議：

## SLAM 使用

```bash
ros2 launch realsense2_camera rs_launch.py \
depth_module.depth_profile:=640x480x15 \
rgb_camera.color_profile:=640x480x15
```

## 如果只是點雲 (影像可以流暢運作)

```bash
ros2 launch realsense2_camera rs_launch.py \
depth_module.depth_profile:=424x240x15 \
rgb_camera.color_profile:=424x240x15
```
