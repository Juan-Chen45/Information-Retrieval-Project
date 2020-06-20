'''
在构建索引过程中储存索引用的压缩算法
'''

def vbencodenumber(n):
    bites = []
    while True:
        bites.insert(0, n % 128)
        bites[0] = bites[0]
        if n < 128:
            break
        n = n // 128
    bites[-1] = bites[-1] + 128
    return bites

def vbencode(numbers):
    bitestream = []
    for n in numbers:
        bites = vbencodenumber(n)
        bitestream = bitestream + bites
    return bytes(bitestream)

def vbdecode(bitestream):
    numbers = []
    n = 0
    # print ("Length: "+str(len(bitestream)))
    for i in range(len(bitestream)):
        if bitestream[i] < 128:
            n = 128*n + bitestream[i]
        else:
            n = 128*n + (bitestream[i] - 128)
            numbers.append(n)
            n = 0
    return numbers


