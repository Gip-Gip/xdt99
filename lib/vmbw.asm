* VDP multi-byte write, where length can be zero

       def  vmbw
       ref  vdpwa, vdpwd

       even

vmbw:
       ori  r0, >4000
       swpb r0
       movb r0, @vdpwa
       swpb r0
       movb r0, @vdpwa

       jmp  !dec
!mov   movb *r1+, @vdpwd
!dec   dec  r2
       joc  -!mov

       rt
