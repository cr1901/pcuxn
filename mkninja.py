from gen.ninja_syntax import *
import os

with open("build.ninja", "w") as fp:
    writer = Writer(fp)

    # TODO: *nix support
    writer.variable("sh_wrap", "cmd /c")
    writer.variable("uxn_path", "..\\uxn")
    # write
    writer.newline()

    # TODO: MSVC support?
    writer.variable("host_cc", "gcc")
    writer.variable("host_cflags", "-O2 -Wall")
    writer.rule(name="host_cc", command="$host_cc $host_cflags -o $out -c $in")
    writer.rule(name="host_ld", command="$host_cc $host_cflags -o $out $in")
    writer.newline()

    writer.build("build/uxnasm.o", "host_cc", "$uxn_path/src/uxnasm.c")
    writer.build("out/uxnasm.exe", "host_ld", "build/uxnasm.o")
    writer.newline()

    writer.variable("wat_cc", "wcl")
    writer.variable("wat_modelchr", "c")
    writer.variable("wat_include", "-Isrc -I$uxn_path\\src")
    writer.variable("wat_cflags", "-0 -bt=dos -m$wat_modelchr $wat_include -q -s -oh -os")
    # TODO: *nix support
    writer.variable("wat_setenv", "C:\\WATCOM\\owsetenv.bat > NUL")
    writer.rule(name="wat_cc",
                command="$sh_wrap $wat_setenv && $wat_cc $wat_cflags -c -fo=$out $in",
                description="$wat_cc $wat_cflags -c -fo=$out $in")
    writer.rule(name="wat_ld",
                command="$sh_wrap $wat_setenv && $wat_cc $wat_cflags -fe=$out $in",
                description="$wat_cc $wat_cflags -fe=$out $in")
    writer.newline()

    writer.build("build/pcuxn.obj", "wat_cc", "src/pcuxn.c", implicit="src/uxn.h", implicit_outputs="pcuxn.err")
    writer.build("build/uxn.obj", "wat_cc", "src/uxn.c", # "$uxn_path/src/uxn.c", # variables={
        #     "wat_include" : "-I$uxn_path\\src"
        # },
        implicit="src/uxn.h",
        implicit_outputs="uxn.err")
    writer.build("out/pcuxn.exe", "wat_ld", ["build/pcuxn.obj", "build/uxn.obj"])
    writer.newline()

    writer.variable("uxnasm", "out/uxnasm.exe")
    writer.rule(name="uxn_rom", command="$uxnasm $in $out")
    writer.newline()

    writer.build("out/console.rom", "uxn_rom", "$uxn_path/projects/examples/devices/console.tal", implicit="out/uxnasm.exe")
    writer.build("out/echo.rom", "uxn_rom", "$uxn_path/projects/examples/devices/console.echo.tal", implicit="out/uxnasm.exe")
    writer.newline()

    # TODO: *nix support
    writer.variable("cp", "copy")
    writer.variable("patch", "patch")
    writer.rule("cp",
                command="$sh_wrap \"$cp $infile $outfile\"",
                description="Copy and $infile for wcl's include ($out)")
    # This rule will probably break if the cp succeeds, but the patch doesn't.
    writer.rule("cp_patch",
                command="$sh_wrap \"$cp $infile $outfile && $patch -Np1 < $patchfile\"",
                description="Copy and patching $infile for wcl ($out)")
    writer.newline()

    writer.build("src/uxn.c", "cp", "$uxn_path/src/uxn.c",
                 variables = {
                     # Use correct path separators.
                    "infile" : "$uxn_path\\src\\uxn.c",
                    "outfile" : "src\\uxn.c",
                 })
    writer.build("src/uxn.h", "cp_patch", ["$uxn_path/src/uxn.h", "src/uxn.h.diff"],
                 variables = {
                     # Use correct path separators.
                    "infile" : "$uxn_path\\src\\uxn.h",
                    "outfile" : "src\\uxn.h",
                    "patchfile" : "src\\uxn.h.diff"
                 })
