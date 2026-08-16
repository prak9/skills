#include <string>
#include <vector>

struct Entry {
  int id;
  std::string payload;
};

std::vector<std::string> LookupAll(const std::vector<int>& queries,
                                   const std::vector<Entry>& entries) {
  std::vector<std::string> result;
  for (int query : queries) {
    for (const Entry& entry : entries) {
      if (entry.id == query) {
        result.push_back(entry.payload);
        break;
      }
    }
  }
  return result;
}
