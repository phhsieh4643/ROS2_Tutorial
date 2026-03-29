# 這是送餐機器人的狀態回報格式
int32 order_id
string delivery_status

# 我們也可以直接引用 ROS 2 內建的其他複雜格式 (例如 geometry_msgs 裡的 Point 座標)
geometry_msgs/Point current_location