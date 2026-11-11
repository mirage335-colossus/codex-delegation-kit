	.file	"core.cpp"
# GNU C++17 (Debian 14.2.0-19) version 14.2.0 (x86_64-linux-gnu)
#	compiled by GNU C version 14.2.0, GMP version 6.3.0, MPFR version 4.2.1, MPC version 1.3.1, isl version isl-0.27-GMP

# warning: MPFR header version 4.2.1 differs from library version 4.2.2.
# GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072
# options passed: -mtune=generic -march=x86-64 -O2 -std=c++17 -fasynchronous-unwind-tables
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
.LCOLDB5:
	.section	.text.startup,"ax",@progbits
.LHOTB5:
	.p2align 4
	.globl	main
	.type	main, @function
main:
.LFB2032:
	.cfi_startproc
# core.cpp:16:   if (argc < 3 || argc > 4) return 2;
	leal	-3(%rdi), %eax	#, _2
# core.cpp:16:   if (argc < 3 || argc > 4) return 2;
	cmpl	$1, %eax	#, _2
	ja	.L46	#,
# core.cpp:15: int main(int argc, char** argv) {
	pushq	%r15	#
	.cfi_def_cfa_offset 16
	.cfi_offset 15, -16
# core.cpp:17:   const std::uint64_t frames = std::strtoull(argv[1], nullptr, 10);
	movl	$10, %edx	#,
# core.cpp:15: int main(int argc, char** argv) {
	pushq	%r14	#
	.cfi_def_cfa_offset 24
	.cfi_offset 14, -24
	pushq	%r13	#
	.cfi_def_cfa_offset 32
	.cfi_offset 13, -32
	pushq	%r12	#
	.cfi_def_cfa_offset 40
	.cfi_offset 12, -40
	pushq	%rbp	#
	.cfi_def_cfa_offset 48
	.cfi_offset 6, -48
	movq	%rsi, %rbp	# tmp365, argv
	pushq	%rbx	#
	.cfi_def_cfa_offset 56
	.cfi_offset 3, -56
	movl	%edi, %ebx	# tmp364, argc
	subq	$104, %rsp	#,
	.cfi_def_cfa_offset 160
# core.cpp:17:   const std::uint64_t frames = std::strtoull(argv[1], nullptr, 10);
	movq	8(%rsi), %rdi	# MEM[(char * *)argv_39(D) + 8B], MEM[(char * *)argv_39(D) + 8B]
	xorl	%esi, %esi	#
	call	__isoc23_strtoull@PLT	#
# core.cpp:18:   const std::uint64_t seed = std::strtoull(argv[2], nullptr, 10);
	movq	16(%rbp), %rdi	# MEM[(char * *)argv_39(D) + 16B], MEM[(char * *)argv_39(D) + 16B]
	movl	$10, %edx	#,
	xorl	%esi, %esi	#
# core.cpp:17:   const std::uint64_t frames = std::strtoull(argv[1], nullptr, 10);
	movq	%rax, %r12	# tmp366, frames
# core.cpp:18:   const std::uint64_t seed = std::strtoull(argv[2], nullptr, 10);
	call	__isoc23_strtoull@PLT	#
	movq	%rax, 16(%rsp)	# tmp367, %sfp
# core.cpp:19:   const bool audit = argc == 4 && std::string(argv[3]) == "--audit";
	cmpl	$4, %ebx	#, argc
	je	.L47	#,
# core.cpp:23:   if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;
	leaq	-1(%r12), %rax	#, _26
# core.cpp:23:   if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;
	cmpq	$499999, %rax	#, _26
	ja	.L11	#,
# core.cpp:27:   const std::uint64_t span = (frames - 1) * output_rate;
	imulq	$48000, %r12, %r12	#, frames, _12
# core.cpp:28:   const std::uint64_t outputs = (span + input_rate - 1) / input_rate;
	movl	$44100, %ecx	#, tmp346
	xorl	%edx, %edx	# tmp345
# core.cpp:19:   const bool audit = argc == 4 && std::string(argv[3]) == "--audit";
	movb	$0, 39(%rsp)	#, %sfp
