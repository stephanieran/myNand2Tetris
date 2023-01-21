Stephanie Ran
MPCS 52011 - Project 8
11/9/2022
-------------------------------
After feedback from vmTranslator part 1, I redesigned my implementation to
increase the readibility and clean up the design. I really tried to get the
bootstrap tests working but I couldn't figure it out. My program ran
successfully with the not bootstrap tests including NestedCall but would fail
the FibonacciElement and StaticsTest tests. I believe this is due to bootstrapping
issues or general issues with the function def/call, but I really couldn't figure
it out. Any guidance on this would be greatly appreciated-- and apologies for 
turning in code that didn't pass all the tests!

To run the program, run the following:

    $ python3 newDriver.py path/name

on either the filepath to the file itself or to the directory. A subsequent
.asm file will be generated in the directory of the file or of the directory whose
path name was given. If a directory path was supplied, the .asm file would need to be
manually moved into the same directory of the .tst file in order for the tests to be ran.