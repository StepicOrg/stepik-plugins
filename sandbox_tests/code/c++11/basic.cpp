#include <iostream>

int main() {
    auto f  = []() {
        std::cout << 42 << std::endl;
    };
    f();
}
