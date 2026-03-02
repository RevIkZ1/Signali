#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <signal.h>
#include <string.h>
int main(int argc,char* argv[])
{
  pid_t nit;
  int pd1[2],pd2[2];
  int status;
  if (pipe(pd1) == -1)
  {
    printf("Greska prilikom kreiranja prvog datavoda!\n");
    return -1;
  }
  if (pipe(pd2) == -1)
  {
    printf("Greska prilikom kreiranja drugog datavoda!\n");
    return -1;
  }
  if((nit=fork())==0)
  {
    close(pd1[1]);
    char naziv[255];
    char rec[255];
    read(pd1[0],&naziv,255);
    read(pd1[0],&rec,255);
    printf("%s\n",rec);
    execl(naziv,naziv,rec,NULL);
    close(pd1[0]);
    exit(0);
  }
  else
  {
    close(pd1[0]);
    write(pd1[1],argv[1],255);
    write(pd1[1],argv[2],255);
    close(pd1[1]);
    wait(&status);
    if (WIFEXITED(status)) {
        printf("Proces dete je izasao sa kodom: %d\n", WEXITSTATUS(status));
    }
  }
}
