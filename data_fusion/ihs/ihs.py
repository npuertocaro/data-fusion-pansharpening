from func.functions import process_imag_to_another_model 
from math import sqrt

def rgb_to_ihs(image_rgb):
    mask_matrix = [[1/3,1/3,1/3], [1/sqrt(6), 1/sqrt(6),-2/sqrt(6)], [1/sqrt(2), -1/sqrt(2), 0]]
    return process_imag_to_another_model(image_rgb,mask_matrix)