# core.cpp:28:   const std::uint64_t outputs = (span + input_rate - 1) / input_rate;
	subq	$3901, %r12	#, _35
# core.cpp:28:   const std::uint64_t outputs = (span + input_rate - 1) / input_rate;
	movq	%r12, %rax	# _35, outputs
	divq	%rcx	# tmp346
	movq	%rax, 24(%rsp)	# outputs, %sfp
# core.cpp:30:   std::cout.precision(audit ? 17 : 9);
	movl	$9, %eax	#, iftmp.4_29
.L27:
# /usr/include/c++/14/ostream:179:       { return _M_insert(__n); }
	movq	24(%rsp), %rsi	# %sfp,
	leaq	_ZSt4cout(%rip), %rdi	#,
# /usr/include/c++/14/bits/ios_base.h:764:       _M_precision = __prec;
	movq	%rax, 16+_ZSt4cout(%rip)	# iftmp.4_29, MEM[(struct ios_base *)&cout + 8B]._M_precision
# /usr/include/c++/14/ostream:179:       { return _M_insert(__n); }
	call	_ZNSo9_M_insertImEERSoT_@PLT	#
	movb	$10, 64(%rsp)	#, MEM[(char *)_53]
	movq	%rax, %rdi	# tmp371, _48
# /usr/include/c++/14/ostream:581:       if (__out.width() != 0)
	movq	(%rax), %rax	# MEM[(struct basic_ostream *)_48]._vptr.basic_ostream, MEM[(struct basic_ostream *)_48]._vptr.basic_ostream
# /usr/include/c++/14/bits/ios_base.h:776:     { return _M_width; }
	movq	-24(%rax), %rax	# MEM[(long int *)_99 + -24B], MEM[(long int *)_99 + -24B]
# /usr/include/c++/14/ostream:581:       if (__out.width() != 0)
	cmpq	$0, 16(%rdi,%rax)	#, MEM[(const struct ios_base *)_102]._M_width
	jne	.L48	#,
# /usr/include/c++/14/ostream:583:       __out.put(__c);
	movl	$10, %esi	#,
	call	_ZNSo3putEc@PLT	#
.L14:
# core.cpp:32:   for (std::uint64_t k = 0; k < outputs; ++k) {
	cmpq	$44099, %r12	#, _35
	je	.L21	#,
# core.cpp:7:   std::uint64_t x = (frame + 1) * 6364136223846793005ULL +
	movabsq	$6364136223846793005, %rbp	#, tmp269
# core.cpp:32:   for (std::uint64_t k = 0; k < outputs; ++k) {
	xorl	%r14d, %r14d	# k
# core.cpp:32:   for (std::uint64_t k = 0; k < outputs; ++k) {
	xorl	%esi, %esi	# ivtmp.98
# core.cpp:37:       const double fraction = static_cast<double>(remainder) / output_rate;
	movq	%r14, %r15	# k, k
	jmp	.L15	#
	.p2align 4,,10
	.p2align 3
.L49:
# /usr/include/c++/14/ostream:582: 	return __ostream_insert(__out, &__c, 1);
	leaq	64(%rsp), %rsi	#, tmp302
	movl	$1, %edx	#,
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT	#
.L19:
	leal	1(%rbx), %eax	#, _11
# core.cpp:38:       for (int c = 0; c < channels; ++c) {
	movabsq	$1442695040888963407, %rbx	#, tmp403
	addq	%rbx, %r14	# tmp403, ivtmp.78
	movl	$1, %ebx	#, c
	cmpl	$2, %eax	#, _11
	jne	.L20	#,
.L44:
	movq	40(%rsp), %rsi	# %sfp, ivtmp.98
# core.cpp:32:   for (std::uint64_t k = 0; k < outputs; ++k) {
	movq	24(%rsp), %rax	# %sfp, outputs
# core.cpp:32:   for (std::uint64_t k = 0; k < outputs; ++k) {
	addq	$1, %r15	#, k
# core.cpp:32:   for (std::uint64_t k = 0; k < outputs; ++k) {
	addq	$44100, %rsi	#, ivtmp.98
	cmpq	%rax, %r15	# outputs, k
	jnb	.L21	#,
