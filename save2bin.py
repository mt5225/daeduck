import binascii

hexstr ='4106110a0b0c3929013031303131303035320050332d324620482f452332b3ebb1a4000000000000b9dfbdc5b1e20000000000000000000000000000000000b5bfc0db0000000000'

binstr = binascii.unhexlify(hexstr)
with open('data/msg01.bin', 'wb') as fout:
    fout.write(binstr)


# read test
with open("./data/msg01.bin", "rb") as binary_file:
    buf = binary_file.read()
    print(binascii.hexlify(buf))