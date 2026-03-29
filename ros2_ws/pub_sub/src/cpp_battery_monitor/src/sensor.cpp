#include <chrono>       // 處理時間單位 (如 1000ms)
#include <functional>   // 提供 std::bind
#include <memory>       // 提供智慧指標
#include <string>
#include "rclcpp/rclcpp.hpp"          // ROS2 最核心的 C++ 系統庫
#include "std_msgs/msg/string.hpp"    // 使用 ROS2 標準定義的 String 訊息格式

using namespace std::chrono_literals; // 允許使用 1000ms, 1s 這種直觀的時間寫法

class BatterySensor : public rclcpp::Node
{
  public:
    // 建構函式：初始化節點名稱為 "battery_sensor"，並將初始電量設為 100
    BatterySensor() : Node("battery_sensor"), battery_level_(100)
    {
      // 【步驟 1】 建立發布者 (Publisher)
      // 主題名稱為 "battery_status"，10 是 Queue Size (佇列大小，緩衝區長度)
      publisher_ = this->create_publisher<std_msgs::msg::String>("battery_status", 10);

      // 【步驟 2】 建立定時器 (Timer)
      // 每 1000ms 觸發一次 timer_callback 函式
      // std::bind 用於指向類別內部的成員函式，this 代表當前這個物件
      timer_ = this->create_wall_timer(
        1000ms, std::bind(&BatterySensor::timer_callback, this));
    }

  private:
    // 每秒會被執行一次的「回呼函式」
    void timer_callback()
    {
      // 1. 準備要發送的訊息物件
      auto message = std_msgs::msg::String();
      message.data = "current battery level: " + std::to_string(battery_level_) + "%";
      
      // 2. 在終端機印出日誌 (Logging)，方便開發者觀察
      // RCLCPP_INFO 類似於 printf，但會帶有時間戳與節點資訊
      RCLCPP_INFO(this->get_logger(), "publish: '%s'", message.data.c_str());
      
      // 3. 正式發布訊息到 Topic
      publisher_->publish(message);
      
      // 4. 模擬電量消耗邏輯
      if (battery_level_ > 0) battery_level_--;
    }

    // 私有變數：使用 SharedPtr (智慧指標) 來管理 ROS2 物件的生命週期
    rclcpp::TimerBase::SharedPtr timer_;                                // 定時器指針
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;     // 發布者指針
    int battery_level_;                                                 // 儲存電量數值
};

int main(int argc, char * argv[])
{
  // 初始化 ROS2 通訊環境
  rclcpp::init(argc, argv);

  // 使用 rclcpp::spin 開始循環執行節點
  // std::make_shared<BatterySensor>() 會實例化節點並交給 spin 管理
  // spin 會讓程式停在這裡，不斷檢查定時器時間到了沒、是否有訊息進來
  rclcpp::spin(std::make_shared<BatterySensor>());

  // 當按下 Ctrl+C 結束程式時，關閉 ROS2 資源
  rclcpp::shutdown();
  
  return 0;
}