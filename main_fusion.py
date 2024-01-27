from func.functions import *
from dotenv import load_dotenv, find_dotenv
import os
import csv
from skimage.exposure import match_histograms
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt
from data_fusion.ihs.ihs import rgb_to_ihs
from data_fusion.a_wavelet.a_wavelet import fusion_twa_multiband
from data_fusion.evaluacion.evaluacion_calidad import (
    test_full_references,
    test_no_references,
    spectral_ERGAS,
    spatial_ERGAS
)

# ========== Carga de Direcciones y Variables de Entorno ==========

print("========== Iniciando Carga de Direcciones y Variables de Entorno ==========")
load_dotenv()

path_root = os.getcwd()
dir_file_type = os.getenv("name_folder")
dir_file_original_images_spectral = os.getenv("direccion_imagenes_ingreso_satelite")
dir_file_original_images_spatial = os.getenv("direccion_imagenes_ingreso_dron")
dir_file_proccesed_images = os.path.join(path_root, dir_file_type, 'processed_images')

spatial_imagen_name = os.getenv("name_image_spatial")
spectral_imagen_name = os.getenv("name_image_spectral")

# ========== Carga de Imágenes ==========

spatial_src = read_tif_image(dir_file_original_images_spatial, spatial_imagen_name)
spectral_src = read_tif_image(dir_file_original_images_spectral, spectral_imagen_name)

# ========== Preprocesamiento de Imágenes ==========

inter_spectral, metadata = resampling_spectral(spectral_src, spatial_src.height, spatial_src.width, 'bilinear') 
spectral_src.close()

# ========== Extracción de Bandas y Creación de Falsos Colores ==========

print("========== Iniciando Fusión de Datos ==========")
bands = get_RGB_bands_satellite_ndarray_and_other_bands(inter_spectral)
[red, green, blue] = bands[0:3]
other_bands = bands[3:]
image_rgb = ndarray_rgb(red, green, blue)

# ========== Creación de la Falsa Pancromática ==========

print("Creación de la falsa pancromática")
pancromatica = get_pancromatica(spatial_src)
spatial_src.close()
pancromatica = pancromatica.astype(np.float64)

# ========== Conversión RGB a IHS e Igualación de Histogramas ==========

print("RGB a IHS")
iv1v2 = rgb_to_ihs(image_rgb)
iv1v2 = iv1v2.astype(np.float64)

print("Igualación los histogramas")
pan_i = match_histograms(pancromatica, iv1v2[:, :, 0])
show_images([pancromatica, pan_i, iv1v2[:, :, 0]], dir_file_proccesed_images, 'gray')
show_hist([pancromatica, pan_i, iv1v2[:, :, 0]], dir_file_proccesed_images, 'gray')

# ========== Selección del Método de Fusión ==========

option = 0
while True:
    option = input("Escoja el método de fusión:\n 1. IHS\n 2. Atrous Wavelet\n")
    if option == "1" or option == "2":
        break
    print("Opción incorrecta")

pan_v1_v2 = iv1v2.copy()

if option == "1":
    # ========== Fusión con Método IHS ==========

    pan_v1_v2[:, :, 0] = pan_i

    print("Conversión de IHS a RGB")
    mask_matrix_to_rgb = [[1, 1/sqrt(6), 1/sqrt(6)], [1, 1/sqrt(6), -1/2], [1, -2/sqrt(6), 0]]
    merged_rgb_image = process_imag_to_another_model(pan_v1_v2, mask_matrix_to_rgb)

    print("Guardando datos fusionados")
    merged_rgb_image_8bits = merged_rgb_image.astype('uint8')
    new_spectral_image = merge_bands(merged_rgb_image_8bits, other_bands)
    resultado_name = f"{'IHS'}_{spectral_imagen_name}_{spatial_imagen_name}"

    with rasterio.open(os.path.join(dir_file_proccesed_images, f"{resultado_name}"),
                       'w',
                       **metadata,
                       ) as dst:
        for ix in range(new_spectral_image.shape[2]):
            dst.write(new_spectral_image[:, :, ix], ix+1)

elif option == "2":
    # ========== Fusión con Método Atrous Wavelet ==========

    fused_image_w = fusion_twa_multiband(image_rgb, pan_i, 5)

    print("Guardando datos fusionados")
    resultado_name = f"{'IHS'}_{spectral_imagen_name}_{spatial_imagen_name}"
    with rasterio.open(os.path.join(dir_file_proccesed_images, f"{resultado_name}"),
                       'w',
                       **metadata,
                       ) as dst:
        for ix in range(fused_image_w.shape[2]):
            dst.write(fused_image_w[:, :, ix], ix+1)


# ========== Evaluación de la Calidad de las Imágenes Fusionadas ==========

print("========== Evaluación de la Calidad de las Imágenes Fusionadas ==========")
# Original
ix_rgb_bands = [3, 2, 1]
# Dimensión espacial
spatial_image_src = read_tif_image(dir_file_original_images_spatial, spatial_imagen_name)
spatial_imagen = np.dstack([spatial_image_src.read(band) for band in ix_rgb_bands])
# Dimensión espectral
spectral_image_src = read_tif_image(dir_file_original_images_spectral, spectral_imagen_name)
spectral_imagen = np.dstack([spectral_image_src.read(band) for band in ix_rgb_bands])
# Resultado
resultado_image_src = read_tif_image(dir_file_proccesed_images, resultado_name)
resultado_imagen = np.dstack([resultado_image_src.read(band) for band in ix_rgb_bands])

# ERGAS espacial y espectral
ergas_x = spectral_ERGAS(spatial_imagen, resultado_imagen, 1/2, [1, 1, 1], 3)
with open(os.path.join(dir_file_proccesed_images, f"{'ergas_espectral'}_{spectral_imagen_name}_{spatial_imagen_name}"), "w", newline="") as f:
    writer = csv.writer(f)
    for test in ergas_x:
        writer.writerow(test)

ergas_s = spatial_ERGAS(spatial_imagen, np.transpose(inter_spectral, (1, 2, 0)), 1/2, [1, 1, 1], 3)
with open(os.path.join(dir_file_proccesed_images, f"{'ergas_espacial'}_{spectral_imagen_name}_{spatial_imagen_name}"), "w", newline="") as f:
    writer = csv.writer(f)
    for test in ergas_x:
        writer.writerow(test)

# Evaluación con librería Sewar
full_reference_espacial = test_full_references(spatial_imagen, resultado_imagen)
with open(os.path.join(dir_file_proccesed_images, f"{'full_reference_espacial'}_{spectral_imagen_name}_{spatial_imagen_name}"), "w", newline="") as f:
    writer = csv.writer(f)
    for test in full_reference_espacial:
        writer.writerow(test)

full_reference_espectral = test_full_references(np.transpose(inter_spectral, (1, 2, 0)), resultado_imagen)
with open(os.path.join(dir_file_proccesed_images, f"{'full_reference_espectral'}_{spectral_imagen_name}_{spatial_imagen_name}"), "w", newline="") as f:
    writer = csv.writer(f)
    for test in full_reference_espectral:
        writer.writerow(test)

full_no_reference = test_no_references(np.transpose(inter_spectral, (1, 2, 0)), pancromatica, resultado_imagen)
with open(os.path.join(dir_file_proccesed_images, f"{'full_no_reference'}_{spectral_imagen_name}_{spatial_imagen_name}"), "w", newline="") as f:
    writer = csv.writer(f)
    for test in full_no_reference:
        writer.writerow(test)