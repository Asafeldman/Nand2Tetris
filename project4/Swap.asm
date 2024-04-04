// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// store maximum value, minimum value and current addresses in pointers maxadr, minadr and curadr
@R14
D = M
@maxadr
M = D
@minadr
M = D
@curadr
M = D

// store maximum value, minimum value and current value in pointers max, min and cur
@R14
A = M
D = M
@max
M = D
@min
M = D
@cur
M = D

// set loop counter i
@i
M = 0

(LOOP)
// while i < arraylength-1:
@R15
D = M - 1
@i
D = M - D
@SWAP
D;JGT
// curadr += 1
// cur = arr[curadr]
@curadr
M = M + 1
A = M
D = M
@cur
M = D

// if cur > max:
// max = cur
// maxadr = curadr
@cur
D = M
@max
D = D - M
@UPDATEMAX
D;JGT

// if cur < min:
// min = cur
// minadr = curadr
@cur
D = M
@min
D = D - M
@UPDATEMIN
D;JLT

// come back here from UPDATEMAX or UPDATEMIN
(CONTINUE)
// i += 1
@i
M = M + 1
@LOOP
0;JMP

(UPDATEMAX)
@cur
D = M
@max
M = D
@curadr
D = M
@maxadr
M = D
// go back to loop
@CONTINUE
0;JMP

(UPDATEMIN)
@cur
D = M
@min
M = D
@curadr
D = M
@minadr
M = D
// go back to loop
@CONTINUE
0;JMP


(SWAP)
// arr[minadr] = max
@max
D = M
@minadr
A = M
M = D

// arr[maxadr] = min
@min
D = M
@maxadr
A = M
M = D

// infinite loop
(END)
@END
0;JMP