from tomobase.data import Sinogram
import napari

def read_sinogram(path):
    return read_to_viewer


def read_to_viewer(path):
    sino = Sinogram.from_file(path)
    name = path.split('/')[-1]
    name = name.split('.')[0]
    _dict = {}
    _dict['name'] = name   
    _dict['contrast_limits'] = [0,sino.data.max()]

    napari.current_viewer().dims.ndisplay = 2
    layer = [sino.to_data_tuple(_dict)]
    return layer

def write_sinogram(path, layerdata, attributes):
    sino = Sinogram.from_data_tuple(layerdata, attributes)
    sino.to_file(path)
    return path