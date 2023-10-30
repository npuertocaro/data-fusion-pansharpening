from osgeo import gdal, ogr
import os

# Definir la función para escalar una imagen de 0 a 1 a 0 a 255
def escalar_imagen(imagen_ruta, salida_ruta):
    ds = gdal.Open(imagen_ruta)
    if ds is None:
        raise Exception(f"No se pudo abrir la imagen raster: {imagen_ruta}")
    
    # Escalar los valores de la imagen
    imagen_escalada = (ds.GetRasterBand(1).ReadAsArray() / 1) * 255

    # Crear un nuevo archivo TIFF para la imagen escalada
    driver = gdal.GetDriverByName('GTiff')
    ds_salida = driver.Create(salida_ruta, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Byte)
    ds_salida.GetRasterBand(1).WriteArray(imagen_escalada)
    ds_salida.SetProjection(ds.GetProjection())
    
    # Cerrar los conjuntos de datos
    ds = None
    ds_salida = None

# Definir la función para cortar y cambiar el sistema de referencia de una imagen
def cortar_y_cambiar_srs(imagen_ruta, shapefile_ruta, salida_ruta, nuevo_srs):
    ds = gdal.Open(imagen_ruta)
    if ds is None:
        raise Exception(f"No se pudo abrir la imagen raster: {imagen_ruta}")

    ds_shapefile = ogr.Open(shapefile_ruta)
    if ds_shapefile is None:
        raise Exception(f"No se pudo abrir el shapefile: {shapefile_ruta}")

    capa_shapefile = ds_shapefile.GetLayer()
    srs_shapefile = capa_shapefile.GetSpatialRef()

    driver = gdal.GetDriverByName('GTiff')
    ds_salida = driver.Create(salida_ruta, ds.RasterXSize, ds.RasterYSize, ds.RasterCount, gdal.GDT_Float32)

    ds_salida.SetProjection(nuevo_srs.ExportToWkt())

    gdal.Warp(ds_salida, ds, cutlineDSName=shapefile_ruta, dstSRS=nuevo_srs)

    ds = None
    ds_salida = None
    ds_shapefile = None

# Lista de rutas de imágenes a procesar
rutas_imagenes = ['imagen1.tif', 'imagen2.tif', 'imagen3.tif']

# Ruta del shapefile y nuevo sistema de referencia
shapefile_ruta = 'shapefile.shp'
nuevo_srs = ogr.osr.SpatialReference()
nuevo_srs.ImportFromEPSG(4326)  # Ejemplo: proyección WGS 84

# Procesar cada imagen
for imagen_ruta in rutas_imagenes:
    # Escalar la imagen y guardarla
    nombre_archivo = os.path.splitext(os.path.basename(imagen_ruta))[0]
    imagen_escalada_ruta = f'{nombre_archivo}_escalada.tif'
    escalar_imagen(imagen_ruta, imagen_escalada_ruta)
    
    # Cortar y cambiar el sistema de referencia de la imagen
    nombre_archivo_salida = f'{nombre_archivo}_cortada_proyectada.tif'
    cortar_y_cambiar_srs(imagen_escalada_ruta, shapefile_ruta, nombre_archivo_salida, nuevo_srs)
    
    print(f"Procesamiento de {imagen_ruta} completado.")

print("Procesamiento de imágenes completado.")
