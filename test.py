import cv2
import numpy as np
import math
import os
import sys
from PIL import Image

usage = "python test.py image block_size(e.g. 8x8)"

astcenc_templates = {
    '1.7(fast)': 'astcenc-1.7.exe -c {} {} {} -time -fast',
    'sse2(fast)': 'astcenc-sse2.exe -cl {} {} {} -fast',
    'sse4.2(fast)': 'astcenc-sse4.2.exe -cl {} {} {} -fast',    
    'avx2(fast)': 'astcenc-avx2.exe -cl {} {} {} -fast',        
    '1.7(medium)': 'astcenc-1.7.exe -c {} {} {} -time -medium',
    'sse2(medium)': 'astcenc-sse2.exe -cl {} {} {} -medium',
    'sse4.2(medium)': 'astcenc-sse4.2.exe -cl {} {} {} -medium',    
    'avx2(medium)': 'astcenc-avx2.exe -cl {} {} {} -medium',            
}

def replace_path(image_path, old, new):
    li = image_path.rsplit(old, 1)
    return new.join(li)

def astc_encode_astcenc(cmd_template, bmp_path, astc_path, block_size):
    cmd = cmd_template.format(bmp_path, astc_path, block_size)
    print(cmd)
    os.system(cmd)

def astc_encode_ispc(bmp_path, astc_path, block_size):
    print('testing encoding via ispc(avx2)...')
    ispc_cmd = 'ispc-avx2\\test_astc.exe'
    cmd = '{} {} {} {}'.format(ispc_cmd, bmp_path, astc_path, block_size) 
    print(cmd)
    os.system(cmd)
    
    print('\ntesting encoding via ispc(avx512)...')
    ispc_cmd = 'ispc-avx512skx-i32x16\\test_astc.exe'
    cmd = '{} {} {} {}'.format(ispc_cmd, bmp_path, astc_path, block_size) 
    os.system(cmd)    
    
def astc_decode(astc_path):
    tga_path = replace_path(astc_path, '.astc', '.tga')
    decode_cmd = 'astcenc-1.7.exe'
    cmd = '{} -d {} {}'.format(decode_cmd, astc_path, tga_path)
    os.system(cmd)
    return tga_path
 
def psnr(img1, img2):
   mse = np.mean((img1/1.0 - img2/1.0) ** 2 )
   if mse < 1.0e-10:
      return 100
   return 10 * math.log10(255.0**2/mse)
   
def print_psnr(image_path1, image_path2):
    tmp_file1 = '_tmp1.bmp'
    tmp_file2 = '_tmp2.bmp'
    img1 = Image.open(image_path1)
    img2 = Image.open(image_path2)
    img1.save(tmp_file1)
    img2.save(tmp_file2)
    data1 = cv2.imread(tmp_file1)
    data2 = cv2.imread(tmp_file2)
    print('\n################')
    print("PSNR: %f" %(psnr(data1, data2)))
    print('################\n')
     
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(usage)
    else:
        bmp_path = sys.argv[1]
        block_size = sys.argv[2]

        astc_path = replace_path(bmp_path, '.bmp', '_' + block_size + '_ispc.astc')
        astc_encode_ispc(bmp_path, astc_path, block_size)
        tga_path = astc_decode(astc_path)
        print_psnr(bmp_path, tga_path)        

        for key in astcenc_templates:
            print('testing astcenc_{}...'.format(key))
            astc_path = replace_path(bmp_path, '.bmp', '_' + block_size + '_' + key + '.astc')
            astc_encode_astcenc(astcenc_templates[key], bmp_path, astc_path, block_size)
            tga_path = astc_decode(astc_path)
            print_psnr(bmp_path, tga_path)


