import numpy as np
import cv2
from scipy import signal

#Filtro para degradar las imágenes en planos Wavelet
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

def a_wavelet(pan_i, i):
    """
    Realiza la transformada wavelet a trous.

    Args:
        pan_i (array): Imagen pancromática.
        i (array): Imagen original.

    Returns:
        array: Imagen fusionada mediante la transformada wavelet a trous.
    """
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

# Código adaptado de PyOSIF: Optical Satellite Imagery Fusion Based on Multiresolution Approaches
# Repositorio: https://github.com/JiahaoJZ/PyOSIF-Optical-satellite-imagery-fusion-based-on-multirresolution-approaches

# Filtro base utilizado para degradar las imágenes en 
base_filter = 1/256 * np.array([[1, 4, 6, 4 ,1],
[4, 16, 24, 16, 4],
[6, 24, 36, 24, 6],
[4, 16, 24, 16, 4],
[1, 4, 6, 4 ,1]])

def obtain_filter(n=0,base_filter=base_filter):
    """
    Obtiene un filtro para degradar la imagen.

    Args:
        n (int): Número de filas y columnas de ceros a agregar al filtro.
        base_filter (array): Filtro base.

    Returns:
        array: Filtro modificado.
    """
    filter = []
    for row in base_filter:
        filter.append(put_n_zeros(row, n))
    return put_n_rows_of_zeros(filter,n)

def put_n_zeros(row, n):
    """
    Agrega ceros a una fila del filtro.

    Args:
        row (array): Fila original del filtro.
        n (int): Número de ceros a agregar.

    Returns:
        array: Fila con ceros agregados.
    """
    result = [row[0]]
    for i in range(1,len(row)):
        result += [0]*n + [row[i]]
    return result

def put_n_rows_of_zeros(matrix, n):
    """
    Agrega filas de ceros entre cada fila de la matriz original.

    Parameters:
    - matrix: Matriz original a la cual se agregarán filas de ceros.
    - n: Número de filas de ceros a agregar entre cada fila de la matriz original.

    Returns:
    - result: Matriz resultante con filas de ceros agregadas.
    """
    zeros = np.zeros((n,len(matrix[0])))
    result = [matrix[0]]
    for i in range(1,len(matrix)):
        result = np.concatenate((result, zeros, [matrix[i]]))
    return result

def twa(arr1, levels, init_level=0):
    """
    Aplica la transformada Wavelet à trous a una imagen.

    Parameters:
    - arr1: Imagen de entrada a la cual se aplicará la transformada.
    - levels: Número de niveles de resolución para aplicar la transformada.
    - init_level: Nivel inicial para comenzar la degradación (por defecto es 0).

    Returns:
    - coefs: Coeficientes de la transformada Wavelet à trous.
    - current_degradation: Imagen degradada en el último nivel de la transformada.
    """
    # Init variables
    previous_degradation = np.array(arr1)
    current_degradation = []
    coefs = np.empty([arr1.shape[0],arr1.shape[1],0])
    # Apply levels - init_level degradations
    for level in range(init_level, levels):
        # Obtain the filter for each level
        a_trous_filter = obtain_filter(level)
        # Convolution between the image and the filter
        current_degradation = signal.convolve2d(previous_degradation, a_trous_filter, mode='same')
        # Obtain the wavelet coefficients
        current_coef = previous_degradation-current_degradation
        current_coef = np.expand_dims(current_coef, axis=2)
        coefs = np.append(coefs, current_coef, axis=2)
        previous_degradation = current_degradation
    return coefs, current_degradation

def fusion_twa_multiband(xs, pan, levels, init_level=0):
    """
    Fusiona imágenes multibanda utilizando la transformada Wavelet à trous.

    Parameters:
    - xs: Imágenes multibanda a fusionar (tensor tridimensional).
    - pan: Imagen pancromática utilizada para la fusión.
    - levels: Número de niveles de resolución para la transformada.
    - init_level: Nivel inicial para comenzar la degradación (por defecto es 0).

    Returns:
    - fused_image: Imagen fusionada.
    """
    # Initialize image
    fused_image = np.empty([xs.shape[0], xs.shape[1], 0])
    # If the panchromatic image has more than one band, we use the first
    if pan.ndim > 2:
        pan = pan[:,:,0]
    # If the multispectral image has 3 bands or more, we start the fusion
    if xs.ndim > 2:
        for nBand in range(xs.shape[2]):
            img_nBand = fusion_twa_single_band(xs[:,:,nBand], pan, levels)
            img_nBand = np.expand_dims(img_nBand, axis=2)
            fused_image = np.append(fused_image, img_nBand, axis=2)
    else:
        print("The first argument must have the shape (x,y,z), received: " + str(xs.shape))
        fused_image = None
    return fused_image

def fusion_twa_single_band(xs, pan, levels, init_level=0):
    """
    Fusiona una banda específica utilizando la transformada Wavelet à trous.

    Parameters:
    - xs: Banda específica de la imagen multibanda a fusionar.
    - pan: Imagen pancromática utilizada para la fusión.
    - levels: Número de niveles de resolución para la transformada.
    - init_level: Nivel inicial para comenzar la degradación (por defecto es 0).

    Returns:
    - fused_band: Banda fusionada.
    """
    # Apply wavelet a trous to both bands, obtain the degradated band of the multiespectral band,
    # and the wavelet coefficients of the panchromatic image
    _, f_xs = twa(xs, levels)
    c_pan, _ = twa(pan, levels)
    # Add the coefficients
    coef_pan = np.sum(c_pan, axis=2)
    # Obtain the fused band
    fused_band = f_xs + coef_pan
    return fused_band
