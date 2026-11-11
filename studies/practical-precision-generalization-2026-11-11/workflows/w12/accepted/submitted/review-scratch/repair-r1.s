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
.LCOLDB6:
	.section	.text.startup,"ax",@progbits
.LHOTB6:
	.p2align 4
	.globl	main
	.type	main, @function
main:
.LFB2034:
	.cfi_startproc
# core.cpp:24:   if (argc < 3 || argc > 4) return 2;
	leal	-3(%rdi), %eax	#, _2
# core.cpp:24:   if (argc < 3 || argc > 4) return 2;
	cmpl	$1, %eax	#, _2
	ja	.L46	#,
# core.cpp:23: int main(int argc, char** argv) {
	pushq	%r15	#
	.cfi_def_cfa_offset 16
	.cfi_offset 15, -16
# core.cpp:25:   const std::uint64_t frames = std::strtoull(argv[1], nullptr, 10);
	movl	$10, %edx	#,
# core.cpp:23: int main(int argc, char** argv) {
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
	movq	%rsi, %rbp	# tmp364, argv
	pushq	%rbx	#
	.cfi_def_cfa_offset 56
	.cfi_offset 3, -56
	movl	%edi, %ebx	# tmp363, argc
	subq	$88, %rsp	#,
	.cfi_def_cfa_offset 144
# core.cpp:25:   const std::uint64_t frames = std::strtoull(argv[1], nullptr, 10);
	movq	8(%rsi), %rdi	# MEM[(char * *)argv_37(D) + 8B], MEM[(char * *)argv_37(D) + 8B]
	xorl	%esi, %esi	#
	call	__isoc23_strtoull@PLT	#
# core.cpp:26:   const std::uint64_t seed = std::strtoull(argv[2], nullptr, 10);
	movq	16(%rbp), %rdi	# MEM[(char * *)argv_37(D) + 16B], MEM[(char * *)argv_37(D) + 16B]
	movl	$10, %edx	#,
	xorl	%esi, %esi	#
# core.cpp:25:   const std::uint64_t frames = std::strtoull(argv[1], nullptr, 10);
	movq	%rax, %r12	# tmp365, frames
# core.cpp:26:   const std::uint64_t seed = std::strtoull(argv[2], nullptr, 10);
	call	__isoc23_strtoull@PLT	#
	movq	%rax, 8(%rsp)	# tmp366, %sfp
# core.cpp:27:   const bool audit = argc == 4 && std::string(argv[3]) == "--audit";
	cmpl	$4, %ebx	#, argc
	je	.L47	#,
# core.cpp:31:   if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;
	leaq	-1(%r12), %rax	#, _24
# core.cpp:31:   if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;
	cmpq	$499999, %rax	#, _24
	ja	.L11	#,
# core.cpp:35:   const std::uint64_t span = (frames - 1) * output_rate;
	imulq	$48000, %r12, %r12	#, frames, _12
# core.cpp:36:   const std::uint64_t outputs = (span + input_rate - 1) / input_rate;
	movl	$44100, %ecx	#, tmp342
	xorl	%edx, %edx	# tmp341
# core.cpp:27:   const bool audit = argc == 4 && std::string(argv[3]) == "--audit";
	movb	$0, 31(%rsp)	#, %sfp
# core.cpp:36:   const std::uint64_t outputs = (span + input_rate - 1) / input_rate;
	subq	$3901, %r12	#, _33
# core.cpp:36:   const std::uint64_t outputs = (span + input_rate - 1) / input_rate;
	movq	%r12, %rax	# _33, outputs
	divq	%rcx	# tmp342
	movq	%rax, 16(%rsp)	# outputs, %sfp
# core.cpp:38:   std::cout.precision(audit ? 17 : 9);
	movl	$9, %eax	#, iftmp.4_27
.L27:
# /usr/include/c++/14/ostream:179:       { return _M_insert(__n); }
	movq	16(%rsp), %rsi	# %sfp,
	leaq	_ZSt4cout(%rip), %rdi	#,
