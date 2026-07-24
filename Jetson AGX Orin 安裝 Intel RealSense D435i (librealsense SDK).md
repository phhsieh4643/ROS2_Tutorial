
# Jetson AGX Orin 安裝 Intel RealSense D435i (librealsense SDK)

本文件說明如何在 **NVIDIA Jetson AGX Orin** 上安裝 Intel RealSense D435i。

適用環境：

- Jetson AGX Orin Developer Kit
- Ubuntu 22.04
- JetPack 6.x
- L4T 36.x
- Kernel 5.15.x
- Intel RealSense D435i
- librealsense v2.58.x

本流程參考官方文件：

https://github.com/realsenseai/librealsense/blob/master/doc/installation_jetson.md

---

# 1. 確認系統資訊

確認 kernel：

```bash
uname -r
````

範例：

```
5.15.148-tegra
```

確認 JetPack / L4T：

```bash
dpkg-query --show nvidia-l4t-core
```

範例：

```
nvidia-l4t-core 36.4.7-xxxx
```

---

# 2. 移除舊版 librealsense

若之前使用 apt 安裝：

```bash
sudo apt remove --purge \
librealsense2 \
librealsense2-dev \
librealsense2-gl \
librealsense2-utils \
librealsense2-udev-rules
```

清理套件：

```bash
sudo apt autoremove
```

---

若之前使用 source build 安裝，需要移除 `/usr/local`：

確認：

```bash
find /usr/local -name "*realsense*"
```

刪除：

```bash
sudo rm -f /usr/local/bin/realsense-viewer
sudo rm -f /usr/local/bin/rs-*

sudo rm -f /usr/local/lib/librealsense2*
sudo rm -f /usr/local/lib/librealsense-file.a

sudo rm -rf /usr/local/include/librealsense2
sudo rm -rf /usr/local/include/librealsense2-gl

sudo rm -rf /usr/local/lib/pkgconfig/realsense2*
sudo rm -rf /usr/local/lib/cmake/realsense2*

sudo ldconfig
```

確認：

```bash
pkg-config --modversion realsense2
```

應顯示：

```
Package realsense2 was not found
```

---

# 3. 安裝必要套件

更新套件：

```bash
sudo apt update
```

安裝依賴：

```bash
sudo apt install \
git \
libssl-dev \
libusb-1.0-0-dev \
libudev-dev \
pkg-config \
libgtk-3-dev \
v4l-utils \
cmake \
build-essential \
-y
```

---

# 4. 下載 librealsense

進入 home：

```bash
cd ~
```

下載：

```bash
git clone https://github.com/realsenseai/librealsense.git
```

進入資料夾：

```bash
cd ~/librealsense
```

確認版本：

```bash
git describe --tags
```

---

# 5. Patch Jetson Kernel

Jetson 預設 kernel 對 RealSense D435i 的 RGB 與 IMU 支援不完整。

需要使用 librealsense 提供的 script 修改 NVIDIA L4T kernel module：

* uvcvideo driver
* HID sensor driver

否則可能只有：

* Depth ✅
* RGB ❌
* IMU ❌

執行：

```bash
cd ~/librealsense

./scripts/patch-realsense-ubuntu-L4T.sh
```

第一次執行可能會出現：

```
License link not found
```

原因：

`patch-realsense-ubuntu-L4T.sh` 內部使用舊 NVIDIA license URL，而 NVIDIA 已更新 L4T release license 位置。

---

## 解決方法：修改 patch script

開啟 script：

```bash
cd ~/librealsense

nano scripts/patch-realsense-ubuntu-L4T.sh
```

找到：

```bash
license_path=
```

附近的 license 檢查區域：

```bash
license="$(curl -L -s ${license_path})"
[[ -z $license || "$license" == "Not found" ]] && echo "License link not found" && exit 2
```

將其註解：

```bash
# license="$(curl -L -s ${license_path})"
# [[ -z $license || "$license" == "Not found" ]] && echo "License link not found" && exit 2
```

儲存：

```
Ctrl + O
Enter
Ctrl + X
```

---

重新執行：

```bash
cd ~/librealsense

./scripts/patch-realsense-ubuntu-L4T.sh
```

此時會繼續下載 NVIDIA kernel source：

```
Create the sandbox - NVIDIA L4T source tree(s)
```

並開始 patch：

```
Copying the patched modules to /lib/modules/<kernel>/extra/
```

過程中：

```
Remove all RealSense cameras attached.
Hit any key when ready
```

請拔掉 RealSense 後按任意鍵。

---

如果看到：

```
Failed to unload module videodev.
Try rebooting
```

屬正常現象。

重新啟動：

```bash
sudo reboot
```

---

## 若出現 videodev 無法卸載

可能看到：

```
modprobe: FATAL: Module videodev is in use.
Failed to unload module videodev.
Try rebooting
```

這是正常現象。

原因：

目前 kernel 正在使用：

```
videodev
 └── tegra_camera
 └── uvcvideo
