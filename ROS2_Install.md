# ROS 2 Humble 安裝與 WSL 基礎操作講義

## Part 1: Windows 環境準備 (WSL 系統)

[cite_start]WSL (Windows Subsystem for Linux) 是由 Microsoft 推出的一款開源工具，讓你可以直接在 Windows 電腦上執行 Linux 程式、跑 Docker 容器、開發程式，並且能與 Windows 主機輕鬆共享檔案 [cite: 3]。

[cite_start]⚠️ **重要提醒**：本講義以 Windows 11 為主 [cite: 4][cite_start]。安裝 ROS 2 Humble 版本時，**必須搭配 Ubuntu 22.04 版本**的 Linux 系統 [cite: 5]。

### 1.1 WSL 常用指令大全

你可以透過 Windows 終端機 (PowerShell 或命令提示字元) 來操作 WSL：

**安裝與啟動**
* `wsl --install`：安裝 WSL 和預設的 Linux 發行版（通常是 Ubuntu）。
* `wsl`：啟動預設的 Linux 發行版。
* `wsl -d <發行版名稱>`：啟動指定的 Linux 發行版（例如 `wsl -d Ubuntu`）。
* `wsl -l -o` (或 `wsl --list --online`)：查看網路上有哪些可供安裝的 Linux 版本。

**系統管理與狀態**
* `wsl -l -v` (或 `wsl --list --verbose`)：列出所有已安裝的發行版、其運行狀態及 WSL 版本。
* `wsl --status`：檢查 WSL 的配置狀態（如預設版本、內核版本等）。
* `wsl --update`：更新 WSL 的內核版本。
* `wsl --version`：查看目前安裝的 WSL 工具版本。

**關閉、設定與解除安裝**
* `exit`：在 Linux 終端機內輸入，可退出該 shell。
* `wsl -t <名稱>` (或 `wsl --terminate <發行版名稱>`)：立即終止指定的發行版。
* `wsl --shutdown`：立即停止所有正在運行的 WSL 發行版和虛擬機器。
* `wsl -s <名稱>` (或 `wsl --set-default <發行版名稱>`)：設定預設啟動的發行版。
* `wsl --set-default-version <版本號>`：設定新安裝發行版時預設使用的 WSL 版本（1 或 2）。
* `wsl --set-version <發行版名稱> <版本號>`：將現有的發行版在 WSL 1 與 WSL 2 之間轉換。
* `wsl --unregister <發行版名稱>`：解除註冊並刪除該發行版（**注意：這會永久刪除該 Linux 內的所有資料**）。

**備份與匯入**
* `wsl --export <發行版名稱> <檔案路徑.tar>`：將發行版匯出成備份檔。
* `wsl --import <新名稱> <安裝路徑> <檔案路徑.tar>`：從備份檔匯入發行版（可用於將 Linux 安裝在非 C 槽的硬碟）。

### 1.2 WSL 實用技巧與疑難排解

* **解決匯入後預設為 root 登入的問題**：
    如果你使用 `wsl --import` 匯入自定義的 Linux 發行版，系統預設會以 root 身分登入。解決方式如下：
    1. 若沒有一般使用者，先建立一個並賦予 sudo 權限：
       ```bash
       sudo adduser <username>
       sudo usermod -aG sudo <username>
       ```
    2. 編輯設定檔 `/etc/wsl.conf`：
       ```bash
       sudo nano /etc/wsl.conf
       ```
    3. 加入以下內容指定預設登入者：
       ```ini
       [user]
       default=<username>
       ```
    4. 回到 Windows 終端機執行 `wsl --terminate <發行版名稱>` 重啟 WSL，下次就會自動以該使用者登入了。
* **快速查看 IP**：輸入 `wsl hostname -I` 即可查看 WSL 內部的 IP 位址。
* **檔案存取**：在 Windows 檔案總管的地址欄輸入 `\\wsl$`，即可存取所有 Linux 系統內的檔案。

---

## Part 2: ROS 2 Humble 安裝步驟 (Ubuntu)

進入你的 Ubuntu 22.04 終端機，依序執行以下步驟來安裝 ROS 2：

### Step 1: 設定語系 (Set Locale)
ROS 2 需要系統支援 UTF-8 編碼。請執行以下指令確保語系設定正確：
```bash
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

### Step 2: 設定軟體源 (Setup Sources)
確認系統已啟用 Ubuntu 的 `universe` 儲存庫，並下載安裝官方最新的 `ros2-apt-source` 輔助套件（這會自動配置好 ROS 2 的金鑰與軟體清單）：
```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y

# 取得最新版的 ros2-apt-source 版本號並下載安裝檔
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

# 執行安裝
sudo dpkg -i /tmp/ros2-apt-source.deb
```

### Step 3: 安裝 ROS 2 套件 (Install ROS 2 packages)
加入軟體源後，**務必先更新並升級現有系統套件**。官方特別警告，若不先執行 upgrade，可能會意外移除重要的系統套件 (如 systemd)。
```bash
sudo apt update
sudo apt upgrade -y
```

升級完成後，安裝包含圖形化工具與教學套件的桌面完整版 (Desktop Install)：
```bash
sudo apt install ros-humble-desktop -y
```

### Step 4: 安裝開發工具 (Development tools)
為了日後能夠順利編譯自己寫的 ROS 2 程式碼，請一併安裝官方推薦的開發工具包：
```bash
sudo apt install ros-dev-tools -y
```

### Step 5: 環境設定 (Environment setup)
要讓終端機能夠識別 ROS 2 的相關指令，必須載入環境設定檔。建議直接將其寫入 `~/.bashrc` 中，這樣每次開啟新終端機就會自動載入：
```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## Part 3: 驗證安裝 (Try some examples)

官方提供了一個簡單的 C++ 發布者 (Talker) 與 Python 訂閱者 (Listener) 範例，我們可以用它來確認核心通訊功能是否正常運作。

1. **開啟第一個終端機**，啟動發布者：
   ```bash
   ros2 run demo_nodes_cpp talker
   ```
   *正常情況下，畫面會不斷印出 `Publishing: 'Hello World: 1'` 的訊息*。

2. **開啟第二個終端機**（不需要關閉第一個），啟動訂閱者：
   ```bash
   ros2 run demo_nodes_py listener
   ```
   *如果設定成功，這個視窗就會同步顯示接收到的 `I heard: [Hello World: 1]`*。

---