# /usr/include/c++/14/bits/ios_base.h:764:       _M_precision = __prec;
	movq	%rax, 16+_ZSt4cout(%rip)	# iftmp.4_27, MEM[(struct ios_base *)&cout + 8B]._M_precision
# /usr/include/c++/14/ostream:179:       { return _M_insert(__n); }
	call	_ZNSo9_M_insertImEERSoT_@PLT	#
	movb	$10, 48(%rsp)	#, MEM[(char *)_53]
	movq	%rax, %rdi	# tmp370, _47
# /usr/include/c++/14/ostream:581:       if (__out.width() != 0)
	movq	(%rax), %rax	# MEM[(struct basic_ostream *)_47]._vptr.basic_ostream, MEM[(struct basic_ostream *)_47]._vptr.basic_ostream
# /usr/include/c++/14/bits/ios_base.h:776:     { return _M_width; }
	movq	-24(%rax), %rax	# MEM[(long int *)_105 + -24B], MEM[(long int *)_105 + -24B]
# /usr/include/c++/14/ostream:581:       if (__out.width() != 0)
	cmpq	$0, 16(%rdi,%rax)	#, MEM[(const struct ios_base *)_108]._M_width
	jne	.L48	#,
# /usr/include/c++/14/ostream:583:       __out.put(__c);
	movl	$10, %esi	#,
	call	_ZNSo3putEc@PLT	#
.L14:
# core.cpp:40:   for (std::uint64_t k = 0; k < outputs; ++k) {
	xorl	%ebx, %ebx	# ivtmp.100
# core.cpp:40:   for (std::uint64_t k = 0; k < outputs; ++k) {
	xorl	%r13d, %r13d	# k
# core.cpp:40:   for (std::uint64_t k = 0; k < outputs; ++k) {
	cmpq	$44099, %r12	#, _33
	jne	.L15	#,
	jmp	.L21	#
	.p2align 4,,10
	.p2align 3
.L49:
# /usr/include/c++/14/ostream:582: 	return __ostream_insert(__out, &__c, 1);
	leaq	48(%rsp), %rsi	#, tmp300
	movl	$1, %edx	#,
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT	#
.L19:
# core.cpp:46:       for (int c = 0; c < channels; ++c) {
	movabsq	$1442695040888963407, %rcx	#, tmp392
	leal	1(%r12), %eax	#, _11
	movl	$1, %r12d	#, c
	addq	%rcx, %r14	# tmp392, ivtmp.80
	cmpl	$2, %eax	#, _11
	jne	.L20	#,
.L26:
# core.cpp:40:   for (std::uint64_t k = 0; k < outputs; ++k) {
	movq	16(%rsp), %rax	# %sfp, outputs
# core.cpp:40:   for (std::uint64_t k = 0; k < outputs; ++k) {
	addq	$1, %r13	#, k
# core.cpp:40:   for (std::uint64_t k = 0; k < outputs; ++k) {
	addq	$44100, %rbx	#, ivtmp.100
	cmpq	%rax, %r13	# outputs, k
	jnb	.L21	#,
.L15:
# core.cpp:43:     const std::uint64_t remainder = position % output_rate;
	movabsq	$-5853766786057164379, %rax	#, tmp373
	movq	8(%rsp), %rdi	# %sfp, seed
# core.cpp:7:   std::uint64_t x = (frame + 1) * 6364136223846793005ULL +
	movabsq	$6364136223846793005, %rbp	#, tmp267
# core.cpp:43:     const std::uint64_t remainder = position % output_rate;
	mulq	%rbx	# ivtmp.100
	movq	%rdx, %rax	# tmp247, _309
# core.cpp:42:     const std::uint64_t index = position / output_rate;
	shrq	$15, %rdx	#, index_54
