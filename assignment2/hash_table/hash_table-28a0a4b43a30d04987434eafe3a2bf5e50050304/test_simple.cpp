#include "include/cuckoo_hash.h"
#include <iostream>

int main() {
    CuckooHashTable ht(2);
    
    std::cout << "Test: Inserting 0-10..." << std::endl;
    for (int i = 0; i < 10; i++) {
        bool result = ht.insert(i);
        if (!result) {
            std::cout << "Failed to insert " << i << std::endl;
            return 1;
        }
    }
    
    std::cout << "\nSearching for 0-10..." << std::endl;
    int missing = 0;
    for (int i = 0; i < 10; i++) {
        bool found = ht.search(i);
        if (!found) {
            std::cout << "Key " << i << " NOT FOUND!" << std::endl;
            missing++;
        }
    }
    
    std::cout << "\nTotal missing keys: " << missing << std::endl;
    return missing;
}
