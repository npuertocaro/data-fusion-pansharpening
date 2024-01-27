from __future__ import annotations
import cv2
import os
import matplotlib.pyplot as pyplot
import numpy as np
import rasterio
from rasterio.plot import show
from rasterio.enums import Resampling

# Función para obtener las bandas RGB de una imagen satelital
get_RGB_bands_satellite = lambda src: [src.read(4),src.read(3),src.read(2)]

# Función para obtener las bandas RGB de una imagen satelital usando DatasetReader y especificando índices
get_RGB_bands_satellite_DatasetReader = lambda src,indexes: [src.read(ix) for ix in indexes]

# Función para obtener las bandas RGB de una imagen satelital representadas como ndarray y otras bandas
get_RGB_bands_satellite_ndarray_and_other_bands = lambda src: [src[ix,:,:] for ix in range(src.shape[0])]

# Función para concatenar bandas RGB y formar una imagen RGB utilizando numpy
ndarray_rgb = lambda r,g,b: np.dstack((r, g, b)) #Concatena RGB con numpy

# Función para concatenar bandas RGB y formar una imagen RGB utilizando OpenCV
rgb_img = lambda red,green,blue : cv2.merge([red,green,blue]) #Concatena RGB con openCv

# Función para procesar una imagen aplicando una máscara y generando una nueva imagen
process_imag_to_another_model = lambda img, mask: np.dstack([
    sum((value*img[:,:,channel]) 
        for value,channel in zip(row,range(img.astype(float).shape[2])))
    for row in mask])

def show_images(images: list, path, cmap:str = None):
    """
    Muestra las imágenes proporcionadas en una fila y guarda la figura.

    Parameters:
    - images: Lista de imágenes.
    - path: Ruta para guardar la figura.
    - cmap: Mapa de colores para mostrar las imágenes (opcional).

    Returns:
    - None
    """
    fig, axs = pyplot.subplots(ncols=len(images), nrows=1, figsize=(20, 10), sharey=True)
    if cmap:
        for ix,axn in enumerate(axs):
            show(images[ix], cmap=cmap, ax=axn)
    else:
        for ix,axn in enumerate(axs):
            show(images[ix], ax=axn)
    for ix,axn in enumerate(axs):
        axn.set_title(f"Imagen {ix}")
    pyplot.savefig(os.path.join(path,'Figura de imágenes - Pan - Igualacion - I.png'), dpi='figure', format=None, bbox_inches='tight')

def show_hist(images: list, path, color:str = 'b'):
    """
    Muestra los histogramas de las imágenes proporcionadas en una fila y guarda la figura.

    Parameters:
    - images: Lista de imágenes.
    - path: Ruta para guardar la figura.
    - color: Color para los histogramas (opcional).

    Returns:
    - None
    """
    fig, axs = pyplot.subplots(ncols=len(images), nrows=1, figsize=(16,9), sharey=True)
    for ix,axn in enumerate(axs):
        axn.hist(images[ix].flatten(), color=color, alpha=0.5, bins=20)
    for ix,axn in enumerate(axs):
        axn.set_title(f"Histograma {ix}")
    pyplot.savefig(os.path.join(path,'Histograma Pan - Igualacion - I.png'), dpi='figure', format=None, bbox_inches='tight')

def read_tif_image(path,image_name) -> rasterio.io.DatasetReader:
    """
    Lee una imagen TIFF y devuelve un objeto DatasetReader.

    Parameters:
    - path: Ruta de la imagen.
    - image_name: Nombre de la imagen.

    Returns:
    - spatial_image_src: Objeto DatasetReader de rasterio.
    """
    return rasterio.open(os.path.join(path,image_name))

def read_tif_image_by_rioxarray(path,image_name):
    """
    Lee una imagen TIFF y devuelve un objeto rioxarray.

    Parameters:
    - path: Ruta de la imagen.
    - image_name: Nombre de la imagen.

    Returns:
    - spatial_image_src: Objeto rioxarray.
    """
    return rasterio.open(os.path.join(path,image_name))

def get_pancromatica(spatial_image_src: rasterio.io.DatasetReader) -> np.ndarray:
    """
    Obtiene la banda pancromática promedio de una imagen multibanda.

    Parameters:
    - spatial_image_src: Objeto DatasetReader de rasterio.

    Returns:
    - pancromatica: Banda pancromática.
    """
    return  (sum(spatial_image_src.read(n).astype('float') for n in [1,2,3])/3).astype('uint8')

def get_equalized_panchromatic(image:np.ndarray) -> list[np.ndarray, np.ndarray]:
    """
    Ecualiza la banda pancromática y aplica CLAHE.

    Parameters:
    - image: Banda pancromática.

    Returns:
    - List con dos imágenes ecualizadas.
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    return [ cv2.equalizeHist(image), clahe.apply(image)]

def resampling_spectral(src,height:int, width:int, interpolation_type:str):
    """
    Realiza un remuestreo de la imagen espectral a una nueva altura y ancho.

    Parameters:
    - src: Objeto DatasetReader de rasterio.
    - height: Nueva altura.
    - width: Nuevo ancho.
    - interpolation_type: Tipo de interpolación.

    Returns:
    - List con la imagen remuestreada y metadatos.
    """
    src_inter = src.read(
        out_shape=(
            src.count,
            int(height),
            int(width),
        ),
        resampling=Resampling[interpolation_type]
    )
    new_transform = src.transform * src.transform.scale(
        (src.width / src_inter.shape[-1]),
        (src.height / src_inter.shape[-2])
    )
    metadata = src.profile
    metadata['transform'] = new_transform
    metadata['width'] = width
    metadata['height'] = height
    return [src_inter, metadata]

def merge_bands(imageRBG:np.ndarray,list_new_bands:list[np.ndarray]) -> np.ndarray:
    """
    Fusiona las bandas RGB con nuevas bandas y devuelve una nueva imagen RGB.

    Parameters:
    - imageRBG: Imagen RGB original.
    - list_new_bands: Lista de nuevas bandas.

    Returns:
    - Nueva imagen RGB.
    """
    return  np.dstack((imageRBG,*list_new_bands))