# core.cpp:43:     const std::uint64_t remainder = position % output_rate;
	shrq	$15, %rax	#, _309
	imulq	$48000, %rax, %rcx	#, _309, tmp249
	movq	%rbx, %rax	# ivtmp.100, _309
	subq	%rcx, %rax	# tmp249, _309
# core.cpp:7:   std::uint64_t x = (frame + 1) * 6364136223846793005ULL +
	leaq	1(%rdx), %rcx	#, _310
	imulq	%rbp, %rcx	# tmp267, _311
	addq	%rdi, %rcx	# seed, _312
# core.cpp:44:     if (audit) {
	cmpb	$0, 31(%rsp)	#, %sfp
	je	.L16	#,
# core.cpp:45:       const double fraction = static_cast<double>(remainder) / output_rate;
	pxor	%xmm0, %xmm0	# _14
# core.cpp:46:       for (int c = 0; c < channels; ++c) {
	xorl	%r12d, %r12d	# c
# core.cpp:10:   x *= 0x9e3779b97f4a7c15ULL;
	movabsq	$-7046029254386353131, %r15	#, tmp272
# core.cpp:45:       const double fraction = static_cast<double>(remainder) / output_rate;
	cvtsi2sdq	%rax, %xmm0	# _309, _14
# core.cpp:45:       const double fraction = static_cast<double>(remainder) / output_rate;
	divsd	.LC2(%rip), %xmm0	#, _14
	movabsq	$4328085122666890221, %rax	#, tmp270
	movsd	%xmm0, (%rsp)	# _14, %sfp
	leaq	(%rcx,%rax), %r14	#, ivtmp.80
.L20:
# core.cpp:9:   x ^= x >> 29;
	movq	%r14, %rsi	# ivtmp.80, _136
# core.cpp:16:   return input_units(frame, channel, seed) * 0.000001;
	pxor	%xmm1, %xmm1	# _43
	pxor	%xmm0, %xmm0	# _63
# core.cpp:9:   x ^= x >> 29;
	shrq	$29, %rsi	#, _136
# /usr/include/c++/14/ostream:232:       { return _M_insert(__f); }
	leaq	_ZSt4cout(%rip), %rdi	#,
# core.cpp:9:   x ^= x >> 29;
	xorq	%r14, %rsi	# ivtmp.80, x
# core.cpp:10:   x *= 0x9e3779b97f4a7c15ULL;
	imulq	%r15, %rsi	# tmp272, x
# core.cpp:11:   x ^= x >> 32;
	movq	%rsi, %rax	# x, _139
	shrq	$32, %rax	#, _139
# core.cpp:11:   x ^= x >> 32;
	xorq	%rax, %rsi	# _139, x_140
# core.cpp:12:   return static_cast<int>(x % 2000001) - 1000000;
	movabsq	$4835700860608086395, %rax	#, tmp374
	mulq	%rsi	# x_140
	shrq	$19, %rdx	#, tmp274
	imulq	$2000001, %rdx, %rdx	#, tmp274, tmp277
	subq	%rdx, %rsi	# tmp277, _141
# core.cpp:12:   return static_cast<int>(x % 2000001) - 1000000;
	subl	$1000000, %esi	#, _143
# core.cpp:16:   return input_units(frame, channel, seed) * 0.000001;
	cvtsi2sdl	%esi, %xmm1	# _143, _43
# core.cpp:7:   std::uint64_t x = (frame + 1) * 6364136223846793005ULL +
	leaq	(%r14,%rbp), %rsi	#, x
# core.cpp:16:   return input_units(frame, channel, seed) * 0.000001;
	mulsd	.LC3(%rip), %xmm1	#, _69
# core.cpp:9:   x ^= x >> 29;
	movq	%rsi, %rax	# x, _121
	shrq	$29, %rax	#, _121
# core.cpp:9:   x ^= x >> 29;
	xorq	%rax, %rsi	# _121, x
