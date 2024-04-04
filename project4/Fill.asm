// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// This program illustrates low-level handling of the screen and keyboard
// devices, as follows.
//
// The program runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
// 
// Assumptions:
// Your program may blacken and clear the screen's pixels in any spatial/visual
// Order, as long as pressing a key continuously for long enough results in a
// fully blackened screen, and not pressing any key for long enough results in a
// fully cleared screen.
//
// Test Scripts:
// For completeness of testing, test the Fill program both interactively and
// automatically.
// 
// The supplied FillAutomatic.tst script, along with the supplied compare file
// FillAutomatic.cmp, are designed to test the Fill program automatically, as 
// described by the test script documentation.
//
// The supplied Fill.tst script, which comes with no compare file, is designed
// to do two things:
// - Load the Fill.hack program
// - Remind you to select 'no animation', and then test the program
//   interactively by pressing and releasing some keyboard keys

// set screen's first row address to currscreenaddr
@SCREEN
D = A
@currscreenaddr
M = D

// set screen's first row address to startscreenaddr
@SCREEN
D = A
@startscreenaddr
M = D

// set screen's last row address to endscreenaddr
@KBD
D = A - 1
@endscreenaddr
M = D

(MAINLOOP)
// if keyboard = 0:
// goto white screen loop
@KBD
D = M
@WHITELOOP
D;JEQ
// else goto black screen loop
@BLACKLOOP
0;JMP

//////////////////////////////////////
// taking care of white screen loop //
/////////////////////////////////////
(WHITELOOP)
// go to current screen address and set it to 0
@currscreenaddr
A = M
M = 0
// checking that currscreenaddr does not go out of bounds
@currscreenaddr
D = M
@endscreenaddr
D = D - M
// D now points to currscreenaddr minus endscreenaddr
// if they are equal, this means we need to go back the mainloop right away so that we don't overflow
@MAINLOOP
D;JEQ
// else, add 1 to the current screen address pointer and only then go back to mainloop
@currscreenaddr
M = M + 1
@MAINLOOP
0;JMP

/////////////////////////////////
// taking care of black screen //
////////////////////////////////
(BLACKLOOP)
// go to current screen row and set it to -1 to paint it black
@currscreenaddr
A = M
M = -1
// checking that currscreenaddr does not go out of bounds
@currscreenaddr
D = M
@startscreenaddr
D = D - M
// D now points to currscreenaddr minus startscreenaddr
// if they are equal, this means we need to go back the mainloop right away so that we don't overflow
@MAINLOOP
D;JEQ
// else, subtract 1 from the current screen address pointer and only then go back to mainloop
@currscreenaddr
M = M - 1
@MAINLOOP
0;JMP