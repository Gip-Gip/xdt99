* memory copy

* copy <r2> bytes from <r1> to <r0>
* NOTE: <r2> must be even and not equal 0!

       def memcpy

memcpy:
       mov  *r1+, *r0+
       dect r2
       jne  memcpy
       rt