# core.cpp:10:   x *= 0x9e3779b97f4a7c15ULL;
	imulq	%r15, %rsi	# tmp272, x
# core.cpp:11:   x ^= x >> 32;
	movq	%rsi, %rax	# x, _124
	shrq	$32, %rax	#, _124
# core.cpp:11:   x ^= x >> 32;
	xorq	%rax, %rsi	# _124, x_125
# core.cpp:12:   return static_cast<int>(x % 2000001) - 1000000;
	movabsq	$4835700860608086395, %rax	#, tmp375
	mulq	%rsi	# x_125
	shrq	$19, %rdx	#, tmp285
	imulq	$2000001, %rdx, %rdx	#, tmp285, tmp288
	subq	%rdx, %rsi	# tmp288, _126
# core.cpp:12:   return static_cast<int>(x % 2000001) - 1000000;
	subl	$1000000, %esi	#, _128
# core.cpp:16:   return input_units(frame, channel, seed) * 0.000001;
	cvtsi2sdl	%esi, %xmm0	# _128, _63
# core.cpp:16:   return input_units(frame, channel, seed) * 0.000001;
	mulsd	.LC3(%rip), %xmm0	#, _49
# core.cpp:49:         std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
	subsd	%xmm1, %xmm0	# _69, _16
# core.cpp:49:         std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
	mulsd	(%rsp), %xmm0	# %sfp, _17
# core.cpp:49:         std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
	addsd	%xmm1, %xmm0	# _69, _18
# /usr/include/c++/14/ostream:232:       { return _M_insert(__f); }
	call	_ZNSo9_M_insertIdEERSoT_@PLT	#
	movq	%rax, %rdi	# tmp371, _57
# core.cpp:49:         std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
	testl	%r12d, %r12d	# c
	je	.L30	#,
	movl	$10, %eax	#, prephitmp_308
	movl	$10, %esi	#, iftmp.5_28
.L17:
	movb	%al, 48(%rsp)	# prephitmp_308, MEM[(char *)_53]
# /usr/include/c++/14/ostream:581:       if (__out.width() != 0)
	movq	(%rdi), %rax	# MEM[(struct basic_ostream *)_57]._vptr.basic_ostream, MEM[(struct basic_ostream *)_57]._vptr.basic_ostream
# /usr/include/c++/14/bits/ios_base.h:776:     { return _M_width; }
	movq	-24(%rax), %rax	# MEM[(long int *)_145 + -24B], MEM[(long int *)_145 + -24B]
# /usr/include/c++/14/ostream:581:       if (__out.width() != 0)
	cmpq	$0, 16(%rdi,%rax)	#, MEM[(const struct ios_base *)_148]._M_width
	jne	.L49	#,
# /usr/include/c++/14/ostream:583:       __out.put(__c);
	call	_ZNSo3putEc@PLT	#
# /usr/include/c++/14/ostream:584:       return __out;
	jmp	.L19	#
.L47:
# core.cpp:27:   const bool audit = argc == 4 && std::string(argv[3]) == "--audit";
	movq	24(%rbp), %r14	# MEM[(char * *)argv_37(D) + 24B], _5
# /usr/include/c++/14/bits/basic_string.h:194: 	: allocator_type(__a), _M_p(__dat) { }
	leaq	64(%rsp), %rbp	#, _96
	leaq	48(%rsp), %r13	#, tmp354
	movq	%rbp, 48(%rsp)	# _96, MEM[(struct _Alloc_hider *)_53]._M_p
# /usr/include/c++/14/bits/basic_string.h:650: 	if (__s == 0)
	testq	%r14, %r14	# _5
	je	.L39	#,
# /usr/include/c++/14/bits/char_traits.h:391: 	return __builtin_strlen(__s);
	movq	%r14, %rdi	# _5,
	call	strlen@PLT	#
