#include "include/cuckoo_hash.h"
#include <iostream>

int main() {
    CuckooHashTable ht(2);
    
    std::cout << "Inserting keys 0-5..." << std::endl;
    for (int i = 0; i < 6; i++) {
        std::cout << "Inserting " << i << "... ";
        bool result = ht.insert(i);
        std::cout << (result ? "OK" : "FAIL") << std::endl;
    }
    
    std::cout << "\nSearching for keys 0-5..." << std::endl;
    for (int i = 0; i < 6; i++) {
        bool found = ht.search(i);
        std::cout << "Key " << i << ": " << (found ? "FOUND" : "NOT FOUND") << std::endl;
    }
    
    return 0;
}
