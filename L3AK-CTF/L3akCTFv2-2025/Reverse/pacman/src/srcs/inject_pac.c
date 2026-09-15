#include "pacman.h"

uint64_t	add_sect_name(struct s_elf64 *elf)
{
	Elf64_Shdr	*symtab;
	uint64_t	off;

	symtab = elf->s_hdr + elf->e_hdr->e_shstrndx;
	off = symtab->sh_offset + symtab->sh_size;
	expand_elf_data(elf, off, S_NAME_LEN);
	elf->ptr = memcpy(elf->ptr + off, S_NAME, S_NAME_LEN - 1) - off;
	shift_offset(elf, off, S_NAME_LEN);
	symtab = elf->s_hdr + elf->e_hdr->e_shstrndx;
	symtab->sh_size += S_NAME_LEN;
	return (symtab->sh_size - S_NAME_LEN - 2);
}

void		prepare_s_data(struct s_elf64 *elf, char *s_data,
			Elf64_Shdr *text, uint32_t new)
{
	uint32_t	jmp;
	uint8_t		key[16];

	if (!text)
		exit_error(ERR_WELL_FORMED);
	if (generate_key(key) < 0)
		exit_error(ERR_UNKNOW);
	memcpy(s_data, &loader, g_loader_sz);
	jmp = elf->e_hdr->e_entry - new - g_loader_sz + 0x20;
	cpr_algo(elf->ptr + text->sh_offset, text->sh_size / 4, key);
	print_key(key);
	memcpy(s_data + g_loader_sz - 0x24, (char*)(&jmp), 4);
	memcpy(s_data + g_loader_sz - 0x20, (char*)key, 16);
	memcpy(s_data + g_loader_sz - 0x10, (char*)(&(text->sh_addr)), 8);
	memcpy(s_data + g_loader_sz - 0x8, (char*)(&(text->sh_size)), 4);
}

uint64_t	add_sect_content(struct s_elf64 *elf,
			Elf64_Phdr *exec_load, Elf64_Shdr *sect)
{
	uint64_t	off;
	char		*s_data;
	uint32_t	align;

	if (!(s_data = malloc(g_loader_sz)))
		exit_error(ERR_UNKNOW);
	align = exec_load->p_memsz - exec_load->p_filesz;
	off = sect->sh_offset;
	if (sect->sh_type != SHT_NOBITS)
		off += sect->sh_size;
	prepare_s_data(elf, s_data, get_sect_from_name(elf, ".text"),
	sect->sh_addr + sect->sh_size);
	expand_elf_data(elf, off, align + g_loader_sz);
	elf->ptr = memcpy(elf->ptr + off
	+ align, s_data, g_loader_sz) - off - align;
	shift_offset(elf, off, g_loader_sz + align);
	free(s_data);
	return (off + align);
}

Elf64_Shdr	fill_section(struct s_elf64 *elf, Elf64_Shdr new, Elf64_Phdr *exec_load)
{
	Elf64_Shdr	*sect;
	uint64_t	addr;

	if (!(sect = get_last_exec_load_sect(elf->s_hdr,
	elf->e_hdr->e_shnum, exec_load)))
		exit_error(ERR_UNKNOW);
	addr = sect->sh_addr + sect->sh_size;
	new.sh_offset = add_sect_content(elf, exec_load, sect);
	new.sh_name = add_sect_name(elf);
	new.sh_size = g_loader_sz;
	new.sh_addr = addr;
	elf->e_hdr->e_entry = addr;
	return (new);
}

Elf64_Shdr	*inject_section(struct s_elf64 *elf, Elf64_Shdr new, Elf64_Phdr *exec_load)
{
	Elf64_Shdr	*sect;
	uint64_t	off;

	if (!(sect = get_last_exec_load_sect(elf->s_hdr,
	elf->e_hdr->e_shnum, exec_load)))
		return (NULL);
	off = (char*)(++sect) - elf->ptr;
	expand_elf_data(elf, off, sizeof(Elf64_Shdr));
	elf->ptr = memcpy(elf->ptr + off,
	(char*)(&new), sizeof(Elf64_Shdr)) - off;
	shift_offset(elf, off, sizeof(Elf64_Shdr));
	exec_load->p_memsz += new.sh_size;
	exec_load->p_filesz = exec_load->p_memsz;
	set_pt_load_flags(elf->p_hdr, elf->e_hdr->e_phnum);
	elf->e_hdr->e_shnum++;
	return (sect);
}
