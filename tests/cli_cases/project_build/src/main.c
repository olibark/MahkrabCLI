#include <stdio.h>

int main(void) {
  FILE *file = fopen("ran.txt", "w");
  if (file) {
    fputs("ran", file);
    fclose(file);
  }
  puts("ran");
  return 0;
}
