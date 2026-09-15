#ifndef PACMAN_H
# define PACMAN_H

# include <ctype.h>
# include <elf.h>
# include <fcntl.h>
# include <stdio.h>
# include <stdlib.h>
# include <string.h>
# include <sys/mman.h>
# include <sys/stat.h>
# include <unistd.h>

# define ERROR		-1
# define SUCCESS	0

# define ELF_MAGIC	0x464c457f
# define ELF_CLASS	2
# define ELF_DATA	1
# define ELF_VERSION	1
# define ELF_OSABI	0
# define ELF_ABIVERSION	0

# define S_NAME		".pac"

# define ERR_FILE 			"Invalid file"
# define ERR_ARCH 			"Not an ELF file"
# define ERR_ARCH_SIZE 		"Not a 64bit file"
# define ERR_EXEC 			"Not an executable file"
# define ERR_WELL_FORMED	"Not well-formed"
# define ERR_NO_PIE			"This executable is not ET_EXEC but ET_DYN"
# define ERR_UNKNOW			"An error has occurred"

# define AR_ELF		0b00000001
# define AR_64		0b00000010
# define AR_32		0b00000100

# define S_NAME_LEN	strlen(S_NAME) + 1

# define NEW_LEN	S_NAME_LEN + sizeof(Elf64_Shdr);

void			loader(void);
extern uint32_t	g_loader_sz;

struct s_file
{
	uint8_t		arch;
	char		*filename;
	size_t		size;
	int64_t		free_size;
	char		*ptr;
};

struct s_elf64
{
	char		*ptr;
	size_t		size;
	int			free_size;
	Elf64_Ehdr	*e_hdr;
	Elf64_Phdr	*p_hdr;
	Elf64_Shdr	*s_hdr;
	char		*strtab;
};

void			shift_offset(struct s_elf64 *elf, uint64_t off, uint64_t size);
void			expand_elf_data(struct s_elf64 *elf, uint64_t off, uint64_t size);
Elf64_Shdr		*get_last_exec_load_sect(Elf64_Shdr *s_hdr,
				int shnum, Elf64_Phdr *exec_load);
Elf64_Phdr		*get_last_exec_load(Elf64_Phdr *p_hdr, int phnum);
Elf64_Shdr		*get_sect_from_name(struct s_elf64 *elf, char *name);
void			*get_strtab(struct s_elf64 *elf);
void			handle_elf64(struct s_elf64 *elf);
void			init_elf64(struct s_file *file,
				struct s_elf64 *elf, uint64_t len);
struct s_elf64	*create_elf64(struct s_file *file);
void			handle_file(struct s_file *file);
void			free_file(struct s_file *file);
struct s_file	*create_file(char *filename);
void			destroy_file(struct s_file *file);
void			get_elfmagic(char *magic);
uint8_t			get_arch(struct s_file *file);
int				init_file(struct s_file **file, char *filename);
uint64_t		add_sect_name(struct s_elf64 *elf);
void			prepare_s_data(struct s_elf64 *elf, char *s_data,
				Elf64_Shdr *text, uint32_t new);
uint64_t		add_sect_content(struct s_elf64 *elf,
				Elf64_Phdr *exec_load, Elf64_Shdr *sect);
Elf64_Shdr		fill_section(struct s_elf64 *elf,
				Elf64_Shdr new, Elf64_Phdr *exec_load);
Elf64_Shdr		*inject_section(struct s_elf64 *elf,
				Elf64_Shdr new, Elf64_Phdr *exec_load);
void			exit_error(const char *err);
int				main(int ac, char **av);
Elf64_Shdr		new_section(void);
void			set_pt_load_flags(Elf64_Phdr *p_hdr, int phnum);
Elf64_Shdr		*prepare_pac(struct s_elf64 *elf);
void			cpr_algo(void *text, size_t sz, uint8_t *key);
int				generate_key(uint8_t *key);
void			print_key(uint8_t *key);

#endif
