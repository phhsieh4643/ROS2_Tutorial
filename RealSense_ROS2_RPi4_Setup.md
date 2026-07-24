# RealSense D435i + ROS2 Humble Installation Guide (Raspberry Pi 4)

## 1. 確認系統環境

```bash
lsb_release -a
```

預期：

```
Ubuntu 22.04 LTS
```

確認 ROS：

```bash
echo $ROS_DISTRO
```

預期：

```
humble
```

---


## Step 0. 移除目前 apt 安裝版本

先清乾淨。

查看：

```bash
apt list --installed | grep realsense
```

目前：

```
ros-humble-librealsense2
ros-humble-realsense2-camera-msgs
ros-humble-realsense2-camera
```

移除：

```bash
sudo apt remove --purge \
ros-humble-librealsense2 \
ros-humble-realsense2-camera \
ros-humble-realsense2-camera-msgs
```

清理：

```bash
sudo apt autoremove
```

確認：

```bash
apt list --installed | grep realsense
```

應該沒有輸出。

---

# Step 1. 建立乾淨 workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

---

# Step 2. 安裝 librealsense SDK

官方 Option 3：

[https://github.com/realsenseai/librealsense](https://github.com/realsenseai/librealsense)

安裝流程： [GitHub][2]

## 安裝依賴

```bash
sudo apt update

sudo apt install \
libusb-1.0-0-dev \
libudev-dev \
libssl-dev \
libelf-dev \
pkg-config \
libgtk-3-dev \
git \
wget \
cmake \
build-essential \
v4l-utils
```

另外 ROS / viewer 需要：

```bash
sudo apt install \
libglfw3-dev \
libgl1-mesa-dev \
libglu1-mesa-dev
```

---

# Step 3. Clone librealsense

建議放 home：

```bash
cd ~

git clone https://github.com/realsenseai/librealsense.git
```

資料夾位置：

```
~/librealsense
```

---

# Step 4. 設定 USB 權限

進入：

```bash
cd ~/librealsense
```

執行：

```bash
./scripts/setup_udev_rules.sh
```

重新載入：

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

拔掉 D435i

重新插入。

---

# Step 5. Kernel patch

這一步 Raspberry Pi 很重要。

官方：

```bash
./scripts/patch-realsense-ubuntu-lts-hwe.sh
```

([GitHub][2])

完成後確認：

```bash
sudo dmesg | tail -n 50
```

看有沒有：

```
uvcvideo: RealSense
```

---

# Step 6. Build librealsense

不要開 viewer（Pi4 沒必要）。

建立：

```bash
cd ~/librealsense

mkdir build
cd build
```

cmake：

```bash
cmake ../ \
-DCMAKE_BUILD_TYPE=Release \
-DBUILD_EXAMPLES=false \
-DBUILD_GRAPHICAL_EXAMPLES=false
```

編譯：

Pi4 建議：

```bash
make -j3
```

安裝：

```bash
sudo make install
```

確認：

```bash
realsense-viewer
```

如果沒有 GUI：

測試：

```bash
rs-enumerate-devices
```

應看到：

```
Intel RealSense D435i
```

---

# Step 7. 安裝 ROS2 realsense-ros

因為 Raspberry Pi 與 Jetson 等平台的 `realsense-ros` 安裝與測試方式相同，請參考獨立的教學文件進行安裝：
👉 **[ROS2 realsense-ros 安裝與測試指南](RealSense_ROS2_realsense-ros_Setup.md)**

---

# 最終目錄應該變成

```
~
├── librealsense          # SDK source
├── ros2_ws
│   └── src
│       └── realsense-ros # ROS2 wrapper
├── turtlebot3_ws
└── ROS2
```

---

[1]: https://github.com/realsenseai/librealsense/blob/master/doc/distribution_linux.md?utm_source=chatgpt.com "librealsense/doc/distribution_linux.md at master · realsenseai/librealsense · GitHub"
[2]: https://github.com/realsenseai/librealsense/blob/master/doc/installation.md?utm_source=chatgpt.com "librealsense/doc/installation.md at master · realsenseai/librealsense · GitHub"
