
#include "linear_probing.h"

LinearProbingHashTable::LinearProbingHashTable(size_t size, double thresholds)
    : m(size), table(size), deleted(size, false), thresholds(thresholds) {
  // TODO: Initialize hash function
}

double LinearProbingHashTable::load_factor() const {
  // TODO: Compute load factor
}

bool LinearProbingHashTable::insert(int key) {
  // TODO: Insert
}

bool LinearProbingHashTable::search(int key) const {
  // TODO: Search
}

bool LinearProbingHashTable::remove(int key) {
  // TODO: Remove
}

void LinearProbingHashTable::rehash() {
  // TODO: Rehash
}
