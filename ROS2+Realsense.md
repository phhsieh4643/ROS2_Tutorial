以下整理的是**在 Raspberry Pi 4 上使用 ROS 2 讀取 Intel RealSense (D435/D435i/D455 等) 相機資料**的完整流程。我主要參考了：

* [RealSense-ROS2-Raspberry-Pi-4](https://github.com/realsenseai/realsense-ros?utm_source=chatgpt.com)（社群整理）
* [realsense-ros 官方 Repository](https://github.com/realsenseai/realsense-ros?utm_source=chatgpt.com)
* [librealsense 官方 Repository](https://github.com/realsenseai/librealsense?utm_source=chatgpt.com)
* ROS 官方與社群安裝經驗([GitHub][1])

---

# 一、建議環境

| 硬體                                 | 建議 |
| ---------------------------------- | -- |
| Raspberry Pi 4 (4GB 或 8GB)         | ✓  |
| Ubuntu 22.04 Server/Desktop 64-bit | ✓  |
| ROS2 Humble                        | ✓  |
| USB3.0 Port                        | 必須 |
| RealSense D435 / D435i / D455      | ✓  |

> Raspberry Pi OS 雖然也能安裝，但 Ubuntu + ROS2 是官方及社群最常使用的組合。

---

# 二、安裝 ROS2

確認已安裝 ROS2 Humble

```bash
source /opt/ros/humble/setup.bash

ros2 doctor
```

若正常會顯示

```
All checks passed
```

---

# 三、安裝 librealsense

RealSense ROS Wrapper **依賴 librealsense**。

官方提供兩種方式：

## 方法一（推薦）

直接安裝 binary package

```bash
sudo apt update

sudo apt install \
ros-humble-librealsense2*
```

這會安裝

* librealsense2
* dev
* utils
* firmware tools

官方目前建議 ROS 使用者直接採用此方式。([GitHub][1])

---

## 方法二（若 Pi 上 binary 有問題）

自行編譯 librealsense

```bash
git clone https://github.com/realsenseai/librealsense.git

cd librealsense

mkdir build
cd build

cmake ..
make -j4

sudo make install
```

如果需要 CUDA、OpenGL 或特殊 kernel patch，再依官方文件調整。([GitHub][2])

---

# 四、確認 Camera 可被辨識

接上 USB3

執行

```bash
rs-enumerate-devices
```

應看到

```
Intel RealSense D435

Serial Number:
Firmware:
USB type: 3.2
```

若沒有：

先檢查

```bash
lsusb
```

應看到

```
Intel Corp.
```

---

# 五、建立 ROS2 Workspace

```bash
mkdir -p ~/ros2_ws/src

cd ~/ros2_ws/src
```

---

# 六、下載 realsense-ros

```bash
git clone https://github.com/realsenseai/realsense-ros.git \
-b ros2-master
```

官方目前使用

```
ros2-master
```

作為最新 ROS2 分支。([GitHub][1])

---

# 七、安裝依賴

```bash
cd ~/ros2_ws

sudo apt install python3-rosdep

sudo rosdep init
rosdep update

rosdep install \
-i \
--from-path src \
--rosdistro humble \
--skip-keys=librealsense2 \
-y
```

如果 librealsense 已安裝

```
--skip-keys=librealsense2
```

即可。

---

# 八、編譯

```bash
cd ~/ros2_ws

colcon build
```

完成後

```
source install/setup.bash
```

建議加入

```
~/.bashrc
```

```
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
```

---

# 九、啟動 Camera

官方最常使用：

```bash
ros2 launch realsense2_camera rs_launch.py
```

若正常

Terminal 會看到

```
RealSense Node Is Up!
```

---

# 十、確認 Topic

列出 Topic

```bash
ros2 topic list
```

通常可看到

```
/camera/color/image_raw

/camera/color/camera_info

/camera/depth/image_rect_raw

/camera/depth/camera_info

/camera/aligned_depth_to_color/image_raw

/camera/imu

/camera/extrinsics/...

/tf

/tf_static
```

---

查看頻率

```bash
ros2 topic hz \
/camera/color/image_raw
```

查看影像

```bash
rqt_image_view
```

或

```bash
ros2 run image_tools showimage \
--ros-args \
-r image:=/camera/color/image_raw
```

---

# 十一、RViz2

```bash
rviz2
```

新增

Image

選擇

```
/camera/color/image_raw
```

若要看 PointCloud

新增

```
PointCloud2
```

Topic

```
/camera/depth/color/points
```

---

# 十二、常用 Launch 參數

### 開啟 PointCloud

```bash
ros2 launch realsense2_camera rs_launch.py \
pointcloud.enable:=true
```

---

### 關閉 RGB

```bash
enable_color:=false
```

---

### 指定解析度

例如

```
640x480@30
```

```bash
depth_module.depth_profile:=640x480x30
```

RGB

```bash
rgb_camera.color_profile:=640x480x30
```

---

### 啟用 IMU

D435i、D455

```bash
enable_gyro:=true

enable_accel:=true

unite_imu_method:=2
```

---

完整例子

```bash
ros2 launch realsense2_camera rs_launch.py \
pointcloud.enable:=true \
enable_gyro:=true \
enable_accel:=true \
unite_imu_method:=2
```

官方支援大部分參數於 launch 時設定。([GitHub][1])

---

# 十三、確認資料

例如

```bash
ros2 topic echo \
/camera/color/camera_info
```

查看 IMU

```bash
ros2 topic echo \
/camera/imu
```

查看 TF

```bash
ros2 run tf2_tools view_frames
```

---

# 十四、常見問題

## (1) Camera 找不到

確認

```
lsusb
```

是否有 Intel

並確認接的是

> USB3 藍色孔

很多人接 USB2 會導致無法開啟 Depth。([Reddit][3])

---

## (2) "No device connected"

通常是

* USB 線材不支援資料傳輸
* USB 電流不足
* USB2 而非 USB3

---

## (3) Frame Rate 很低

例如只有

```
5 FPS
```

可降低解析度

```
640×480
```

或

```
424×240
```

Pi4 CPU 不足時不要直接使用

```
1280×720@30
```

---

## (4) PointCloud 很慢

建議：

```
640×480

pointcloud.enable:=true
```

避免同時開

* RGB Full HD
* Depth Full HD

---

# 十五、推薦的 Raspberry Pi 4 設定

若後續要做 SLAM（如 RTAB-Map、ORB-SLAM3、Nav2 等），建議使用以下較平衡的設定：

```bash
ros2 launch realsense2_camera rs_launch.py \
depth_module.depth_profile:=640x480x30 \
rgb_camera.color_profile:=640x480x30 \
pointcloud.enable:=true \
align_depth.enable:=true \
enable_gyro:=true \
enable_accel:=true \
unite_imu_method:=2
```

這組設定兼顧了 CPU 負載與 SLAM 所需的 RGB、Depth、PointCloud、IMU 資料來源，對 Raspberry Pi 4 而言是較穩定且常見的配置。

[1]: https://github.com/realsenseai/realsense-ros?utm_source=chatgpt.com "GitHub - realsenseai/realsense-ros: ROS Wrapper for RealSense™ Cameras · GitHub"
[2]: https://github.com/realsenseai/librealsense?utm_source=chatgpt.com "GitHub - realsenseai/librealsense: RealSense SDK · GitHub"
[3]: https://www.reddit.com/r/ROS/comments/1drntfp?utm_source=chatgpt.com "[ROS2][Humble] Issues with Running Intel Depth Camera Node"
