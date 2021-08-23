#include "doswrap.h"

#include <stdlib.h>
#include <dos.h>
#include <io.h>

// dos_wrap_error_t dos_read_noblock(int handle, void *buffer, unsigned count, unsigned * bytes)
// {
//
// }

// 0- Okay, Nonzero- error
int input_status(int handle, dos_wrap_error_t * err)
{
    union REGS in_regs, out_regs;

    in_regs.h.ah = 0x44;
    in_regs.h.al = 6;
    in_regs.w.bx = handle;

    intdos(&in_regs, &out_regs);

    if(out_regs.w.cflag == 1)
    {
        if(err != NULL)
        {
            err->reason = SYSCALL_ERROR;
            err->code = out_regs.w.ax;
        }

        return -1;
    }

    if(out_regs.h.al == 0)
    {
        if(err != NULL)
        {
            err->reason = NOT_READY;
            err->code = out_regs.h.al;
        }

        return -2;
    }

    if(err != NULL)
    {
        err->reason = DOS_WRAP_OKAY;
        err->code = out_regs.h.al;
    }

    return 0;
}


// 1- Yes, 0- Everything else
int is_char_device(int handle, dos_wrap_error_t * err)
{
    return 0;
}

dos_wrap_error_t dev_attr(int handle, int * code)
{
    union REGS in_regs, out_regs;
    dos_wrap_error_t rc;

    in_regs.h.ah = 0x44;
    in_regs.h.al = 0;
    in_regs.w.bx = handle;

    intdos(&in_regs, &out_regs);

    if(out_regs.w.cflag == 1)
    {
        rc.code = out_regs.w.ax;
        rc.reason = SYSCALL_ERROR;
        return rc;
    }
    else
    {
        rc.code = out_regs.w.dx;
        rc.reason = DOS_WRAP_OKAY;
    }

    return rc;
}
