	push	rbp
	mov	rbp, rsp
	push	r12
	push	rbx
	sub	rsp, 80
	mov	BYTE PTR [rbp - 17], 1
	mov	rax, QWORD PTR [rip + 0x2CEA]
	mov	rdi, rax
	mov	eax, 0
	call	0x1010d0
	mov	rdx, QWORD PTR [rip + 0x2CF6]
	lea	rax, [rbp - 96]
	mov	esi, 64
	mov	rdi, rax
	call	0x1010e0
	movzx	eax, BYTE PTR [rbp - 87]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 96]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 84]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 83]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x10164a
	mov	esi, r12d
	mov	edi, eax
	call	0x1016c8
	mov	esi, ebx
	mov	edi, eax
	call	0x10153b
	cmp	eax, 4902
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 76]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 74]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 86]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 82]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x10164a
	mov	esi, r12d
	mov	edi, eax
	call	0x101401
	mov	esi, ebx
	mov	edi, eax
	call	0x1016c8
	cmp	eax, -64
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 94]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 84]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 86]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 89]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x1016c8
	mov	esi, r12d
	mov	edi, eax
	call	0x101401
	mov	esi, ebx
	mov	edi, eax
	call	0x101401
	cmp	eax, -71
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 85]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 80]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 89]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 76]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x1016c8
	mov	esi, r12d
	mov	edi, eax
	call	0x1015b8
	mov	esi, ebx
	mov	edi, eax
	call	0x10153b
	cmp	eax, 8930
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 89]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 81]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 88]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 95]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x10153b
	mov	esi, r12d
	mov	edi, eax
	call	0x1016c8
	mov	esi, ebx
	mov	edi, eax
	call	0x10153b
	cmp	eax, 278822
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 76]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 88]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 95]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 74]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x1016c8
	mov	esi, r12d
	mov	edi, eax
	call	0x1016c8
	mov	esi, ebx
	mov	edi, eax
	call	0x10164a
	cmp	eax, 115
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 95]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 85]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 76]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 78]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x10164a
	mov	esi, r12d
	mov	edi, eax
	call	0x101381
	mov	esi, ebx
	mov	edi, eax
	call	0x1016c8
	cmp	eax, 229
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 75]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 92]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 96]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 83]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x10153b
	mov	esi, r12d
	mov	edi, eax
	call	0x10153b
	mov	esi, ebx
	mov	edi, eax
	call	0x1015b8
	cmp	eax, 80
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 74]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 90]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 84]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 92]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x101381
	mov	esi, r12d
	mov	edi, eax
	call	0x1016c8
	mov	esi, ebx
	mov	edi, eax
	call	0x1016c8
	cmp	eax, 140
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 90]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 93]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 77]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 79]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x101401
	mov	esi, r12d
	mov	edi, eax
	call	0x1015b8
	mov	esi, ebx
	mov	edi, eax
	call	0x1015b8
	test	eax, eax
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 91]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 78]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 94]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 93]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x1016c8
	mov	esi, r12d
	mov	edi, eax
	call	0x101381
	mov	esi, ebx
	mov	edi, eax
	call	0x10153b
	cmp	eax, 6560
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 82]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 90]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 96]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 78]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x10153b
	mov	esi, r12d
	mov	edi, eax
	call	0x1015b8
	mov	esi, ebx
	mov	edi, eax
	call	0x101381
	cmp	eax, 64
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 91]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 92]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 94]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 94]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x1015b8
	mov	esi, r12d
	mov	edi, eax
	call	0x10164a
	mov	esi, ebx
	mov	edi, eax
	call	0x1015b8
	cmp	eax, 82
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 81]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 84]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 87]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 96]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x1016c8
	mov	esi, r12d
	mov	edi, eax
	call	0x10153b
	mov	esi, ebx
	mov	edi, eax
	call	0x101401
	cmp	eax, 1996
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 85]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 75]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 84]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 79]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x10153b
	mov	esi, r12d
	mov	edi, eax
	call	0x101381
	mov	esi, ebx
	mov	edi, eax
	call	0x1016c8
	cmp	eax, 8692
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 79]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 74]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 84]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 74]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x1015b8
	mov	esi, r12d
	mov	edi, eax
	call	0x101381
	mov	esi, ebx
	mov	edi, eax
	call	0x1016c8
	cmp	eax, 173
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 79]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 73]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 80]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 73]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x1016c8
	mov	esi, r12d
	mov	edi, eax
	call	0x1015b8
	mov	esi, ebx
	mov	edi, eax
	call	0x10153b
	cmp	eax, 105
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 75]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 95]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 96]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 94]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x101401
	mov	esi, r12d
	mov	edi, eax
	call	0x1015b8
	mov	esi, ebx
	mov	edi, eax
	call	0x101401
	cmp	eax, -65
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 94]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 96]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 74]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 82]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x10153b
	mov	esi, r12d
	mov	edi, eax
	call	0x1016c8
	mov	esi, ebx
	mov	edi, eax
	call	0x10153b
	cmp	eax, 475020
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 76]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 78]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 81]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 92]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x101401
	mov	esi, r12d
	mov	edi, eax
	call	0x10153b
	mov	esi, ebx
	mov	edi, eax
	call	0x101401
	cmp	eax, 859
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 95]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 91]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 88]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 95]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x101401
	mov	esi, r12d
	mov	edi, eax
	call	0x10153b
	mov	esi, ebx
	mov	edi, eax
	call	0x10153b
	cmp	eax, 12546
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 90]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 93]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 80]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 82]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x101401
	mov	esi, r12d
	mov	edi, eax
	call	0x101381
	mov	esi, ebx
	mov	edi, eax
	call	0x101401
	cmp	eax, -38
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 85]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 75]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 75]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 73]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x1016c8
	mov	esi, r12d
	mov	edi, eax
	call	0x1015b8
	mov	esi, ebx
	mov	edi, eax
	call	0x1015b8
	cmp	eax, 2
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 90]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 77]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 83]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 73]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x1015b8
	mov	esi, r12d
	mov	edi, eax
	call	0x101381
	mov	esi, ebx
	mov	edi, eax
	call	0x101401
	cmp	eax, 99
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 92]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 80]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 73]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 85]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x101381
	mov	esi, r12d
	mov	edi, eax
	call	0x1016c8
	mov	esi, ebx
	mov	edi, eax
	call	0x1016c8
	cmp	eax, 217
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 88]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 93]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 83]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 83]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x10153b
	mov	esi, r12d
	mov	edi, eax
	call	0x1016c8
	mov	esi, ebx
	mov	edi, eax
	call	0x101381
	cmp	eax, 13666
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 88]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 95]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 81]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 75]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x1015b8
	mov	esi, r12d
	mov	edi, eax
	call	0x1016c8
	mov	esi, ebx
	mov	edi, eax
	call	0x10164a
	cmp	eax, 113
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	movzx	eax, BYTE PTR [rbp - 85]
	movsx	ebx, al
	movzx	eax, BYTE PTR [rbp - 94]
	movsx	r12d, al
	movzx	eax, BYTE PTR [rbp - 81]
	movsx	edx, al
	movzx	eax, BYTE PTR [rbp - 82]
	movsx	eax, al
	mov	esi, edx
	mov	edi, eax
	call	0x1015b8
	mov	esi, r12d
	mov	edi, eax
	call	0x101401
	mov	esi, ebx
	mov	edi, eax
	call	0x1016c8
	cmp	eax, -96
	sete	al
	movzx	edx, al
	movzx	eax, BYTE PTR [rbp - 17]
	and	eax, edx
	test	eax, eax
	setne	al
	mov	BYTE PTR [rbp - 17], al
	cmp	BYTE PTR [rbp - 17], 0
	je	.L6
	mov	rax, QWORD PTR [rip + 0x2CFB]
	mov	rdi, rax
	call	0x1010a0
	jmp	.L7
.L6:
	mov	rax, QWORD PTR [rip + 0x2CF2]
	mov	rdi, rax
	call	0x1010a0
.L7:
	mov	eax, 0
	add	rsp, 80
	pop	rbx
	pop	r12
	pop	rbp
	ret