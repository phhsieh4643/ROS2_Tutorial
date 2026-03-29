#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

// _1 是一個佔位符 (Placeholder)，代表 callback 函式會接收到的第一個參數
// 在這裡就是收到的訊息本身
using std::placeholders::_1;

class BatteryDashboard : public rclcpp::Node
{
  public:
    BatteryDashboard() : Node("battery_dashboard")
    {
      // 1. 建立訂閱者：綁定 'battery_status' 主題與 topic_callback
      // 使用 std::bind：必須手動寫 _1, _2 等佔位符來對應參數位置。
      subscription_ = this->create_subscription<std_msgs::msg::String>("battery_status", 10, std::bind(&BatteryDashboard::topic_callback, this, _1));
    }

  private:
    // 2. 實作 topic_callback (參數為 const std_msgs::msg::String & msg)
    void topic_callback(const std_msgs::msg::String & msg)
    {
      // 3. 在函式內印出收到的數據
      RCLCPP_INFO(this->get_logger(), "Dashboard received: '%s'", msg.data.c_str());
    }
    // 4. 宣告訂閱者的智慧指標變數
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  // 5. 初始化、啟動 spin、關閉 rclcpp
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<BatteryDashboard>());
  rclcpp::shutdown();
  return 0;
}