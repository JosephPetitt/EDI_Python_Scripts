import array
import string
import sys
import glob
import os

try:
    # If available use the psyco optimizing routines.  This will speed
    # up execution by 2x.
    import psyco.classes
    base_class = psyco.classes.psyobj
except ImportError:
    base_class = object

alphanums = string.letters + string.digits

class BadFile(Exception):
    """Raised when file corruption is detected."""

class Parser(base_class):
    """Parse out segments from the X12 raw data files.

    Raises the BadFile exception when data corruption is detected.

    Attributes:
        delimiters
            A string where
            [0] == segment separator
            [1] == element separator
            [2] == sub-element separator
            [3] == repetition separator (if ISA version >= 00405
    """
    def __init__(self, filename=None):
        self.delimiters = ''
        if filename:
            self.open_file(filename)

    def __iter__(self):
        """Return the iterator for use in a for loop"""
        return self

    def open_file(self, filename):
        self.fp = open(filename, 'r')
        self.in_isa = False

    def next(self):
        """return the next segment from the file or raise StopIteration

        Here we'll return the next segment, this will be a 'bare' segment
        without the segment terminator.

        We're using the array module.  Written in C this should be very
        efficient at adding and converting to a string.
        """
        seg = array.array('c')
        if not self.in_isa:
            #We're at the begining of a file or interchange so we need
            #to handle it specially.  We read in the first 105 bytes,
            #ignoring new lines.  After that we read in the segment
            #terminator.
            while len(seg) != 106:
                i = self.fp.read(1)
                if i == '\0': continue
                if i == '':
                    if len(seg) == 0:
                        # We have reached the end of the file normally.
                        raise StopIteration
                    else:
                        # We have reached the end of the file, this is an error
                        # since we are in the middle of an ISA loop.
                        raise BadFile('Unexpected EOF found')
                if len(seg) < 105:
                    # While we're still gathering the 'main' portion of the
                    # ISA, we ignore NULLs and newlines.
                    if i != '\n':
                        # We're still in the 'middle' of the ISA, we won't
                        # accept NULLs or line feeds.
                        try:
                            seg.append(i)
                        except TypeError:
                            # This should never occur in a valid file.
                            print 'Type error on appending "%s"' % i
                else:
                    # We're at the end of the ISA, we'll accept *any*
                    # character except the NULL as the segment terminator for
                    # now.  We'll check for validity next.
                    if i == '\n':
                        # Since we're breaking some lines at position
                        # 80 on a given line, we need to also check the
                        # first character after the line break to make
                        # sure that the newline is supposed to be the
                        # terminator.  If it is, we just backup to
                        # reset the file pointer and move on.
                        pos = self.fp.tell()
                        next_char = self.fp.read(1)
                        if next_char != 'G':
                            i = next_char
                        else:
                            self.fp.seek(pos)
                    try:
                        seg.append(i)
                    except TypeError:
                        print 'Type error on appending "%s"' % i

            self.version = seg[84:89].tostring()
            self.delimiters = seg[105] + seg[3] + seg[104]
            if self.version >= '00405':
                self.delimiters = seg[105] + seg[3] + seg[104] + seg[83]

            # Verify that the delimiters are valid.
            for delim in self.delimiters:
                if delim in alphanums:
                    raise BadFile('"%s" is not a valid delimiter' % delim)

            # Set the flag to process everything else as normal segments.
            self.in_isa = True

            # Pop off the segment terminator.
            seg.pop()
            return seg.tostring()
        else:
            #We're somewhere in the body of the X12 message.  We just
            #read until we find the segment terminator and return the
            #segment.  (We still ignore line feeds unless the line feed
            #is the segment terminator.
            if self.delimiters[0] == '\n':
                return self.fp.readline()[:-1]
            else:
                fp_read = self.fp.read
                while 1:
                    i = fp_read(1)
                    if i == '\0': continue
                    if i == self.delimiters[0]:
                        # End of segment found, exit the loop and return the
                        # segment.
                        segment = seg.tostring()
                        if segment.startswith('IEA'):
                            self.in_isa = False
                        return segment
                    elif i != '\n':
                        try:
                            seg.append(i)
                        except TypeError:
                            raise BadFile('Corrupt characters found in data or unexpected EOF')


