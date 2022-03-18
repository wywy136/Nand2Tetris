// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.


// ptr = SCREEN
// While True
// If key pressed
//     if ptr < KBD
//         set black
//         ptr += 1
// Else
//     if ptr > SCREEN
//         set white
//         ptr -= 1

    @SCREEN  // ptr = SCREEN
    D=A
    @0
    M=D  // R[0] = ptr

(LOOP)
    @KBD  // keyboard
    D=M
    @CLEAR  // if D = 0, then there is no key being pressed, clear the screen
    D;JEQ
    @FILL  // otherwise fill the screen
    0;JMP

(CLEAR)
    @0
    D=M
    @SCREEN
    D=D-A

    @LOOP  // if ptr < SCREEN, then continue
    D;JLT

    @0
    A=M  // move to the ptr
    M=0  // set ptr to white
    @0
    M=M-1  // ptr -= 1

    @LOOP
    0;JMP

(FILL)
    @0
    D=M
    @KBD
    D=A-D

    @LOOP  // if ptr > KBD, then continue
    D;JEQ

    @0
    A=M  // move to the ptr
    M=-1  // set ptr to black
    @0
    M=M+1

    @LOOP
    0;JMP