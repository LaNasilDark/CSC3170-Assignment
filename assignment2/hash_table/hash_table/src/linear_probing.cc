
#include "linear_probing.h"

LinearProbingHashTable::LinearProbingHashTable(size_t size, double thresholds)
    : m(size), table(size), deleted(size, false), thresholds(thresholds) {
  // Initialize hash function: h(x) = x mod m
  h_func = [this](int x) { return static_cast<size_t>(x) % m; };
}

double LinearProbingHashTable::load_factor() const {
  // Count occupied slots (only entries that currently store a key)
  // Deleted slots are NOT counted
  size_t occupied = 0;
  for (const auto& elem : table) {
    if (elem.has_value()) {
      occupied++;
    }
  }
  return static_cast<double>(occupied) / m;
}

bool LinearProbingHashTable::insert(int key) {
  // Check if load factor exceeds threshold before insertion
  if (load_factor() >= thresholds) {
    rehash();
  }

  // Find position for insertion using linear probing
  size_t start_pos = h_func(key);
  size_t pos = start_pos;
  
  do {
    // If slot is empty or deleted, we can insert here
    if (!table[pos].has_value()) {
      table[pos] = key;
      deleted[pos] = false;
      return true;
    }
    
    // If key already exists, insertion is successful (duplicate allowed)
    if (table[pos].has_value() && table[pos].value() == key) {
      return true;
    }
    
    // Linear probing: move to next slot
    pos = (pos + 1) % m;
  } while (pos != start_pos);
  
  // Table is full (should not happen if rehashing works correctly)
  return false;
}

bool LinearProbingHashTable::search(int key) const {
  size_t start_pos = h_func(key);
  size_t pos = start_pos;
  
  do {
    // If slot is empty and not deleted, key doesn't exist
    if (!table[pos].has_value() && !deleted[pos]) {
      return false;
    }
    
    // If slot has the key, found it
    if (table[pos].has_value() && table[pos].value() == key) {
      return true;
    }
    
    // Continue probing (need to check deleted slots too)
    pos = (pos + 1) % m;
  } while (pos != start_pos);
  
  return false;
}

bool LinearProbingHashTable::remove(int key) {
  size_t start_pos = h_func(key);
  size_t pos = start_pos;
  
  do {
    // If slot is empty and not deleted, key doesn't exist
    if (!table[pos].has_value() && !deleted[pos]) {
      return false;
    }
    
    // If slot has the key, mark it as deleted (lazy deletion)
    if (table[pos].has_value() && table[pos].value() == key) {
      table[pos].reset();  // Clear the value
      deleted[pos] = true; // Mark as deleted
      return true;
    }
    
    // Continue probing
    pos = (pos + 1) % m;
  } while (pos != start_pos);
  
  return false;
}

void LinearProbingHashTable::rehash() {
  // Save all existing keys
  std::vector<int> all_keys;
  for (const auto& elem : table) {
    if (elem.has_value()) {
      all_keys.push_back(elem.value());
    }
  }
  
  // Double the table size
  m = m * 2;
  
  // Update hash function with new m
  h_func = [this](int x) { return static_cast<size_t>(x) % m; };
  
  // Resize tables and reset deleted flags
  table.clear();
  table.resize(m);
  deleted.clear();
  deleted.resize(m, false);
  
  // Reinsert all keys
  for (int key : all_keys) {
    size_t pos = h_func(key);
    
    // Find an empty slot using linear probing
    while (table[pos].has_value()) {
      pos = (pos + 1) % m;
    }
    
    table[pos] = key;
    deleted[pos] = false;
  }
}
