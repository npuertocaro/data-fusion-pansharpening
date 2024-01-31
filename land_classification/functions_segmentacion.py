import os
import rasterio
from rasterio.transform import from_origin
import rsgislib.segmentation.shepherdseg as shepherdseg
from rsgislib import vectorutils

def segmentar_con_shepherd(input_img, output_clumps_img, output_mean_img=None, 
                           output_shapefile=None, gdalformat='KEA', calc_stats=True, bands=None, 
                           num_clusters=60, min_n_pxls=100, dist_thres=100, sampling=100, km_max_iter=200, 
                           process_in_mem=False, save_process_stats=False):
    """
    Realiza la segmentación de una imagen utilizando el algoritmo de Shepherd.

    Args:
        input_img (str): Ruta de la imagen de entrada que se desea segmentar.
        output_clumps_img (str): Ruta de salida donde se guarda la imagen segmentada (clumps).
        output_mean_img (str, opcional): Ruta de salida donde se guarda la imagen de valores medios de las bandas dentro de cada segmento.
        output_shapefile (str, opcional): Ruta de salida donde se guarda el shapefile resultante de la segmentación.
        gdalformat (str): Formato de salida para la imagen segmentada ('KEA', 'GTiff', etc.).
        calc_stats (bool): Indica si se deben calcular estadísticas para la imagen resultante.
        bands (list, opcional): Lista de bandas a utilizar para la segmentación. Si no se especifica, se utilizan todas las bandas disponibles en la imagen de entrada.
        num_clusters (int): Número de clústeres a utilizar en el algoritmo de K-Means para la segmentación.
        min_n_pxls (int): Tamaño mínimo de un segmento (clump) en píxeles.
        dist_thres (int): Umbral de distancia para la segmentación.
        sampling (int): Porcentaje de píxeles de la imagen de entrada a utilizar para el proceso de segmentación.
        km_max_iter (int): Número máximo de iteraciones permitidas para el algoritmo K-Means.
        process_in_mem (bool): Indica si se debe realizar el procesamiento en memoria (True) o en disco (False).
        save_process_stats (bool): Indica si se deben guardar estadísticas del proceso de segmentación.
    """
    if not os.path.exists(input_img):
        raise FileNotFoundError(f"La imagen de entrada '{input_img}' no existe.")

    # Ejecutar la segmentación de Shepherd
    shepherdseg.run_shepherd_segmentation(input_img, output_clumps_img, out_mean_img=output_mean_img,
                                          gdalformat=gdalformat, calc_stats=calc_stats, bands=bands,
                                          num_clusters=num_clusters, min_n_pxls=min_n_pxls, dist_thres=dist_thres,
                                          sampling=sampling, km_max_iter=km_max_iter, process_in_mem=process_in_mem,
                                          save_process_stats=save_process_stats)

    # Convertir la imagen segmentada en un shapefile si se especifica la ruta de salida
    if output_shapefile:
        vectorutils.raster2poly(output_clumps_img, output_shapefile, imgBand=1, simplify=True)

