import numpy as np
import napari
import inspect
from collections.abc import Iterable
import time
import copy as deepcopy

from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QSpinBox, QHBoxLayout, QLineEdit, QVBoxLayout, QCheckBox, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt

from abc import ABC, abstractmethod


from tomobase.data import Volume, Sinogram, Data
from tomobase.log import logger
from tomobase.tiltschemes.tiltscheme import TiltScheme
from tomobase.registrations.datatypes import TOMOBASE_DATATYPES
from tomobase.registrations.tiltschemes import TOMOBASE_TILTSCHEMES
from tdtomonapari.napari.base.components import CollapsableWidget
from tdtomonapari.napari.base.plugins.layerselect import LayerSelctWidget
from tdtomonapari.napari.base.plugins.tiltselect import TiltSelectWidget
from tdtomonapari.napari.base.utils import get_value, get_widget, connect
from threading import Thread
from napari.qt.threading import create_worker
from tomobase.typehints import TILTANGLETYPE

class ProcessWidget(QWidget):
    def __init__(self, process:dict, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)

        self.viewer = viewer

        self.process = process['controller'].controller
        self.name = process['name']
    
        self.isinitialized = False
        self.isrunning = False
        
        #Setup widgets and layouts
        self.button_confirm = QPushButton('Confirm')
        self.button_initialize = QPushButton('Initialize')
        self.button_initialize.setVisible(False)
        self.custom_widgets = {
            'Name': [],
            'Label': [],
            'Widget': []
        }

        self.selected_widget = None
        if inspect.isclass(self.process):
            self.setupFromClass()
        else:
            self.setupFromFunc()
        
        self.layout = QGridLayout()
        
        # Ensure selected_widget is initialized
        if self.selected_widget is not None:
            self.layout.addWidget(self.selected_widget, 0, 0, 1, 2)
        
        self.layout.addWidget(self.button_initialize, 1, 0, 1, 2)
               
        for j, key in enumerate(self.custom_widgets['Name']):
            if isinstance(self.custom_widgets['Widget'][j], (LayerSelctWidget, TiltSelectWidget)):
                self.layout.addWidget(self.custom_widgets['Widget'][j], j + 2, 0, 1, 2)
            else:
                self.layout.addWidget(self.custom_widgets['Label'][j], j + 2, 0)
                self.layout.addWidget(self.custom_widgets['Widget'][j], j + 2, 1)
        
        self.layout.addWidget(self.button_confirm, j + 3, 0, 1, 2)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        
        # Connect Signals
        self.button_confirm.clicked.connect(self.onConfirm)
        self.button_initialize.clicked.connect(self.initializeClass)
        
    def setupFromFunc(self):
        signature = inspect.signature(self.process)
        self.getWidgets(signature)

    def setupFromClass(self):
        signature = inspect.signature(self.process.__init__)
        self.getWidgets(signature)

    def getWidgets(self, signature):
        banned = ['self', 'kwargs']

        for name, param in signature.parameters.items():
            if name not in banned:
                if param.annotation == Volume or param.annotation == Sinogram:
                    self.custom_widgets['Widget'].append(LayerSelctWidget([param.annotation.get_type_id()], True, self.viewer))
                    self.custom_widgets['Name'].append(name)
                    self.custom_widgets['Label'].append('Layer')
                elif param.annotation == TILTANGLETYPE:
                    self.custom_widgets['Widget'].append(TiltSelectWidget(self.viewer))
                    self.custom_widgets['Name'].append(name)
                    self.custom_widgets['Label'].append(None)
                else:
                    wname, wlabel, widget = get_widget(name, param)
                    if wname is not None:
                        self.custom_widgets['Widget'].append(widget)
                        self.custom_widgets['Name'].append(wname)
                        self.custom_widgets['Label'].append(wlabel)

    def initializeClass(self):
        if self.isinitialized:
            return
        
        self.isinitialized = True
        self.selected_layer = self.selected_widget.getLayer()
        
        if self.selected_layer is not None:
            if self.selected_layer.metadata['ct metadata']['type'] == TOMOBASE_DATATYPES.VOLUME.value():
                input = Volume.from_data_tuple(self.selected_layer)  
                dict_args = {'vol':input}
            elif self.selected_layer.metadata['ct metadata']['type'] == TOMOBASE_DATATYPES.SINOGRAM.value():
                input = Sinogram.from_data_tuple(self.selected_layer)
                dict_args = {'sino':input}
                
        for i, key in enumerate(self.custom_widgets['Name']):
            dict_args[self.custom_widgets['Name'][i]] = get_value(self.custom_widgets['Widget'][i])
            
        self.process = self.process(**dict_args)
        presets = self.process.generate()
        
        for widget in self.custom_widgets['Widget']:
            connect(widget, self.runUpdate)
        
        self.layers = []
        if not isinstance(presets, Iterable):
            presets = [presets]
            
        for i in presets:
            if isinstance(i, Sinogram):
                self.viewer.dims.ndisplay = 2
            elif isinstance(i, Volume):
                self.viewer.dims.ndisplay = 3
                
                layerdata = i.to_data_tuple()
                layer = self.viewer._add_layer_from_data(*layerdata)
                self.layers.append(*layer)
       
        self.worker = create_worker(self.runUpdateThread)
        self.worker.returned.connect(self.onUpdateComplete)
        
    def validate(self):
        return True
     
    def onConfirm(self):
        if not self.validate():
            return
        worker = create_worker(self.runProcess)
        worker.start()
        worker.returned.connect(self.onProcessComplete)
    
    def onProcessComplete(self, output):
        logger.info(f'Process {self.name} completed')
        logger.debug(f'Output: {output}')
        if output is not None:
            if not isinstance(output, Iterable):
                output = [output]
            
            i = 0
            for item in output:
                if isinstance(item, Data):
                    if self.inplace:
                        layerdata = item.to_data_tuple(attributes={'name': self.name})
                        self.selected_layers[i].data = layerdata[0]
                        i+=1
                    else:
                        layerdata = item.to_data_tuple(attributes={'name': self.name + str(np.random.randint(0, 1000))})
                        if isinstance(item, Sinogram):
                            self.viewer.dims.ndisplay = 2
                        elif isinstance(item, Volume):
                            self.viewer.dims.ndisplay = 3
                        self.viewer._add_layer_from_data(*layerdata)
        
        for layer in self.selected_layers:
            layer.refresh()
        
    
    def runProcess(self):
        if inspect.isclass(self.process):
            pass
        else: 
            pass
        
        values = {}
        self.selected_layers = []
        for i, key in enumerate(self.custom_widgets['Name']):
            values[key] = get_value(self.custom_widgets['Widget'][i]) 
            if self.custom_widgets['Label'][i] == 'Layer':
                self.selected_layers.append(values[key])
                layertype_id = values[key].metadata['ct metadata']['type']
                layertype = TOMOBASE_DATATYPES.key(layertype_id).capitalize()
                class_ = globals().get(layertype)
                values[key] = class_.from_data_tuple(values[key])
                
                
        logger.info(f"print values: {values}")
        
        if inspect.isclass(self.process):
            process = self.process.apply
        else:
            process = self.process

        self.inplace = False
        if 'inplace' in values:
            self.inplace = values['inplace']
            
        outs = process(**values)
        logger.info(f'Process {self.name} completed')  
        return outs
        
    def runUpdate(self):
        if self.isrunning:
            return
        for i, key in enumerate(self.custom_widgets['Name']):
            setattr(self.process, self.custom_widgets['Name'][i], get_value(self.custom_widgets['Widget'][i]))  
            
        self.worker.start()

    def runUpdateThread(self):
        outputs = self.process.update()
        if not isinstance(outputs, Iterable):
            outputs = [outputs]  
        return outputs
            
    def onUpdateComplete(self, values):
        self.isrunning = False
        for i, layer in enumerate(self.layers):
            layer.data = values[i]._transpose_to_view(use_copy=True)
            layer.refresh()
