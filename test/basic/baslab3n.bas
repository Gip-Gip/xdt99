100 REM EXT; BASIC; SAMPLE
110 CALL CLEAR :: CALL SCREEN(15)
120 IF A>0 THEN A=1 ELSE GOTO 140
130 A=A+1 :: GOSUB 160 :: GO TO 150
140 GO SUB 160 :: GOTO 120
150 A=A-1 :: IF A=1 THEN 130 ELSE A=A+2 :: GOTO 120
160 GO SUB 180 :: ON A GO TO 120,130,140
170 RETURN
180 A=A*2 :: RETURN
