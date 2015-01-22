#include <tunables/global>

{{ OCTAVE_BIN }} {
	#include <abstractions/base>
	/usr/lib/**.oct	        rm,
	/usr/share/octave/**    rmix,
	/etc/passwd             r,
	/etc/inputrc            r,
	/etc/nsswitch.conf      r,

    {% for INSTANCE in INSTANCES %}
    {{ INSTANCE.ARENA_DIR }}/codejail-*/     r,
    {{ INSTANCE.ARENA_DIR }}/codejail-*/**   r,
    {% endfor %}
}
