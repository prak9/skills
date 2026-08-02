#include <mutex>
#include <vector>

class Store {
 public:
  bool DeleteRef(int id) {
    std::lock_guard<std::mutex> lock(mu_);
    return DeleteRefLocked(id);
  }

 private:
  bool DeleteRefLocked(int id);
  std::mutex mu_;
};

bool DeleteBatch(Store& store, const std::vector<int>& ids) {
  bool all_deleted = true;
  for (int id : ids) {
    all_deleted = store.DeleteRef(id) && all_deleted;
  }
  return all_deleted;
}