# /usr/include/c++/14/bits/basic_string.tcc:225: 	size_type __dnew = static_cast<size_type>(std::distance(__beg, __end));
	movq	%rax, 40(%rsp)	# tmp223, __dnew
# /usr/include/c++/14/bits/char_traits.h:391: 	return __builtin_strlen(__s);
	movq	%rax, %rbx	# tmp367, tmp223
# /usr/include/c++/14/bits/basic_string.tcc:227: 	if (__dnew > size_type(_S_local_capacity))
	cmpq	$15, %rax	#, tmp223
	ja	.L50	#,
# /usr/include/c++/14/bits/basic_string.h:432: 	if (__n == 1)
	cmpq	$1, %rax	#, tmp223
	jne	.L8	#,
# /usr/include/c++/14/bits/char_traits.h:350: 	__c1 = __c2;
	movzbl	(%r14), %eax	# MEM[(const char_type &)_5], _104
# /usr/include/c++/14/bits/char_traits.h:350: 	__c1 = __c2;
	movb	%al, 64(%rsp)	# _104, MEM[(char_type &)_53 + 16]
.L9:
# /usr/include/c++/14/bits/basic_string.tcc:251: 	_M_set_length(__dnew);
	movq	40(%rsp), %rax	# __dnew, __dnew.9_99
# /usr/include/c++/14/bits/char_traits.h:350: 	__c1 = __c2;
	movq	48(%rsp), %rdx	# MEM[(struct basic_string *)_53]._M_dataplus._M_p, MEM[(struct basic_string *)_53]._M_dataplus._M_p
# /usr/include/c++/14/bits/basic_string.h:223:       { _M_string_length = __length; }
	movq	%rax, 56(%rsp)	# __dnew.9_99, MEM[(struct basic_string *)_53]._M_string_length
# /usr/include/c++/14/bits/char_traits.h:350: 	__c1 = __c2;
	movb	$0, (%rdx,%rax)	#, MEM[(char_type &)_101]
# /usr/include/c++/14/bits/basic_string.h:3776: 	       && !_Traits::compare(__lhs.data(), __rhs, __lhs.size());
	cmpq	$7, 56(%rsp)	#, MEM[(struct basic_string *)_53]._M_string_length
	je	.L51	#,
# /usr/include/c++/14/bits/basic_string.h:809:       { _M_dispose(); }
	movq	%r13, %rdi	# tmp354,
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv@PLT	#
.L11:
# core.cpp:24:   if (argc < 3 || argc > 4) return 2;
	movl	$2, %eax	#, <retval>
.L1:
# core.cpp:64: }
	addq	$88, %rsp	#,
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
# core.cpp:24:   if (argc < 3 || argc > 4) return 2;
	movl	$2, %eax	#, <retval>
# core.cpp:64: }
	ret	
.L48:
	.cfi_def_cfa_offset 144
	.cfi_offset 3, -56
	.cfi_offset 6, -48
	.cfi_offset 12, -40
	.cfi_offset 13, -32
	.cfi_offset 14, -24
	.cfi_offset 15, -16
# /usr/include/c++/14/ostream:582: 	return __ostream_insert(__out, &__c, 1);
	leaq	48(%rsp), %rsi	#, tmp246
	movl	$1, %edx	#,
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT	#
# /usr/include/c++/14/ostream:582: 	return __ostream_insert(__out, &__c, 1);
	jmp	.L14	#
	.p2align 4,,10
	.p2align 3
.L16:
# core.cpp:55:       const float fraction = static_cast<float>(remainder) / static_cast<float>(output_rate);
	pxor	%xmm0, %xmm0	# _19
# core.cpp:56:       for (int c = 0; c < channels; ++c) {
	xorl	%r12d, %r12d	# c
# core.cpp:10:   x *= 0x9e3779b97f4a7c15ULL;
	movabsq	$-7046029254386353131, %r15	#, tmp306
# core.cpp:55:       const float fraction = static_cast<float>(remainder) / static_cast<float>(output_rate);
	cvtsi2ssq	%rax, %xmm0	# _309, _19
