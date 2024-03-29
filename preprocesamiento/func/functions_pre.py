import os
import numpy as np
import rasterio
from func.functions import read_tif_image
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.merge import merge
from rasterio.enums import Resampling
from rasterio.mask import mask
import fiona
import matplotlib.pyplot as pyplot
import imageio as imageio

def transformacion_8bit(directorio_originales, directorio_destino):
    """ Aplica una transformación 8-bit a las imágenes en el directorio de origen y guarda las imágenes en el directorio de destino.
    Args:
        directorio_originales (str): Directorio que contiene las imágenes satelitales originales.
        directorio_destino (str): Directorio donde se guardarán las imágenes transformadas.
    """
    # Asegúrate de que el directorio de destino exista
    if not os.path.exists(directorio_destino):
        os.makedirs(directorio_destino)
    # Aplica la transformación 8-bit a las imágenes en el directorio original y guárdalas en el directorio de destino
    for nombre_archivo in os.listdir(directorio_originales):
        if nombre_archivo.endswith(('.tif')):  # Filtra solo los archivos de imagen
            imagen_src = read_tif_image(directorio_originales, nombre_archivo)
            metadata = imagen_src.meta
            metadata.update(
                dtype=rasterio.uint8,
                count=1,
                nodata=0
                )
            datos_imagen = imagen_src.read(1)
            valor_max = np.max(datos_imagen, where=(datos_imagen < 65535), initial=0)
            valor_min = datos_imagen.min()
            print(valor_min, valor_max)
            # Aplica la transformación 8-bit ajustando los valores de píxeles al rango de 0 a 255
            datos_imagen_transformados = np.interp(datos_imagen, (valor_min, valor_max), (0, 255))
            # Guarda la imagen transformada en el directorio de destino
            ruta_imagen_destino = os.path.join(directorio_destino, nombre_archivo)
            # Crea una nueva imagen con Rasterio
            with rasterio.open(ruta_imagen_destino, 'w', **metadata) as dst:
                dst.write(datos_imagen_transformados.astype(rasterio.uint8), 1)  # Escribe los datos en la banda 1
            print(f'Imagen {nombre_archivo} transformada y guardada en {ruta_imagen_destino}')

def reproject_images(directorio_originales, directorio_destino, dst_crs):
    """
    Reproyecta imágenes a un nuevo sistema de referencia de coordenadas.

    Parameters:
    - directorio_originales (str): Ruta al directorio que contiene las imágenes originales.
    - directorio_destino (str): Ruta al directorio donde se guardarán las imágenes reproyectadas.
    - dst_crs (str): Sistema de referencia de coordenadas de destino (por ejemplo, 'EPSG:4326').

    Returns:
    - None
    """
    # Asegúrate de que el directorio de destino exista
    if not os.path.exists(directorio_destino):
        os.makedirs(directorio_destino)
    # Lista de extensiones de archivo válidas
    extensiones_validas = ('.tif')
    for nombre_archivo in os.listdir(directorio_originales):
        if nombre_archivo.lower().endswith(extensiones_validas):  # Filtra solo las extensiones válidas
            ruta_completa = os.path.join(directorio_originales, nombre_archivo)
            with rasterio.open(ruta_completa) as src:
                transform, width, height = calculate_default_transform(
                    src.crs, dst_crs, src.width, src.height, *src.bounds)
                imagen = src.meta.copy()
                imagen.update({
                    'crs': dst_crs,
                    'transform': transform,
                    'width': width,
                    'height': height
                })
                # Genera el nombre del archivo de destino en el directorio destino
                nombre_archivo_destino = os.path.splitext(nombre_archivo)[0] + '_reprojected.tif'
                ruta_completa_destino = os.path.join(directorio_destino, nombre_archivo_destino)
                with rasterio.open(ruta_completa_destino, 'w', **imagen) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=dst_crs,
                            resampling=Resampling.bilinear)            
            print(f'Imagen {nombre_archivo} reproyectada y guardada en {ruta_completa_destino}')

