#include <chrono>
#include <iostream>
#include <map>
#include <mutex>
#include <queue>
#include <string>
#include <vector>

enum class OrderStatus { NEW, PENDING, FILLED, CANCELLED, REJECTED };
enum class Side { BUY, SELL };

struct Order {
  std::string order_id;
  std::string symbol;
  Side side;
  double price;
  int quantity;
  OrderStatus status;
  std::chrono::system_clock::time_point timestamp;
};

class OMS {
public:
  void submit_order(const Order &order) {
    std::lock_guard<std::mutex> lock(mtx_);
    orders_[order.order_id] = order;
    orders_[order.order_id].status = OrderStatus::PENDING;
    pending_queue_.push(order.order_id);
    std::cout << "[OMS] Order submitted: " << order.order_id << " for "
              << order.symbol << std::endl;
  }

  void process_orders() {
    std::lock_guard<std::mutex> lock(mtx_);
    while (!pending_queue_.empty()) {
      std::string id = pending_queue_.front();
      pending_queue_.pop();

      // Auto-fill order for simulation
      orders_[id].status = OrderStatus::FILLED;
      std::cout << "[OMS] Order filled: " << id << std::endl;
    }
  }

  OrderStatus get_status(const std::string &id) {
    std::lock_guard<std::mutex> lock(mtx_);
    if (orders_.count(id))
      return orders_[id].status;
    return OrderStatus::REJECTED;
  }

private:
  std::map<std::string, Order> orders_;
  std::queue<std::string> pending_queue_;
  std::mutex mtx_;
};

/*
 * Note: This facilitates standalone OMS logic testing.
 * Production implementation requires a dedicated IPC controller.
 */
int main() {
  OMS oms;
  Order o1{"ord_001",
           "AAPL",
           Side::BUY,
           150.0,
           100,
           OrderStatus::NEW,
           std::chrono::system_clock::now()};
  oms.submit_order(o1);
  oms.process_orders();
  return 0;
}
