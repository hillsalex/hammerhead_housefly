#!/usr/bin/env python

__version__ = '2.1'
__author__  = "Avinash Kak (kak@purdue.edu)"
__date__    = '2011-February-13'
__url__     = 'http://RVL4.ecn.purdue.edu/~kak/dist/BitVector-2.1.html'
__copyright__ = "(C) 2011 Avinash Kak. Python Software Foundation."


import array
import operator

_hexdict = { '0' : '0000', '1' : '0001', '2' : '0010', '3' : '0011',
             '4' : '0100', '5' : '0101', '6' : '0110', '7' : '0111',
             '8' : '1000', '9' : '1001', 'a' : '1010', 'b' : '1011',
             'c' : '1100', 'd' : '1101', 'e' : '1110', 'f' : '1111' }

def _readblock( blocksize, bitvector ):                              #(R1)
    ''' 
    If this function can read all blocksize bits, it peeks ahead to see
    if there is anything more to be read in the file. It uses
    tell-read-seek mechanism for this in lines (R18) through (R21).  If
    there is nothing further to be read, it sets the more_to_read attribute
    of the bitvector object to False.  Obviously, this can only be done for
    seekable streams such as those connected with disk files.  According to
    Blair Houghton, a similar feature could presumably be implemented for
    socket streams by using recv() or recvfrom() if you set the flags
    argument to MSG_PEEK.
    '''
    global hexdict                                                   #(R2)
    bitstring = ''                                                   #(R3)
    i = 0                                                            #(R4)
    while ( i < blocksize / 8 ):                                     #(R5)
        i += 1                                                       #(R6)
        byte = bitvector.FILEIN.read(1)                              #(R7)
        if byte == '':                                               #(R8)
            if len(bitstring) < blocksize:                           #(R9)
                bitvector.more_to_read = False                      #(R10)
            return bitstring                                        #(R11)
        hexvalue = hex( ord( byte ) )                               #(R12)
        hexvalue = hexvalue[2:]                                     #(R13)
        if len( hexvalue ) == 1:                                    #(R14)
            hexvalue = '0' + hexvalue                               #(R15)
        bitstring += _hexdict[ hexvalue[0] ]                        #(R16)
        bitstring += _hexdict[ hexvalue[1] ]                        #(R17)
    file_pos = bitvector.FILEIN.tell()                              #(R18)
    # peek at the next byte; moves file position only if a
    # byte is read
    next_byte = bitvector.FILEIN.read(1)                            #(R19)
    if next_byte:                                                   #(R20)
        # pretend we never read the byte                   
        bitvector.FILEIN.seek( file_pos )                           #(R21)
    else:                                                           #(R22)
        bitvector.more_to_read = False                              #(R23)
    return bitstring                                                #(R24)


#--------------------  BitVector Class Definition   ----------------------