# core.cpp:55:       const float fraction = static_cast<float>(remainder) / static_cast<float>(output_rate);
	divss	.LC4(%rip), %xmm0	#, _19
	movabsq	$4328085122666890221, %rax	#, tmp304
	movss	%xmm0, (%rsp)	# _19, %sfp
	leaq	(%rcx,%rax), %r14	#, ivtmp.92
.L25:
# core.cpp:9:   x ^= x >> 29;
	movq	%r14, %rsi	# ivtmp.92, _176
# core.cpp:20:   return static_cast<float>(input_units(frame, channel, seed)) * 0.000001f;
	pxor	%xmm1, %xmm1	# _76
	pxor	%xmm0, %xmm0	# _73
# core.cpp:9:   x ^= x >> 29;
	shrq	$29, %rsi	#, _176
# /usr/include/c++/14/ostream:239: 	return _M_insert(static_cast<double>(__f));
	leaq	_ZSt4cout(%rip), %rdi	#,
# core.cpp:9:   x ^= x >> 29;
	xorq	%r14, %rsi	# ivtmp.92, x
# core.cpp:10:   x *= 0x9e3779b97f4a7c15ULL;
	imulq	%r15, %rsi	# tmp306, x
# core.cpp:11:   x ^= x >> 32;
	movq	%rsi, %rax	# x, _179
	shrq	$32, %rax	#, _179
# core.cpp:11:   x ^= x >> 32;
	xorq	%rax, %rsi	# _179, x_180
# core.cpp:12:   return static_cast<int>(x % 2000001) - 1000000;
	movabsq	$4835700860608086395, %rax	#, tmp376
	mulq	%rsi	# x_180
	shrq	$19, %rdx	#, tmp308
	imulq	$2000001, %rdx, %rdx	#, tmp308, tmp311
	subq	%rdx, %rsi	# tmp311, _181
# core.cpp:12:   return static_cast<int>(x % 2000001) - 1000000;
	subl	$1000000, %esi	#, _183
# core.cpp:20:   return static_cast<float>(input_units(frame, channel, seed)) * 0.000001f;
	cvtsi2ssl	%esi, %xmm1	# _183, _76
# core.cpp:7:   std::uint64_t x = (frame + 1) * 6364136223846793005ULL +
	leaq	(%r14,%rbp), %rsi	#, x
# core.cpp:20:   return static_cast<float>(input_units(frame, channel, seed)) * 0.000001f;
	mulss	.LC5(%rip), %xmm1	#, _77
# core.cpp:9:   x ^= x >> 29;
	movq	%rsi, %rax	# x, _161
	shrq	$29, %rax	#, _161
# core.cpp:9:   x ^= x >> 29;
	xorq	%rax, %rsi	# _161, x
# core.cpp:10:   x *= 0x9e3779b97f4a7c15ULL;
	imulq	%r15, %rsi	# tmp306, x
# core.cpp:11:   x ^= x >> 32;
	movq	%rsi, %rax	# x, _164
	shrq	$32, %rax	#, _164
# core.cpp:11:   x ^= x >> 32;
	xorq	%rax, %rsi	# _164, x_165
# core.cpp:12:   return static_cast<int>(x % 2000001) - 1000000;
	movabsq	$4835700860608086395, %rax	#, tmp377
	mulq	%rsi	# x_165
	shrq	$19, %rdx	#, tmp319
	imulq	$2000001, %rdx, %rdx	#, tmp319, tmp322
	subq	%rdx, %rsi	# tmp322, _166
# core.cpp:12:   return static_cast<int>(x % 2000001) - 1000000;
	subl	$1000000, %esi	#, _168
# core.cpp:20:   return static_cast<float>(input_units(frame, channel, seed)) * 0.000001f;
	cvtsi2ssl	%esi, %xmm0	# _168, _73
