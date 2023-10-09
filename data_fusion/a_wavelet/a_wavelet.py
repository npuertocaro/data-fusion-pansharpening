import numpy as np
import cv2

#Filtro de paso bajo para extraer los planos Wavelet
filtro_5x5 = np.array([
    [1/256, 1/64, 3/128, 1/64, 1/256],
    [1/64, 1/16, 3/32, 1/16, 1/64],
    [3/128, 3/32, 9/64, 3/32, 3/128],
    [1/64, 1/16, 3/32, 1/16, 1/64],
    [1/256, 1/64, 3/128, 1/64, 1/256],
])
filtro_9x9 = np.array([
    [1/256, 0, 1/64, 0, 3/128, 0, 1/64, 0, 1/256],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1/64, 0, 1/16, 0, 3/32, 0, 1/16, 0, 1/64],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [3/128, 0, 3/32, 0, 9/64, 0, 3/32, 0, 3/128],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1/64, 0, 1/16, 0, 3/32, 0, 1/16, 0, 1/64],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1/256, 0, 1/64, 0, 3/128, 0, 1/64, 0, 1/256],
])

#Filtro de 5x5
def a_wavelet(pan_i, i):
    #Filtro de 5x5
    processed_image_f1 = cv2.filter2D(pan_i,-1,filtro_5x5)
    #Primer plano Wavelet Pan_I - El filtro 5x5
    w1 = pan_i - processed_image_f1
    #Filtro de 9x9
    processed_image_f2 = cv2.filter2D(pan_i,-1,filtro_9x9)
    #Segundo plano Wavelet Filtro 5x5 - Filtro 9x9
    w2 = processed_image_f1 - processed_image_f2
    #Se suma la intensidad por la suma de esos planos Wavelet
    N_INT = i + w1 + w2
    return N_INT