.L15:
# core.cpp:35:     const std::uint64_t remainder = position % output_rate;
	movabsq	$-5853766786057164379, %rax	#, tmp374
	movq	16(%rsp), %rbx	# %sfp, seed
	mulq	%rsi	# ivtmp.98
	movq	%rdx, %rax	# tmp249, _315
# core.cpp:34:     const std::uint64_t index = position / output_rate;
	shrq	$15, %rdx	#, index_54
# core.cpp:35:     const std::uint64_t remainder = position % output_rate;
	shrq	$15, %rax	#, _315
	imulq	$48000, %rax, %rcx	#, _315, tmp251
	movq	%rsi, %rax	# ivtmp.98, _315
	subq	%rcx, %rax	# tmp251, _315
# core.cpp:7:   std::uint64_t x = (frame + 1) * 6364136223846793005ULL +
	leaq	1(%rdx), %rcx	#, _316
	imulq	%rbp, %rcx	# tmp269, _317
	addq	%rbx, %rcx	# seed, _318
# core.cpp:36:     if (audit) {
	cmpb	$0, 39(%rsp)	#, %sfp
	je	.L16	#,
# core.cpp:37:       const double fraction = static_cast<double>(remainder) / output_rate;
	pxor	%xmm0, %xmm0	# _14
# core.cpp:38:       for (int c = 0; c < channels; ++c) {
	movq	%rsi, 40(%rsp)	# ivtmp.98, %sfp
# core.cpp:38:       for (int c = 0; c < channels; ++c) {
	xorl	%ebx, %ebx	# c
# core.cpp:10:   x *= 0x9e3779b97f4a7c15ULL;
	movabsq	$-7046029254386353131, %r13	#, tmp274
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	movabsq	$4835700860608086395, %r12	#, tmp278
# core.cpp:37:       const double fraction = static_cast<double>(remainder) / output_rate;
	cvtsi2sdq	%rax, %xmm0	# _315, _14
	movabsq	$4328085122666890221, %rax	#, tmp272
# core.cpp:37:       const double fraction = static_cast<double>(remainder) / output_rate;
	divsd	.LC2(%rip), %xmm0	#, _14
	leaq	(%rcx,%rax), %r14	#, ivtmp.78
	movsd	%xmm0, 8(%rsp)	# _14, %sfp
.L20:
# core.cpp:9:   x ^= x >> 29;
	movq	%r14, %rcx	# ivtmp.78, _132
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	pxor	%xmm1, %xmm1	# _140
	pxor	%xmm0, %xmm0	# _123
# core.cpp:9:   x ^= x >> 29;
	shrq	$29, %rcx	#, _132
# /usr/include/c++/14/ostream:232:       { return _M_insert(__f); }
	leaq	_ZSt4cout(%rip), %rdi	#,
# core.cpp:9:   x ^= x >> 29;
	xorq	%r14, %rcx	# ivtmp.78, x
# core.cpp:10:   x *= 0x9e3779b97f4a7c15ULL;
	imulq	%r13, %rcx	# tmp274, x
# core.cpp:11:   x ^= x >> 32;
	movq	%rcx, %rax	# x, _135
	shrq	$32, %rax	#, _135
# core.cpp:11:   x ^= x >> 32;
	xorq	%rax, %rcx	# _135, x_136
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	movq	%rcx, %rax	# x_136, tmp375
	mulq	%r12	# tmp278
	shrq	$19, %rdx	#, tmp276
	imulq	$2000001, %rdx, %rdx	#, tmp276, tmp279
	subq	%rdx, %rcx	# tmp279, _137
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	subl	$1000000, %ecx	#, _139
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	cvtsi2sdl	%ecx, %xmm1	# _139, _140
# core.cpp:7:   std::uint64_t x = (frame + 1) * 6364136223846793005ULL +
	leaq	(%r14,%rbp), %rcx	#, x
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	mulsd	.LC3(%rip), %xmm1	#, _141
# core.cpp:9:   x ^= x >> 29;
	movq	%rcx, %rax	# x, _115
	shrq	$29, %rax	#, _115
