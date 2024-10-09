from functools import partial
from typing import List
from napari.types import LayerData
from tomobase.log import logger
import napari

def _load_data(name, **kwargs) -> List[LayerData]:
    from tomobase import phantoms
    if name == 'nanocage':
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
 

# fmt: off
TDTOMO_NAPARI_SAMPLE_DATA = [
    'nanocage' 
]

globals().update({key: partial(_load_data, key) for key in TDTOMO_NAPARI_SAMPLE_DATA})