def recortar_con_shapefile(directorio_imagenes, directorio_shapefile, directorio_salida):
    """
    Recorta imágenes utilizando un archivo shapefile que define la geometría de recorte.

    Parameters:
    - directorio_imagenes (str): Ruta al directorio que contiene las imágenes a recortar.
    - directorio_shapefile (str): Ruta al archivo shapefile que define la geometría de recorte.
    - directorio_salida (str): Ruta al directorio donde se guardarán las imágenes recortadas.

    Returns:
    - None
    """
    # Abre el shapefile y obtiene la geometría (en este caso, asumimos un solo polígono)
    with fiona.open(directorio_shapefile, "r") as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]
    # Asegúrate de que el directorio de destino exista
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)
    for nombre_archivo in os.listdir(directorio_imagenes):
        if nombre_archivo.endswith(('.tif')):
            ruta_completa = os.path.join(directorio_imagenes, nombre_archivo)
            with rasterio.open(ruta_completa) as imgs:
                # Máscara de la imagen con la geometría del polígono
                out_image, out_transform = mask(imgs, shapes, crop=True)
                # Copia de los metadatos de la imagen original
                out_meta = imgs.meta.copy()
                # Actualiza la información de la transformación
                out_meta.update({"driver": "GTiff",
                                 "height": out_image.shape[1],
                                 "width": out_image.shape[2],
                                 "transform": out_transform})
                # Guarda la imgs recortada en la carpeta de salida
                nombre_salida = os.path.join(directorio_salida, f"recortada_{nombre_archivo}")
                with rasterio.open(nombre_salida, "w", **out_meta) as dest:
                    dest.write(out_image)
            print(f'Imagen {nombre_archivo} recortada al área y guardada en {directorio_salida}')

def desconcatenar_bandas_uav(directorio_imagenes, nombre_archivo, directorio_salida):
    """
    Desconcatena y guarda las bandas de una imagen UAV en archivos GeoTIFF individuales.

    Parameters:
    - directorio_imagenes (str): Ruta al directorio que contiene la imagen UAV.
    - nombre_archivo (str): Nombre del archivo de imagen UAV.
    - directorio_salida (str): Ruta al directorio donde se guardarán las bandas desconcatenadas.

    Returns:
    - None
    """
    # Abre la imagen raster
    imagen_espacial = os.path.join(directorio_imagenes, nombre_archivo)
    with rasterio.open(imagen_espacial) as src:
        # Lee todas las bandas
        bandas = src.read()
        # Obtiene metadatos para las bandas
        meta = src.meta
    # Desconcatena las bandas
    red = bandas[0, :, :]
    green = bandas[1, :, :]
    blue = bandas[2, :, :]
    print(red.shape)
    # Guarda cada banda por separado
    for nombre_banda, banda in zip(['Banda_R', 'Banda_G', 'Banda_B'], [red, green, blue]):
        meta_banda = meta.copy()
        meta_banda.update(
            count=1
            )
        # Actualiza el nombre del archivo de salida con el nombre de la banda
        nombre_salida = os.path.join(directorio_salida, f"{nombre_banda}.tif")
        # Guarda la banda como un nuevo archivo GeoTIFF
        with rasterio.open(nombre_salida, 'w', **meta_banda) as dest:
            dest.write(banda,1)