class BitVector( object ):                                           #(A1)

    def __init__( self, *args, **kwargs ):                           #(A2)
        if args:                                                     #(A3)
               raise ValueError(                                     #(A4)
                      '''BitVector constructor can only be called with
                         keyword arguments for the following keywords:
                         filename, fp, size, intVal, bitlist, and
                         bitstring)''')                              #(A5)
        allowed_keys = 'bitlist','bitstring','filename','fp','intVal','size'
                                                                     #(A6)
        keywords_used = kwargs.keys()
        for keyword in keywords_used:
            if keyword not in allowed_keys: 
                raise ValueError("Wrong keyword used --- check spelling")
                                                                     #(A7)
        filename = fp = intVal = size = bitlist = bitstring = None   #(A8)
        if kwargs.has_key('filename'):filename=kwargs.pop('filename')#(A9)
        if kwargs.has_key('fp'):           fp = kwargs.pop('fp')    #(A10)
        if kwargs.has_key('size'):       size = kwargs.pop('size')  #(A11)
        if kwargs.has_key('intVal'):   intVal = kwargs.pop('intVal')#(A12)
        if kwargs.has_key('bitlist'):
                               bitlist = kwargs.pop('bitlist')      #(A13)
        if kwargs.has_key('bitstring') :
                               bitstring = kwargs.pop('bitstring')  #(A14)
        self.filename = None                                        #(A15)
        self.size = 0                                               #(A16)
        self.FILEIN = None                                          #(A17)
        self.FILEOUT = None                                         #(A18)
        
        if filename:                                                #(A19)
            if fp or size or intVal or bitlist or bitstring:        #(A20)
                raise ValueError(                                   #(A21)
                  '''When filename is specified, you cannot
                     give values to any other constructor args''')
            self.filename = filename                                #(A22)
            self.FILEIN = open( filename, 'rb' )                    #(A23)
            self.more_to_read = True                                #(A24)
            return                                                  #(A25)
        elif fp:                                                    #(A26)
            if filename or size or intVal or bitlist or bitstring:  #(A27)
                raise ValueError(                                   #(A28)
                  '''When fileobject is specified, you cannot      
                     give values to any other constructor args''')
            bits = self.read_bits_from_fileobject( fp )             #(A29)
            bitlist =  map( int, bits )                             #(A30)
            self.size = len( bitlist )                              #(A31)
        elif intVal or intVal == 0:                                 #(A32)
            if filename or fp or bitlist or bitstring:              #(A33)
                raise ValueError(                                   #(A34)
                  '''When intVal is specified, you can only give
                     a value to the 'size' constructor arg''')
            if intVal == 0:                                         #(A35)
                bitlist = [0]                                       #(A36)
                if not size:                                        #(A37)
                    self.size = 1                                   #(A38)
                else:                                               #(A39)
                    if size < len(bitlist):                         #(A40)
                        raise ValueError(                           #(A41)
                          '''The value specified for size must be at least
                             as large as for the smallest bit vector
                             possible for intVal''')
                    n = size - len(bitlist)                         #(A42)
                    bitlist = [0]*n + bitlist                       #(A43)
                    self.size = len( bitlist )                      #(A44)
            else:                                                   #(A45)
                hexVal = hex( intVal ).lower().rstrip('l')          #(A46)
                hexVal = hexVal[2:]                                 #(A47)
                if len( hexVal ) == 1:                              #(A48)
                    hexVal = '0' + hexVal                           #(A49)
                bitlist = ''.join(map(lambda x: _hexdict[x],hexVal))#(A50)
                bitlist =  map( int, bitlist )                      #(A51)
                i = 0                                               #(A52)
                while ( i < len( bitlist ) ):                       #(A53)
                    if bitlist[i] == 1: break                       #(A54)
                    i += 1                                          #(A55)
                del bitlist[0:i]                                    #(A56)
                if not size:                                        #(A57)
                    self.size = len( bitlist )                      #(A58)
                else:                                               #(A59)
                    if size < len(bitlist):                         #(A60)
                        raise ValueError(                           #(A61)
                          '''The value specified for size must be at least
                             as large as for the smallest bit vector
                             possible for intVal''')
                    n = size - len(bitlist)                         #(A62)
                    bitlist = [0]*n + bitlist                       #(A63)
                    self.size = len( bitlist )                      #(A64)
        elif size >= 0:                                             #(A65)
            if filename or fp or intVal or bitlist or bitstring:    #(A66)
                raise ValueError(                                   #(A67)
                  '''When size is specified (without an intVal), you cannot
                     give values to any other constructor args''')
            self.size = size                                        #(A68)
            two_byte_ints_needed = (size + 15) // 16                #(A69)
            self.vector = array.array('H', [0]*two_byte_ints_needed)#(A70)
            return                                                  #(A71)
        elif bitstring or bitstring == '':                          #(A72)
            if filename or fp or size or intVal or bitlist:         #(A73)
                raise ValueError(                                   #(A74)
                  '''When a bitstring is specified, you cannot
                     give values to any other constructor args''')
            bitlist =  map( int, list(bitstring) )                  #(A75)
            self.size = len( bitlist )                              #(A76)
        elif bitlist:                                               #(A77)
            if filename or fp or size or intVal or bitstring:       #(A78)
                raise ValueError(                                   #(A79)
                  '''When bits are specified, you cannot give values to any
                     other constructor args''')
            self.size = len( bitlist )                              #(A80)
        else:                                                       #(A81)
            raise ValueError("wrong arg(s) for constructor")        #(A82) 
        two_byte_ints_needed = (len(bitlist) + 15) // 16            #(A83)
        self.vector = array.array( 'H', [0]*two_byte_ints_needed )  #(A84)
        map( self._setbit, enumerate(bitlist), bitlist)             #(A85)


    def _setbit( self, posn, val ):                                  #(B1)
        'Set the bit at the designated position to the value shown'
        if val not in (0, 1):                                        #(B2)
            raise ValueError( "incorrect value for a bit" )          #(B3)
        if isinstance( posn, (tuple) ):                              #(B4)
            posn = posn[0]                                           #(B5)
        if  posn >= self.size or posn < -self.size:                  #(B6)
            raise ValueError( "index range error" )                  #(B7)   
        if posn < 0: posn = self.size + posn                         #(B8)
        block_index = posn // 16                                     #(B9)
        shift = posn & 15                                           #(B10)
        cv = self.vector[block_index]                               #(B11)
        if ( cv >> shift ) & 1 != val:                              #(B12)
            self.vector[block_index] = cv ^ (1 << shift)            #(B13)


    def _getbit( self, posn ):                                       #(C1)
        'Get the bit from the designated position'
        if  posn >= self.size or posn < -self.size:                  #(C2)
            raise ValueError( "index range error" )                  #(C3)   
        if posn < 0: posn = self.size + posn                         #(C4)
        return ( self.vector[posn//16] >> (posn&15) ) & 1            #(C5)


    def __xor__(self, other):                                        #(E1)
        '''
        Take a bitwise 'xor' of the bit vector on which the method is
        invoked with the argument bit vector.  Return the result as a new
        bit vector.  If the two bit vectors are not of the same size, pad
        the shorter one with zeros from the left.
        '''
        if self.size < other.size:                                   #(E2)
            bv1 = self._resize_pad_from_left(other.size - self.size) #(E3)
            bv2 = other                                              #(E4)
        elif self.size > other.size:                                 #(E5)
            bv1 = self                                               #(E6)
            bv2 = other._resize_pad_from_left(self.size - other.size)#(E7)
        else:                                                        #(E8)
            bv1 = self                                               #(E9)
            bv2 = other                                             #(E10)
        res = BitVector( size = bv1.size )                          #(E11)
        lpb = map(operator.__xor__, bv1.vector, bv2.vector)         #(E12) 
        res.vector = array.array( 'H', lpb )                        #(E13)
        return res                                                  #(E14)


    def __and__(self, other):                                        #(F1)
        '''
        Take a bitwise 'and' of the bit vector on which the method is
        invoked with the argument bit vector.  Return the result as a new
        bit vector.  If the two bit vectors are not of the same size, pad
        the shorter one with zeros from the left.
        '''      
        if self.size < other.size:                                   #(F2)
            bv1 = self._resize_pad_from_left(other.size - self.size) #(F3)
            bv2 = other                                              #(F4)
        elif self.size > other.size:                                 #(F5)
            bv1 = self                                               #(F6)
            bv2 = other._resize_pad_from_left(self.size - other.size)#(F7)
        else:                                                        #(F8)
            bv1 = self                                               #(F9)
            bv2 = other                                             #(F10)
        res = BitVector( size = bv1.size )                          #(F11)
        lpb = map(operator.__and__, bv1.vector, bv2.vector)         #(F12) 
        res.vector = array.array( 'H', lpb )                        #(F13)
        return res                                                  #(F14)


    def __or__(self, other):                                         #(G1)
        '''
        Take a bitwise 'or' of the bit vector on which the method is
        invoked with the argument bit vector.  Return the result as a new
        bit vector.  If the two bit vectors are not of the same size, pad
        the shorter one with zero's from the left.
        '''
        if self.size < other.size:                                   #(G2)
            bv1 = self._resize_pad_from_left(other.size - self.size) #(G3)
            bv2 = other                                              #(G4)
        elif self.size > other.size:                                 #(G5)
            bv1 = self                                               #(G6)
            bv2 = other._resize_pad_from_left(self.size - other.size)#(G7)
        else:                                                        #(G8)
            bv1 = self                                               #(G9)
            bv2 = other                                             #(G10)
        res = BitVector( size = bv1.size )                          #(G11)
        lpb = map(operator.__or__, bv1.vector, bv2.vector)          #(G12) 
        res.vector = array.array( 'H', lpb )                        #(G13)
        return res                                                  #(G14)


    def __invert__(self):                                            #(H1)
        '''
        Invert the bits in the bit vector on which the method is invoked
        and return the result as a new bit vector.
        '''
        res = BitVector( size = self.size )                          #(H2)
        lpb = map( operator.__inv__, self.vector )                   #(H3) 
        res.vector = array.array( 'H' )                              #(H3)
        for i in range(len(lpb)):                                    #(H4)
            res.vector.append( lpb[i] & 0x0000FFFF )                 #(H5)
        return res                                                   #(H6)


    def __add__(self, other):                                        #(J1)
        '''
        Concatenate the argument bit vector with the bit vector on which
        the method is invoked.  Return the concatenated bit vector as a new
        BitVector object.
        '''
        i = 0                                                        #(J2)
        outlist = []                                                 #(J3)
        while ( i < self.size ):                                     #(J4)
            outlist.append( self[i] )                                #(J5)
            i += 1                                                   #(J6)
        i = 0                                                        #(J7)
        while ( i < other.size ):                                    #(J8)
            outlist.append( other[i] )                               #(J9)
            i += 1                                                  #(J10)
        return BitVector( bitlist = outlist )                       #(J11)


    def _getsize(self):                                              #(K1)
        'Return the number of bits in a bit vector.'
        return self.size                                             #(K2)


    def read_bits_from_file(self, blocksize):                        #(L1)
        '''
        Read blocksize bits from a disk file and return a BitVector object
        containing the bits.  If the file contains fewer bits than
        blocksize, construct the BitVector object from however many bits
        there are in the file.  If the file contains zero bits, return a
        BitVector object of size attribute set to 0.
        '''
        error_str = '''You need to first construct a BitVector
        object with a filename as  argument'''                       #(L2)
        if not self.filename:                                        #(L3)
            raise SyntaxError( error_str )                           #(L4)
        if blocksize % 8 != 0:                                       #(L5)
            raise ValueError( "block size must be a multiple of 8" ) #(L6)
        bitstr = _readblock( blocksize, self )                       #(L7)
        if len( bitstr ) == 0:                                       #(L8)
            return BitVector( size = 0 )                             #(L9)
        else:                                                       #(L10)
            return BitVector( bitstring = bitstr )                  #(L11)


    def read_bits_from_fileobject( self, fp ):                       #(M1)
        '''
        This function is meant to read a bit string from a file like
        object.
        '''
        bitlist = []                                                 #(M2)
        while 1:                                                     #(M3)
            bit = fp.read()                                          #(M4)
            if bit == '': return bitlist                             #(M5)
            bitlist += bit                                           #(M6)


    def write_bits_to_fileobject( self, fp ):                        #(N1)
        '''
        This function is meant to write a bit vector directly to a file
        like object.  Note that whereas 'write_to_file' method creates a
        memory footprint that corresponds exactly to the bit vector, the
        'write_bits_to_fileobject' actually writes out the 1's and 0's as
        individual items to the file object.  That makes this method
        convenient for creating a string representation of a bit vector,
        especially if you use the StringIO class, as shown in the test
        code.
        '''
        for bit_index in range(self.size):                           #(N2)
            if self[bit_index] == 0:                                 #(N3)
                fp.write( '0' )                                      #(N4)
            else:                                                    #(N5)
                fp.write( '1' )                                      #(N6)


    def divide_into_two(self):                                       #(P1)
        '''
        Divides an even-sized bit vector into two and returns the two
        halves as a list of two bit vectors.
        '''
        if self.size % 2 != 0:                                       #(P2)
            raise ValueError( "must have even num bits" )            #(P3)
        i = 0                                                        #(P4)
        outlist1 = []                                                #(P5)
        while ( i < self.size /2 ):                                  #(P6)
            outlist1.append( self[i] )                               #(P7)
            i += 1                                                   #(P8)
        outlist2 = []                                                #(P9)
        while ( i < self.size ):                                    #(P10)
            outlist2.append( self[i] )                              #(P11)
            i += 1                                                  #(P12)
        return [ BitVector( bitlist = outlist1 ),
                 BitVector( bitlist = outlist2 ) ]                  #(P13)


    def permute(self, permute_list):                                 #(Q1)
        '''
        Permute a bit vector according to the indices shown in the second
        argument list.  Return the permuted bit vector as a new bit vector.
        '''
        if max(permute_list) > self.size -1:                         #(Q2)
            raise ValueError( "Bad permutation index" )              #(Q3)
        outlist = []                                                 #(Q4)
        i = 0                                                        #(Q5)
        while ( i < len( permute_list ) ):                           #(Q6)
            outlist.append( self[ permute_list[i] ] )                #(Q7)
            i += 1                                                   #(Q8)
        return BitVector( bitlist = outlist )                        #(Q9)


    def unpermute(self, permute_list):                               #(S1)
        '''
        Unpermute the bit vector according to the permutation list supplied
        as the second argument.  If you first permute a bit vector by using
        permute() and then unpermute() it using the same permutation list,
        you will get back the original bit vector.
        '''
        if max(permute_list) > self.size -1:                         #(S2)
            raise ValueError( "Bad permutation index" )              #(S3)
        if self.size != len( permute_list ):                         #(S4)
            raise ValueError( "Bad size for permute list" )          #(S5)
        out_bv = BitVector( size = self.size )                       #(S6)
        i = 0                                                        #(S7)
        while ( i < len(permute_list) ):                             #(S8)
            out_bv[ permute_list[i] ] = self[i]                      #(S9)
            i += 1                                                  #(S10)
        return out_bv                                               #(S11)


    def write_to_file(self, file_out):                               #(T1)
        '''
        (Contributed by Joe Davidson) Write the bitvector to the file
        object file_out.  (A file object is returned by a call to
        open()). Since all file I/O is byte oriented, the bitvector must be
        multiple of 8 bits. Each byte treated as MSB first (0th index).
        '''
        err_str = '''Only a bit vector whose length is a multiple of 8 can
            be written to a file.  Use the padding functions to satisfy
            this constraint.'''                                      #(T2)
        if not self.FILEOUT: 
            self.FILEOUT = file_out
        if self.size % 8:                                            #(T3)
            raise ValueError( err_str )                              #(T4)
        for byte in range(self.size/8 ):                             #(T5)
            value = 0                                                #(T6)
            for bit in range(8):                                     #(T7)
                value += (self._getbit( byte*8 + (7 - bit) ) << bit )#(T8)
            file_out.write( chr(value) )                             #(T9)


    def close_file_object(self):                                     #(U1)
        '''
        For closing a file object that was used for reading the bits into
        one or more BitVector objects.
        '''
        if not self.FILEIN:                                          #(U2)
            raise SyntaxError( "No associated open file" )           #(U3)
        self.FILEIN.close()                                          #(U4)


    def intValue(self):                                              #(V1)
        'Return the integer value of a bitvector'
        intVal = 0                                                   #(V2)
        for i in range(self.size):                                   #(V3)
            intVal += self[i] * (2 ** (self.size - i - 1))           #(V4)
        return intVal                                                #(V5)

            
    def __lshift__( self, n ):                                       #(W1)
        'For an in-place left circular shift by n bit positions'
        for i in range(n):                                           #(W2)
            self.circular_rotate_left_by_one()                       #(W3)
    def __rshift__( self, n ):                                       #(W4)
        'For an in-place right circular shift by n bit positions.'
        for i in range(n):                                           #(W5)
            self.circular_rotate_right_by_one()                      #(W6)


    def circular_rotate_left_by_one(self):                           #(X1)
        'For a one-bit in-place left circular shift'
        size = len(self.vector)                                      #(X2)
        bitstring_leftmost_bit = self.vector[0] & 1                  #(X3)
        left_most_bits = map(operator.__and__, self.vector, [1]*size)#(X4)
        left_most_bits.append(left_most_bits[0])                     #(X5)
        del(left_most_bits[0])                                       #(X6)
        self.vector = map(operator.__rshift__, self.vector, [1]*size)#(X7)
        self.vector = map( operator.__or__, self.vector, \
             map(operator.__lshift__, left_most_bits, [15]*size) )   #(X8)
        self._setbit(self.size -1, bitstring_leftmost_bit)           #(X9)


    def circular_rotate_right_by_one(self):                          #(Y1)
        'For a one-bit in-place right circular shift'
        size = len(self.vector)                                      #(Y2)
        bitstring_rightmost_bit = self[self.size - 1]                #(Y3)
        right_most_bits = map( operator.__and__,
                               self.vector, [0x8000]*size )          #(Y4)
        self.vector = \
             map( operator.__and__, self.vector, [~0x8000]*size )    #(Y5)
        right_most_bits.insert(0, bitstring_rightmost_bit)           #(Y6)
        right_most_bits.pop()                                        #(Y7)
        self.vector = map(operator.__lshift__, self.vector, [1]*size)#(Y8)
        self.vector = map( operator.__or__, self.vector, \
             map(operator.__rshift__, right_most_bits, [15]*size) )  #(Y9)
        self._setbit(0, bitstring_rightmost_bit)                    #(Y10)


    def circular_rot_left(self):                                     #(Z1)
        '''
        This is merely another implementation of the method
        circular_rotate_left_by_one() shown above.  This one does NOT use
        map functions.  This method carries out a one-bit left circular
        shift of a bit vector.
        '''
        max_index = (self.size -1)  // 16                            #(Z2)
        left_most_bit = self.vector[0] & 1                           #(Z3)
        self.vector[0] = self.vector[0] >> 1                         #(Z4)
        for i in range(1, max_index + 1):                            #(Z5)
            left_bit = self.vector[i] & 1                            #(Z6)
            self.vector[i] = self.vector[i] >> 1                     #(Z7)
            self.vector[i-1] |= left_bit << 15                       #(Z8)
        self._setbit(self.size -1, left_most_bit)                    #(Z9)


    def circular_rot_right(self):                                    #(a1)
        '''
        This is merely another implementation of the method
        circular_rotate_right_by_one() shown above.  This one does NOT use
        map functions.  This method does a one-bit right circular shift of
        a bit vector.
        '''
        max_index = (self.size -1)  // 16                            #(a2)
        right_most_bit = self[self.size - 1]                         #(a3)
        self.vector[max_index] &= ~0x8000                            #(a4)
        self.vector[max_index] = self.vector[max_index] << 1         #(a5)
        for i in range(max_index-1, -1, -1):                         #(a6)
            right_bit = self.vector[i] & 0x8000                      #(a7)
            self.vector[i] &= ~0x8000                                #(a8)
            self.vector[i] = self.vector[i] << 1                     #(a9)
            self.vector[i+1] |= right_bit >> 15                     #(a10)
        self._setbit(0, right_most_bit)                             #(a11)


    def shift_left_by_one(self):                                     #(b1)
        '''
        For a one-bit in-place left non-circular shift.  Note that
        bitvector size does not change.  The leftmost bit that moves
        past the first element of the bitvector is discarded and 
        rightmost bit of the returned vector is set to zero.
        '''
        size = len(self.vector)                                      #(b2)
        left_most_bits = map(operator.__and__, self.vector, [1]*size)
        left_most_bits.append(left_most_bits[0])                     #(b3)
        del(left_most_bits[0])                                       #(b4)
        self.vector = map(operator.__rshift__, self.vector, [1]*size)#(b5)
        self.vector = map( operator.__or__, self.vector, \
             map(operator.__lshift__, left_most_bits, [15]*size) )   #(b6)
        self._setbit(self.size -1, 0)                                #(b7)


    def shift_right_by_one(self):                                    #(c1)
        '''
        For a one-bit in-place right non-circular shift.  Note that
        bitvector size does not change.  The rightmost bit that moves
        past the last element of the bitvector is discarded and 
        leftmost bit of the returned vector is set to zero.
        '''
        size = len(self.vector)                                      #(c2)
        right_most_bits = map( operator.__and__,\
                               self.vector, [0x8000]*size )          #(c3)
        self.vector = \
             map( operator.__and__, self.vector, [~0x8000]*size )    #(c4)
        right_most_bits.insert(0, 0)                                 #(c5)
        right_most_bits.pop()                                        #(c6)
        self.vector = map(operator.__lshift__, self.vector, [1]*size)#(c7)
        self.vector = map( operator.__or__, self.vector, \
             map(operator.__rshift__, right_most_bits, [15]*size) )  #(c8)
        self._setbit(0, 0)                                           #(c9)


    def shift_left( self, n ):                                       #(d1)
        'For an in-place left non-circular shift by n bit positions'
        for i in range(n):                                           #(d2)
            self.shift_left_by_one()                                 #(d3)
    def shift_right( self, n ):                                      #(d4)
        'For an in-place right non-circular shift by n bit positions.'
        for i in range(n):                                           #(d5)
            self.shift_right_by_one()                                #(d6)


    # Allow array like subscripting for getting and setting:
    __getitem__ = _getbit                                            #(e1)

    def __setitem__(self, pos, item):                                #(e2)
        '''
        This is needed for both slice assignments and for index
        assignments.  It checks the types of pos and item to see if the
        call is for slice assignment.  For slice assignment, pos must be of
        type 'slice' and item of type BitVector.  For index assignment, the
        argument types are checked in the _setbit() method.
        '''      
        # The following section is for slice assignment:
        if isinstance( pos, slice ):                                 #(e3)
            if (not isinstance( item, BitVector )):                  #(e4)
                raise TypeError('For slice assignment, \
                        the right hand side must be a BitVector')    #(e5)
            if ( (pos.stop - pos.start) != len(item) ):              #(e6)
                raise ValueError('incompatible lengths for \
                                               slice assignment')    #(e7)
            for i in range( pos.start, pos.stop ):                   #(e8)
                self[i] = item[ i - pos.start ]                      #(e9)
            return                                                  #(e10)
        # For index assignment use _setbit()
        self._setbit( pos, item )                                   #(e11)


    def __getslice__(self, i, j):                                    #(f1)
        'Allow slicing with [i:j], [:], etc.'
        slicebits = []                                               #(f2)
        if j > self.size: j = self.size                              #(f3)
        for x in range(i,j):                                         #(f4)
            slicebits.append( self[x] )                              #(f5)
        return BitVector( bitlist = slicebits )                      #(f6)


    # Allow len() to work:
    __len__ = _getsize                                               #(g1)
    # Allow int() to work:
    __int__ = intValue                                               #(g2)

    def __iter__( self ):                                            #(g3)
        '''
        To allow iterations over a bit vector by supporting the 'for bit in
        bit_vector' syntax:
        '''
        return BitVectorIterator( self )                             #(g4)


    def __str__( self ):                                             #(h1)
        'To create a print representation'
        if self.size == 0:                                           #(h2)
            return ''                                                #(h3)
        return ''.join( map( str, self ) )                           #(h4)


    # Compare two bit vectors:
    def __eq__(self, other):                                         #(i1)
        if self.size != other.size:                                  #(i2)
            return False                                             #(i3)
        i = 0                                                        #(i4)
        while ( i < self.size ):                                     #(i5)
            if (self[i] != other[i]): return False                   #(i6)
            i += 1                                                   #(i7)
        return True                                                  #(i8)
    def __ne__(self, other):                                         #(i9)
        return not self == other                                    #(i10)
    def __lt__(self, other):                                        #(i11)
        return self.intValue() < other.intValue()                   #(i12)
    def __le__(self, other):                                        #(i13)
        return self.intValue() <= other.intValue()                  #(i14)
    def __gt__(self, other):                                        #(i15)
        return self.intValue() > other.intValue()                   #(i16)
    def __ge__(self, other):                                        #(i17)
        return self.intValue() >= other.intValue()                  #(i18)


    def _make_deep_copy( self ):                                     #(j1)
        'Make a deep copy of a bit vector'
        copy = str( self )                                           #(j2)
        return BitVector( bitstring = copy )                         #(j3)
    def _resize_pad_from_left( self, n ):                            #(j4)
        '''
        Resize a bit vector by padding with n 0's from the left. Return the
        result as a new bit vector.
        '''
        new_str = '0'*n + str( self )                                #(j5)
        return BitVector( bitstring = new_str )                      #(j6)
    def _resize_pad_from_right( self, n ):                           #(j7)
        '''
        Resize a bit vector by padding with n 0's from the right. Return
        the result as a new bit vector.
        '''
        new_str = str( self ) + '0'*n                                #(j8)
        return BitVector( bitstring = new_str )                      #(j9)
    def pad_from_left( self, n ):                                   #(j10)
        'Pad a bit vector with n zeros from the left'
        new_str = '0'*n + str( self )                               #(j11)
        bitlist =  map( int, list(new_str) )                        #(j12)
        self.size = len( bitlist )                                  #(j13)
        two_byte_ints_needed = (len(bitlist) + 15) // 16            #(j14)
        self.vector = array.array( 'H', [0]*two_byte_ints_needed )  #(j15)
        map( self._setbit, enumerate(bitlist), bitlist)             #(j16)
    def pad_from_right( self, n ):                                  #(j17)
        'Pad a bit vector with n zeros from the right'
        new_str = str( self ) + '0'*n                               #(j18)
        bitlist =  map( int, list(new_str) )                        #(j19)
        self.size = len( bitlist )                                  #(j20)
        two_byte_ints_needed = (len(bitlist) + 15) // 16            #(j21)
        self.vector = array.array( 'H', [0]*two_byte_ints_needed )  #(j22)
        map( self._setbit, enumerate(bitlist), bitlist)             #(j23)


    def __contains__( self, otherBitVec ):                           #(k1)
        '''
        This supports 'if x in y' and 'if x not in y' syntax for bit
        vectors.
        '''
        if self.size == 0:                                           #(k2)
              raise ValueError, "First arg bitvec has no bits"       #(k3)
        elif self.size < otherBitVec.size:                           #(k4)
              raise ValueError, "First arg bitvec too short"         #(k5)
        max_index = self.size - otherBitVec.size + 1                 #(k6)
        for i in range(max_index):                                   #(k7)
              if self[i:i+otherBitVec.size] == otherBitVec:          #(k8)
                    return True                                      #(k9)
        return False                                                #(k10)


    def reset( self, val ):                                          #(m1)
        '''
        Resets a previously created BitVector to either all zeros or all
        ones depending on the argument val.  Returns self to allow for
        syntax like
               bv = bv1[3:6].reset(1)
        or
               bv = bv1[:].reset(1)
        '''
        if val not in (0,1):                                         #(m2)
            raise ValueError( "Incorrect reset argument" )           #(m3)
        bitlist = [val for i in range( self.size )]                  #(m4)
        map( self._setbit, enumerate(bitlist), bitlist )             #(m5)
        return self                                                  #(m6)


    def count_bits( self ):                                          #(n1)
        '''
        Return the number of bits set in a BitVector instance.
        '''
        return reduce( lambda x, y: int(x)+int(y), self )            #(n2)


    def setValue(self, *args, **kwargs ):                            #(p1)
        '''
        Changes the bit pattern associated with a previously constructed
        BitVector instance.  The allowable modes for changing the internally
        stored bit pattern are the same as for the constructor.
        '''
        self.__init__( *args, **kwargs )                             #(p2)


    def count_bits_sparse( self ):                                   #(q1)
        '''
        For sparse bit vectors, this method, contributed by Rhiannon, will
        be much faster.  She estimates that if a bit vector with over 2
        millions bits has only five bits set, this will return the answer
        in 1/18 of the time taken by the count_bits() method.  Note
        however, that count_bits() may work much faster for dense-packed
        bit vectors.  Rhianon's implementation is based on an algorithm
        generally known as the Brian Kernighan's way, although its
        antecedents predate its mention by Kernighan and Ritchie.
        '''
        num = 0                                                      #(q2)
        for intval in self.vector:                                   #(q3)
            if intval == 0: continue                                 #(q4)
            c = 0; iv = intval                                       #(q5)
            while iv > 0:                                            #(q6)
                iv = iv & (iv -1)                                    #(q7)
                c = c + 1                                            #(q8)
            num = num + c                                            #(q9)
        return num                                                  #(q10)


    def jaccard_similarity( self, other ):                           #(r1)
        ''' 
        Computes the Jaccard similarity coefficient between two bit vectors
        '''
        assert self.size == other.size, 'vectors of unequal length'  #(r2)
        intersect = self & other                                     #(r3)
        union = self | other                                         #(r4)
        return ( intersect.count_bits_sparse()\
                  / float( union.count_bits_sparse() ) )             #(r5)
    def jaccard_distance( self, other ):                             #(r6)
        ''' 
        Computes the Jaccard distance between two bit vectors
        '''
        assert self.size == other.size, 'vectors of unequal length'  #(r7)
        return 1 - self.jaccard_similarity( other )                  #(r8)
    def hamming_distance( self, other ):                             #(r9)
        '''
        Computes the Hamming distance between two bit vectors
        '''
        assert self.size == other.size, 'vectors of unequal length' #(r10)
        diff = self ^ other                                         #(r11)
        return diff.count_bits_sparse()                             #(r12)


    def next_set_bit(self, from_index=0):                            #(s1)
        '''
        This method, contributed by Jason Allum, calculates the number of
        bit positions from the current position index to the next set bit.
        '''
        assert from_index >= 0, 'from_index must be nonnegative'     #(s2)
        i = from_index                                               #(s3)
        v = self.vector                                              #(s4)
        l = len(v)                                                   #(s5)
        o = i >> 4                                                   #(s6)
        m = 1 << (i & 0x0F)                                          #(s7)
        while o < l:                                                 #(s8)
            h = v[o]                                                 #(s9)
            if h:                                                   #(s10)
                while m != (1 << 0x10):                             #(s11)
                    if h & m: return i                              #(s12)
                    m <<= 1                                         #(s13)
                    i += 1                                          #(s14)
            else:                                                   #(s15)
                i += 0x10                                           #(s16)
            m = 1                                                   #(s17)
            o += 1                                                  #(s18)
        return -1                                                   #(s19)


    def rank_of_bit_set_at_index( self, position ):                  #(t1)
        '''
        For a bit that is set at the argument 'position', this method
        returns how many bits are set to the left of that bit.  For
        example, in the bit pattern 000101100100, a call to this method
        with position set to 9 will return 4.
        '''
        assert self[position] == 1, 'the arg bit not set'
        bv = self[0:position+1]                                      #(t2)
        return bv.count_bits()                                       #(t3)
    def isPowerOf2( self ):                                          #(t4)
        '''
        Determines whether the integer value of a bit vector is a power of
        2.
        '''
        if self.intValue() == 0: return False                        #(t5)
        bv = self & BitVector( intVal = self.intValue() - 1 )        #(t6)
        if bv.intValue() == 0: return True                           #(t7)
        return False                                                 #(t7)
    def isPowerOf2_sparse( self ):                                   #(t8)
        '''
        Faster version of isPowerOf2() for sparse bit vectors
        '''
        if self.count_bits_sparse() == 1: return True                #(t9)
        return False                                                #(t10)


    def reverse( self ):                                             #(u1)
        '''
        Returns a new bit vector by reversing the bits in the bit vector on
        which the method is invoked.
        '''
        reverseList = []                                             #(u2)
        i = 1                                                        #(u3)
        while ( i < self.size + 1 ):                                 #(u4)
            reverseList.append( self[ -i ] )                         #(u5)
            i += 1                                                   #(u6)
        return BitVector( bitlist = reverseList )                    #(u7)


    def gcd( self, other ):                                          #(v1)
        ''' 
        Using Euclid's Algorithm, returns the greatest common divisor of
        the integer value of the bit vector on which the method is invoked
        and the integer value of the argument bit vector.
        '''
        a = self.intValue(); b = other.intValue()                    #(v2)
        if a < b: a,b = b,a                                          #(v3)
        while b != 0:                                                #(v4)
            a, b = b, a % b                                          #(v5)
        return BitVector( intVal = a )                               #(v6)
    def multiplicative_inverse( self, modulus ):                     #(v7)
        '''
        Calculates the multiplicative inverse of a bit vector modulo the
        bit vector that is supplied as the argument. Code based on the
        Extended Euclid's Algorithm.
        '''
        MOD = mod = modulus.intValue(); num = self.intValue()        #(v8)
        x, x_old = 0L, 1L                                            #(v9)
        y, y_old = 1L, 0L                                           #(v10)
        while mod:                                                  #(v11)
            quotient = num // mod                                   #(v12)
            num, mod = mod, num % mod                               #(v13)
            x, x_old = x_old - x * quotient, x                      #(v14)
            y, y_old = y_old - y * quotient, y                      #(v15)
        if num != 1:                                                #(v16)
            return None                                             #(v17)
        else:                                                       #(v18)
            MI = (x_old + MOD) % MOD                                #(v19)
            return BitVector( intVal = MI )                         #(v20)


    def length(self):                                                #(w1)
        return self.size                                             #(w2)
    def deep_copy(self):                                             #(w3)
        return self._make_deep_copy()                                #(w4)


    def gf_multiply(self, b):                                        #(x1)
        '''
        In the set of polynomials defined over GF(2), multiplies
        the bitvector on which the method is invoked with the 
        bitvector b.  Returns the product bitvector.
        '''
        a = self.deep_copy()                                         #(x2)
        b_copy = b.deep_copy()                                       #(x3)
        a_highest_power = a.length() - a.next_set_bit(0) - 1         #(x4)
        b_highest_power = b.length() - b_copy.next_set_bit(0) - 1    #(x5)
        result = BitVector( size = a.length()+b_copy.length() )      #(x6)
        a.pad_from_left( result.length() - a.length() )              #(x7)
        b_copy.pad_from_left( result.length() - b_copy.length() )    #(x8)
        for i,bit in enumerate(b_copy):                              #(x9)
            if bit == 1:                                            #(x10)
                power = b_copy.length() - i - 1                     #(x11)
                a_copy = a.deep_copy()                              #(x12)
                a_copy.shift_left( power )                          #(x13)
                result ^=  a_copy                                   #(x14)
        return result                                               #(x15)


    def gf_divide(self, mod, n):                                    #(y1)
        '''
        Carries out modular division of a bitvector by the 
        modulus bitvector mod in GF(2^n) finite field.
        Returns both the quotient and the remainder.
        '''
        num = self                                                  #(y2)
        if mod.length() > n+1:                                      #(y3)
            raise ValueError("Modulus bit pattern too long")        #(y4)
        quotient = BitVector( intVal = 0, size = num.length() )     #(y5)
        remainder = num.deep_copy()                                 #(y6)
        i = 0                                                       #(y7)
        while 1:                                                    #(y8)
            i = i+1                                                 #(y9)
            if (i==num.length()): break                            #(y10)
            mod_highest_power = mod.length()-mod.next_set_bit(0)-1 #(y11)
            if remainder.next_set_bit(0) == -1:                    #(y12)
                remainder_highest_power = 0                        #(y13)
            else:                                                  #(y14)
                remainder_highest_power = remainder.length() \
                                  - remainder.next_set_bit(0) - 1  #(y15)
            if (remainder_highest_power < mod_highest_power) \
                  or int(remainder)==0:                            #(y16)
                break                                              #(y17)
            else:                                                  #(y18)
                exponent_shift = remainder_highest_power \
                                            - mod_highest_power    #(y19)
                quotient[quotient.length()-exponent_shift-1] = 1   #(y20)
                quotient_mod_product = mod.deep_copy();            #(y21)
                quotient_mod_product.pad_from_left(remainder.length() - \
                                              mod.length() )       #(y22)
                quotient_mod_product.shift_left(exponent_shift)    #(y23)
                remainder = remainder ^ quotient_mod_product       #(y24)
        if remainder.length() > n:                                 #(y25)
            remainder = remainder[remainder.length()-n:]           #(y26)
        return quotient, remainder                                 #(y27)


    def gf_multiply_modular(self, b, mod, n):                       #(z1)
        '''
        Multiplies a bitvector with the bitvector b in GF(2^n)
        finite field with the modulus bit pattern set to mod
        '''
        a = self                                                    #(z2)
        a_copy = a.deep_copy()                                      #(z3)
        b_copy = b.deep_copy()                                      #(z4)
        product = a_copy.gf_multiply(b_copy)                        #(z5)
        quotient, remainder = product.gf_divide(mod, n)             #(z6)
        return remainder                                            #(z7)

    def gf_MI(self, mod, n):                                       #(gf1)
        '''
        Returns the multiplicative inverse of a vector in the GF(2^n)
        finite field with the modulus polynomial set to mod
        '''
        num = self                                                 #(gf2)
        NUM = num.deep_copy(); MOD = mod.deep_copy()               #(gf3)
        x = BitVector( size=mod.length() )                         #(gf3)
        x_old = BitVector( intVal=1, size=mod.length() )           #(gf4)
        y = BitVector( intVal=1, size=mod.length() )               #(gf5)
        y_old = BitVector( size=mod.length() )                     #(gf6)
        while int(mod):                                            #(gf7)
            quotient, remainder = num.gf_divide(mod, n)            #(gf8)
            num, mod = mod, remainder                              #(gf9)
            x, x_old = x_old ^ quotient.gf_multiply(x), x         #(gf10)
            y, y_old = y_old ^ quotient.gf_multiply(y), y         #(gf11)
        if int(num) != 1:                                         #(gf12)
            return "NO MI. However, the GCD of ", str(NUM), " and ", \
                                 str(MOD), " is ", str(num)       #(gf13)
        else:                                                     #(gf14)
            z = x_old ^ MOD                                       #(gf15)
            quotient, remainder = z.gf_divide(MOD, n)             #(gf16)
            return remainder                                      #(gf17)


#-----------------------  BitVectorIterator Class -----------------------

class BitVectorIterator:                                            #(IT1)
    def __init__( self, bitvec ):                                   #(IT2)
        self.items = []                                             #(IT3)
        for i in range( bitvec.size ):                              #(IT4)
            self.items.append( bitvec._getbit(i) )                  #(IT5)
        self.index = -1                                             #(IT6)
    def __iter__( self ):                                           #(IT7)
        return self                                                 #(IT8)
    def next( self ):                                               #(IT9)
        self.index += 1                                            #(IT10)
        if self.index < len( self.items ):                         #(IT11)
            return self.items[ self.index ]                        #(IT12)
        else:                                                      #(IT13)
            raise StopIteration                                    #(IT14)

#------------------------  End of Class Definition -----------------------

#------------------------     Test Code Follows    -----------------------

if __name__ == '__main__':

    # Construct a bit vector of size 0
    print "\nConstructing a bit vector of size 0:"
    bv1 = BitVector( size = 0 )
    print bv1                                   # no output

    # Construct a bit vector of size 2:
    print "\nConstructing a bit vector of size 2:"
    bv2 = BitVector( size = 2 )
    print bv2                                   # 00

    # Joining two bit vectors:
    print "\nOutput concatenation of two previous bit vectors:"
    print bv1 + bv2                             # 00

    # Construct a bit vector with a tuple of bits:
    print "\nThis is a bit vector from a tuple of bits:"
    bv = BitVector( bitlist = (1, 0, 0, 1) )
    print bv                                    # 1001

    # Construct a bit vector with a list of bits:    
    print "\nThis is a bit vector from a list of bits:"
    bv = BitVector( bitlist = [1, 1, 0, 1] )
    print bv                                    # 1101
    
    # Construct a bit vector from an integer
    bv = BitVector( intVal = 5678 )
    print "\nBit vector constructed from integer 5678:"
    print bv                                    # 1011000101110
    print "\nBit vector constructed from integer 0:"
    bv = BitVector( intVal = 0 )
    print bv                                    # 0
    print "\nBit vector constructed from integer 2:"
    bv = BitVector( intVal = 2 )
    print bv                                    # 10
    print "\nBit vector constructed from integer 3:"
    bv = BitVector( intVal = 3 )
    print bv                                    # 11
    print "\nBit vector constructed from integer 123456:"
    bv = BitVector( intVal = 123456 )
    print bv                                    # 11110001001000000
    print "\nInt value of the previous bit vector as computed by intVal():"
    print bv.intValue()                         # 123456
    print "\nInt value of the previous bit vector as computed by int():"
    print int( bv )                             # 123456

    # Construct a bit vector directly from a file-like object:
    import StringIO
    x = "111100001111"
    fp_read = StringIO.StringIO( x )
    bv = BitVector( fp = fp_read )
    print "\nBit vector constructed directed from a file like object:"
    print bv                                    # 111100001111 

    # Construct a bit vector directly from a bit string:
    bv = BitVector( bitstring = '00110011' )
    print "\nBit Vector constructed directly from a string:"
    print bv                                    # 00110011

    bv = BitVector( bitstring = '' )
    print "\nBit Vector constructed directly from an empty string:"
    print bv                                    # nothing

    print "\nInteger value of the previous bit vector:"
    print bv.intValue()                         # 0

    # Test array-like indexing for a bit vector:
    bv = BitVector( bitstring = '110001' )
    print "\nPrints out bits individually from bitstring 110001:"
    print bv[0], bv[1], bv[2], bv[3], bv[4], bv[5]       # 1 1 0 0 0 1
    print "\nSame as above but using negative array indexing:"
    print bv[-1], bv[-2], bv[-3], bv[-4], bv[-5], bv[-6] # 1 0 0 0 1 1

    # Test setting bit values with positive and negative
    # accessors:
    bv = BitVector( bitstring = '1111' )
    print "\nBitstring for 1111:"
    print bv                                    # 1111

    print "\nReset individual bits of above vector:"
    bv[0]=0;bv[1]=0;bv[2]=0;bv[3]=0        
    print bv                                    # 0000
    print "\nDo the same as above with negative indices:"
    bv[-1]=1;bv[-2]=1;bv[-4]=1
    print bv                                    # 1011

    print "\nCheck equality and inequality ops:"
    bv1 = BitVector( bitstring = '00110011' )
    bv2 = BitVector( bitlist = [0,0,1,1,0,0,1,1] )
    print bv1 == bv2                            # True
    print bv1 != bv2                            # False
    print bv1 < bv2                             # False
    print bv1 <= bv2                            # True
    bv3 = BitVector( intVal = 5678 )
    print bv3.intValue()                        # 5678
    print bv3                                   # 10110000101110
    print bv1 == bv3                            # False
    print bv3 > bv1                             # True
    print bv3 >= bv1                            # True


    # Create a string representation of a bit vector:
    fp_write = StringIO.StringIO()
    bv.write_bits_to_fileobject( fp_write )
    print "\nGet bit vector written out to a file-like object:"
    print fp_write.getvalue()                   # 1011 

    print "\nExperiments with bitwise logical operations:"
    bv3 = bv1 | bv2                              
    print bv3                                   # 00110011
    bv3 = bv1 & bv2
    print bv3                                   # 00110011
    bv3 = bv1 + bv2
    print bv3                                   # 0011001100110011
    bv4 = BitVector( size = 3 )
    print bv4                                   # 000
    bv5 = bv3 + bv4
    print bv5                                   # 0011001100110011000
    bv6 = ~bv5
    print bv6                                   # 1100110011001100111
    bv7 = bv5 & bv6
    print bv7                                   # 0000000000000000000
    bv7 = bv5 | bv6
    print bv7                                   # 1111111111111111111

    print "\nTry logical operations on bit vectors of different sizes:"
    print BitVector( intVal = 6 ) ^ BitVector( intVal = 13 )   # 1011
    print BitVector( intVal = 6 ) & BitVector( intVal = 13 )   # 0100
    print BitVector( intVal = 6 ) | BitVector( intVal = 13 )   # 1111

    print BitVector( intVal = 1 ) ^ BitVector( intVal = 13 )   # 1100
    print BitVector( intVal = 1 ) & BitVector( intVal = 13 )   # 0001
    print BitVector( intVal = 1 ) | BitVector( intVal = 13 )   # 1101

    print "\nExperiments with setbit() and getsize():"
    bv7[7] = 0
    print bv7                                   # 1111111011111111111
    print len( bv7 )                            # 19
    bv8 = (bv5 & bv6) ^ bv7
    print bv8                                   # 1111111011111111111
    

    print "\nConstruct a bit vector from what is in the file testinput1.txt:"
    bv = BitVector( filename = 'TestBitVector/testinput1.txt' )
    #print bv                                    # nothing to show
    bv1 = bv.read_bits_from_file(64)    
    print "\nPrint out the first 64 bits read from the file:"
    print bv1
         # 0100000100100000011010000111010101101110011001110111001001111001
    print "\nRead the next 64 bits from the same file:"
    bv2 = bv.read_bits_from_file(64)    
    print bv2
         # 0010000001100010011100100110111101110111011011100010000001100110
    print "\nTake xor of the previous two bit vectors:"
    bv3 = bv1 ^ (bv2)
    print bv3
         # 0110000101000010000110100001101000011001000010010101001000011111

    print "\nExperiment with dividing an even-sized vector into two:"
    [bv4, bv5] = bv3.divide_into_two()
    print bv4                            # 01100001010000100001101000011010
    print bv5                            # 00011001000010010101001000011111

    # Permute a bit vector:
    print "\nWe will use this bit vector for experiments with permute()"
    bv1 = BitVector( bitlist = [1, 0, 0, 1, 1, 0, 1] )
    print bv1                                    # 1001101
    
    bv2 = bv1.permute( [6, 2, 0, 1] )
    print "\nPermuted and contracted form of the previous bit vector:"
    print bv2                                    # 1010

    print "\nExperiment with writing an internally generated bit vector out to a disk file:"
    bv1 = BitVector( bitstring = '00001010' ) 
    FILEOUT = open( 'TestBitVector/test.txt', 'wb' )
    bv1.write_to_file( FILEOUT )
    FILEOUT.close()
    bv2 = BitVector( filename = 'TestBitVector/test.txt' )
    bv3 = bv2.read_bits_from_file( 32 )
    print "\nDisplay bit vectors written out to file and read back from the file and their respective lengths:"
    print bv1, bv3
    print len(bv1), len(bv3)


    print "\nExperiments with reading a file from the beginning to end:"
    bv = BitVector( filename = 'TestBitVector/testinput4.txt' )
    print "\nHere are all the bits read from the file:"
    while (bv.more_to_read):
        bv_read = bv.read_bits_from_file( 64 )
        print bv_read
    print

    print "\nExperiment with closing a file object and start extracting bit vectors from the file from the beginning again:"
    bv.close_file_object()
    bv = BitVector( filename = 'TestBitVector/testinput4.txt' )
    bv1 = bv.read_bits_from_file(64)        
    print "\nHere are all the first 64 bits read from the file again after the file object was closed and opened again:"
    print bv1           
    FILEOUT = open( 'TestBitVector/testinput5.txt', 'wb' )
    bv1.write_to_file( FILEOUT )
    FILEOUT.close()

    print "\nExperiment in 64-bit permutation and unpermutation of the previous 64-bit bitvector:"
    print "The permutation array was generated separately by the Fisher-Yates shuffle algorithm:"
    bv2 = bv1.permute( [22, 47, 33, 36, 18, 6, 32, 29, 54, 62, 4,
                        9, 42, 39, 45, 59, 8, 50, 35, 20, 25, 49,
                        15, 61, 55, 60, 0, 14, 38, 40, 23, 17, 41,
                        10, 57, 12, 30, 3, 52, 11, 26, 43, 21, 13,
                        58, 37, 48, 28, 1, 63, 2, 31, 53, 56, 44, 24,
                        51, 19, 7, 5, 34, 27, 16, 46] )
    print "Permuted bit vector:"
    print bv2

    bv3 = bv2.unpermute( [22, 47, 33, 36, 18, 6, 32, 29, 54, 62, 4,
                          9, 42, 39, 45, 59, 8, 50, 35, 20, 25, 49,
                          15, 61, 55, 60, 0, 14, 38, 40, 23, 17, 41,
                          10, 57, 12, 30, 3, 52, 11, 26, 43, 21, 13,
                          58, 37, 48, 28, 1, 63, 2, 31, 53, 56, 44, 24,
                          51, 19, 7, 5, 34, 27, 16, 46] )    
    print "Unpurmute the bit vector:"
    print bv3
    print
    print

    print "\nTry circular shifts to the left and to the right for the following bit vector:"
    print bv3   # 0100000100100000011010000111010101101110011001110111001001111001
    print "\nCircular shift to the left by 7 positions:"
    bv3 << 7
    print bv3   # 1001000000110100001110101011011100110011101110010011110010100000

    print "\nCircular shift to the right by 7 positions:"
    bv3 >> 7
    print bv3   # 0100000100100000011010000111010101101110011001110111001001111001

    print "Test len() on the above bit vector:"
    print len( bv3 )                      # 64

    print "\nTest forming a [5:22] slice of the above bit vector:"
    bv4 = bv3[5:22]
    print bv4                             # 00100100000011010

    print "\nTest the iterator:"
    for bit in bv4:
        print bit,                        # 0 0 1 0 0 1 0 0 0 0 0 0 1 1 0 1 0
    print
    
    print "\nDemonstrate padding a bit vector from left:"
    bv = BitVector( bitstring = '101010' )
    bv.pad_from_left( 4 )
    print bv                              # 0000101010
    print "\nDemonstrate padding a bit vector from right:"
    bv.pad_from_right( 4 )
    print bv                              # 00001010100000

    print "\nTest the syntax 'if bit_vector_1 in bit_vector_2' syntax:"
    try:
        bv1 = BitVector( bitstring = '0011001100' )
        bv2 = BitVector( bitstring = '110011' )
        if bv2 in bv1:
            print "%s is in %s" % (bv2, bv1)
        else:
            print "%s is not in %s" % (bv2, bv1)
    except ValueError, arg:
        print "Error Message: " + str(arg)

    print "\nTest the size modifier when a bit vector is initialized with the intVal method:"
    bv = BitVector( intVal = 45, size = 16 )
    print bv                              # 0000000000101101
    bv = BitVector( intVal = 0, size = 8 )    
    print bv                              # 00000000
    bv = BitVector( intVal = 1, size = 8 )    
    print bv                              # 00000001

    print "\nTesting slice assignment:"
    bv1 = BitVector( size = 25 )
    print "bv1= ", bv1                    # 0000000000000000000000000
    bv2 = BitVector( bitstring = '1010001' )
    print "bv2= ", bv2                    # 1010001
    bv1[6:9]  = bv2[0:3]
    print "bv1= ", bv1                    # 0000001010000000000000000

    print "\nTesting reset function:"
    bv1.reset( 1 )             
    print "bv1= ", bv1                    # 1111111111111111111111111
    print bv1[3:9].reset(0)               # 000000
    print bv1[:].reset(0)                 # 0000000000000000000000000

    print "\nTesting count_bit():"
    bv = BitVector( intVal = 45, size = 16 )
    y = bv.count_bits()
    print y
    bv = BitVector( bitstring = '100111' )
    print bv.count_bits()
    bv = BitVector( bitstring = '00111000' )
    print bv.count_bits()
    bv = BitVector( bitstring = '001' )
    print bv.count_bits()
    bv = BitVector( bitstring = '00000000000000' )
    print bv.count_bits()

    print "\nTest setValue idea:"
    bv = BitVector( intVal = 7, size =16 )
    print bv                              # 0000000000000111
    bv.setValue( intVal = 45 )
    print bv                              # 101101

    print "\nTesting count_bits_sparse():"
    bv = BitVector( size = 2000000 )
    bv[345234] = 1
    bv[233]=1
    bv[243]=1
    bv[18]=1
    bv[785] =1
    print "The number of bits set: ", bv.count_bits_sparse()     # 5

    print "\nTesting Jaccard similarity and distance and Hamming distance:"
    bv1 = BitVector( bitstring = '11111111' )
    bv2 = BitVector( bitstring = '00101011' )
    print "Jaccard similarity: ", bv1.jaccard_similarity( bv2 )  # 0.5
    print "Jaccard distance: ", bv1.jaccard_distance( bv2 )      # 0.5
    print "Jaccard distance: ", bv1.hamming_distance( bv2 )      # 4

    print "\nTesting next_set_bit():"
    bv = BitVector( bitstring = '00000000000001' )
    print bv.next_set_bit( 5 )                                   # 13

    print "\nTesting rank_of_bit_set_at_index():"
    bv = BitVector( bitstring = '01010101011100' )
    print bv.rank_of_bit_set_at_index( 10 )                      # 6

    print "\nTesting isPowerOf2():"
    bv = BitVector( bitstring = '10000000001110' )
    print "int value: ", int( bv )                               # 826
    print bv.isPowerOf2()                                        # False
    print "\nTesting isPowerOf2_sparse():"              
    print bv.isPowerOf2_sparse()                                 # False

    print "\nTesting reverse():"
    bv = BitVector( bitstring = '0001100000000000001' )
    print "original bv: ", bv                    # 0001100000000000001
    print "reversed bv: ", bv.reverse()          # 1000000000000011000

    print "\nTesting Greatest Common Divisor (gcd):"
    bv1 = BitVector( bitstring = '01100110' )
    print "first arg bv: ", bv1, "   of int value: ", int(bv1)    # 102
    bv2 = BitVector( bitstring = '011010' ) 
    print "second arg bv: ", bv2, "   of int value: ", int(bv2)   # 26
    bv = bv1.gcd( bv2 )
    print "gcd is: ", bv, "   of int value: ", int(bv)            # 2

    print "\nTesting multiplicative_inverse:"
    bv_modulus = BitVector( intVal = 32 )
    print "modulus is bv: ", bv_modulus, "   of int value: ", int(bv_modulus)
    bv = BitVector( intVal = 17 ) 
    print "bv: ", bv, "   of int value: ", int(bv)
    result = bv.multiplicative_inverse( bv_modulus )
    if result is not None:
        print "MI is: ", result, "   of int value: ", int(result)
    else: print "No multiplicative inverse in this case"

    print "\nTest multiplication in GF(2):"
    a = BitVector( bitstring='0110001' )
    b = BitVector( bitstring='0110' )
    c = a.gf_multiply(b)
    print "Product of a=", a, " b=", b, " is ", c


    print "\nTest division in GF(2^n):"
    mod = BitVector( bitstring='100011011' )          # AES modulus
    n = 8
    a = BitVector( bitstring='11100010110001' )
    quotient, remainder = a.gf_divide(mod, n)
    print "Dividing a=", a, " by mod=", mod, " in GF(2^8) returns the quotient ", quotient, " and the remainder ", remainder


    print "\nTest modular multiplication in GF(2^n):"
    modulus = BitVector( bitstring='100011011' )     # AES modulus
    n = 8
    a = BitVector( bitstring='0110001' )
    b = BitVector( bitstring='0110' )
    c = a.gf_multiply_modular(b, modulus, n)
    print "Modular product of a=", a, " b=", b, " in GF(2^8) is ", c


    print "\nTest multiplicative inverses in GF(2^3) with " + \
                                   "modulus polynomial = x^3 + x + 1:"
    print "Find multiplicative inverse of a single bit array"
    modulus = BitVector( bitstring='100011011' )     # AES modulus
    n = 8
    a = BitVector( bitstring='00110011' )
    mi = a.gf_MI(modulus,n)
    print "Multiplicative inverse of ", a, " in GF(2^8) is", mi

    print "\nIn the following three rows shown, the first row shows the " +\
          "\nbinary code words, the second the multiplicative inverses," +\
          "\nand the third the product of a binary word with its" +\
          "\nmultiplicative inverse:\n"
    mod = BitVector( bitstring = '1011' )
    n = 3
    bitarrays = [BitVector(intVal=x, size=n) for x in range(1,2**3)]
    mi_list = [x.gf_MI(mod,n) for x in bitarrays]
    mi_str_list = [str(x.gf_MI(mod,n)) for x in bitarrays]
    print "bit arrays in GF(2^3): ", [str(x) for x in bitarrays]
    print "multiplicati_inverses: ", mi_str_list

    products = [ str(bitarrays[i].gf_multiply_modular(mi_list[i], mod, n)) \
                        for i in range(len(bitarrays)) ]
    print "bit_array * multi_inv: ", products


    # UNCOMMENT THE FOLLOWING LINES FOR
    # DISPLAYING ALL OF THE MULTIPLICATIVE 
    # INVERSES IN GF(2^8) WITH THE AES MODULUS:

#    print   
#    print "\nMultiplicative inverses in GF(2^8) with "  + \
#                      "modulus polynomial x^8 + x^4 + x^3 + x + 1:"
#    print "\n(This may take a few seconds)\n"
#    mod = BitVector( bitstring = '100011011' )
#    n = 8
#    bitarrays = [BitVector(intVal=x, size=n) for x in range(1,2**8)]
#    mi_list = [x.gf_MI(mod,n) for x in bitarrays]
#    mi_str_list = [str(x.gf_MI(mod,n)) for x in bitarrays]
#    print "\nMultiplicative Inverses:\n\n", mi_str_list
#
#    products = [ str(bitarrays[i].gf_multiply_modular(mi_list[i], mod, n)) \
#                        for i in range(len(bitarrays)) ]
#    print "\nShown below is the product of each binary code word " +\
#                     "in GF(2^3) and its multiplicative inverse:\n\n"
#    print products

