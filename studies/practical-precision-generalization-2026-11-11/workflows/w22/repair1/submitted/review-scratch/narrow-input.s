	.file	"narrow-input.cpp"
	.text
#APP
	.globl _ZSt21ios_base_library_initv
	.section	.rodata.str1.8,"aMS",@progbits,1
	.align 8
.LC0:
	.string	"basic_string: construction from null is not valid"
	.section	.rodata.str1.1,"aMS",@progbits,1
.LC1:
	.string	"--audit"
#NO_APP
	.section	.text.unlikely,"ax",@progbits
.LCOLDB6:
	.section	.text.startup,"ax",@progbits
.LHOTB6:
	.p2align 4
	.globl	main
	.type	main, @function
main:
.LFB2033:
	.cfi_startproc
	leal	-3(%rdi), %eax
	cmpl	$1, %eax
	ja	.L46
	pushq	%r15
	.cfi_def_cfa_offset 16
	.cfi_offset 15, -16
	movl	$10, %edx
	pushq	%r14
	.cfi_def_cfa_offset 24
	.cfi_offset 14, -24
	pushq	%r13
	.cfi_def_cfa_offset 32
	.cfi_offset 13, -32
	pushq	%r12
	.cfi_def_cfa_offset 40
	.cfi_offset 12, -40
	movq	%rsi, %r12
	pushq	%rbp
	.cfi_def_cfa_offset 48
	.cfi_offset 6, -48
	pushq	%rbx
	.cfi_def_cfa_offset 56
	.cfi_offset 3, -56
	movl	%edi, %ebx
	subq	$88, %rsp
	.cfi_def_cfa_offset 144
	movq	8(%rsi), %rdi
	xorl	%esi, %esi
	call	__isoc23_strtoull@PLT
	movq	16(%r12), %rdi
	movl	$10, %edx
	xorl	%esi, %esi
	movq	%rax, %rbp
	call	__isoc23_strtoull@PLT
	movq	%rax, 16(%rsp)
	cmpl	$4, %ebx
	je	.L47
	leaq	-1(%rbp), %rax
	cmpq	$499999, %rax
	ja	.L11
	movb	$0, 15(%rsp)
.L29:
	cmpq	$1, %rbp
	je	.L30
	imulq	$48000, %rbp, %rbp
	movl	$44100, %ecx
	xorl	%edx, %edx
	subq	$3901, %rbp
	movq	%rbp, %rax
	divq	%rcx
	movq	%rax, %rbp
.L12:
	cmpb	$0, 15(%rsp)
	movl	$9, %eax
	je	.L13
	movl	$17, %eax
.L13:
	leaq	_ZSt4cout(%rip), %rdi
	movq	%rbp, %rsi
	movq	%rax, 16+_ZSt4cout(%rip)
	call	_ZNSo9_M_insertImEERSoT_@PLT
	movb	$10, 48(%rsp)
	movq	%rax, %rdi
	movq	(%rax), %rax
	movq	-24(%rax), %rax
	cmpq	$0, 16(%rdi,%rax)
	je	.L14
	leaq	48(%rsp), %rsi
	movl	$1, %edx
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
.L15:
	testq	%rbp, %rbp
	je	.L23
	imulq	$44100, %rbp, %rax
	xorl	%ebx, %ebx
	movq	%rax, 24(%rsp)
	jmp	.L22
	.p2align 4,,10
	.p2align 3
.L48:
	leaq	48(%rsp), %rsi
	movl	$1, %edx
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
.L20:
	movabsq	$1442695040888963407, %rcx
	leal	1(%r12), %eax
	movl	$1, %r12d
	addq	%rcx, %r15
	cmpl	$2, %eax
	jne	.L21
.L28:
	addq	$44100, %rbx
	cmpq	%rbx, 24(%rsp)
	je	.L23
.L22:
	movabsq	$-5853766786057164379, %rax
	movq	16(%rsp), %rdi
	movabsq	$6364136223846793005, %rbp
	mulq	%rbx
	movq	%rdx, %rax
	shrq	$15, %rdx
	shrq	$15, %rax
	imulq	$48000, %rax, %rcx
	movq	%rbx, %rax
	subq	%rcx, %rax
	leaq	1(%rdx), %rcx
	imulq	%rbp, %rcx
	addq	%rdi, %rcx
	cmpb	$0, 15(%rsp)
	je	.L17
	pxor	%xmm0, %xmm0
	xorl	%r12d, %r12d
	movabsq	$-7046029254386353131, %r14
	movabsq	$4835700860608086395, %r13
	cvtsi2sdq	%rax, %xmm0
	divsd	.LC2(%rip), %xmm0
	movabsq	$4328085122666890221, %rax
	movsd	%xmm0, (%rsp)
	leaq	(%rcx,%rax), %r15
