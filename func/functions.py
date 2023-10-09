from __future__ import annotations
import cv2
import os
import matplotlib.pyplot as pyplot
import numpy as np
import rasterio
from rasterio.plot import show
from rasterio.enums import Resampling

get_RGB_bands_satellite = lambda src: [src.read(4),src.read(3),src.read(2)]
get_RGB_bands_satellite_DatasetReader = lambda src,indexes: [src.read(ix) for ix in indexes]
get_RGB_bands_satellite_ndarray_and_other_bands = lambda src: [src[ix,:,:] for ix in range(src.shape[0])]

# Functions to merge R,G,B
ndarray_rgb = lambda r,g,b: np.dstack((r, g, b)) # Merge r,g and b with numpy
rgb_img = lambda red,green,blue : cv2.merge([red,green,blue]) # Merge r,g and b with openCv


process_imag_to_another_model = lambda img, mask: np.dstack([
    sum((value*img[:,:,channel]) 
        for value,channel in zip(row,range(img.astype(float).shape[2])))
    for row in mask])

def show_images(images: list, cmap:str = None):
    fig, axs = pyplot.subplots(ncols=len(images), nrows=1, figsize=(15, 9), sharey=True)
    if cmap:
        for ix,axn in enumerate(axs):
            show(images[ix], cmap=cmap, ax=axn)
    else:
        for ix,axn in enumerate(axs):
            show(images[ix], ax=axn)
    for ix,axn in enumerate(axs):
        axn.set_title(f"imagen {ix}")

def show_hist(images: list, color:str = 'b'):
    fig, axs = pyplot.subplots(ncols=len(images), nrows=1, figsize=(10, 9), sharey=True)
    for ix,axn in enumerate(axs):
        axn.hist(images[ix].flatten(), color=color, alpha=0.5, bins=20)
    for ix,axn in enumerate(axs):
        axn.set_title(f"imagen {ix}")

def read_tif_image(path,image_name) -> rasterio.io.DatasetReader:
    return rasterio.open(os.path.join(path,image_name))

def read_tif_image_by_rioxarray(path,image_name):
    return rasterio.open(os.path.join(path,image_name))

def get_pancromatica(spatial_image_src: rasterio.io.DatasetReader) -> np.ndarray:
    return  (sum(spatial_image_src.read(n).astype('float') for n in [1,2,3])/3).astype('uint8')

def get_equalized_panchromatic(image:np.ndarray) -> list[np.ndarray, np.ndarray]:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    return [ cv2.equalizeHist(image), clahe.apply(image)]

def resampling_spectral(src,height:int, width:int, interpolation_type:str):
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

def merge_bands(imageRBG:np.ndarray,list_new_bands:list[np.ndarray]) -> np.ndarray :
    return  np.dstack((imageRBG,*list_new_bands))