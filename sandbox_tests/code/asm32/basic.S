.text
    .global main
    .extern puts

main:
    push %ebp
    mov  %esp, %ebp
    push $stdout
    call puts
    add  $4, %esp
    xor  %eax, %eax
    leave
    ret

.data
stdout:
    .asciz "42"
