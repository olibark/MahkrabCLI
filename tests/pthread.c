#include <pthread.h>
#include <stdio.h>

void* thread_func(void* arg) {
    printf("Inside thread.\n");
    return NULL;
}

int main() {
    pthread_t thread;
    pthread_create(&thread, NULL, thread_func, NULL);
    pthread_join(thread, NULL);
    printf("Thread finished.\n");
    return 0;
}
