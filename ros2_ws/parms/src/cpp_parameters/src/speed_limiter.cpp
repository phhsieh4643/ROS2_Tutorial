#include <chrono>
#include <string>
#include <rclcpp/rclcpp.hpp>

using namespace std::chrono_literals;

class SpeedLimiterNode : public rclcpp::Node
{
public:
  SpeedLimiterNode() : Node("speed_limiter")
  {
    // 1. 建立參數描述
    auto param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    param_desc.description = "機器人的最高移動速限 (m/s)";

    // 2. 宣告參數，名稱為 "max_speed"，預設值為 1.0
    this->declare_parameter("max_speed", 1.0, param_desc);

    // 3. 建立計時器
    timer_ = this->create_wall_timer(
      1000ms, std::bind(&SpeedLimiterNode::timer_callback, this));
  }

private:
  void timer_callback()
  {
    // 4. 取得參數值，並轉型為 double (浮點數)
    double current_speed_limit = this->get_parameter("max_speed").as_double();

    // 印出狀態
    RCLCPP_INFO(this->get_logger(), "目前最高限速設定為: %.2f m/s", current_speed_limit);
  }
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SpeedLimiterNode>());
  rclcpp::shutdown();
  return 0;
}