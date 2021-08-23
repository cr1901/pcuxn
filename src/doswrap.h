#ifndef DOSWRAP_H
#define DOSWRAP_H

#include <dos.h>

typedef enum
{
    DOS_WRAP_OKAY,
    NOT_A_DEVICE,
    NOT_READY,
    SYSCALL_ERROR,
} dos_wrap_error_tag;

typedef struct dos_wrap_error
{
    dos_wrap_error_tag reason;
    int code;
} dos_wrap_error_t;

int input_status(int handle, dos_wrap_error_t * err);
dos_wrap_error_t dev_attr(int handle, int * code);

/* CTTY for the duration of the program. */
/* int redirect_con(char * fn); */

#endif
