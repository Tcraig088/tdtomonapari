import numpy as np
import inspect
from collections.abc import Iterable
from abc import ABC, abstractmethod
import time

import coolname

import napari
from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QSpinBox, QHBoxLayout, QLineEdit, QVBoxLayout, QCheckBox, QPushButton, QGridLayout, QDoubleSpinBox
from qtpy.QtCore import Qt, Signal
from threading import Thread
from napari.qt.threading import create_worker

from tomobase.data import Volume, Sinogram, Data
from tomobase.globals import logger, xp,  TOMOBASE_DATATYPES, progresshandler, GPUContext
from tdtomonapari.registration import TDTOMONAPARI_VARIABLES

from tdtomonapari.napari.base.components import CollapsableWidget, ProgressWidget
from tdtomonapari.napari.base.utils import get_values, get_widgets, LayerSelectWidget

class ProcessWidget(QWidget):
    closed = Signal()

    def __init__(self, process, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.process = process.value
        self.name = process.name
        self.progress = {}

        self.widget_list = get_widgets(self.process, self.viewer)
        count = len([item for item in self.widget_list if isinstance(item.widget, LayerSelectWidget)])
        if count == 1:
            self.widget_list[0].widget.linkLayer()

        self.confirm_button = QPushButton('Confirm')

        self.layout = QVBoxLayout()
        for i, item in enumerate(self.widget_list):
            self.layout.addWidget(item.widget)

        self.layout.addWidget(self.confirm_button)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.confirm_button.clicked.connect(self.onConfirm)

        progresshandler.added.connect(self.onProgressStart)
        progresshandler.added_subsignal.connect(self.onSubSignalProgressStart)


    def onProgressStart(self, progress):
        signal_key = progress.upper().replace(' ', '_')
        if progresshandler[signal_key].name == self.process.__name__ or progresshandler[signal_key].value.inheritor == self.process.__name__:
            self.progress[progress] = ProgressWidget(progress, self.viewer)
            self.layout.addWidget(self.progress[progress])
    

    def onSubSignalProgressStart(self, progress, subprogress):
        if progress in self.progress:
            self.progress[subprogress] = ProgressWidget(subprogress, self.viewer)
            self.layout.addWidget(self.progress[subprogress])


    def onConfirm(self):
        self.start_time = time.perf_counter()
        worker = create_worker(self.runProcess)
        worker.start()
        worker.returned.connect(self.onComplete)
        self.confirm_button.hide()
        
    def runProcess(self):
        logger.info(f'Process {self.name} started')
        values = get_values(self.widget_list)


        if 'inplace' not in values:
            self.inplace = False 
        else:
            self.inplace = values['inplace']

        layer_names = []
        for i, item in enumerate(self.widget_list):
            if isinstance(item.widget, LayerSelectWidget):
                layer_names.append(item.widget.getLayerName())
       
        self.outputs = self.process(**values)
        self.layer_indices = LayerSelectWidget.getLayerIndex(self.viewer, layer_names)

    def processOutput(self, output, inplace, indices):
        if isinstance(output, Data):
            output.set_context(GPUContext.NUMPY, 0)
            if inplace:
                index = indices[0]
                layerdata = output.to_data_tuple()
                self.viewer.layers[index].data = layerdata[0]
                self.viewer.layers[index].metadata = layerdata[1]['metadata']
                self.viewer.layers[index].scale = layerdata[1]['scale']
                indices.pop()
            else:
                name = coolname.generate_slug(2).replace('-', ' ').title().replace(' ', '')
                layerdata = output.to_data_tuple(attributes={'name': name})
                self.viewer._add_layer_from_data(*layerdata)
        else:
            name = coolname.generate_slug()
            TDTOMONAPARI_VARIABLES[name] = output
            TDTOMONAPARI_VARIABLES.refresh()

        for layer in self.viewer.layers:
            layer.refresh()

    def onComplete(self):
        if isinstance(self.outputs, tuple):
            for item in self.outputs:
                self.processOutput(item, self.inplace, self.layer_indices)
        else:
            self.processOutput(self.outputs, self.inplace, self.layer_indices)

        elapsed = time.perf_counter() - self.start_time
        # reformat to hh: mm: ss
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)

        logger.info(f'Process {self.name} completed in {int(hours):02}h : {int(minutes):02}m : {np.round(seconds,3)}s')

        
        self.close()
        self.closed.emit()

                            


class ProcessWidget2(QWidget):
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
