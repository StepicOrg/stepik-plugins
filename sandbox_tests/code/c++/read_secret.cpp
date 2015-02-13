#include <iostream>
#include <fstream>
#include <string>

int main(){
    std::ifstream secret_file;
    secret_file.open("{{ SECRET_FILE }}");
    if(!secret_file.is_open())
        return -1;
    std::string s;
    getline(secret_file, s);
    std::cout << s;
    secret_file.close();
}
