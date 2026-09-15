#include <stdio.h>
#include <stdlib.h>
#include <time.h>

char username[64];
int nhonks = 0;

const char thegoose[] = "\n\
                                                        _...--. \n\
                                        _____......----'     .' \n\
                                  _..-''                   .' \n\
                                .'                       ./ \n\
                        _.--._.'                       .' | \n\
                     .-'                           .-.'  / \n\
                   .'   _.-.                     .  \   ' \n\
                 .'  .'   .'    _    .-.        / `./  : \n\
               .'  .'   .'  .--' `.  |  \  |`. |     .' \n\
            _.'  .'   .' `.'       `-'   \ / |.'   .' \n\
         _.'  .-'   .'     `-.            `      .' \n\
       .'   .'    .'          `-.._ _ _ _ .-.    : \n\
      /    /o _.-'               .--'   .'   \   | \n\
    .'-.__..-'                  /..    .`    / .' \n\
  .'   . '                       /.'/.'     /  | \n\
 `---'                                   _.'   ' \n\
                                       /.'    .' \n\
                                        /.'/.' \n\
";

void
setuser()
{
	printf("Welcome to the goose game.\nHere you have to guess a-priori, how many HONKS you will receive from a very angry goose.\nGodspeed.\n");
	printf("How shall we call you?\n> ");
	scanf("%64s", username);
	return 0;
}

int
guess()
{
	int guess=0, i=0;
	printf("%s\n\nso %s. how many honks?", thegoose, username);
	scanf("%d", &guess); 
	printf("\n");
	for (i=0; i<nhonks; i++) {
		printf(" HONK ");
	}
	printf("\n");
	return (guess == nhonks);
}

void
highscore()
{
	char fstr[] = "wow %s you're so good. what message would you like to leave to the world?";
	char nam[32];
	char buf[128];
	char msg[128];
	printf("what's your name again?");
	scanf("%31s", nam);
	buf[31]=0;
	sprintf(buf, fstr, nam);
	printf(buf);
	read(0, msg, 1024);
	printf("got it. bye now.");
	return;
}

int 
main(int argc, char *argv[])
{
        setvbuf(stdout, NULL, _IONBF, 0);
        srand(time(NULL));
	setuser();
        nhonks = (rand() % 91) + 10;
	if (guess()) 
		highscore();
	 else 
		printf("tough luck. THE GOOSE WINS! GET THE HONK OUT!\n");
	return 0;
}