# core.cpp:9:   x ^= x >> 29;
	xorq	%rax, %rcx	# _115, x
# core.cpp:10:   x *= 0x9e3779b97f4a7c15ULL;
	imulq	%r13, %rcx	# tmp274, x
# core.cpp:11:   x ^= x >> 32;
	movq	%rcx, %rax	# x, _118
	shrq	$32, %rax	#, _118
# core.cpp:11:   x ^= x >> 32;
	xorq	%rax, %rcx	# _118, x_119
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	movq	%rcx, %rax	# x_119, tmp376
	mulq	%r12	# tmp278
	shrq	$19, %rdx	#, tmp287
	imulq	$2000001, %rdx, %rdx	#, tmp287, tmp290
	subq	%rdx, %rcx	# tmp290, _120
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	subl	$1000000, %ecx	#, _122
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	cvtsi2sdl	%ecx, %xmm0	# _122, _123
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	mulsd	.LC3(%rip), %xmm0	#, _124
# core.cpp:41:         std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
	subsd	%xmm1, %xmm0	# _141, _16
# core.cpp:41:         std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
	mulsd	8(%rsp), %xmm0	# %sfp, _17
# core.cpp:41:         std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
	addsd	%xmm1, %xmm0	# _141, _18
# /usr/include/c++/14/ostream:232:       { return _M_insert(__f); }
	call	_ZNSo9_M_insertIdEERSoT_@PLT	#
	movq	%rax, %rdi	# tmp372, _58
# core.cpp:41:         std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
	testl	%ebx, %ebx	# c
	je	.L30	#,
	movl	$10, %eax	#, prephitmp_314
	movl	$10, %esi	#, iftmp.5_30
.L17:
	movb	%al, 64(%rsp)	# prephitmp_314, MEM[(char *)_53]
# /usr/include/c++/14/ostream:581:       if (__out.width() != 0)
	movq	(%rdi), %rax	# MEM[(struct basic_ostream *)_58]._vptr.basic_ostream, MEM[(struct basic_ostream *)_58]._vptr.basic_ostream
# /usr/include/c++/14/bits/ios_base.h:776:     { return _M_width; }
	movq	-24(%rax), %rax	# MEM[(long int *)_143 + -24B], MEM[(long int *)_143 + -24B]
# /usr/include/c++/14/ostream:581:       if (__out.width() != 0)
	cmpq	$0, 16(%rdi,%rax)	#, MEM[(const struct ios_base *)_146]._M_width
	jne	.L49	#,
# /usr/include/c++/14/ostream:583:       __out.put(__c);
	call	_ZNSo3putEc@PLT	#
# /usr/include/c++/14/ostream:584:       return __out;
	jmp	.L19	#
.L47:
# core.cpp:19:   const bool audit = argc == 4 && std::string(argv[3]) == "--audit";
	movq	24(%rbp), %r14	# MEM[(char * *)argv_39(D) + 24B], _5
# /usr/include/c++/14/bits/basic_string.h:194: 	: allocator_type(__a), _M_p(__dat) { }
	leaq	80(%rsp), %rbp	#, _90
	leaq	64(%rsp), %r13	#, tmp358
	movq	%rbp, 64(%rsp)	# _90, MEM[(struct _Alloc_hider *)_53]._M_p
# /usr/include/c++/14/bits/basic_string.h:650: 	if (__s == 0)
	testq	%r14, %r14	# _5
	je	.L38	#,
# /usr/include/c++/14/bits/char_traits.h:391: 	return __builtin_strlen(__s);
	movq	%r14, %rdi	# _5,
	call	strlen@PLT	#
# /usr/include/c++/14/bits/basic_string.tcc:225: 	size_type __dnew = static_cast<size_type>(std::distance(__beg, __end));
	movq	%rax, 56(%rsp)	# tmp225, __dnew
# /usr/include/c++/14/bits/char_traits.h:391: 	return __builtin_strlen(__s);
	movq	%rax, %rbx	# tmp368, tmp225
