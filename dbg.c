#include <sys/ptrace.h>
#include <stdio.h>
#include <stdlib.h>

char dummy_str[] = "This is a string";

void cleanup_and_exit()
{
    exit(1);
}


int being_debugged()
{
    if(ptrace(PTRACE_TRACEME, 0, NULL, 0) > 0) {
        cleanup_and_exit();
    } else {
        printf("Something fishy\n");
        return 0;
    }
}


int main(int argc, char **argv)
{
    if(being_debugged()) {
        printf("being debugged!\n");
    } else {
        printf("everything okay\n");
    }

    return 0;
}
