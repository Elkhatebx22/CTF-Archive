#include <err.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#define MAXTHREAD 10
#define CMDLEN 16
#define NAMELEN 32

unsigned int nthread;
pthread_t threads[MAXTHREAD];
pthread_t *curthread;

typedef struct printarg {
	unsigned int sleeptime;
	unsigned int ntimes;
	char *name;
	size_t len;
} printarg_t;

const char* title =
"  ▄████▄   ██░ ██  █    ██  ███▄    █  ██ ▄█▀▓██   ██▓▄▄▄█████▓ ██░ ██  ██▀███  ▓█████ ▄▄▄      ▓█████▄   ██████ \n"
" ▒██▀ ▀█  ▓██░ ██▒ ██  ▓██▒ ██ ▀█   █  ██▄█▒  ▒██  ██▒▓  ██▒ ▓▒▓██░ ██▒▓██ ▒ ██▒▓█   ▀▒████▄    ▒██▀ ██▌▒██    ▒ \n"
" ▒▓█    ▄ ▒██▀▀██░▓██  ▒██░▓██  ▀█ ██▒▓███▄░   ▒██ ██░▒ ▓██░ ▒░▒██▀▀██░▓██ ░▄█ ▒▒███  ▒██  ▀█▄  ░██   █▌░ ▓██▄   \n"
" ▒▓▓▄ ▄██▒░▓█ ░██ ▓▓█  ░██░▓██▒  ▐▌██▒▓██ █▄   ░ ▐██▓░░ ▓██▓ ░ ░▓█ ░██ ▒██▀▀█▄  ▒▓█  ▄░██▄▄▄▄██ ░▓█▄   ▌  ▒   ██▒\n"
" ▒ ▓███▀ ░░▓█▒░██▓▒▒█████▓ ▒██░   ▓██░▒██▒ █▄  ░ ██▒▓░  ▒██▒ ░ ░▓█▒░██▓░██▓ ▒██▒░▒████▒▓█   ▓██▒░▒████▓ ▒██████▒▒\n"
" ░ ░▒ ▒  ░ ▒ ░░▒░▒░▒▓▒ ▒ ▒ ░ ▒░   ▒ ▒ ▒ ▒▒ ▓▒   ██▒▒▒   ▒ ░░    ▒ ░░▒░▒░ ▒▓ ░▒▓░░░ ▒░ ░▒▒   ▓▒█░ ▒▒▓  ▒ ▒ ▒▓▒ ▒ ░\n"
"   ░  ▒    ▒ ░▒░ ░░░▒░ ░ ░ ░ ░░   ░ ▒░░ ░▒ ▒░ ▓██ ░▒░     ░     ▒ ░▒░ ░  ░▒ ░ ▒░ ░ ░  ░ ▒   ▒▒ ░ ░ ▒  ▒ ░ ░▒  ░ ░\n"
" ░         ░  ░░ ░ ░░░ ░ ░    ░   ░ ░ ░ ░░ ░  ▒ ▒ ░░    ░       ░  ░░ ░  ░░   ░    ░    ░   ▒    ░ ░  ░ ░  ░  ░  \n"
" ░ ░       ░  ░  ░   ░              ░ ░  ░    ░ ░               ░  ░  ░   ░        ░  ░     ░  ░   ░          ░  \n"
" ░                                            ░ ░                                            ░                   \n"
"parsing was never our strongest point. we're artists here.                                                       \n"
"one line per thread, timeouts, protections on. far. out. man. use it like:                                       \n"
"CHUNKS 3                                                                                                         \n"
"CHUNK 3 100 @@@@@@@@@@@@@    @@@@@@@@@@@     @@@@@@@@@@@@@@@@@@                                                  \n"
"CHUNK 2 100    ##########  #############     ###############                                                     \n"
"CHUNK 1 100       ####   ##################     #######                                                          \n";





const char *chonk = "\n" 
" .       . \n"
" |\_---_/|\n"
"/   o_o   \\\n"
"|    U    |\n"
"\\  ._I_.  /\n"
" `-_____-'\n"
"          \n"
"He is just a chonky boy,\n"
"that likes to play with threads.\n"
"He's the one the blue team lead,\n"
"cries about and dreads.\n"
"Root access? Easy as a sneeze\n"
"He purrs while cracking RSA keys\n"
"His belly jiggles as he types\n"
"connecting programs through his pipes\n"
"A chonky legend, round and wide\n"
"With kernel knowledge deep inside\n"
"He owns the net, he rules the stack\n"
"This fluffy, funky, hacker cat!\n";

printarg_t pa;

void *
print(void *arg)
{
	int cnt, sl;
	char name[64] = {0};
	printarg_t *pa = (printarg_t *) arg;
	cnt = pa->ntimes;
	sl = pa->sleeptime;
	memcpy(name, pa->name, pa->len);
	while (cnt--) {
		printf("%s\n", name);
		sleep(sl);
	}
	return NULL;
}

void
parsecmd(char *cmd, size_t len)
{
	char *err = NULL, *endp = NULL;
	unsigned int i;
	bzero(&pa, sizeof(printarg_t));
	if(strncmp(cmd, "CHUNKS ", 7) == 0) {
		nthread = (unsigned int) strtoul(cmd+7, NULL, 10);
		if (nthread < 0 || nthread > MAXTHREAD)
			errx(-1, "bad number of threads");
		printf("set nthread to %u\n", nthread);  
	} else if(strncmp(cmd, "CHUNK ", 5) == 0) { /* this is a bug with no impact. the strncmp should be at 6 to include space */
		if (nthread > 0) {
			/* will parse a command line CHUNK SLEEPTIME NTIMES THREADNAME. SLEETIME and NTIMES should be ints */
			pa.sleeptime = strtoul(cmd+6, &endp, 10);
			pa.ntimes = strtoul(endp+1, &endp, 10);
			pa.name = endp+1;
			pa.len = len - (endp+1-cmd);
			pthread_create(curthread++, NULL, print, (void *) &pa);
			nthread--;
		} else {
			printf("no threads remaining\n");
		}
	} else if(strncmp(cmd, "CHONK ", 5) == 0) {
		printf("%s\n", chonk);
	} else {
		printf("unknown command\n");
	}
}

int
main(int argc, char *argv[])
{
	setbuf(stdout, NULL);
	setbuf(stdin, NULL);
	size_t linelen = 0;
	int i = 0;
	char buf[1024] = {0};
	curthread = threads;
	printf("%s", title);
	while((linelen = read(0, buf, 1023)) != -1) {
		parsecmd(buf, linelen);
	}
	for(i=0; i< MAXTHREAD; i++)
		if(threads[i] != NULL)
			pthread_join(threads[i], NULL);
}
