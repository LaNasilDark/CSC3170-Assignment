#include "include/cuckoo_hash.h"
#include <iostream>

void debug_tables(const CuckooHashTable& ht, const std::string& msg) {
    std::cout << "=== " << msg << " ===" << std::endl;
}

int main() {
    std::cout << "Creating hash table with size 2..." << std::endl;
    CuckooHashTable ht(2);
    
    std::cout << "\n--- Inserting keys 0-5 ---" << std::endl;
    for (int i = 0; i < 6; i++) {
        std::cout << "Inserting " << i << "... ";
        bool result = ht.insert(i);
        std::cout << (result ? "OK" : "FAIL") << std::endl;
    }
    
    std::cout << "\n--- Searching for keys 0-5 ---" << std::endl;
    int found_count = 0;
    for (int i = 0; i < 6; i++) {
        bool found = ht.search(i);
        std::cout << "Key " << i << ": " << (found ? "FOUND" : "NOT FOUND") << std::endl;
        if (found) found_count++;
    }
    
    std::cout << "\nTotal found: " << found_count << " / 6" << std::endl;
    
    return (found_count == 6) ? 0 : 1;
}
