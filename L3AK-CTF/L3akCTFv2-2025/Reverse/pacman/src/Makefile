NAME			=	pacman
SHELL			=	/bin/bash

AC				=	nasm
CC				=	gcc
AFLAGS			=	-f elf64
CFLAGS			=	-g -Wall -Wextra -Werror

SRCS_DIR		=	srcs/
C_SRCS_LIST		=	expand_elf.c get_elf.c handle_elf.c key.c \
					handle_file.c inject_pac.c main.c prepare_pac.c utils.c
ASM_SRCS_LIST	=	loader.s cpr_algo.s
ASM_SRCS		=	$(addprefix $(SRCS_DIR), $(ASM_SRCS_LIST))
C_SRCS			=	$(addprefix $(SRCS_DIR), $(C_SRCS_LIST))

OBJS_DIR		=	objs/
OBJS_LIST		:=	$(patsubst %.c, %.o, $(C_SRCS_LIST)) $(patsubst %.s, %.o, $(ASM_SRCS_LIST))
OBJS			=	$(addprefix $(OBJS_DIR), $(OBJS_LIST))

HEADERS			=	-I ./includes -I ./includes/sys

.PHONY : all clean fclean re

all : $(NAME)

$(NAME) : $(OBJS)
	@$(CC) $(CFLAGS) $^ -o $@

$(OBJS_DIR)%.o : $(SRCS_DIR)%.c includes/*.h
	@mkdir -p $(OBJS_DIR)
	@$(CC) $(CFLAGS) $(HEADERS) -c $< -o $@

$(OBJS_DIR)%.o : $(SRCS_DIR)%.s includes/*.h
	@mkdir -p $(OBJS_DIR)
	@$(AC) $(AFLAGS) $< -o $@

clean :
	@rm -rf $(OBJS_DIR)

fclean : clean
	@rm -rf $(OBJS_DIR)
	@rm -rf $(NAME)

re : fclean all