.L21:
	movq	%r15, %rsi
	pxor	%xmm1, %xmm1
	pxor	%xmm0, %xmm0
	shrq	$29, %rsi
	leaq	_ZSt4cout(%rip), %rdi
	xorq	%r15, %rsi
	imulq	%r14, %rsi
	movq	%rsi, %rax
	shrq	$32, %rax
	xorq	%rax, %rsi
	movq	%rsi, %rax
	mulq	%r13
	shrq	$19, %rdx
	imulq	$2000001, %rdx, %rdx
	subq	%rdx, %rsi
	subl	$1000000, %esi
	cvtsi2sdl	%esi, %xmm1
	leaq	(%r15,%rbp), %rsi
	mulsd	.LC3(%rip), %xmm1
	movq	%rsi, %rax
	shrq	$29, %rax
	xorq	%rax, %rsi
	imulq	%r14, %rsi
	movq	%rsi, %rax
	shrq	$32, %rax
	xorq	%rax, %rsi
	movq	%rsi, %rax
	mulq	%r13
	shrq	$19, %rdx
	imulq	$2000001, %rdx, %rdx
	subq	%rdx, %rsi
	subl	$1000000, %esi
	cvtsi2sdl	%esi, %xmm0
	mulsd	.LC3(%rip), %xmm0
	subsd	%xmm1, %xmm0
	mulsd	(%rsp), %xmm0
	addsd	%xmm1, %xmm0
	call	_ZNSo9_M_insertIdEERSoT_@PLT
	movq	%rax, %rdi
	testl	%r12d, %r12d
	je	.L32
	movl	$10, %eax
	movl	$10, %esi
.L18:
	movb	%al, 48(%rsp)
	movq	(%rdi), %rax
	movq	-24(%rax), %rax
	cmpq	$0, 16(%rdi,%rax)
	jne	.L48
	call	_ZNSo3putEc@PLT
	jmp	.L20
.L47:
	movq	24(%r12), %r14
	leaq	64(%rsp), %r12
	leaq	48(%rsp), %r13
	movq	%r12, 48(%rsp)
	testq	%r14, %r14
	je	.L41
	movq	%r14, %rdi
	call	strlen@PLT
	movq	%rax, 40(%rsp)
	movq	%rax, %rbx
	cmpq	$15, %rax
	ja	.L49
	cmpq	$1, %rax
	jne	.L8
	movzbl	(%r14), %eax
	movb	%al, 64(%rsp)
.L9:
	movq	40(%rsp), %rax
	movq	48(%rsp), %rdx
	movq	%rax, 56(%rsp)
	movb	$0, (%rdx,%rax)
	cmpq	$7, 56(%rsp)
	je	.L50
	movq	%r13, %rdi
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv@PLT
.L11:
	movl	$2, %eax
.L1:
	addq	$88, %rsp
	.cfi_def_cfa_offset 56
	popq	%rbx
	.cfi_def_cfa_offset 48
	popq	%rbp
	.cfi_def_cfa_offset 40
	popq	%r12
	.cfi_def_cfa_offset 32
	popq	%r13
	.cfi_def_cfa_offset 24
	popq	%r14
	.cfi_def_cfa_offset 16
	popq	%r15
	.cfi_def_cfa_offset 8
	ret
.L46:
	.cfi_restore 3
	.cfi_restore 6
	.cfi_restore 12
	.cfi_restore 13
	.cfi_restore 14
	.cfi_restore 15
	movl	$2, %eax
	ret
.L30:
	.cfi_def_cfa_offset 144
	.cfi_offset 3, -56
	.cfi_offset 6, -48
	.cfi_offset 12, -40
	.cfi_offset 13, -32
	.cfi_offset 14, -24
	.cfi_offset 15, -16
	xorl	%ebp, %ebp
	jmp	.L12
	.p2align 4,,10
	.p2align 3
.L17:
	pxor	%xmm0, %xmm0
	xorl	%r12d, %r12d
	movabsq	$-7046029254386353131, %r14
	movabsq	$4835700860608086395, %r13
	cvtsi2ssq	%rax, %xmm0
	divss	.LC4(%rip), %xmm0
	movabsq	$4328085122666890221, %rax
	movss	%xmm0, (%rsp)
	leaq	(%rcx,%rax), %r15
