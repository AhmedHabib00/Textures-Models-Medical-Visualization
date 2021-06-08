import vtk
import sys
from PyQt5 import QtCore , QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog,QFileDialog
from PyQt5 import Qt
from vtk.util import numpy_support
from vtk.util.colors import tomato
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from Gui_1 import Ui_MainWindow 

path='./data'

surfaceExtractor = vtk.vtkContourFilter()
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.vtkWidget = None
        self.vl = None
        self.ren = None
        self.iren = None
        self.reader= None
        self.PathDicom =''
        self.mode = True
        self.volumeColor = None
        self.pushButton.clicked.connect(self.openDICOM)
        self.pushButton_3.clicked.connect(self.invert)
        self.pushButton_4.clicked.connect(self.invert_2)
        self.horizontalSlider.valueChanged.connect(self.slider_SLOT)

    def openDICOM(self):
         if (self.PathDicom == ''):
            name=QFileDialog.getExistingDirectory(self, 'Open folder',path)
            self.PathDicom = name
            self.VtkRender()
         else:
            name=QFileDialog.getExistingDirectory(self, 'Open folder',path)
            self.PathDicom = name
            self.VtkMain() 

    def VtkRender(self):
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl = Qt.QVBoxLayout() 
        self.vl.addWidget(self.vtkWidget)
        self.VtkMain()
        

    def VtkMain(self):
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDataByteOrderToLittleEndian()
        self.reader.SetDirectoryName(self.PathDicom)
        self.reader.Update()

        if(self.mode):
            self.surfaceRendering()
        else:
            self.rayCastingRendering()

    def invert(self):
         self.mode = False; 
         self.VtkMain()


    def invert_2(self):
         self.mode = True
         self.VtkMain()                    

    def surfaceRendering(self):
        surfaceExtractor.SetInputConnection(self.reader.GetOutputPort())
        surfaceExtractor.SetValue(0, -500)
        surfaceNormals = vtk.vtkPolyDataNormals()
        surfaceNormals.SetInputConnection(surfaceExtractor.GetOutputPort())
        surfaceNormals.SetFeatureAngle(60.0)
        surfaceMapper = vtk.vtkPolyDataMapper()
        surfaceMapper.SetInputConnection(surfaceNormals.GetOutputPort())
        surfaceMapper.ScalarVisibilityOff()
        surface = vtk.vtkActor()
        surface.SetMapper(surfaceMapper)
        aCamera = vtk.vtkCamera()
        aCamera.SetViewUp(0, 0, -1)
        aCamera.SetPosition(0, 1, 0)
        aCamera.SetFocalPoint(0, 0, 0)
        aCamera.ComputeViewPlaneNormal()
        self.ren.AddActor(surface)
        self.ren.SetActiveCamera(aCamera)
        self.ren.ResetCamera()
        self.ren.SetBackground(0, 0, 0)
        self.ren.ResetCameraClippingRange()
        self.frame.setLayout(self.vl)
        self.vtkWidget.Initialize()
        self.vtkWidget.GetRenderWindow().Render()
        self.vtkWidget.Start()
        self.vtkWidget.show()

    def rayCastingRendering(self):
        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputConnection(self.reader.GetOutputPort())
        volumeMapper.SetBlendModeToComposite()
        self.volumeColor = vtk.vtkColorTransferFunction()
        self.volumeColor.AddRGBPoint(1500, 0.0, 0.0, 0.0)
        self.volumeColor.AddRGBPoint(1500,  1.0, 0.5, 0.3)
        self.volumeColor.AddRGBPoint(500, 1.0, 0.5, 0.3)
        self.volumeColor.AddRGBPoint(1000, 1.0, 1.0, 0.9)
        volumeScalarOpacity = vtk.vtkPiecewiseFunction()
        volumeScalarOpacity.AddPoint(-500,    0.00)
        volumeScalarOpacity.AddPoint(0,  0.15)
        volumeScalarOpacity.AddPoint(500, 0.15)
        volumeScalarOpacity.AddPoint(1000, 0.85)
        volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(180,   2.0)
        volumeGradientOpacity.AddPoint(45,  1.5)
        volumeGradientOpacity.AddPoint(50, 1.0)
        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(self.volumeColor)
        volumeProperty.SetScalarOpacity(volumeScalarOpacity)
        volumeProperty.SetGradientOpacity(volumeGradientOpacity)
        volumeProperty.SetInterpolationTypeToLinear()
        volumeProperty.ShadeOn()
        volumeProperty.SetAmbient(0.4)
        volumeProperty.SetDiffuse(0.6)
        volumeProperty.SetSpecular(0.2)
        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)
        self.ren.AddViewProp(volume) 
        camera =  self.ren.GetActiveCamera()
        c = volume.GetCenter()
        camera.SetFocalPoint(c[0], c[1], c[2])
        camera.SetPosition(c[0] + 700, c[1], c[2])
        camera.SetViewUp(0, 0, -1)
        self.frame.setLayout(self.vl)
        self.vtkWidget.Initialize()
        self.vtkWidget.GetRenderWindow().Render()
        self.vtkWidget.Start()
        self.vtkWidget.show()

    def slider_SLOT(self,val):
            surfaceExtractor.SetValue(0, val)
            self.vtkWidget.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

















