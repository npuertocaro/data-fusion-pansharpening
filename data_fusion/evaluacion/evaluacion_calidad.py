from sewar.full_ref import uqi, ergas, sam
from sewar.no_ref import d_lambda, d_s
import numpy as np

def test_full_references(original_imagen,proccesed_imagen):
    print('Calculando índices de calidad full references. Por favor espera...')
    return [("UQI", uqi(original_imagen, proccesed_imagen)),
            ("ERGAS", ergas(original_imagen, proccesed_imagen)),
            ("SAM: ", sam(original_imagen, proccesed_imagen))]

def test_no_references(spectral_imagen,pancromatica,proccesed_imagen,):
    print('Calculando índices de calidad no references. Por favor espera...')
    return [("D_Lambda", d_lambda(spectral_imagen, proccesed_imagen)),
            ("D_S", d_s(pancromatica, np.transpose(spectral_imagen,(1,0,2)), proccesed_imagen,q=1,r=1,ws=1))]

