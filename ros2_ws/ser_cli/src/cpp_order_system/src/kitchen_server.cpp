#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"
#include <memory>

// 1. 實作 take_order 回呼函式，參數為 Request 與 Response 的 shared_ptr
void take_order(const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request,
          std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response)
{
    // 2. 計算 request 內的 a(漢堡) + b(薯條) 並填入 response->sum
    response->sum = request->a + request->b;
    // 3. 印出收到的訂單內容 (RCLCPP_INFO)
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "收到訂單：漢堡 %ld 份, 薯條 %ld 份", request->a, request->b);
}

int main(int argc, char **argv)
{
  // 4. 初始化 rclcpp
  rclcpp::init(argc, argv);
  // 5. 建立節點 "kitchen_node"
  auto node = rclcpp::Node::make_shared("kitchen_node");
  // 6. 建立服務端 (create_service)，名稱取為 "place_order"，並綁定上述的 take_order 函式
  auto service = node->create_service<example_interfaces::srv::AddTwoInts>("place_order", take_order);
  // 7. 啟動節點 (spin)、關閉 rclcpp
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}