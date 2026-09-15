#include "pacman.h"

void	print_key(uint8_t *key)
{
	int	i;

	printf("key: ");
	i = 0;
	while (i < 16)
		printf("%02hhx ", key[i++]);
	printf("| %.16s\n", (char*)key);
}

int		generate_key(uint8_t *key)
{
	char	buf[16];
	int		fd;
	int		i;
	int		j;

	i = 0;
	if ((fd = open("/dev/urandom", 0)) < 0)
		exit_error(ERR_UNKNOW);
	while (i < 16 && read(fd, buf, 16) == 16)
	{
		j = 0;
		while (j < 16)
			if (isalnum(buf[j++]))
			{
				key[i++] = buf[--j];
				break ;
			}
	}
	close(fd);
	return (i == 16 ? 0 : -1);
}
