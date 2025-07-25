#include <iostream>

#include "TuringClient.h"



int main () {
    std::cout << "hello world" << std::endl;
    using namespace turingClient;
    TuringClient client("localhost");
}
