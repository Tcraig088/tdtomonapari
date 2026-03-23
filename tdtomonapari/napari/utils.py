import magicgui
import napari
import collections.abc
from collections.abc import Iterable 


from tomobase.core.registers import logger, proxy, GPUContext, image_datatypes_register


from qtpy.QtWidgets import QWidget, QVBoxLayout, QMenu, QAction, QDockWidget, QLabel
from qtpy.QtCore import Qt

def _buildcontextwidget(viewer: 'napari.viewer.Viewer'):
    """Build the context widget for the viewer.

    Args:
        viewer (napari.viewer.Viewer): The napari viewer instance.
    """
    
    gui = magicgui.magicgui(proxy.set_context, 
                            call_button=False, 
                            auto_call=True, 
                            context={"choices": list(GPUContext), 'value':proxy.context},
                            device={"value":proxy.device, 'min':0, 'max':20})
                            
    viewer.window.add_dock_widget(gui, name='Context', area='right')



def _checklayertype(layer: 'napari.layers.Layer'):
    if 'ct metadata' not in layer.metadata:
        return False
    return layer

def selectioninfowidget(layer):
    note = QLabel(f"Layer: {layer.name}")
    selectioninfowidget.layout().addWidget(note)
    for key, value in layer.metadata['ct metadata'].items():
        note = QLabel(f"{key}: {value}")
        selectioninfowidget.layout().addWidget(note)
    
def _buildselectioninfowidgets(viewer: 'napari.viewer.Viewer'):
    # delete all widgets in the layer info widget
    logger.debug("Building selection info widgets")
    main_window = viewer.window._qt_window
    for child in main_window.children():
        if child.objectName() == "layer information":
            layer_information = child
            break
        
    # delete all widgets in the layer information widget
    for child in layer_information.children():
        child.deleteLater()
        
    layers = viewer.layers.selection.active
    selected_layers = []
    if layers is not None:
        #check if single layer or iterable
        if not isinstance(layers, Iterable):
            selected_layers = [layers] if _checklayertype(layers) else []
        else:
            for layer in layers:
                if _checklayertype(layer):
                    selected_layers.append(layer)
                    
    if selected_layers is None or len(selected_layers) == 0:
        note = QLabel("No layers selected")
        layer_information.layout().addWidget(note)
        
    else:
        for layer in selected_layers:
            gui = magicgui.magicgui(selectioninfowidget, 
                                    layer={"value":layer}, 
                                    call_button=False, 
                                    auto_call=True)
            gui.layer.native.setEnabled(False)
            layer_information.layout().addWidget(gui)


def layerinfowidget(layers: list['napari.layers.Layer']=[], viewer: 'napari.viewer.Viewer'=None):
    if layers is None:
        return

    widget_list = []
    if len(layers) == 0:
        note = QLabel("No layers selected")
        layerinfowidget.layout().addWidget(note)
    else:
        for layer in layers:
            note = QLabel(f"Layer: {layer.name}")
            layerinfowidget.layout().addWidget(note)
            
    viewer.layers.selection.events.changed.connect(lambda event: _buildselectioninfowidgets(viewer))
    viewer.layers.events.inserted.connect(lambda event: _buildselectioninfowidgets(viewer))
    viewer.layers.events.removed.connect(lambda event: _buildselectioninfowidgets(viewer))
    

def _buildlayerinfowidget(viewer: 'napari.viewer.Viewer'):
    """Build the layer info widget for the viewer.
    Args:
        viewer (napari.viewer.Viewer): The napari viewer instance.
    """
    main_window = viewer.window._qt_window
    for child in main_window.children():
        if child.objectName() == "layer controls":
            layer_controls = child
            break

    layers = viewer.layers.selection.active
    selected_layers = []
    if layers is not None:
        #check if single layer or iterable
        if not isinstance(layers, Iterable):
            selected_layers = [layers] if _checklayertype(layers) else []
        else:
            for layer in layers:
                if _checklayertype(layer):
                    selected_layers.append(layer)

    
    gui = magicgui.magicgui(layerinfowidget, 
                            layers={"value":selected_layers}, 
                            call_button=False, 
                            auto_call=True)
    gui.layers.native.setEnabled(False)
    
    docked_gui = viewer.window.add_dock_widget(gui, name='layer information', area='right')

    if layer_controls is not None:
        viewer.window._qt_window.tabifyDockWidget(layer_controls, docked_gui)


def workspacewidget(table:dict[str, int]):
    pass


def _buildworkspacewidget(viewer: 'napari.viewer.Viewer'):
    """Build the workspace widget for the viewer.
    Args:
        viewer (napari.viewer.Viewer): The napari viewer instance.
    """
    main_window = viewer.window._qt_window
    for child in main_window.children():
        if child.objectName() == "layer list":
            layer_list = child
            break


    gui = magicgui.magicgui(workspacewidget, call_button=True)
    docked_gui = viewer.window.add_dock_widget(gui, name='workspace', area='left')
    
    if layer_list is not None:
        viewer.window._qt_window.tabifyDockWidget(layer_list, docked_gui)
    return





    
    
    