# core.cpp:20:   return static_cast<float>(input_units(frame, channel, seed)) * 0.000001f;
	mulss	.LC5(%rip), %xmm0	#, _74
# core.cpp:59:         const float value = a + fraction * (b - a);
	subss	%xmm1, %xmm0	# _77, _21
# core.cpp:59:         const float value = a + fraction * (b - a);
	mulss	(%rsp), %xmm0	# %sfp, _22
# core.cpp:59:         const float value = a + fraction * (b - a);
	addss	%xmm1, %xmm0	# _77, value_59
# /usr/include/c++/14/ostream:239: 	return _M_insert(static_cast<double>(__f));
	cvtss2sd	%xmm0, %xmm0	# value_59, _70
	call	_ZNSo9_M_insertIdEERSoT_@PLT	#
	movq	%rax, %rdi	# tmp372, _71
# core.cpp:60:         std::cout << value << (c ? '\n' : ' ');
	testl	%r12d, %r12d	# c
	je	.L31	#,
	movl	$10, %eax	#, prephitmp_307
	movl	$10, %esi	#, iftmp.6_29
.L22:
	movb	%al, 48(%rsp)	# prephitmp_307, MEM[(char *)_53]
# /usr/include/c++/14/ostream:581:       if (__out.width() != 0)
	movq	(%rdi), %rax	# MEM[(struct basic_ostream *)_71]._vptr.basic_ostream, MEM[(struct basic_ostream *)_71]._vptr.basic_ostream
# /usr/include/c++/14/bits/ios_base.h:776:     { return _M_width; }
	movq	-24(%rax), %rax	# MEM[(long int *)_185 + -24B], MEM[(long int *)_185 + -24B]
# /usr/include/c++/14/ostream:581:       if (__out.width() != 0)
	cmpq	$0, 16(%rdi,%rax)	#, MEM[(const struct ios_base *)_188]._M_width
	je	.L23	#,
# /usr/include/c++/14/ostream:582: 	return __ostream_insert(__out, &__c, 1);
	leaq	48(%rsp), %rsi	#, tmp335
	movl	$1, %edx	#,
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT	#
.L24:
# core.cpp:56:       for (int c = 0; c < channels; ++c) {
	movabsq	$1442695040888963407, %rcx	#, tmp402
	leal	1(%r12), %eax	#, _150
	movl	$1, %r12d	#, c
	addq	%rcx, %r14	# tmp402, ivtmp.92
	cmpl	$2, %eax	#, _150
	jne	.L25	#,
	jmp	.L26	#
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
	movl	$32, %eax	#, prephitmp_307
# core.cpp:60:         std::cout << value << (c ? '\n' : ' ');
	movl	$32, %esi	#, iftmp.6_29
	jmp	.L22	#
	.p2align 4,,10
	.p2align 3
.L30:
	movl	$32, %eax	#, prephitmp_308
# core.cpp:49:         std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
	movl	$32, %esi	#, iftmp.5_28
	jmp	.L17	#
.L21:
# core.cpp:64: }
	xorl	%eax, %eax	# <retval>
	jmp	.L1	#
.L8:
# /usr/include/c++/14/bits/char_traits.h:421: 	if (__n == 0)
	testq	%rax, %rax	# tmp223
	je	.L9	#,
	movq	%rbp, %rdi	# _96, _96
.L7:
# /usr/include/c++/14/bits/char_traits.h:427: 	return static_cast<char_type*>(__builtin_memcpy(__s1, __s2, __n));
	movq	%rbx, %rdx	# tmp223,
	movq	%r14, %rsi	# _5,
	call	memcpy@PLT	#
# /usr/include/c++/14/bits/char_traits.h:427: 	return static_cast<char_type*>(__builtin_memcpy(__s1, __s2, __n));
	jmp	.L9	#
