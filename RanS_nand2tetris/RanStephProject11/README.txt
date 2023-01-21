Stephanie Ran
MPCS 52011
Project 11 - FULL COMPILER (Part II)
12/9/2022
-----------------
The JackCompiler passes 4 out of the 6 tests. I couldn't for the life of me fix Pong and Complex Arrays.

Run this code from the src directory to generate an output .vm file. As mentioned in the assignment description, this
will overwrite existing files with the same name!

    $ python3 JackCompiler.py /file/path

The above code should work for directories or individual files. A corresponding .vm file will be generated for each
.jack file. The name of the file would be the same as the .jack file except with the .vm extension. The .vm files can
then be used in the VMemulator for testing.

Notes:
    - I couldn't figure out how to get the number of arguments to show up correctly for function calls. It seemed as if
    each time I did a new test, the number of arguments would get messed up again. I got it to work for the first 4 tests
    though!
    - I don't know how to stop __pycache__ from generating, but I'm worried that removing it will disrupt my program so I'm
    keeping it in my submission