import math
from sewar.full_ref import uqi, ergas, sam
from sewar.no_ref import d_lambda, d_s
import numpy as np

def test_full_references(original_imagen,proccesed_imagen):
    """
    Calcula índices de calidad full references.

    Args:
        original_imagen (array): La imagen original de referencia.
        proccesed_imagen (array): La imagen procesada que se compara con la imagen original.

    Returns:
        list: Lista de tuplas que contienen el nombre del índice y su valor.
    """
    return [("UQI", uqi(original_imagen, proccesed_imagen)),
            ("ERGAS", ergas(original_imagen, proccesed_imagen)),
            ("SAM: ", sam(original_imagen, proccesed_imagen))]

def test_no_references(spectral_imagen,pancromatica,proccesed_imagen):
    """
    Calcula índices de calidad no references.

    Args:
        spectral_imagen (array): La imagen multiespectral de referencia.
        pancromatica (array): La imagen pancromática utilizada en el proceso.
        proccesed_imagen (array): La imagen procesada que se compara con la imagen de referencia.

    Returns:
        list: Lista de tuplas que contienen el nombre del índice y su valor.
    """
    return [("D_Lambda", d_lambda(spectral_imagen, proccesed_imagen)),
            ("D_S", d_s(pancromatica, np.transpose(spectral_imagen,(1,0,2)), proccesed_imagen,q=1,r=1,ws=1))]

# Código adaptado de PyOSIF: Optical Satellite Imagery Fusion Based on Multiresolution Approaches
# Repositorio: https://github.com/JiahaoJZ/PyOSIF-Optical-satellite-imagery-fusion-based-on-multirresolution-approaches

def spectral_ERGAS(img_origND, img_fusND, ratio, coef_rad, n_band):
    """
    Calcula el índice ERGAS para imágenes espectrales.

    Args:
        img_origND (array): Imagen original antes de la conversión a radiancia (3D array).
        img_fusND (array): Imagen fusionada antes de la conversión a radiancia (3D array).
        ratio (float): Ratio de escala espectral.
        coef_rad (array): Coeficientes de radiación para cada banda.
        n_band (int): Número de bandas espectrales.

    Returns:
        float: Valor del índice ERGAS.
    """
    # Initialize variables
    img_orig = np.empty(img_origND.shape)
    img_fus = np.empty(img_fusND.shape)
    dif_imgs = np.empty(img_fusND.shape)
    mean_img_orig = np.empty(n_band)
    mean_img_fus = np.empty(n_band)
    std_imgs = np.empty(n_band)
    rmse_img_fus = np.empty(n_band)
    razon_img_fus = np.empty(n_band)

    for i in range(n_band):
        # Digital image to radiance
        img_orig[:,:,i] = img_origND[:,:,i]*coef_rad[i]
        img_fus[:,:,i] = img_fusND[:,:,i]*coef_rad[i]

        # Mean value of the radiances per band
        mean_img_orig[i] = img_orig[:,:,i].mean()
        mean_img_fus[i] = img_fus[:,:,i].mean()

        # Diference between the multispectral image and the fused image
        dif_imgs[:,:,i] = img_orig[:,:,i] - img_fus[:,:,i]
        std_imgs[i] = np.std(dif_imgs[:,:,i])

        # RMSE of the band
        rmse_img_fus[i] = (mean_img_orig[i] - mean_img_fus[i])**2 + std_imgs[i]**2

        # Image ratio
        razon_img_fus[i] = rmse_img_fus[i]/(mean_img_orig[i]**2)

    # Spectral ergas
    return 100*(ratio**2)*math.sqrt(razon_img_fus.mean())

def spatial_ERGAS(img_panND, img_fusND, ratio, coef_rad, n_band):
    """
    Calcula el índice ERGAS para imágenes espaciales.

    Args:
        img_panND (array): Imagen pancromática antes de la conversión a radiancia (2D array).
        img_fusND (array): Imagen fusionada antes de la conversión a radiancia (3D array).
        ratio (float): Ratio de escala espacial.
        coef_rad (array): Coeficientes de radiación para cada banda.
        n_band (int): Número de bandas espectrales.

    Returns:
        float: Valor del índice ERGAS.
    """
    # Initialize variables
    img_panc = np.empty(img_fusND.shape)
    img_fus = np.empty(img_fusND.shape)
    dif_imgs = np.empty(img_fusND.shape)
    img_pan_hist = np.empty(img_fusND.shape)
    mean_img_pan = np.empty(n_band)
    mean_img_multi = np.empty(n_band) # multi is the fused img
    rmse_img_fus = np.empty(n_band)
    razon_img_fus = np.empty(n_band)
    std_imgs = np.empty(n_band)

    for i in range(n_band):
        # Digital image to radiance
        img_panc[:,:,i] = img_panND*coef_rad[i]
        img_fus[:,:,i] = img_fusND[:,:,i]*coef_rad[i]

        # Mean value of the radiances per band
        mean_img_pan[i] = img_panc[:,:,i].mean()
        mean_img_multi[i] = img_fus[:,:,i].mean()

        # Histogram of the panchromatic image
        delta_media = mean_img_multi[i] - mean_img_pan[i]
        img_pan_hist[:,:,i] = img_panc[:,:,i] + delta_media

        # Mean value of the panchromatic image histogram
        mean_img_pan[i] = img_pan_hist[:,:,i].mean()

        # Diference between the panchromatic image and the fused image
        dif_imgs[:,:,i] = img_pan_hist[:,:,i] - img_fus[:,:,i]
        std_imgs[i] = np.std(dif_imgs[:,:,i])

        # RMSE of the band
        rmse_img_fus[i] = (mean_img_pan[i] - mean_img_multi[i])**2 + std_imgs[i]**2

        # Image ratio
        razon_img_fus[i] = rmse_img_fus[i]/(mean_img_pan[i]**2)

    # Spatial ERGAS
    return 100*(ratio**2)*math.sqrt(razon_img_fus.mean())