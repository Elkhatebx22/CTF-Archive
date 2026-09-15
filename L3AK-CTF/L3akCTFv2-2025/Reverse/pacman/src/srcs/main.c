#include "pacman.h"

void exit_error(const char *err)
{
	fprintf(stderr, "[ PACKER ] : %s\n", err);
	exit(EXIT_FAILURE);
}

int main(int argc, char **argv)
{
	struct s_file *file;

	if (argc != 2) {
		fprintf(stderr, "Usage: %s [ELF-64 EXECUTABLE]\n", argv[0]);
		return EXIT_FAILURE;
	}

	file = create_file(argv[1]);
	if (!file)
		exit_error(ERR_FILE);

	handle_file(file);
	destroy_file(file);

	return EXIT_SUCCESS;
}
