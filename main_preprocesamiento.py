from preprocesamiento.func.functions_pre import *
from func.functions import *
from dotenv import load_dotenv

#Cargar direcciones (path) y buscar las variables de entorno
load_dotenv()

path_root = os.getcwd()
directorio_originales = os.getenv("ruta_folder_bandas")
directorio_destino = os.getenv("ruta_folder_bandas_8BIT")

### PREPROCESA
#MIENTO IMÁGENES SATELITALES ###

# # Transformación 8-bit Satelite
# transformacion_8bit(directorio_originales, directorio_destino)
# print("Transformación de imágenes a 8 bit completado")

# # Proyección de EPSG 4326 a EPSG 9377 Satelite
# directorio_8bit = os.getenv("ruta_folder_bandas_8BIT")
# directorio_proyectadas = os.getenv("ruta_del_directorio_transformadas_EPSG")
# epsg_proyeccion = 9377
# reproject_images(directorio_8bit, directorio_proyectadas, epsg_proyeccion)
# print("Reproyección de imágenes a EPSG 9377 completado")

# # Recortar imagenes de satelite
# directorio_proyectadas = os.getenv("ruta_del_directorio_transformadas_EPSG")
# directorio_recortadas = os.getenv("ruta_del_directorio_recortadas")
# shapefile_ruta = os.getenv("shapefile_ruta")
# recortar_con_shapefile(directorio_proyectadas, shapefile_ruta, directorio_recortadas)
# print("Imágenes recortadas al área de estudio completo")

### PREPROCESAMIENTO OTROS DATOS ###

# # Proyección de EPSG 4326 a EPSG 9377 UAV
# epsg_proyeccion = 9377
# directorio_uav = os.getenv("ruta_folder_imagenes_uav")
# directorio_proyectadas_uav = os.getenv("ruta_del_directorio_transformadas__uav_EPSG")
# reproject_images(directorio_uav, directorio_proyectadas_uav, epsg_proyeccion)
# print("Reproyección de imágenes UAV a EPSG 9377 completado")

# # Proyección de EPSG 4326 a EPSG 9377 Avion
# epsg_proyeccion = 9377
# directorio_av = os.getenv("ruta_folder_imagenes_avion")
# directorio_proyectadas_av = os.getenv("ruta_del_directorio_transformadas_avion_EPSG")
# reproject_images(directorio_av, directorio_proyectadas_av, epsg_proyeccion)
# print("Reproyección de imágenes avión a EPSG 9377 completado")

# #Desconcatenación de bandas uav
# directorio_imagen_uav = os.getenv("ruta_del_directorio_transformadas__uav_EPSG")
# nombre_imagen = os.getenv("nombre_imagen")
# directorio_salida_imagen_uav = os.getenv("directorio_salida_imagen_uav")
# desconcatenar_bandas_uav(directorio_imagen_uav, nombre_imagen, directorio_salida_imagen_uav)

#Desconcatenación de bandas avion
directorio_imagen_avion = os.getenv("ruta_del_directorio_transformadas_avion_EPSG")
nombre_imagen_avion = os.getenv("nombre_imagen_avion")
directorio_salida_imagen_avion = os.getenv("directorio_salida_imagen_avion")
desconcatenar_bandas_avion(directorio_imagen_avion, nombre_imagen_avion, directorio_salida_imagen_avion)

# Transformación relativa de radiancia uav
directorio_dron = os.getenv("directorio_salida_imagen_uav")
directorio_satelite = os.getenv("ruta_del_directorio_recortadas")
directorio_destino = os.getenv("directorio_imagen_uav_reflec_correc")
shapefile_ruta = os.getenv("direccion_shape_correccion_puntos")
transformacion_radiancia(directorio_dron, directorio_satelite, directorio_destino, shapefile_ruta)

# # Unir bandas Satelite 2022
# directorio_recortadas = os.getenv("ruta_del_directorio_recortadas")
# banda_B = os.getenv("banda_B")
# banda_G = os.getenv("banda_G")
# banda_R = os.getenv("banda_R")
# banda_NIR = os.getenv("banda_NIR")

# banda_1 = os.path.join(directorio_recortadas, banda_B)
# banda_2 = os.path.join(directorio_recortadas, banda_G)
# banda_3 = os.path.join(directorio_recortadas, banda_R)
# banda_4 = os.path.join(directorio_recortadas, banda_NIR)

# direccion_salida_fusion = os.getenv("direccion_imagenes_ingreso_satelite")
# union_satelite_RGB = '20221224T152641_10_RGB432.tif'
# union_satelite_falsocolor = '20221224T152641_10_RGB832.tif'
# direccion_salida_rgb = os.path.join(direccion_salida_fusion, union_satelite_RGB)
# direccion_salida_fc = os.path.join(direccion_salida_fusion, union_satelite_falsocolor)
# #Resolucion de 10m RGB color 432
# crear_imagen_rgb(banda_3, banda_2, banda_1, direccion_salida_rgb)

# #Resolucion de 10m falso color 832
# crear_imagen_rgb(banda_4, banda_2, banda_1, direccion_salida_fc)

# # Unir bandas Satelite 2020
# directorio_recortadas = os.getenv("ruta_del_directorio_recortadas")
# banda_B = os.getenv("banda_B")
# banda_G = os.getenv("banda_G")
# banda_R = os.getenv("banda_R")
# banda_NIR = os.getenv("banda_NIR")

# banda_1 = os.path.join(directorio_recortadas, banda_B)
# banda_2 = os.path.join(directorio_recortadas, banda_G)
# banda_3 = os.path.join(directorio_recortadas, banda_R)
# banda_4 = os.path.join(directorio_recortadas, banda_NIR)

# direccion_salida_fusion = os.getenv("direccion_imagenes_ingreso_satelite_2")
# union_satelite_RGB = '20201025T152641_10_RGB432.tif'
# union_satelite_falsocolor = '20201025T152641_10_RGB832.tif'
# direccion_salida_rgb = os.path.join(direccion_salida_fusion, union_satelite_RGB)
# direccion_salida_fc = os.path.join(direccion_salida_fusion, union_satelite_falsocolor)
# #Resolucion de 10m RGB color 432
# crear_imagen_rgb(banda_3, banda_2, banda_1, direccion_salida_rgb)

# #Resolucion de 10m falso color 832
# crear_imagen_rgb(banda_4, banda_2, banda_1, direccion_salida_fc)

# # Unir bandas uav rgb
# directorio_destino = os.getenv("directorio_imagen_uav_reflec_correc")
# banda_B = os.getenv("banda_B_uav")
# banda_G = os.getenv("banda_G_uav")
# banda_R = os.getenv("banda_R_uav")
# banda_1_uav = os.path.join(directorio_destino, banda_B)
# banda_2_uav = os.path.join(directorio_destino, banda_G)
# banda_3_uav = os.path.join(directorio_destino, banda_R)

# direccion_salida_rgb = os.getenv("direccion_imagenes_ingreso_dron")
# union_uav = os.getenv("name_image_spatial")
# direccion_salida = os.path.join(direccion_salida_rgb, union_uav)

# crear_imagen_rgb(banda_3_uav, banda_2_uav, banda_1_uav, direccion_salida)