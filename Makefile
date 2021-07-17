include include.mk

MODELCHR=c
CC=wcl
CFLAGS=-0 -bt=dos -m$(MODELCHR) -Isrc -q -s -oh -os
LD=wlink
LDFLAGS=system dos option quiet option map=build/pcuxn.map

all: build/console.rom build/pcuxn.exe build/uxnasm.exe

# Main exes
build/pcuxn.exe: build/pcuxn.obj build/uxn.obj
	$(LD) $(LDFLAGS) name build/pcuxn.exe file { build/pcuxn.obj build/uxn.obj }

build/uxnasm.exe: $(UXN)/src/uxnasm.c
	gcc -O2 -o $@ $<

build/pcuxn.obj: src/pcuxn.c src/uxn.h
	$(CC) $(CFLAGS) -c -fo=$@ $<

build/uxn.obj: src/uxn.c src/uxn.h
	$(CC) $(CFLAGS) -c -fo=$@ $<

# Include path conflict... source directory is favored over mine
src/uxn.c: $(UXN)/src/uxn.c
	cp $(UXN)/src/uxn.c src

src/uxn.h: $(UXN)/src/uxn.h src/uxn.h.diff
	cp $(UXN)/src/uxn.h src
	patch -Np1 < src/uxn.h.diff

# Helper targets
clean:
	rm -rf build/*{.exe, .obj, .o, .map, .rom}

dosbox:
	dosbox-x -c "mount c build" -c "c:"

# Projects
build/console.rom: $(UXN)/projects/examples/devices/console.tal
	build/uxnasm.exe $< $@
