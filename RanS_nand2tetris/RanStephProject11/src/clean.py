import os
# this program cleans a given file of whitespace and comments

def clean(filepath):
    '''
    Remove c-style comments and whitespaces from a file

        Inputs:
            filepath (string): the file path

        Returns: nothing (generates out file)
    '''
    newLines=[]
    listofLines = []

    if os.path.exists(filepath):
        with open(filepath, 'r') as f: #open the file for reading
            lines = f.readlines()
            partOfComment=False
            for s in lines:
                if s != "\n": #if the line is not empty
                    k=len(s)
                    if not partOfComment:
                        strLine = ""
                        i=0
                        while i < k:
                            if partOfComment:
                                if(s[i]=="*"):
                                    if(i+1<k and s[i+1]=="/"):
                                        partOfComment=False
                                        i+=1
                                i+=1
                                continue
                            if(s[i]=='\"'):
                                strLine+=s[i]
                                i += 1
                                while i<k and s[i]!='\"':
                                    strLine+=s[i]
                                    i += 1
                                continue

                            #case //
                            if s[i]=='/':
                                if i+1<k and s[i+1]=='/':
                                    strLine+='\n'
                                    break

                                #case /* */
                                if i+1<k and s[i+1]=='*':
                                    partOfComment=True
                                    i+=1

                            if not partOfComment:
                                strLine += s[i]
                            i+=1
                        newLines.append(strLine)

                    else:
                        for i in range(0, k):
                            if s[i]=='*':
                                if i+1<k and s[i+1]=='/':
                                    partOfComment=False
                                    newLines.append("\n")
                
    else:
        raise FileNotFoundError('File does not exist')

    for line in newLines:
        if (line == '\n' or line.isspace()): # if the line is empty or only
                                             # has whitespace
            newLines.remove(line)

    found = False
    for line in newLines:
        if line != '\n' and line != '' and not line.isspace():
            found=True
        if found:
            if line != '\n' and line != '' and not line.isspace():
                line = line.lstrip()
                line = line.rstrip()
                listofLines.append(line + '\n')

    counter = 1
    for line in listofLines:
        counter += 1

    return listofLines