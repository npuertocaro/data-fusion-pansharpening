from func.functions import *
import matplotlib.pyplot as plt
from dotenv import load_dotenv, find_dotenv
import os
import csv
from data_fusion.ihs.ihs import rgb_to_ihs
from data_fusion.a_wavelet.a_wavelet import a_wavelet
from data_fusion.evaluacion.evaluacion_calidad import test_full_references, test_no_references
from skimage.exposure import match_histograms
import cv2
import numpy as np
from math import sqrt

#Cargar direcciones (path) y buscar las variables de entorno
load_dotenv()

path_root = os.getcwd()
dir_file_type = os.getenv("name_folder")
dir_file_original_images_spectral = os.getenv("direccion_imagenes_ingreso_satelite")
dir_file_original_images_spatial = os.getenv("direccion_imagenes_ingreso_dron")
dir_file_proccesed_images = os.path.join(path_root,dir_file_type,'processed_images')

spatial_imagen_name = os.getenv("name_image_spatial")
spectral_imagen_name = os.getenv("name_image_spectral")

#Cargar las imágenes
spatial_src = read_tif_image(dir_file_original_images_spatial,spatial_imagen_name)
spectral_src = read_tif_image(dir_file_original_images_spectral,spectral_imagen_name)
print(spatial_src.shape)
print(spectral_src.shape)

#Leo la imagen y reesampling, el metadata me guarda los datos originales de la espectral
print("Leyendo imágenes y haciendo resampling")
inter_spectral, metadata = resampling_spectral(spectral_src,spatial_src.height,spatial_src.width,'bilinear') 
spectral_src.close()
print(inter_spectral.shape)

print(metadata, spectral_src)

# Cargar las bandas y se guardan como una lista de bandas separadas
print("Cargar las bandas y se guardan como una lista de bandas separadas")
bands = get_RGB_bands_satellite_ndarray_and_other_bands(inter_spectral)
[red,green,blue] = bands[0:3]
other_bands = bands[3:]
image_rgb = ndarray_rgb(red,green,blue)
print(image_rgb.shape)

# Creacion de la falsa pancromatica
print("Creación de la falsa pancromática")
pancromatica = get_pancromatica(spatial_src)
spatial_src.close()
pancromatica = pancromatica.astype(np.float64)

#RGB TO IHS
print("RGB a IHS")
iv1v2 = rgb_to_ihs(image_rgb)
iv1v2 = iv1v2.astype(np.float64)

#Ecualizar los histogramas
print("Ecualizar los histogramas")
pan_i = match_histograms(pancromatica,iv1v2[:,:,0])
#cv2.imwrite(os.path.join(dir_file_proccesed_images,"Imagen_ecualizada.png"),pan_i.astype('int64'))
show_images([pancromatica,pan_i,iv1v2[:,:,0]],dir_file_proccesed_images, 'gray')
show_hist([pancromatica,pan_i,iv1v2[:,:,0]],dir_file_proccesed_images, 'blue')

#Preguntar qué método de fusión quiere ejecutar
option = 0
while(True):
    option = input("Escoja el método de fusión: \n 1. IHS \n 2. Atrous Wavelet \n")
    if(option == "1" or option == "2"):
        break
    print("Opción incorrecta")

pan_v1_v2 = iv1v2.copy()

if(option == "1"):
    pan_v1_v2[:,:,0] = pan_i
elif(option == "2"):
    N_INT = a_wavelet(pan_i, iv1v2[:,:,0])
    pan_v1_v2[:,:,0] = N_INT

#Conversión de IHS a RGB
print("Conversión de IHS a RGB")
mask_matrix_to_rgb = [[1 ,1/sqrt(6), 1/sqrt(6)],[1, 1/sqrt(6), -1/2],[1, -2/sqrt(6), 0]]
merged_rgb_image = process_imag_to_another_model(pan_v1_v2,mask_matrix_to_rgb)

#Guardar datos fusionados
print("Guardando datos fusionados...")
merged_rgb_image_8bits = merged_rgb_image.astype('uint8')
new_spectral_image = merge_bands(merged_rgb_image_8bits,other_bands)

resultado_name = f"{'wavelet_resultado'if option=='2' else 'ihs_resultado'}_{spectral_imagen_name}"

with rasterio.open(os.path.join(dir_file_proccesed_images,f"{resultado_name}"), 
                'w',
                **metadata,
                ) as dst:
        for ix in range(new_spectral_image.shape[2]):
            dst.write(new_spectral_image[:,:,ix], ix+1)

#Cálculo de indices de calidad

#Original
ix_rgb_bands = [3,2,1]
#Dimension espacial
spatial_image_src = read_tif_image(dir_file_original_images_spatial,spatial_imagen_name)
spatial_imagen = np.dstack([spatial_image_src.read(band) for band in ix_rgb_bands])
#Dimension espectral
spectral_image_src = read_tif_image(dir_file_original_images_spectral,spectral_imagen_name)
spectral_imagen = np.dstack([spectral_image_src.read(band) for band in ix_rgb_bands])

#Resultado
resultado_image_src = read_tif_image(dir_file_proccesed_images,resultado_name)
resultado_imagen = np.dstack([resultado_image_src.read(band) for band in ix_rgb_bands])

#Evaluación
indices_full_reference_spacial = test_full_references(spatial_imagen,resultado_imagen)
indices_full_reference_spectral = test_full_references(np.transpose(inter_spectral,(1,2,0)),resultado_imagen)

print("Calculo de indices espectrales full reference espacial")
with open(os.path.join(dir_file_proccesed_images,"indices_calidad_espacial_full_references.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    for test in indices_full_reference_spacial:
        writer.writerow(test)

print("Calculo de indices espectrales full reference espectral")
with open(os.path.join(dir_file_proccesed_images,"indices_calidad_espectral_full_references.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    for test in indices_full_reference_spectral:
        writer.writerow(test)

print(np.transpose(inter_spectral, (1, 2, 0)).shape)
print(pancromatica.shape)
print(resultado_imagen.shape)

indices_full_no_reference = test_no_references(np.transpose(inter_spectral,(1,2,0)),pancromatica,resultado_imagen)

print("Calculo de indices espectrales no full reference")
with open(os.path.join(dir_file_proccesed_images,"indices_calidad_no_full_references.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    for test in indices_full_no_reference:
        writer.writerow(test)