from collections import OrderedDict
import crc16 # https://code.google.com/p/pycrc16/

BYTESTUFF = { 
    0x8E: [ 0x9E, 0x81],
    0x9E: [ 0x9E, 0x91],
    0xAE: [ 0x9E, 0xA1]
}

BYTESDESTUFF = { 
    b'\x9E\x81' : 0x8E,
    b'\x9E\x91' : 0x9E,
    b'\x9E\xA1' : 0xAE
    }

#renders a dict into bytearray 
def renderToByteArray(fields):
    return bytearray().join([ba for k, ba in fields.items() ])
    
def byteStuff(ba):
    stuffed = []
    for byte in ba:
        if byte in BYTESTUFF:
            stuffed.append( BYTESTUFF[byte][0])
            stuffed.append( BYTESTUFF[byte][1])
        else:
            stuffed.append( byte)
    
    return bytearray(stuffed)

def byteUnstuff(ba):
    unstuffed = []
    skipme = False
    
    for pos in range(0, len(ba)-1):
        twobytes = ba[pos: pos+2]
        if bytes(twobytes) in BYTESDESTUFF:
            unstuffed.append(BYTESDESTUFF[bytes(ba[pos: pos+2])])
            skipme=True
        else:
            if not skipme:
                unstuffed.append(ba[pos])
            else:
                skipme=False

    if not skipme:
        unstuffed.append(ba[-1])
    
    return bytearray(unstuffed)
        
    
 # Returns: two bytes hex encoded string tuple (MSB, LSB)
def crc_to_hex(_crc):
    (_msb, _lsb) = crcformat(_crc)

    if len(_msb[2:]) is 1:
        hex_msb = '0' + _msb[2:]
    else:
        hex_msb = _msb[2:]

    if len(_lsb[2:]) is 1:
        hex_lsb = '0' + _lsb[2:]
    else:
        hex_lsb = _lsb[2:]

    return (hex_msb, hex_lsb)
    
# Returns: two bytes hex tuple (MSB, LSB)
def crcformat(crc):
    msb = hex(crc >> 8)
    lsb = hex(crc & 0x00FF)
    return (msb, lsb)

# FSLP format:         |startflag|channelnumber|payload|checksum|endflag|
class Frame():
    fields = OrderedDict ([
        ('channel'        ,     bytearray([0x00])),
        ('payload'        ,     bytearray()),
        ('crc16'          ,     bytearray(2))
    ])
    
    _startflag = bytearray([0x8E])
    _endflag   = bytearray([0xAE])
    
    def __init__(self, payload = bytearray()):
        self.fields['payload'] = payload
        
    def raw(self):
        assert (len(self.fields['channel'])==1)
        #compute crc
        _crc = crc16.crc16xmodem(bytes(self.fields['channel']+self.fields['payload']), 0x1d0f)
        (_x, _y) = crc_to_hex(_crc) 
        self.fields['crc16'] = bytearray.fromhex(_x) + bytearray.fromhex(_y)
        assert (len(self.fields['crc16'])==2)
        packet = byteStuff(renderToByteArray(self.fields))
        return self._startflag + packet + self._endflag
        

# FBP format:         |sequencenumber|commandid|commandstatus|databytes
class Fbp():
    fields = OrderedDict ([
        ('sequencenumber' ,     bytearray([0x42, 0xAE, 0x42, 0x9E])),
        ('commandid'      ,     bytearray(4)),
        ('commandstatus'  ,     bytearray([0xFF, 0xFF, 0xFF, 0xFF])),
        ('data'           ,     bytearray())
    ])
    
    def __init__(self, commandid, data=bytearray()):
        self.fields['commandid']= commandid
        self.fields['data'] = data
    
    def raw(self):
        assert (len(self.fields['sequencenumber'])==4)
        assert (len(self.fields['commandid'])==4)
        assert (len(self.fields['commandstatus'])==4)
        return renderToByteArray(self.fields)

# END 
