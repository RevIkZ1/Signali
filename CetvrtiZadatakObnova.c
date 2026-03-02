#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <dirent.h>
#include <sys/stat.h>
struct fajl
{
    char ime[255];
    int velicina;
};
struct fajl najveci;
void processdir(char* foldername, int dubina)
{
    DIR* dp;
    struct dirent* dirp;
    int brfldr, brdat, brlnk;
    struct stat statbuf;
    int result;
    if(dubina>=3)
    {
        return;
    }
    if ((dp = opendir(foldername)) == NULL)
    {
        printf("Greska prilikom otvaranja foldera %s!\n", foldername);
        return;
    }

    while( (dirp = readdir(dp)) != NULL )
    {
        char tmp[1024] = "";
        strcat(tmp, foldername);
        strcat(tmp, "/");
        strcat(tmp, dirp->d_name);

        if ((result = stat(tmp, &statbuf)) == -1)
        {
            printf("Neuspesno citanje podataka o objektu: %s\n", tmp);
            continue;
        }

        if(S_ISREG(statbuf.st_mode))
        {
            if(najveci.velicina<statbuf.st_size)
            {
                strcpy(najveci.ime,dirp->d_name);
                najveci.velicina=statbuf.st_size;
                printf("Ime fajla: %s\n",najveci.ime);
                printf("Velicina fajla: %d\n",najveci.velicina);
            }
        }
        if (S_ISDIR(statbuf.st_mode)
        && strcmp(dirp->d_name, ".") != 0
        && strcmp(dirp->d_name, "..") != 0)
        {
            printf("Otvaram folder %s.\n", tmp);
            processdir(tmp, dubina+1);
        }
    }
    closedir(dp);
}
int main(int argc, char* argv[])
{
 if (argc != 2)
 {
    printf("Neophodna su dva argumenta (putanja do foldera i string koji se trazi)!\n");
    exit(1);
 }
 najveci.velicina=0;
 processdir(argv[1], 0);
 printf("Ime fajla: %s\n",najveci.ime);
 printf("Velicina fajla: %d\n",najveci.velicina);
}
