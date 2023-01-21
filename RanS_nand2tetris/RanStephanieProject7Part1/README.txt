Stephanie Ran
Project 7 - Part 1
MPCS 52011
11/2/2022
-----------------------------------------
the vmTranslator should work as expected. To run the program, make sure
you're in the same directory as the source code and then utilize a command
line argument with the filepath of the .vm file to be converted into a
.asm file:

    $ python3 vmTranslator.py /FILE/PATH

The .asm file will be found in the same directory as the .vm file used
to run the program on. The subsequent .asm file can be used for testing.

I tested my program by running the VM Translator on the different test
programs and using the CPU emulator to test the generated .asm files.
The comparisons ended successfully for the different tests supplied.