#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <ctype.h>
#include <semaphore.h>
sem_t sem1,sem2;
int broj;
void* funkcija(void *arg)
{
    while(1)
    {
        sem_wait(&sem2);
        if(broj==0)
            break;
        for(int i=broj;i>=0;i--)
        {
            printf("%d\n",i);
            sleep(1);
        }
        sem_post(&sem1);
    }
}
int main()
{
    pthread_t nit1;
    sem_init(&sem1,0,1);
    sem_init(&sem2,0,0);
    pthread_create(&nit1,NULL,funkcija,NULL);
    do
    {
        sem_wait(&sem1);
        printf("Unesi broj: ");
        scanf("%d",&broj);
        sem_post(&sem2);
    }while(broj!=0);
    pthread_join(nit1,NULL);
}