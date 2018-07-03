#include <sys/ptrace.h>
#include <stdio.h>
#include <stdlib.h>
#include<unistd.h>

void cleanup_and_exit()
{
    exit(1);
}


int being_debugged()
{
    if(ptrace(PTRACE_TRACEME, 0, NULL, 0) < 0) {
        cleanup_and_exit();
    } else {
        printf("Something fishy\n");
        return 0;
    }
}


int main(int argc, char **argv)
{
    int i = 0;
    for(i = 0; i < 100; i++){
        if(being_debugged()) {
            printf("being debugged!\n");
        } else {
            printf("everything okay\n");
        }
        sleep(1);
    }

    return 0;
}