def desconcatenar_bandas_avion(directorio_imagenes, nombre_archivo, directorio_salida):
    """
    Desconcatena y guarda las bandas de una imagen de avión en archivos GeoTIFF individuales.

    Parameters:
    - directorio_imagenes (str): Ruta al directorio que contiene la imagen de avión.
    - nombre_archivo (str): Nombre del archivo de imagen de avión.
    - directorio_salida (str): Ruta al directorio donde se guardarán las bandas desconcatenadas.

    Returns:
    - None
    """
    # Abre la imagen raster
    imagen_espacial = os.path.join(directorio_imagenes, nombre_archivo)
    with rasterio.open(imagen_espacial) as src:
        # Lee todas las bandas
        bandas = src.read()
        # Obtiene metadatos para las bandas
        meta = src.meta
    # Desconcatena las bandas
    red = bandas[0, :, :]
    green = bandas[1, :, :]
    blue = bandas[2, :, :]
    alpha = bandas[3, :, :]
    print(red.shape)
    # Guarda cada banda por separado
    for nombre_banda, banda in zip(['red', 'green', 'blue', 'alpha'], [red, green, blue, alpha]):
        meta_banda = meta.copy()
        meta_banda.update(
            count=1
            )
        # Actualiza el nombre del archivo de salida con el nombre de la banda
        nombre_salida = os.path.join(directorio_salida, f"{nombre_banda}.tif")
        # Guarda la banda como un nuevo archivo GeoTIFF
        with rasterio.open(nombre_salida, 'w', **meta_banda) as dest:
            dest.write(banda,1)

def extraer_valores(imagen, puntos):
    """
    Extrae los valores de píxeles de una imagen para una lista de puntos.

    Parameters:
    - imagen (str): Ruta al archivo de imagen.
    - puntos (list): Lista de puntos en formato GeoJSON.

    Returns:
    - List con los valores de píxeles correspondientes a cada punto.
    """
    values = []
    with rasterio.open(imagen) as src:
        for punto in puntos:
            lon, lat = punto["geometry"]["coordinates"]
            row, col = src.index(lon, lat)
            valor_pixel = src.read(1, window=((row, row + 1), (col, col + 1)))
            values.append(valor_pixel[0][0])
    return values

def transformacion_radiancia(directorio_dron, directorio_satelite, directorio_destino,direccion_shapefile):
    """
    Realiza la transformación de radiancia y la interpolación de imágenes de dron utilizando imágenes satelitales.

    Parameters:
    - directorio_dron (str): Ruta al directorio que contiene las imágenes de dron.
    - directorio_satelite (str): Ruta al directorio que contiene las imágenes satelitales.
    - directorio_destino (str): Ruta al directorio donde se guardarán las imágenes de dron transformadas.
    - direccion_shapefile (str): Ruta al archivo shapefile con la información de los puntos.

    Returns:
    - None
    """
        # Cargar puntos desde shapefile
    with fiona.open(direccion_shapefile, 'r') as shp:
        puntos = list(shp)
    # Asegúrate de que el directorio de destino exista
    if not os.path.exists(directorio_destino):
        os.makedirs(directorio_destino)
    # Lista de extensiones de archivos de imagen admitidas
    extensiones_validas = ('.tif')
    # Itera sobre los archivos en el directorio del dron
    for nombre_archivo_dron in os.listdir(directorio_dron):
        if nombre_archivo_dron.endswith(extensiones_validas):
            # Lee la banda del dron
            imagen_dron = os.path.join(directorio_dron, nombre_archivo_dron)
            with rasterio.open(imagen_dron) as banda_dron:
                metadata = banda_dron.meta
                banda_dron = banda_dron.read(1)
            # Identifica la banda del satélite correspondiente
            if 'Banda_B' in nombre_archivo_dron:
                nombre_archivo_satelite = 'recortada_RT_T18NXL_20221224T152641_B02_reprojected.tif'
            elif 'Banda_R' in nombre_archivo_dron:
                nombre_archivo_satelite = 'recortada_RT_T18NXL_20221224T152641_B04_reprojected.tif'
            elif 'Banda_G' in nombre_archivo_dron:
                nombre_archivo_satelite = 'recortada_RT_T18NXL_20221224T152641_B03_reprojected.tif'
            else:
                print(f'No se puede identificar la banda correspondiente para {nombre_archivo_dron}')
                continue
            ruta_archivo_satelite = os.path.join(directorio_satelite, nombre_archivo_satelite)
            # Lee la banda del satélite
            banda_satelite = leer_banda(ruta_archivo_satelite)
            # Interpola la banda del dron con la banda correspondiente del satélite
            valor_max = np.max(banda_satelite, where=(banda_satelite < 255), initial=0)
            print(valor_max)
            valor_min = banda_satelite.min()
            print(valor_min)
            banda_interpolada = np.interp(banda_dron, (banda_dron.min(), banda_dron.max()), (valor_min, valor_max))
            # Guarda la banda interpolada en el directorio de destino
            ruta_banda_destino = os.path.join(directorio_destino, nombre_archivo_dron)
            # Guarda la banda como un nuevo archivo GeoTIFF
            with rasterio.open(ruta_banda_destino, 'w', **metadata) as dest:
                dest.write(banda_interpolada,1)
            print(f'Banda de drone {nombre_archivo_dron} interpolada y guardada en {ruta_banda_destino}')
            
            # Extraer valores de píxeles de ambas imágenes para los puntos 
            valores_satelital = extraer_valores(ruta_archivo_satelite, puntos) 
            valores_dron = extraer_valores(ruta_banda_destino, puntos) 
            print("Valores verdaderos (Imagen Satelital):", valores_satelital) 
            print("Valores relativamente ajustados (Imagen UAS):", valores_dron)

