#include "cuckoo_hash.h"
#include <set>

// Helper function for rehashing with a given set of keys
static void rehash_with_keys(size_t& m, 
                              std::vector<std::optional<int>>& table1,
                              std::vector<std::optional<int>>& table2,
                              std::function<size_t(int)>& h1_func,
                              std::function<size_t(int)>& h2_func,
                              const std::vector<int>& keys_to_insert) {
  std::vector<int> all_keys = keys_to_insert;

  // Keep trying with doubled table sizes until all keys can be inserted
  bool success = false;
  while (!success) {
    // Double the table size
    m = m * 2;
    
    // Update hash functions with new m
    h1_func = [m](int x) { return static_cast<size_t>(x) % m; };
    h2_func = [m](int x) { return (static_cast<size_t>(x) / m) % m; };
    
    table1.clear();
    table1.resize(m);
    table2.clear();
    table2.resize(m);

    success = true;
    // Try to reinsert all keys
    for (size_t key_idx = 0; key_idx < all_keys.size(); key_idx++) {
      int key = all_keys[key_idx];
      int current_key = key;
      int attempts = 0;
      const int max_attempts = 2 * m;
      bool inserted = false;

      while (attempts < max_attempts) {
        // Try to insert into table1
        size_t pos1 = h1_func(current_key);
        if (!table1[pos1].has_value()) {
          table1[pos1] = current_key;
          inserted = true;
          break;
        }

        // Evict from table1 and try table2
        int evicted = table1[pos1].value();
        table1[pos1] = current_key;
        current_key = evicted;
        attempts++;

        // Try to insert into table2
        size_t pos2 = h2_func(current_key);
        if (!table2[pos2].has_value()) {
          table2[pos2] = current_key;
          inserted = true;
          break;
        }

        // Evict from table2 and continue
        evicted = table2[pos2].value();
        table2[pos2] = current_key;
        current_key = evicted;
        attempts++;
      }

      if (!inserted) {
        // Failed to insert, need to collect all keys and try again with larger table
        std::set<int> keys_set(all_keys.begin(), all_keys.end());
        
        // Add the key that couldn't be inserted
        keys_set.insert(current_key);
        
        // Add all keys from the partially filled tables
        for (const auto& elem : table1) {
          if (elem.has_value()) {
            keys_set.insert(elem.value());
          }
        }
        for (const auto& elem : table2) {
          if (elem.has_value()) {
            keys_set.insert(elem.value());
          }
        }
        
        // Convert set back to vector (this eliminates duplicates)
        all_keys.assign(keys_set.begin(), keys_set.end());
        
        success = false;
        break; // Break from the for loop and restart with larger m
      }
    }
  }
}

CuckooHashTable::CuckooHashTable(size_t size)
    : m(size), table1(size), table2(size) {
  // Initialize hash functions
  // h1(x) = x mod m
  h1_func = [this](int x) { return static_cast<size_t>(x) % m; };
  // h2(x) = floor(x/m) mod m
  h2_func = [this](int x) { return (static_cast<size_t>(x) / m) % m; };
}

bool CuckooHashTable::insert(int key) {
  // Check if key already exists in either table
  if (search(key)) {
    return true; // Key already exists, insertion successful
  }

  int current_key = key;
  int attempts = 0;
  const int max_attempts = 2 * m;

  while (attempts < max_attempts) {
    // Try to insert into table1
    size_t pos1 = h1_func(current_key);
    if (!table1[pos1].has_value()) {
      table1[pos1] = current_key;
      return true;
    }

    // Evict from table1 and try table2
    int evicted = table1[pos1].value();
    table1[pos1] = current_key;
    current_key = evicted;
    attempts++;

    // Try to insert into table2
    size_t pos2 = h2_func(current_key);
    if (!table2[pos2].has_value()) {
      table2[pos2] = current_key;
      return true;
    }

    // Evict from table2 and continue
    evicted = table2[pos2].value();
    table2[pos2] = current_key;
    current_key = evicted;
    attempts++;
  }

  // Cycle detected, need to rehash
  // current_key contains a key that was evicted but couldn't be reinserted
  // We need to save it before rehashing
  std::vector<int> keys_to_preserve;
  keys_to_preserve.push_back(current_key);
  keys_to_preserve.push_back(key); // Also save the original key being inserted
  
  for (const auto& elem : table1) {
    if (elem.has_value()) {
      keys_to_preserve.push_back(elem.value());
    }
  }
  for (const auto& elem : table2) {
    if (elem.has_value()) {
      keys_to_preserve.push_back(elem.value());
    }
  }
  
  // Remove duplicates
  std::set<int> unique_keys(keys_to_preserve.begin(), keys_to_preserve.end());
  keys_to_preserve.assign(unique_keys.begin(), unique_keys.end());
  
  rehash_with_keys(m, table1, table2, h1_func, h2_func, keys_to_preserve);
  return search(key); // Check if key was successfully inserted during rehash
}

bool CuckooHashTable::search(int key) const {
  // Check both positions
  size_t pos1 = h1_func(key);
  if (table1[pos1].has_value() && table1[pos1].value() == key) {
    return true;
  }

  size_t pos2 = h2_func(key);
  if (table2[pos2].has_value() && table2[pos2].value() == key) {
    return true;
  }

  return false;
}

bool CuckooHashTable::remove(int key) {
  // Check table1
  size_t pos1 = h1_func(key);
  if (table1[pos1].has_value() && table1[pos1].value() == key) {
    table1[pos1].reset();
    return true;
  }

  // Check table2
  size_t pos2 = h2_func(key);
  if (table2[pos2].has_value() && table2[pos2].value() == key) {
    table2[pos2].reset();
    return true;
  }

  return false;
}

void CuckooHashTable::rehash() {
  // Save all existing keys
  std::vector<int> all_keys;
  for (const auto& elem : table1) {
    if (elem.has_value()) {
      all_keys.push_back(elem.value());
    }
  }
  for (const auto& elem : table2) {
    if (elem.has_value()) {
      all_keys.push_back(elem.value());
    }
  }
  
  rehash_with_keys(m, table1, table2, h1_func, h2_func, all_keys);
}