# /usr/include/c++/14/bits/basic_string.tcc:227: 	if (__dnew > size_type(_S_local_capacity))
	cmpq	$15, %rax	#, tmp225
	ja	.L50	#,
# /usr/include/c++/14/bits/basic_string.h:432: 	if (__n == 1)
	cmpq	$1, %rax	#, tmp225
	jne	.L8	#,
# /usr/include/c++/14/bits/char_traits.h:350: 	__c1 = __c2;
	movzbl	(%r14), %eax	# MEM[(const char_type &)_5], _98
# /usr/include/c++/14/bits/char_traits.h:350: 	__c1 = __c2;
	movb	%al, 80(%rsp)	# _98, MEM[(char_type &)_53 + 16]
.L9:
# /usr/include/c++/14/bits/basic_string.tcc:251: 	_M_set_length(__dnew);
	movq	56(%rsp), %rax	# __dnew, __dnew.9_93
# /usr/include/c++/14/bits/char_traits.h:350: 	__c1 = __c2;
	movq	64(%rsp), %rdx	# MEM[(struct basic_string *)_53]._M_dataplus._M_p, MEM[(struct basic_string *)_53]._M_dataplus._M_p
# /usr/include/c++/14/bits/basic_string.h:223:       { _M_string_length = __length; }
	movq	%rax, 72(%rsp)	# __dnew.9_93, MEM[(struct basic_string *)_53]._M_string_length
# /usr/include/c++/14/bits/char_traits.h:350: 	__c1 = __c2;
	movb	$0, (%rdx,%rax)	#, MEM[(char_type &)_95]
# /usr/include/c++/14/bits/basic_string.h:3776: 	       && !_Traits::compare(__lhs.data(), __rhs, __lhs.size());
	cmpq	$7, 72(%rsp)	#, MEM[(struct basic_string *)_53]._M_string_length
	je	.L51	#,
# /usr/include/c++/14/bits/basic_string.h:809:       { _M_dispose(); }
	movq	%r13, %rdi	# tmp358,
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv@PLT	#
.L11:
# core.cpp:16:   if (argc < 3 || argc > 4) return 2;
	movl	$2, %eax	#, <retval>
.L1:
# core.cpp:56: }
	addq	$104, %rsp	#,
	.cfi_def_cfa_offset 56
	popq	%rbx	#
	.cfi_def_cfa_offset 48
	popq	%rbp	#
	.cfi_def_cfa_offset 40
	popq	%r12	#
	.cfi_def_cfa_offset 32
	popq	%r13	#
	.cfi_def_cfa_offset 24
	popq	%r14	#
	.cfi_def_cfa_offset 16
	popq	%r15	#
	.cfi_def_cfa_offset 8
	ret	
.L46:
	.cfi_restore 3
	.cfi_restore 6
	.cfi_restore 12
	.cfi_restore 13
	.cfi_restore 14
	.cfi_restore 15
# core.cpp:16:   if (argc < 3 || argc > 4) return 2;
	movl	$2, %eax	#, <retval>
# core.cpp:56: }
	ret	
.L48:
	.cfi_def_cfa_offset 160
	.cfi_offset 3, -56
	.cfi_offset 6, -48
	.cfi_offset 12, -40
	.cfi_offset 13, -32
	.cfi_offset 14, -24
	.cfi_offset 15, -16
# /usr/include/c++/14/ostream:582: 	return __ostream_insert(__out, &__c, 1);
	leaq	64(%rsp), %rsi	#, tmp248
	movl	$1, %edx	#,
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT	#
# /usr/include/c++/14/ostream:582: 	return __ostream_insert(__out, &__c, 1);
	jmp	.L14	#
	.p2align 4,,10
	.p2align 3
.L16:
# core.cpp:47:       const float fraction = static_cast<float>(remainder) / static_cast<float>(output_rate);
	pxor	%xmm0, %xmm0	# _19
# core.cpp:48:       for (int c = 0; c < channels; ++c) {
	movq	%rsi, 40(%rsp)	# ivtmp.98, %sfp
