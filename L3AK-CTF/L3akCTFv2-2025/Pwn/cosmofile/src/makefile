# compiled with cosmocc version 4.0.2

# mkdir cosmocc
# wget https://cosmo.zip/pub/cosmocc/cosmo-4.0.2.zip
# cd cosmocc
# unzip cosmo-4.0.2.zip

CC = ./cosmocc/bin/cosmocc

all: cosmofile clean

cosmofile: cosmofile.c
	$(CC) -o cosmofile cosmofile.c
	mv cosmofile.com.dbg cosmofile

clean:
	rm -f cosmofile.aarch64.elf
