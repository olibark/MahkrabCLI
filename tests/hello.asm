section .data
    msg db "Hello, world!", 10    ; the string to print, 10 is the ASCII for newline
    msglen equ $ - msg           ; the length of the string

section .text
    global _start                ; declare _start as the entry point for the linker

_start:
    ; System call sys_write (syscall number 1)
    ; Registers for x86-64 Linux syscall convention:
    mov rax, 1                   ; syscall number for sys_write
    mov rdi, 1                   ; file descriptor 1 is stdout
    mov rsi, msg                 ; address of the string to write
    mov rdx, msglen              ; number of bytes to write
    syscall                      ; call the kernel

    ; System call sys_exit (syscall number 60)
    ; Registers for x86-64 Linux syscall convention:
    mov rax, 60                  ; syscall number for sys_exit
    xor rdi, rdi                 ; exit status 0 (successful)
    syscall                      ; call the kernel nasm -f elf64 -o hello_nasm.o hello_nasm.asm    ld -o hello hello_nasm.o 


;nasm -f elf64 -o build/$fileNameWithoutExt.o $fileName && ld -o build/$fileNameWithoutExt build/$fileNameWithoutExt.o && ./build/$fileNameWithoutExt