# core.cpp:48:       for (int c = 0; c < channels; ++c) {
	xorl	%ebx, %ebx	# c
# core.cpp:10:   x *= 0x9e3779b97f4a7c15ULL;
	movabsq	$-7046029254386353131, %r13	#, tmp308
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	movabsq	$4835700860608086395, %r12	#, tmp312
# core.cpp:47:       const float fraction = static_cast<float>(remainder) / static_cast<float>(output_rate);
	cvtsi2ssq	%rax, %xmm0	# _315, _19
	movabsq	$4328085122666890221, %rax	#, tmp306
# core.cpp:47:       const float fraction = static_cast<float>(remainder) / static_cast<float>(output_rate);
	divss	.LC4(%rip), %xmm0	#, _19
	leaq	(%rcx,%rax), %r14	#, ivtmp.90
	movss	%xmm0, 8(%rsp)	# _19, %sfp
.L25:
# core.cpp:9:   x ^= x >> 29;
	movq	%r14, %rcx	# ivtmp.90, _176
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	pxor	%xmm1, %xmm1	# _184
	pxor	%xmm0, %xmm0	# _167
# core.cpp:9:   x ^= x >> 29;
	shrq	$29, %rcx	#, _176
# /usr/include/c++/14/ostream:239: 	return _M_insert(static_cast<double>(__f));
	leaq	_ZSt4cout(%rip), %rdi	#,
# core.cpp:9:   x ^= x >> 29;
	xorq	%r14, %rcx	# ivtmp.90, x
# core.cpp:10:   x *= 0x9e3779b97f4a7c15ULL;
	imulq	%r13, %rcx	# tmp308, x
# core.cpp:11:   x ^= x >> 32;
	movq	%rcx, %rax	# x, _179
	shrq	$32, %rax	#, _179
# core.cpp:11:   x ^= x >> 32;
	xorq	%rax, %rcx	# _179, x_180
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	movq	%rcx, %rax	# x_180, tmp377
	mulq	%r12	# tmp312
	shrq	$19, %rdx	#, tmp310
	imulq	$2000001, %rdx, %rdx	#, tmp310, tmp313
	subq	%rdx, %rcx	# tmp313, _181
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	subl	$1000000, %ecx	#, _183
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	cvtsi2sdl	%ecx, %xmm1	# _183, _184
# core.cpp:7:   std::uint64_t x = (frame + 1) * 6364136223846793005ULL +
	leaq	(%r14,%rbp), %rcx	#, x
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	mulsd	.LC3(%rip), %xmm1	#, _185
# core.cpp:9:   x ^= x >> 29;
	movq	%rcx, %rax	# x, _159
	shrq	$29, %rax	#, _159
# core.cpp:9:   x ^= x >> 29;
	xorq	%rax, %rcx	# _159, x
# core.cpp:10:   x *= 0x9e3779b97f4a7c15ULL;
	imulq	%r13, %rcx	# tmp308, x
# core.cpp:49:         const float a = static_cast<float>(input_sample(index, c, seed));
	cvtsd2ss	%xmm1, %xmm1	# _185, a
# core.cpp:11:   x ^= x >> 32;
	movq	%rcx, %rax	# x, _162
	shrq	$32, %rax	#, _162
# core.cpp:11:   x ^= x >> 32;
	xorq	%rax, %rcx	# _162, x_163
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	movq	%rcx, %rax	# x_163, tmp378
	mulq	%r12	# tmp312
	shrq	$19, %rdx	#, tmp322
	imulq	$2000001, %rdx, %rdx	#, tmp322, tmp325
	subq	%rdx, %rcx	# tmp325, _164
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	subl	$1000000, %ecx	#, _166
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	cvtsi2sdl	%ecx, %xmm0	# _166, _167
# core.cpp:12:   return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
	mulsd	.LC3(%rip), %xmm0	#, _168
# core.cpp:50:         const float b = static_cast<float>(input_sample(index + 1, c, seed));
	cvtsd2ss	%xmm0, %xmm0	# _168, b_61
# core.cpp:51:         const float value = a + fraction * (b - a);
	subss	%xmm1, %xmm0	# a, _23
