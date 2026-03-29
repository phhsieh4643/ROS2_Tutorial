#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

using namespace std::chrono_literals;

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("waiter_node");
  
  // 建立客戶端，指定與 Server 相同的服務型態與名稱 ('place_order')
  auto client = node->create_client<example_interfaces::srv::AddTwoInts>("place_order");

  // 準備請求資料 (2份漢堡，3份薯條)
  auto request = std::make_shared<example_interfaces::srv::AddTwoInts::Request>();
  request->a = 2;
  request->b = 3;

  // 使用 while 迴圈等待廚房上線，每秒檢查一次
  while (!client->wait_for_service(1s)) {
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "呼叫廚房中，請稍後...");
  }

  RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "服務生送出訂單：2 漢堡, 3 薯條...");
  
  // 非同步發送請求 (async_send_request 不會卡死主程式)
  auto result = client->async_send_request(request);
  
  // 等待 Server 回傳結果，若成功則印出
  if (rclcpp::spin_until_future_complete(node, result) == rclcpp::FutureReturnCode::SUCCESS) {
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "廚房回報：總共 %ld 份餐點準備中！", result.get()->sum);
  } else {
    RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "點餐失敗，廚房無回應");
  }

  rclcpp::shutdown();
  return 0;
}