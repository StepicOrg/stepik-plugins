#include <stdio.h>

int main() {
    FILE *fp;
    fp = fopen("{{ SECRET_FILE }}", "r");
    if (fp == NULL) {
        fprintf(stderr, "Can't open input file\n");
        return -1;
    }
    char s[12];
    fgets(s, sizeof(s), fp);
    printf("%s", s);
}
