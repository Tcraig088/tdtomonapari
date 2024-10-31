from functools import partial
from typing import List
from napari.types import LayerData
from tomobase.log import logger
from tomobase.tiltschemes import GRS, Incremental
from tomobase import phantoms
from tomobase import processes
import napari

def _load_data(name, **kwargs) -> List[LayerData]:
    match name:
        case 'nanocage':
            obj = phantoms.nanocage()
            _dict =  kwargs
            _dict['viewsettings'] = {}
            _dict['viewsettings']['colormap'] = 'magma'  
            _dict['viewsettings']['contrast_limits'] = [0,3]
            _dict['viewsettings']['rendering'] = 'attenuated_mip'
            _dict['name'] = 'Nanocage'
            napari.current_viewer().dims.ndisplay = 3
            layer = [obj._to_napari_layer(True, **_dict)]
            return layer
        case 'nanocage2d':
            vol = phantoms.nanocage()
            grs = Incremental(-70, 70,2)
            angles = [grs.get_angle() for i in range(1, 71)]
            sino = processes.project(vol, angles)
            
            _dict =  kwargs
            _dict['name'] = 'Nanocage 2D'
            napari.current_viewer().dims.ndisplay = 2
            layer = [sino.to_data_tuple(_dict)]
            return layer

# fmt: off
TDTOMO_NAPARI_SAMPLE_DATA = [
    'nanocage', 'nanocage2d'
]

globals().update({key: partial(_load_data, key) for key in TDTOMO_NAPARI_SAMPLE_DATA})