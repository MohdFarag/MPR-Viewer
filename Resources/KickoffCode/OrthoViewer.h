#ifndef ORTHOVIEWER_H
#define ORTHOVIEWER_H

#include "qmainwindow.h"
#include <QFileDialog>
#include <QString>
#include "TreePointLists.h"
#include "SegmentationList.h"

#include "ui_uiOrthoViewer.h"

#include <vtkRenderer.h>
#include <vtkRenderWindow.h>
#include <vtkImageReslice.h>
#include <vtkMetaImageReader.h>
#include <vtkImageActor.h>
#include <vtkImageMapToWindowLevelColors.h>
#include <vtkInteractorStyleMy2D.h>
#include <vtkImageData.h>
#include <vtkCamera.h>
#include <vtkImageShiftScale.h>
#include <vtkAbstractTransform.h>
#include <vtkLinearTransform.h>
#include <vtkLookupTable.h>
#include <vtkInformation.h>
#include <vtkTextActor.h>
#include <vtkImageBlend.h>
#include <vtkImageMapToColors.h>

#include "CommandSliceSelect.h"
#include "CommandSegment.h"
#include "SegmentationImage.h"

#include <iostream>
#include <vector>
#include <stdio.h>

using namespace std;



class OrthoViewer : public QMainWindow, private Ui_MainWindow
{
    Q_OBJECT

public:

    // Constructor/Destructor
    OrthoViewer(QWidget* parent = 0);
    ~OrthoViewer();

public slots:


protected:

protected slots:

private:

	// additional UI stuff
	TreePointLists *treePointLists;

	SegmentationList *segmentationList;

	// vtk stuff
	vector<vtkRenderer*> vecRenderer;

	vtkMetaImageReader *imageReader;

	vtkImageShiftScale *imageShiftScale;
	
	vtkImageMapToWindowLevelColors *imageWindowLevel;

	vtkImageMapToColors *imageMapToColors;

	vtkLookupTable *grayscaleLut;

	vtkImageData *segmentationImage;

	vtkImageMapToColors *segmentationLabelImage;

	vtkLookupTable *segmentationLabelLookupTable;

	vtkImageBlend *imageBlender;

	
	vector<vtkImageReslice*> vecReslice;

	vector<vtkImageActor*> vecImageActor;

	vector<vtkImageActor*> vecImageActorOrtho;

	vector<vtkInteractorStyleMy2D*> vecInteractorStyle;
	
	vector<vtkTextActor*> vecTextActor;

	CommandSliceSelect* commandSliceSelect;

	CommandSegment* commandSegment;

	
		
	private slots:
		void on_actionExit_triggered(bool checked=false);
		void on_actionOpen_triggered(bool checked=false);
		void on_actionFullScreen_triggered(bool checked=false);
		void on_buttonMaximize_ul_clicked(bool checked=false);
		void on_buttonMaximize_ur_clicked(bool checked=false);
		void on_buttonMaximize_ll_clicked(bool checked=false);
		void on_buttonMaximize_lr_clicked(bool checked=false);
  
};

#endif // OrthoViewer_H

