
#include <llvm/BinaryFormat/ELF.h>

extern "C"
{
#include <stdlib.h>
#include <stdio.h>
#include <elf.h>
    int main(int argc, char **argv)
    {
        if (argc <= 1)
            return -1;
        FILE *fp = fopen(argv[1], "r+");
        Elf64_Ehdr teh;
        fread(&teh, sizeof(teh), 1, fp);
        fseek(fp, 0, SEEK_SET);

        if (teh.e_ident[EI_CLASS] == ELFCLASS64)
        {
            Elf64_Ehdr eh;
            fread(&eh, sizeof(eh), 1, fp);
            Elf64_Phdr *ph = (Elf64_Phdr *)malloc(eh.e_phnum * eh.e_phentsize);
            Elf64_Shdr *sh = (Elf64_Shdr *)malloc(eh.e_shnum * eh.e_shentsize);
            fseek(fp, eh.e_phoff, SEEK_SET);
            fread(ph, eh.e_phentsize, eh.e_phnum, fp);
            fseek(fp, eh.e_shoff, SEEK_SET);
            fread(sh, eh.e_shentsize, eh.e_shnum, fp);
            for (int i = 0; i < eh.e_phnum; i++)
            {
                if (ph[i].p_vaddr <= eh.e_entry && ph[i].p_vaddr + ph[i].p_memsz > eh.e_entry)
                {
                    fseek(fp, eh.e_phoff + i * eh.e_phentsize + offsetof(Elf64_Phdr, p_flags), SEEK_SET);
                    ph[i].p_flags |= PF_W;
                    fwrite(&ph[i].p_flags, sizeof(ph[i].p_flags), 1, fp);
                }
            }
            for (int i = 0; i < eh.e_shnum; i++)
            {
                if (sh[i].sh_addr <= eh.e_entry && sh[i].sh_addr + sh[i].sh_size > eh.e_entry)
                {
                    fseek(fp, eh.e_shoff + i * eh.e_shentsize + offsetof(Elf64_Shdr, sh_flags), SEEK_SET);
                    sh[i].sh_flags |= SHF_WRITE;
                    fwrite(&sh[i].sh_flags, sizeof(sh[i].sh_flags), 1, fp);
                }
            }
            free(ph);
            free(sh);
        }
        else
        {
            Elf32_Ehdr eh;
            fread(&eh, sizeof(eh), 1, fp);
            Elf32_Phdr *ph = (Elf32_Phdr *)malloc(eh.e_phnum * eh.e_phentsize);
            Elf32_Shdr *sh = (Elf32_Shdr *)malloc(eh.e_shnum * eh.e_shentsize);
            fseek(fp, eh.e_phoff, SEEK_SET);
            fread(ph, eh.e_phentsize, eh.e_phnum, fp);
            fseek(fp, eh.e_shoff, SEEK_SET);
            fread(sh, eh.e_shentsize, eh.e_shnum, fp);
            for (int i = 0; i < eh.e_phnum; i++)
            {
                if (ph[i].p_vaddr <= eh.e_entry && ph[i].p_vaddr + ph[i].p_memsz > eh.e_entry)
                {
                    fseek(fp, eh.e_phoff + i * eh.e_phentsize + offsetof(Elf32_Phdr, p_flags), SEEK_SET);
                    ph[i].p_flags |= PF_W;
                    fwrite(&ph[i].p_flags, sizeof(ph[i].p_flags), 1, fp);
                }
            }
            for (int i = 0; i < eh.e_shnum; i++)
            {
                if (sh[i].sh_addr <= eh.e_entry && sh[i].sh_addr + sh[i].sh_size > eh.e_entry)
                {
                    fseek(fp, eh.e_shoff + i * eh.e_shentsize + offsetof(Elf32_Shdr, sh_flags), SEEK_SET);
                    sh[i].sh_flags |= SHF_WRITE;
                    fwrite(&sh[i].sh_flags, sizeof(sh[i].sh_flags), 1, fp);
                }
            }
            free(ph);
            free(sh);
        }
        fflush(fp);
        fclose(fp);
        return 0;
    }
}
