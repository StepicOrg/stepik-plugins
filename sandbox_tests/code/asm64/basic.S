.text
    .global main
    .extern puts

main:
    pushq   %rbp
    movq    %rsp, %rbp
    leaq    stdout(%rip), %rdi
    callq   puts
    xorl    %eax, %eax
    popq    %rbp
    ret

.data
stdout:
    .asciz "42"