.L51:
# /usr/include/c++/14/bits/char_traits.h:381: 	return __builtin_memcmp(__s1, __s2, __n);
	movq	48(%rsp), %rdi	# MEM[(struct basic_string *)_53]._M_dataplus._M_p,
	movl	$7, %edx	#,
	leaq	.LC1(%rip), %rsi	#, tmp237
	call	memcmp@PLT	#
# /usr/include/c++/14/bits/basic_string.h:809:       { _M_dispose(); }
	movq	%r13, %rdi	# tmp354,
# /usr/include/c++/14/bits/char_traits.h:381: 	return __builtin_memcmp(__s1, __s2, __n);
	movl	%eax, %ebx	# tmp369, tmp238
# /usr/include/c++/14/bits/basic_string.h:809:       { _M_dispose(); }
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv@PLT	#
# core.cpp:31:   if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;
	leaq	-1(%r12), %rax	#, _6
# core.cpp:31:   if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;
	cmpq	$499999, %rax	#, _6
	ja	.L11	#,
# core.cpp:31:   if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;
	testl	%ebx, %ebx	# tmp238
	jne	.L11	#,
# core.cpp:31:   if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;
	cmpq	$65536, %r12	#, frames
	ja	.L11	#,
# core.cpp:35:   const std::uint64_t span = (frames - 1) * output_rate;
	imulq	$48000, %r12, %r12	#, frames, _297
# core.cpp:36:   const std::uint64_t outputs = (span + input_rate - 1) / input_rate;
	movl	$44100, %ecx	#, tmp349
	xorl	%edx, %edx	# tmp348
	movb	$1, 31(%rsp)	#, %sfp
# core.cpp:36:   const std::uint64_t outputs = (span + input_rate - 1) / input_rate;
	subq	$3901, %r12	#, _33
# core.cpp:36:   const std::uint64_t outputs = (span + input_rate - 1) / input_rate;
	movq	%r12, %rax	# _33, outputs
	divq	%rcx	# tmp349
	movq	%rax, 16(%rsp)	# outputs, %sfp
# core.cpp:38:   std::cout.precision(audit ? 17 : 9);
	movl	$17, %eax	#, iftmp.4_27
	jmp	.L27	#
.L50:
# /usr/include/c++/14/bits/basic_string.tcc:229: 	    _M_data(_M_create(__dnew, size_type(0)));
	movq	%r13, %rdi	# tmp354,
	leaq	40(%rsp), %rsi	#, tmp225
	xorl	%edx, %edx	#
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@PLT	#
# /usr/include/c++/14/bits/basic_string.h:218:       { _M_dataplus._M_p = __p; }
	movq	%rax, 48(%rsp)	# _96, MEM[(struct basic_string *)_53]._M_dataplus._M_p
# /usr/include/c++/14/bits/basic_string.tcc:229: 	    _M_data(_M_create(__dnew, size_type(0)));
	movq	%rax, %rdi	# tmp368, _96
# /usr/include/c++/14/bits/basic_string.h:255:       { _M_allocated_capacity = __capacity; }
	movq	40(%rsp), %rax	# __dnew, __dnew
	movq	%rax, 64(%rsp)	# __dnew, MEM[(struct basic_string *)_53].D.27255._M_allocated_capacity
	jmp	.L7	#
	.cfi_endproc
	.section	.text.unlikely
	.cfi_startproc
	.type	main.cold, @function
main.cold:
.LFSB2034:
.L39:
	.cfi_def_cfa_offset 144
	.cfi_offset 3, -56
	.cfi_offset 6, -48
	.cfi_offset 12, -40
	.cfi_offset 13, -32
	.cfi_offset 14, -24
	.cfi_offset 15, -16
# /usr/include/c++/14/bits/basic_string.h:651: 	  std::__throw_logic_error(__N("basic_string: "
	leaq	.LC0(%rip), %rdi	#, tmp221
	call	_ZSt19__throw_logic_errorPKc@PLT	#
	.cfi_endproc
.LFE2034:
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