# core.cpp:51:         const float value = a + fraction * (b - a);
	mulss	8(%rsp), %xmm0	# %sfp, _24
# core.cpp:51:         const float value = a + fraction * (b - a);
	addss	%xmm1, %xmm0	# a, value_62
# /usr/include/c++/14/ostream:239: 	return _M_insert(static_cast<double>(__f));
	cvtss2sd	%xmm0, %xmm0	# value_62, _68
	call	_ZNSo9_M_insertIdEERSoT_@PLT	#
	movq	%rax, %rdi	# tmp373, _66
# core.cpp:52:         std::cout << value << (c ? '\n' : ' ');
	testl	%ebx, %ebx	# c
	je	.L31	#,
	movl	$10, %eax	#, prephitmp_313
	movl	$10, %esi	#, iftmp.6_31
.L22:
	movb	%al, 64(%rsp)	# prephitmp_313, MEM[(char *)_53]
# /usr/include/c++/14/ostream:581:       if (__out.width() != 0)
	movq	(%rdi), %rax	# MEM[(struct basic_ostream *)_66]._vptr.basic_ostream, MEM[(struct basic_ostream *)_66]._vptr.basic_ostream
# /usr/include/c++/14/bits/ios_base.h:776:     { return _M_width; }
	movq	-24(%rax), %rax	# MEM[(long int *)_187 + -24B], MEM[(long int *)_187 + -24B]
# /usr/include/c++/14/ostream:581:       if (__out.width() != 0)
	cmpq	$0, 16(%rdi,%rax)	#, MEM[(const struct ios_base *)_190]._M_width
	je	.L23	#,
# /usr/include/c++/14/ostream:582: 	return __ostream_insert(__out, &__c, 1);
	leaq	64(%rsp), %rsi	#, tmp339
	movl	$1, %edx	#,
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT	#
.L24:
# core.cpp:48:       for (int c = 0; c < channels; ++c) {
	movabsq	$1442695040888963407, %rsi	#, tmp413
	leal	1(%rbx), %eax	#, _148
	movl	$1, %ebx	#, c
	addq	%rsi, %r14	# tmp413, ivtmp.90
	cmpl	$2, %eax	#, _148
	jne	.L25	#,
	jmp	.L44	#
	.p2align 4,,10
	.p2align 3
.L23:
# /usr/include/c++/14/ostream:583:       __out.put(__c);
	call	_ZNSo3putEc@PLT	#
# /usr/include/c++/14/ostream:584:       return __out;
	jmp	.L24	#
	.p2align 4,,10
	.p2align 3
.L31:
	movl	$32, %eax	#, prephitmp_313
# core.cpp:52:         std::cout << value << (c ? '\n' : ' ');
	movl	$32, %esi	#, iftmp.6_31
	jmp	.L22	#
	.p2align 4,,10
	.p2align 3
.L30:
	movl	$32, %eax	#, prephitmp_314
# core.cpp:41:         std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
	movl	$32, %esi	#, iftmp.5_30
	jmp	.L17	#
.L21:
# core.cpp:56: }
	xorl	%eax, %eax	# <retval>
	jmp	.L1	#
.L8:
# /usr/include/c++/14/bits/char_traits.h:421: 	if (__n == 0)
	testq	%rax, %rax	# tmp225
	je	.L9	#,
	movq	%rbp, %rdi	# _90, _90
.L7:
# /usr/include/c++/14/bits/char_traits.h:427: 	return static_cast<char_type*>(__builtin_memcpy(__s1, __s2, __n));
	movq	%rbx, %rdx	# tmp225,
	movq	%r14, %rsi	# _5,
	call	memcpy@PLT	#
# /usr/include/c++/14/bits/char_traits.h:427: 	return static_cast<char_type*>(__builtin_memcpy(__s1, __s2, __n));
	jmp	.L9	#
.L51:
# /usr/include/c++/14/bits/char_traits.h:381: 	return __builtin_memcmp(__s1, __s2, __n);
	movq	64(%rsp), %rdi	# MEM[(struct basic_string *)_53]._M_dataplus._M_p,
	movl	$7, %edx	#,
	leaq	.LC1(%rip), %rsi	#, tmp239
	call	memcmp@PLT	#