f = open("C:/Users/joseph.petitt/Documents/SFTP_Files/Working/KYHCOutFH837DE.txt","w") #Enter the txt file you want the parsed 837's to be written to
if __name__ == '__main__':
    # Sample usage

    f.write("File_Name{Line_Number{Interchange_Ctrl_Nbr{Group_Ctrl_Nbr{Transaction_Ctrl_Nbr{Transaction_Line_Nbr{X12_Segment{Segment_Type{DE01{DE02{DE03{DE04{DE05{DE06{DE07{DE08{DE09{DE10{DE11{DE12{DE13{DE14{DE15{DE16{DE17{DE18{DE19{DE20{DE21{DE22{DE23{DE24{DE25{DE26{DE27{DE28{DE29{DE30{DE31" + "\n")
    path = 'C:/Users/joseph.petitt/Documents/SFTP_Files/Working/KYH*.837' #enter the directory to run the script on
    files=glob.glob(path)
    for File in files:
        fileName = os.path.basename(File)
        
        
        message = Parser(File)
        print fileName
        lineNumber = 1
        for segment in message:
            
            
            if segment.find("ISA*",0,4) != -1: #Find the ISA segment and get the Interchange Control Number, write the ISA segment to the file with delimiters
                ISA = segment.split("*")
                Interchange_Ctrl_Nbr = ISA[13]
                
                
                f.write(fileName + "{" + str(lineNumber) + "{" + Interchange_Ctrl_Nbr + "{{{{" + segment + "~" + "{" + ISA[0] + "{" + ISA[1] + "{" + ISA[2] + "{" + ISA[3] + "{" + ISA[4] + "{" + ISA[5] + "{" + ISA[6] + "{" + ISA[7] + "{" + ISA[8] + "{" + ISA[9] + "{" + ISA[10] + "{" + ISA[11] + "{" + ISA[12] + "{" + ISA[13] + "{" + ISA[14] + "{" + ISA[15] + "{" + ISA[16] + "{{{{{{{{{{{{{{{" + "\n")
                continue
            if segment.find("GS*",0,3) != -1:  #find the GS segment and get the Group Control Number, write the GS segment to the file with delimiters
                GS = segment.split("*")
                Group_Control_Nbr = GS[6]
                lineNumber += 1
                f.write(fileName + "{" + str(lineNumber) + "{" + Interchange_Ctrl_Nbr + "{" + Group_Control_Nbr + "{{{" + segment + "~" + "{" + GS[0] + "{" + GS[1] + "{" + GS[2] + "{" + GS[3] + "{" + GS[4] + "{" + GS[5] + "{" + GS[6] + "{" + GS[7] + "{" + GS[8] + "{{{{{{{{{{{{{{{{{{{{{{{" + "\n")
                lineNumber += 1
                continue
            if segment.find("ST*",0,3) != -1:   #find the ST segement and get the Transaction Control Number as set the Transaction Line Number
                ST = segment.split("*")
                Transaction_Ctrl_Nbr = ST[2]
                Transaction_Line_Nbr = 1
            if segment.find("GE*",0,3) != -1: 
                GE = segment.split("*")
                f.write(fileName + "{" + str(lineNumber) + "{" + Interchange_Ctrl_Nbr + "{" + Group_Control_Nbr + "{{{" + segment + "~" + "{" + GE[0] + "{" + GE[1] + "{" + GE[2] + "{{{{{{{{{{{{{{{{{{{{{{{{{{{{{" + "\n")
                lineNumber += 1
                continue
            if segment.find("IEA*",0,4) != -1:
                IEA = segment.split("*")
                f.write(fileName + "{" + str(lineNumber) + "{" + Interchange_Ctrl_Nbr + "{{{{" + segment + "~" + "{" + IEA[0] + "{" + IEA[1] + "{" + IEA[2] + "{{{{{{{{{{{{{{{{{{{{{{{{{{{{{" + "\n")
                continue

            DE = segment.split("*") 
            while len(DE) != 31: #if a segement has less than 31 data elements add blanks, this allows printing of the correct amount of delimeters
                DE.append("")
            
            f.write(fileName + "{" + str(lineNumber) + "{" + Interchange_Ctrl_Nbr + "{" + Group_Control_Nbr + "{" + Transaction_Ctrl_Nbr + "{" + str(Transaction_Line_Nbr) + "{" + segment + "~" + "{" + DE[0] + "{" + DE[1] + "{" + DE[2] + "{" + DE[3] + "{" + DE[4] + "{" + DE[5] + "{" + DE[6] + "{" + DE[7] + "{" + DE[8] + "{" + DE[9] + "{" + DE[10] + "{" + DE[11] + "{" + DE[12] + "{" + DE[13] +"{" + DE[14] + "{" + DE[15] + "{" + DE[16] + "{" + DE[17] + "{" + DE[18] + "{" + DE[19] + "{" + DE[20] + "{" + DE[21] + "{" + DE[22] + "{" + DE[23] + "{" + DE[24] + "{" + DE[25] + "{" + DE[26] + "{" + DE[27] + "{" + DE[28] + "{" + DE[29] + "{" + DE[30] + "{" + "\n")
            lineNumber += 1
            Transaction_Line_Nbr += 1
       # Write out each segment to the file with de-Normalization attributes, individual data elements, and trailing delimeters, increment the line number and transaction line number

f.close()
        # Dispatch based on elements[0]...
