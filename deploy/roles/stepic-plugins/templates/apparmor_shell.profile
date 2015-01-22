#include <tunables/global>

{{ BASH_BIN }} {
    #include <abstractions/base>

    {{ ARENA_DIR }}/**                 r,

    set rlimit nproc <= 0, # forbid forking
    set rlimit as <= 1G,   # limit memory(address space)
}
