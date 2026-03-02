#include <stdio.h>
#include <stdlib.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/wait.h>
struct poruka{
  long tip;
  int broj;
};
int globzbir=0;
int zbirovi(int n) {
    int zbir = 0;
    if (n < 0) n = -n;
    while (n > 0) {
        zbir += n % 10;
        n /= 10;
    }
    globzbir+=zbir;
    return zbir;
}
int main()
{
  key_t key=ftok("red",65);
  int msgid=msgget(key,0666|IPC_CREAT);
  pid_t p1;
  struct poruka msg;
  if((p1=fork())==0)
  {
    for(int i=0;i<10;i++)
    {
        msgrcv(msgid,&msg,sizeof(msg)-sizeof(long),1,0);
        printf("Zbir brojeva je: %d\n",zbirovi(msg.broj));
        msg.tip=2;
        msgsnd(msgid,&msg,sizeof(msg)-sizeof(long),0);
    }
    exit(0);
  }
  for(int i=0;i<10;i++)
  {
    msg.tip=1;
    printf("Unesi broj: ");
    scanf("%d",&msg.broj);
    msgsnd(msgid,&msg,sizeof(msg)-sizeof(long),0);
    msgrcv(msgid,&msg,sizeof(msg)-sizeof(long),2,0);
  }
  wait(NULL);
  msgctl(msgid, IPC_RMID, NULL);
}