.L27:
	movq	%r15, %rsi
	pxor	%xmm1, %xmm1
	pxor	%xmm0, %xmm0
	shrq	$29, %rsi
	leaq	_ZSt4cout(%rip), %rdi
	xorq	%r15, %rsi
	imulq	%r14, %rsi
	movq	%rsi, %rax
	shrq	$32, %rax
	xorq	%rax, %rsi
	movq	%rsi, %rax
	mulq	%r13
	shrq	$19, %rdx
	imulq	$2000001, %rdx, %rdx
	subq	%rdx, %rsi
	subl	$1000000, %esi
	cvtsi2ssl	%esi, %xmm1
	leaq	(%r15,%rbp), %rsi
	mulss	.LC5(%rip), %xmm1
	movq	%rsi, %rax
	shrq	$29, %rax
	xorq	%rax, %rsi
	imulq	%r14, %rsi
	movq	%rsi, %rax
	shrq	$32, %rax
	xorq	%rax, %rsi
	movq	%rsi, %rax
	mulq	%r13
	shrq	$19, %rdx
	imulq	$2000001, %rdx, %rdx
	subq	%rdx, %rsi
	subl	$1000000, %esi
	cvtsi2ssl	%esi, %xmm0
	mulss	.LC5(%rip), %xmm0
	subss	%xmm1, %xmm0
	mulss	(%rsp), %xmm0
	addss	%xmm1, %xmm0
	cvtss2sd	%xmm0, %xmm0
	call	_ZNSo9_M_insertIdEERSoT_@PLT
	movq	%rax, %rdi
	testl	%r12d, %r12d
	je	.L33
	movl	$10, %eax
	movl	$10, %esi
.L24:
	movb	%al, 48(%rsp)
	movq	(%rdi), %rax
	movq	-24(%rax), %rax
	cmpq	$0, 16(%rdi,%rax)
	je	.L25
	leaq	48(%rsp), %rsi
	movl	$1, %edx
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
.L26:
	movabsq	$1442695040888963407, %rcx
	leal	1(%r12), %eax
	movl	$1, %r12d
	addq	%rcx, %r15
	cmpl	$2, %eax
	jne	.L27
	jmp	.L28
	.p2align 4,,10
	.p2align 3
.L25:
	call	_ZNSo3putEc@PLT
	jmp	.L26
	.p2align 4,,10
	.p2align 3
.L33:
	movl	$32, %eax
	movl	$32, %esi
	jmp	.L24
	.p2align 4,,10
	.p2align 3
.L32:
	movl	$32, %eax
	movl	$32, %esi
	jmp	.L18
.L23:
	xorl	%eax, %eax
	jmp	.L1
.L14:
	movl	$10, %esi
	call	_ZNSo3putEc@PLT
	jmp	.L15
.L8:
	testq	%rax, %rax
	je	.L9
	movq	%r12, %rdi
.L7:
	movq	%rbx, %rdx
	movq	%r14, %rsi
	call	memcpy@PLT
	jmp	.L9
.L50:
	movq	48(%rsp), %rdi
	movl	$7, %edx
	leaq	.LC1(%rip), %rsi
	call	memcmp@PLT
	movq	%r13, %rdi
	movl	%eax, %ebx
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv@PLT
	leaq	-1(%rbp), %rax
	cmpq	$499999, %rax
	ja	.L11
	testl	%ebx, %ebx
	jne	.L11
	cmpq	$65536, %rbp
	ja	.L11
	movb	$1, 15(%rsp)
	jmp	.L29
.L49:
	movq	%r13, %rdi
	leaq	40(%rsp), %rsi
	xorl	%edx, %edx
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@PLT
	movq	%rax, 48(%rsp)
	movq	%rax, %rdi
	movq	40(%rsp), %rax
	movq	%rax, 64(%rsp)
	jmp	.L7
	.cfi_endproc
	.section	.text.unlikely
	.cfi_startproc
	.type	main.cold, @function
main.cold:
.LFSB2033:
.L41:
	.cfi_def_cfa_offset 144
	.cfi_offset 3, -56
	.cfi_offset 6, -48
	.cfi_offset 12, -40
	.cfi_offset 13, -32
	.cfi_offset 14, -24
	.cfi_offset 15, -16
	leaq	.LC0(%rip), %rdi
	call	_ZSt19__throw_logic_errorPKc@PLT
	.cfi_endproc
.LFE2033:
	.section	.text.startup
	.size	main, .-main
	.section	.text.unlikely
	.size	main.cold, .-main.cold
.LCOLDE6:
	.section	.text.startup
.LHOTE6:
	.section	.rodata.cst8,"aM",@progbits,8
	.align 8
.LC2:
	.long	0
	.long	1088909312
	.align 8
.LC3:
	.long	-1598689907
	.long	1051772663
	.section	.rodata.cst4,"aM",@progbits,4
	.align 4
.LC4:
	.long	1195081728
	.align 4
.LC5:
	.long	897988541
	.ident	"GCC: (Debian 14.2.0-19) 14.2.0"
	.section	.note.GNU-stack,"",@progbits
