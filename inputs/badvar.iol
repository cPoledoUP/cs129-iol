IOL
    INT num IS 0 INT res IS 0
    STR msg1 STR msg2 STR msg3
    BEG msg1 BEG msg2
    BEG 31s
    NEWLN PRINT msg1 badvar INT dupvar
    NEWLN
    INTO res IS MULT num num
    PRINT msg2
    PRINT MULT num 2 STR dupvar
    NEWL!N
    PRINT msg3
    PRINT res
LOI