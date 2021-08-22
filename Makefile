include include.mk

MODELCHR=c
CC=wcl
CFLAGS=-0 -bt=dos -m$(MODELCHR) -Isrc -q -s -oh -os
LD=wlink
LDFLAGS=system dos option quiet option map=build/pcuxn.map

all: build/console.rom build/echo.rom build/pcuxn.exe build/uxnasm.exe

# Main exes
build/pcuxn.exe: build/pcuxn.obj build/uxn.obj build/doswrap.obj
	$(LD) $(LDFLAGS) option map=build/pcuxn.map name $@ file { $^ }

build/uxnasm.exe: $(UXN)/src/uxnasm.c
	gcc -O2 -o $@ $<

build/%.obj: src/%.c src/uxn.h
	$(CC) $(CFLAGS) -c -fo=$@ $<

# Include path conflict... source directory is favored over mine
src/uxn.c: $(UXN)/src/uxn.c
	cp $(UXN)/src/uxn.c src

src/uxn.h: $(UXN)/src/uxn.h src/uxn.h.diff
	cp $(UXN)/src/uxn.h src
	patch -Np1 < src/uxn.h.diff

# Helper targets
clean:
	rm -rf build/*.exe build/*.obj build/*.o  build/*.map build/*.rom

dosbox:
	dosbox-x -c "mount c build" -c "c:"

# Projects
build/console.rom: $(UXN)/projects/examples/devices/console.tal build/uxnasm.exe
	build/uxnasm.exe $< $@

build/echo.rom: $(UXN)/projects/examples/devices/console.echo.tal build/uxnasm.exe
	build/uxnasm.exe $< $@
