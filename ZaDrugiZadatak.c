#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <signal.h>

int main(int argc,char* argv[])
{
    int broj=atoi(argv[1]);
    printf("Broj %d\n",broj);
}