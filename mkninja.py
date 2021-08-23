import argparse
import os
import platform

from gen.ninja_syntax import *

def configure(user_vars):
    pass

def write_ninja(user_vars):
    # Let's avoid mixed slashes altogether (MSYS2 Python inside bash prompt).
    def np(path):
        return os.path.normpath(path).replace("/", "\\")

    with open("build.ninja", "w") as fp:
        writer = Writer(fp)

        if platform.system() == "Windows":
            writer.variable("sh_wrap", "cmd /c")
            writer.variable("null", "NUL")
            writer.variable("cp", "copy")
        else:
            writer.variable("sh_wrap", "sh -c")
            writer.variable("null", "/dev/null")
            writer.variable("cp", "cp")
        writer.variable("uxn_path", np(os.path.abspath(user_vars.uxn)))
        writer.newline()

        # TODO: MSVC support?
        writer.variable("host_cc", "gcc")
        writer.variable("host_cflags", "-O2 -Wall -Wno-unknown-pragmas")
        writer.rule("host_cc", "$host_cc $host_cflags -o $out -c $in")
        writer.rule("host_ld", "$host_cc $host_cflags -o $out $in")
        writer.newline()

        writer.build(np("build/uxnasm.o"), "host_cc", np("$uxn_path/src/uxnasm.c"))
        writer.build(np("out/uxnasm.exe"), "host_ld", np("build/uxnasm.o"))
        writer.newline()

        writer.variable("wat_cc", "wcl")
        writer.variable("wat_ld", "wlink")
        writer.variable("wat_modelchr", user_vars.memmodel)
        writer.variable("wat_include", "-Isrc") # -I$uxn_path\\src")
        writer.comment("Avoid error files (fr) until I can figure out how to do conditional implicit outputs.")
        writer.variable("wat_cflags", "-0 -bt=dos -m$wat_modelchr -q -s -oh -os -fr=")
        writer.variable("wat_ldflags", "system dos option quiet")
        if platform.system() == "Windows":
            writer.variable("wat_setenv", "{} > $null".format(np(os.path.join(user_vars.watcom, "owsetenv.bat"))))
        else:
            writer.variable("wat_setenv", ". {} > $null".format(np(os.path.join(user_vars.watcom, "owsetenv.sh"))))
        writer.rule("wat_cc", "$sh_wrap $wat_setenv && $wat_cc $wat_cflags $wat_include -c -ad=$depfile -add=$in -adt=$out -fo=$out $in",
                    description="$wat_cc $wat_cflags $wat_include -c -ad=$depfile -add=$in -adt=$out -fo=$out $in")
        writer.rule("wat_ld_map", "$sh_wrap $wat_setenv && $wat_ld $wat_ldflags option map=$mapfile name $outfile file { $in }",
                    description="$wat_ld $wat_ldflags option map=$mapfile name $outfile file { $in }")
        writer.newline()

        writer.build(np("build/pcuxn.obj"), "wat_cc", np("src/pcuxn.c"),
                     implicit=np("src/uxn.h"),
                     variables={
                        "depfile" : np("build/pcuxn.d")
                     }) #, implicit_outputs="pcuxn.err")
        # TODO: Try np("$uxn_path/src/uxn.c") eventually? If include file handling behaves...
        writer.build(np("build/uxn.obj"), "wat_cc", np("src/uxn.c"),
                     implicit=np("src/uxn.h"),
                     variables={
                        "depfile" : np("build/uxn.d"),
                        # "wat_include" : "-I$uxn_path\\src"
                     }) #, implicit_outputs="uxn.err")
        writer.build(np("build/doswrap.obj"), "wat_cc", np("src/doswrap.c"),
                     variables={
                        "depfile" : np("build/doswrap.d"),
                     }) #, implicit_outputs="doswrap.err")
        writer.build(np("build/console.obj"), "wat_cc", np("src/devices/console.c"),
                     variables={
                        "depfile" : np("build/console.d"),
                     }) #, implicit_outputs="console.err")
        writer.build([np("out/pcuxn.exe"), np("build/pcuxn.map")], "wat_ld_map",
                [np("build/pcuxn.obj"), np("build/uxn.obj"), np("build/doswrap.obj"),
                 np("build/console.obj")],
                variables = {
                    "outfile" : np("out/pcuxn.exe"),
                    "mapfile" : np("build/pcuxn.map")
                })
        writer.newline()

        writer.variable("uxnasm", np("out/uxnasm.exe"))
        writer.rule("uxn_rom", "$uxnasm $in $out")
        writer.newline()

        writer.build(np("out/console.rom"), "uxn_rom", np("$uxn_path/projects/examples/devices/console.tal"), implicit=np("out/uxnasm.exe"))
        writer.build(np("out/echo.rom"), "uxn_rom", np("$uxn_path/projects/examples/devices/console.echo.tal"), implicit=np("out/uxnasm.exe"))
        writer.newline()

        writer.variable("patch", "patch")
        writer.rule("cp", "$sh_wrap \"$cp $in $out > $null\"",
                    description="Copy and $in for wcl's include ($out)")
        writer.comment("This rule will probably break if the cp succeeds, but the patch doesn't.")
        writer.rule("cp_patch", "$sh_wrap \"$cp $infile $out > $null && $patch -Np1 < $patchfile\"",
                    description="Copy and patching $infile for wcl ($out)")
        writer.newline()

        writer.build(np("src/uxn.c"), "cp", np("$uxn_path/src/uxn.c"))
        writer.build(np("src/uxn.h"), "cp_patch", [np("$uxn_path/src/uxn.h"), np("src/uxn.h.diff")],
                     variables = {
                        "infile" : np("$uxn_path/src/uxn.h"),
                        "patchfile" : np("src/uxn.h.diff")
                     })

        writer.newline()
        writer.comment("Build everything except the dosbox target.")
        writer.default([np("out/pcuxn.exe"), np("out/console.rom"), np("out/echo.rom")])

        if user_vars.dosbox:
            writer.newline()
            writer.variable("dosbox", np(user_vars.dosbox))
            writer.rule("dosbox", command="$dosbox -c \"mount c out\" -c \"c:\"\"", pool="console")
            writer.newline()

            writer.build("dosbox", "dosbox")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uxn", help="path to uxn source", required=True)
    parser.add_argument("--watcom", help="path to WATCOM distribution (default: C:\\WATCOM)", default=os.path.abspath("C:\\WATCOM"))
    parser.add_argument("--memmodel", help="DOS memory model to use (default: c)", default="c")
    parser.add_argument("--dosbox", help="path to DOSBOX binary")
    args = parser.parse_args()
    configure(args)
    write_ninja(args)
