Stephanie Ran
MPCS 52011
Project 10 - COMPILER Syntax Analysis (PART 1)
11/30/2022
-----------------
The CompilationEngine and JackTokenizer should both be working according to their specifications.
Run this code from the src directory to generate an output .xml file. As mentioned in the assignment description, this
will overwrite existing files with the same name!

    $ python3 CompilationEngine.py /file/path

The above code should work for directories or individual files. A corresponing .xml file will be generated for each
.jack file. The name of the file would be the same as the .jack file except with the .xml extension. Then, the TextComparer
can be used to compare the output file with the test file.

    $ TextComparer.sh /file/path/to/testfile.xml /file/path/to/outputFile.xml

Notes:
    - To mark string constants, I appended "XmarkerX" to the end of the string. I'm not sure if this was the best way to
    indicate strings, but the program seemse to work on all the dry tests.
    - There were some functions in the JackTokenizer that I didn't use at all in the CompilationEngine but were listed
    in the API documentation from the textbook. I included them since they were listed in the text, but I'm making a note
    here that I didn't use them
    - I don't know how to stop __pycache__ from generating, but I'm worried that removing it will disrupt my program so I'm
    keeping it in my submission