# /usr/include/c++/14/bits/basic_string.h:809:       { _M_dispose(); }
	movq	%r13, %rdi	# tmp358,
# /usr/include/c++/14/bits/char_traits.h:381: 	return __builtin_memcmp(__s1, __s2, __n);
	movl	%eax, %ebx	# tmp370, tmp240
# /usr/include/c++/14/bits/basic_string.h:809:       { _M_dispose(); }
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv@PLT	#
# core.cpp:23:   if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;
	leaq	-1(%r12), %rax	#, _6
# core.cpp:23:   if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;
	cmpq	$499999, %rax	#, _6
	ja	.L11	#,
# core.cpp:23:   if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;
	testl	%ebx, %ebx	# tmp240
	jne	.L11	#,
# core.cpp:23:   if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;
	cmpq	$65536, %r12	#, frames
	ja	.L11	#,
# core.cpp:27:   const std::uint64_t span = (frames - 1) * output_rate;
	imulq	$48000, %r12, %r12	#, frames, _303
# core.cpp:28:   const std::uint64_t outputs = (span + input_rate - 1) / input_rate;
	movl	$44100, %ecx	#, tmp353
	xorl	%edx, %edx	# tmp352
	movb	$1, 39(%rsp)	#, %sfp
# core.cpp:28:   const std::uint64_t outputs = (span + input_rate - 1) / input_rate;
	subq	$3901, %r12	#, _35
# core.cpp:28:   const std::uint64_t outputs = (span + input_rate - 1) / input_rate;
	movq	%r12, %rax	# _35, outputs
	divq	%rcx	# tmp353
	movq	%rax, 24(%rsp)	# outputs, %sfp
# core.cpp:30:   std::cout.precision(audit ? 17 : 9);
	movl	$17, %eax	#, iftmp.4_29
	jmp	.L27	#
.L50:
# /usr/include/c++/14/bits/basic_string.tcc:229: 	    _M_data(_M_create(__dnew, size_type(0)));
	movq	%r13, %rdi	# tmp358,
	leaq	56(%rsp), %rsi	#, tmp227
	xorl	%edx, %edx	#
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@PLT	#
# /usr/include/c++/14/bits/basic_string.h:218:       { _M_dataplus._M_p = __p; }
	movq	%rax, 64(%rsp)	# _90, MEM[(struct basic_string *)_53]._M_dataplus._M_p
# /usr/include/c++/14/bits/basic_string.tcc:229: 	    _M_data(_M_create(__dnew, size_type(0)));
	movq	%rax, %rdi	# tmp369, _90
# /usr/include/c++/14/bits/basic_string.h:255:       { _M_allocated_capacity = __capacity; }
	movq	56(%rsp), %rax	# __dnew, __dnew
	movq	%rax, 80(%rsp)	# __dnew, MEM[(struct basic_string *)_53].D.27255._M_allocated_capacity
	jmp	.L7	#
	.cfi_endproc
	.section	.text.unlikely
	.cfi_startproc
	.type	main.cold, @function
main.cold:
.LFSB2032:
.L38:
	.cfi_def_cfa_offset 160
	.cfi_offset 3, -56
	.cfi_offset 6, -48
	.cfi_offset 12, -40
	.cfi_offset 13, -32
	.cfi_offset 14, -24
	.cfi_offset 15, -16
# /usr/include/c++/14/bits/basic_string.h:651: 	  std::__throw_logic_error(__N("basic_string: "
	leaq	.LC0(%rip), %rdi	#, tmp223
	call	_ZSt19__throw_logic_errorPKc@PLT	#
	.cfi_endproc
.LFE2032:
	.section	.text.startup
	.size	main, .-main
	.section	.text.unlikely
	.size	main.cold, .-main.cold
.LCOLDE5:
	.section	.text.startup
.LHOTE5:
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
	.ident	"GCC: (Debian 14.2.0-19) 14.2.0"
	.section	.note.GNU-stack,"",@progbits
