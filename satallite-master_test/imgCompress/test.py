import os

path = os.path.dirname(os.getcwd())

print path

png2j2k = path + '\\imgCompress\\transcoding\\openjpeg\\bin\\opj_compress.exe -i ' + path + '\\img\\lena1.png -o "' + path + '\\imgCompress\\transcoding\\transcoding\\Service Provider\\lena.j2k" -TP R'
j2k2part = 'cd ' + path + '\\imgCompress\\transcoding\\transcoding && transcoding.exe 2 enc.j2k part.j2k 3'
j2k2key = 'cd ' + path + '\\imgCompress\\transcoding\\transcoding && transcoding.exe 1 lena.j2k enc.j2k lena.key'

def img_encode_test():
    # print png2j2k
    # print j2k2key
    # print j2k2part
    if os.system(png2j2k) == 0:
        print 2
        if os.system(j2k2key) == 0:
            print 3
            if os.system(j2k2part) == 0:
                print 4
                
    print 1
img_encode_test()
    