```

無法直接卸載。

重新啟動：

```bash
sudo reboot
```

---

## Reboot 後確認 patch 是否成功

確認 patched module：

```bash
find /lib/modules/$(uname -r) -name "*uvcvideo*"
```

應看到：

```
/lib/modules/<kernel>/kernel/drivers/media/usb/uvc/uvcvideo.ko

/lib/modules/<kernel>/extra/uvcvideo.ko
```

更新 module：

```bash
sudo depmod -a
```

載入 patched driver：

```bash
sudo modprobe uvcvideo
```

確認：

```bash
modinfo uvcvideo | grep filename
```

正確結果：

```
filename:
/lib/modules/<kernel>/extra/uvcvideo.ko
```

代表 Jetson 已使用 librealsense patch 後的 UVC driver。


---

# 6. 確認 patched UVC driver

重新登入後：

```bash
find /lib/modules/$(uname -r) -name "*uvcvideo*"
```

應看到：

```
/lib/modules/<kernel>/extra/uvcvideo.ko
```

更新 module：

```bash
sudo depmod -a
```

載入：

```bash
sudo modprobe uvcvideo
```

確認：

```bash
lsmod | grep uvcvideo
```

確認使用 patched driver：

```bash
modinfo uvcvideo | grep filename
```

應為：

```
/lib/modules/<kernel>/extra/uvcvideo.ko
```

---

# 7. 設定 USB 權限 (udev rules)

進入 librealsense：

```bash
cd ~/librealsense
```

執行：

```bash
./scripts/setup_udev_rules.sh
```

成功：

```
udev-rules successfully installed
```

重新載入：

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

# 8. 編譯 librealsense SDK

建立 build：

```bash
cd ~/librealsense

mkdir build
cd build
```

使用 CMake：

```bash
cmake .. \
-DBUILD_EXAMPLES=true \
-DCMAKE_BUILD_TYPE=release \
-DFORCE_RSUSB_BACKEND=false \
-DBUILD_WITH_CUDA=true
```

說明：

| 參數                        | 功能                   |
| ------------------------- | -------------------- |
| BUILD_EXAMPLES            | 建立 viewer 和測試工具      |
| FORCE_RSUSB_BACKEND=false | 使用 kernel UVC driver |
| BUILD_WITH_CUDA=true      | 啟用 Jetson CUDA       |

---

編譯：

```bash
make -j$(($(nproc)-1))
```

---

安裝：

```bash
sudo make install
```

更新 library：

```bash
sudo ldconfig
```

---

# 9. 測試 SDK

確認工具：

```bash
which realsense-viewer
```

應：

```
/usr/local/bin/realsense-viewer
```

確認 camera：

```bash
rs-enumerate-devices
```

應看到：

```
Intel RealSense D435i
```

---

# 10. 開啟 RealSense Viewer

執行：

```bash
realsense-viewer
```

正常應看到：

| Sensor | 狀態              |
| ------ | --------------- |
| Depth  | Frames received |
| RGB    | Frames received |
| Gyro   | Frames received |
| Accel  | Frames received |

---

# 11. 問題排查

## 只有 Depth，RGB / IMU 無資料

確認：

```bash過程中：

```
Remove all RealSense cameras attached.
Hit any key when ready
```

請拔掉 RealSense 後按任意鍵。

---

如果看到：

```
Failed to unload module videodev.
Try rebooting
```

屬正常現象。

重新啟動：

```bash
sudo reboot
```
lsmod | grep uvcvideo
```

必須使用：

```
extra/uvcvideo.ko
```

確認：

```bash
sudo dmesg | grep -i hid
```

應看到：

```
hid-sensor-hub
RealSense Depth Camera 435i
```

---

## 找不到 rs-enumerate-devices

確認安裝：

```bash
ls /usr/local/bin
```

若存在：

```
rs-enumerate-devices
```

加入 PATH：

```bash
export PATH=/usr/local/bin:$PATH
```

---

## 確認 video device

```bash
v4l2-ctl --list-devices
```

正常：

```
Intel(R) RealSense(TM) Depth Camera 435i

/dev/video0
/dev/video1
/dev/video2
/dev/video3
/dev/video4
/dev/video5
```

---

# 12. 安裝完成確認

完成後：

```
Jetson AGX Orin
        |
        |
librealsense 2.58.x
        |
        |
patched uvcvideo driver
        |
        |
RealSense D435i
        |
        |
Depth + RGB + IMU
```

即可進一步安裝：

* [realsense-ros2 wrapper 安裝與測試指南](RealSense_ROS2_realsense-ros_Setup.md)
* RTAB-Map
* ORB-SLAM3
* RGB-D SLAM 系統