def leer_banda(ruta_archivo):
    """
    Lee una banda de un archivo raster.

    Parameters:
    - ruta_archivo (str): Ruta al archivo raster.

    Returns:
    - Datos de la banda leída.
    """
    with rasterio.open(ruta_archivo) as src:
        return src.read(1)

def guardar_banda(ruta_archivo, datos_banda):
    """
    Guarda una banda en un nuevo archivo raster.

    Parameters:
    - ruta_archivo (str): Ruta al nuevo archivo raster.
    - datos_banda: Datos de la banda a guardar.

    Returns:
    - None
    """
    with rasterio.open(ruta_archivo, 'w', driver='GTiff', height=datos_banda.shape[0], width=datos_banda.shape[1], count=1, dtype=datos_banda.dtype) as dst:
        dst.write(datos_banda, 1)

def crear_imagen_rgb(ruta_b1, ruta_b2, ruta_b3, ruta_destino):
    """
    Crea una imagen RGB a partir de tres bandas raster.

    Parameters:
    - ruta_b1 (str): Ruta a la primera banda.
    - ruta_b2 (str): Ruta a la segunda banda.
    - ruta_b3 (str): Ruta a la tercera banda.
    - ruta_destino (str): Ruta al nuevo archivo raster RGB.

    Returns:
    - None
    """
    # Abre cada banda por separado
    with rasterio.open(ruta_b1) as src1, rasterio.open(ruta_b2) as src2, rasterio.open(ruta_b3) as src3:
        # Lee todas las bandas
        banda_1 = src1.read(1)
        banda_2 = src2.read(1)
        banda_3 = src3.read(1)
        # Obtiene metadatos para una de las bandas (en este caso, la banda_1)
        metabanda = src1.meta
        metabanda.update(
                dtype=rasterio.uint8,
                count=3,
                )
    # Agrega impresiones para verificar las dimensiones antes de la concatenación
    print(f"Dimensiones banda_1: {banda_1.shape}")
    print(f"Dimensiones banda_2: {banda_2.shape}")
    print(f"Dimensiones banda_3: {banda_3.shape}")

    # Concatena las bandas a lo largo del tercer eje para formar una imagen RGB
    imagen_unida = np.dstack([banda_1, banda_2, banda_3])
    print(f"Dimensiones imagen_unida: {imagen_unida.shape}")

    with rasterio.open(ruta_destino, 'w', **metabanda) as dest:
        for ix in range(imagen_unida.shape[2]):
            dest.write(imagen_unida[:,:,ix], ix+1)