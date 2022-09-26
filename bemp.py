class Bemp:

    def __init__(self):
        self.method = "ASCII"
        self.speed = 38400
        self.bytesize = 8
        self.parity = "N"
        self.stopbits = 1
        self.address = 1
        self.di_count_address = 0x100
        self.di_start_address = 0x500
        self.di_count = 96
