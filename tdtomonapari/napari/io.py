from tomobase.data import Sinogram
import napari

def read_sinogram(path):
    return read_to_viewer


def read_to_viewer(path):
    sino = Sinogram.from_file(path)
    
    _dict = {}
    _dict['viewsettings'] = {}
    _dict['viewsettings']['colormap'] = 'gray'  
    _dict['viewsettings']['contrast_limits'] = [0,sino.data.max()]

    napari.current_viewer().dims.ndisplay = 2
    layer = [sino._to_napari_layer(True, **_dict)]
    return layer