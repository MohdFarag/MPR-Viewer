#include <qapplication.h>

#include "OrthoViewer.h"


// Constructor
OrthoViewer::OrthoViewer(QWidget* p) 
 : QMainWindow(p)
{
  setupUi(this);
  // Setup additional UI stuff

  this->treePointLists = new TreePointLists(this->pagePointLists);
  this->gridLayout_3->addWidget(this->treePointLists);
  this->treePointLists->setVisible(true);

  this->segmentationList = new SegmentationList(this->pageSegmentationList);
  this->segmentationList->setVisible(true);


  // vtk stuff
  imageReader = vtkMetaImageReader::New();
  imageReader->SetFileName("C:\\Temp\\out.mhd");
  imageReader->UpdateWholeExtent();
  cout << imageReader->GetAnatomicalOrientation() << endl;

  double *range = imageReader->GetOutput()->GetScalarRange();
  
  imageShiftScale = vtkImageShiftScale::New();
  imageShiftScale->SetInput(imageReader->GetOutput());
  imageShiftScale->SetOutputScalarTypeToUnsignedChar();
  imageShiftScale->SetShift(-(double)range[0]);
  imageShiftScale->SetScale(255.0/(double)(range[1]-range[0]));
  imageShiftScale->UpdateWholeExtent();

  imageWindowLevel = vtkImageMapToWindowLevelColors::New();
  imageWindowLevel->SetInputConnection(imageShiftScale->GetOutputPort());
  imageWindowLevel->SetWindow(100.0);
  imageWindowLevel->SetLevel(50.0);
  imageWindowLevel->UpdateWholeExtent();

  imageMapToColors = vtkImageMapToColors::New();

  imageMapToColors->SetOutputFormatToRGBA();
  imageMapToColors->SetInput(imageWindowLevel->GetOutput());
  
  grayscaleLut = vtkLookupTable::New();
  grayscaleLut->SetNumberOfTableValues(256);
  grayscaleLut->SetTableRange(0, 255);
  grayscaleLut->SetRampToLinear();
  grayscaleLut->SetHueRange(0, 0);
  grayscaleLut->SetSaturationRange(0, 0);
  grayscaleLut->SetValueRange(0, 1);
  grayscaleLut->SetAlphaRange(1, 1);
  grayscaleLut->Build();
  imageMapToColors->SetLookupTable(grayscaleLut);
  imageMapToColors->UpdateWholeExtent();

  segmentationImage = vtkImageData::New();
  segmentationImage->DeepCopy(imageShiftScale->GetOutput());
  int sz = segmentationImage->GetDimensions()[0] * segmentationImage->GetDimensions()[1] * segmentationImage->GetDimensions()[2];
  unsigned char * pt= (unsigned char*)(segmentationImage->GetScalarPointer());
  for(int i=0;i<sz;i++)
	pt[i]=0;
  segmentationImage->Update();

  segmentationLabelImage = vtkImageMapToColors::New();
  segmentationLabelImage->SetInput(segmentationImage);
  segmentationLabelImage->SetOutputFormatToRGBA();
  segmentationLabelLookupTable = vtkLookupTable::New();
  segmentationLabelLookupTable->SetNumberOfTableValues(256);
  segmentationLabelLookupTable->SetTableRange(0, 255);
  segmentationLabelLookupTable->SetTableValue(0, 0, 1, 0, 0.0);
  segmentationLabelLookupTable->SetTableValue(1, 1.0, 0, 0, 0.5);
  segmentationLabelImage->SetLookupTable(segmentationLabelLookupTable);
  segmentationLabelImage->UpdateWholeExtent();

  imageBlender = vtkImageBlend::New();
  imageBlender->AddInput(imageMapToColors->GetOutput());
  imageBlender->AddInput(segmentationLabelImage->GetOutput());
  imageBlender->SetOpacity(0, 1);
  imageBlender->SetOpacity(1, 1);
  imageBlender->UpdateWholeExtent();

  commandSliceSelect = CommandSliceSelect::New();
  commandSliceSelect->imageWindowLevel = imageWindowLevel;
  treePointLists->currentPoint = commandSliceSelect->currentPoint;

  commandSegment = CommandSegment::New();
  commandSegment->setSegmentationImage(segmentationImage);
  commandSegment->setRealImage(imageShiftScale->GetOutput());


  for(int i=0;i<3;i++)
  {
	vecReslice.push_back(vtkImageReslice::New());
	commandSliceSelect->vecImageReslice.push_back(vecReslice[i]);
	commandSegment->vecImageReslice.push_back(vecReslice[i]);
  }


  vecReslice[0]->SetResliceAxesDirectionCosines(1, 0, 0, 0, -1, 0, 0, 0, 1);
  vecReslice[1]->SetResliceAxesDirectionCosines(0, 1, 0, 0, 0, 1, 1, 0, 0);
  vecReslice[2]->SetResliceAxesDirectionCosines(1, 0, 0, 0, 0, 1, 0, 1, 0);


  for(int i=0;i<3;i++)
	  vecImageActor.push_back(vtkImageActor::New());


  for(int i=0;i<4;i++)
  {
	  vecRenderer.push_back(vtkRenderer::New());
	  commandSegment->vecRenderer.push_back(this->vecRenderer[i]);
	  //vecRenderer[i]->GetActiveCamera()->SetParallelProjection(1);
  }

  this->treePointLists->ren = vecRenderer[3];
  this->treePointLists->image = imageWindowLevel->GetOutput();

  for(int i=0;i<3;i++)
	  vecInteractorStyle.push_back(vtkInteractorStyleMy2D::New());

  for(int i=0;i<3;i++)
  {
	  vecInteractorStyle[i]->InteractorNumber = i;
	  vecInteractorStyle[i]->AddObserver(vtkCommand::UserEvent, commandSliceSelect);
	  vecInteractorStyle[i]->AddObserver(vtkCommand::WindowLevelEvent, commandSliceSelect);
	  vecInteractorStyle[i]->AddObserver(vtkCommand::StartWindowLevelEvent, commandSliceSelect);
	  vecInteractorStyle[i]->AddObserver(vtkCommand::SelectionChangedEvent, commandSliceSelect);
	  vecInteractorStyle[i]->AddObserver(UserCommand::StartSegmentationAdd, commandSegment);
	  vecInteractorStyle[i]->AddObserver(UserCommand::StartSegmentationSub, commandSegment);
	  vecInteractorStyle[i]->AddObserver(UserCommand::StopSegmentationAdd, commandSegment);
	  vecInteractorStyle[i]->AddObserver(UserCommand::StopSegmentationSub, commandSegment);
	  vecInteractorStyle[i]->AddObserver(UserCommand::MoveSegmentationAdd, commandSegment);
	  vecInteractorStyle[i]->AddObserver(UserCommand::MoveSegmentationSub, commandSegment);
	  vecInteractorStyle[i]->SegmentationModeEnabled = false;
	  this->segmentationList->vecInteractorStyle.push_back(vecInteractorStyle[i]);

	  commandSliceSelect->styleId[i] = vecInteractorStyle[i];
	  commandSliceSelect->vecImageActor.push_back(vecImageActor[i]);

	  commandSegment->styleId[i] = vecInteractorStyle[i];
  }
  
  for(int i=0;i<4;i++)
  {
	  vecTextActor.push_back(vtkTextActor::New());
	  vecTextActor[i]->SetPosition(5, 5);
	  vecRenderer[i]->AddActor2D(vecTextActor[i]);
	  char s[50];
	  sprintf_s(s, "L/W: %2.1f/%2.1f | (x,y,z): (%.1f, %.1f, %.1f)", 50.0, 100.0, 0.0, 0.0, 0.0);
	  vecTextActor[i]->SetInput(s);
  }

  commandSliceSelect->vecTextActor = vecTextActor;

  this->qvtkWidget_ul->GetRenderWindow()->AddRenderer(vecRenderer[0]);
  this->qvtkWidget_ur->GetRenderWindow()->AddRenderer(vecRenderer[1]);
  this->qvtkWidget_ll->GetRenderWindow()->AddRenderer(vecRenderer[2]);
  this->qvtkWidget_lr->GetRenderWindow()->AddRenderer(vecRenderer[3]);

  this->segmentationList->renderer = vecRenderer[3];
  this->segmentationList->segmentationBufferImage = segmentationImage;
  this->segmentationList->commandSegment = commandSegment;

  this->qvtkWidget_ul->GetRenderWindow()->GetInteractor()->SetInteractorStyle(vecInteractorStyle[0]);
  this->qvtkWidget_ur->GetRenderWindow()->GetInteractor()->SetInteractorStyle(vecInteractorStyle[1]);
  this->qvtkWidget_ll->GetRenderWindow()->GetInteractor()->SetInteractorStyle(vecInteractorStyle[2]);
  commandSliceSelect->interactorStyleWindow3D = this->qvtkWidget_lr->GetRenderWindow()->GetInteractor()->GetInteractorStyle();
  commandSegment->styleId[3] = this->qvtkWidget_lr->GetRenderWindow()->GetInteractor()->GetInteractorStyle();

  
  for(int i=0;i<3;i++)
  {
	  vecReslice[i]->SetInput(imageBlender->GetOutput());
	  vecReslice[i]->SetOutputDimensionality(2);
	  vecReslice[i]->SetInterpolationModeToLinear();
	  //vecReslice[i]->SetInterpolationModeToNearestNeighbor();
	  vecReslice[i]->UpdateWholeExtent();
	  vecImageActorOrtho.push_back(vtkImageActor::New());
	  vecImageActorOrtho[i]->SetInput(vecReslice[i]->GetOutput());
	  vecImageActorOrtho[i]->SetUserMatrix(vecReslice[i]->GetResliceAxes());
      vecImageActor[i]->SetInput(vecReslice[i]->GetOutput());
	  vecRenderer[i]->AddActor(vecImageActor[i]);
	  vecRenderer[3]->AddActor(vecImageActorOrtho[i]);
  }

}

OrthoViewer::~OrthoViewer()
{
	for(int i=0;i<4;i++)
		vecRenderer[i]->Delete();

	for(int i=0;i<3;i++)
		vecReslice[i]->Delete();

	for(int i=0;i<3;i++)
		vecImageActor[i]->Delete();

	imageReader->Delete();
}


void OrthoViewer::on_actionExit_triggered(bool checked)
{
	qApp->exit();
}

void OrthoViewer::on_actionOpen_triggered(bool checked)
{
	QString fileName = QFileDialog::getOpenFileName(this, tr("Open Image"), "c:\\temp", tr("Image Files (*.mhd)"));
	if(fileName == "")
		return;

	this->statusbar->showMessage("Reading file" + fileName);

	imageReader->SetFileName(fileName.toStdString().c_str());
	imageReader->UpdateWholeExtent();
	double *range = imageReader->GetOutput()->GetScalarRange();

	imageShiftScale->SetShift(-(double)range[0]);
	imageShiftScale->SetScale(255.0/(double)(range[1]-range[0]));
	imageShiftScale->UpdateWholeExtent();

	imageWindowLevel->SetWindow(100.0);
	imageWindowLevel->SetLevel(50.0);
	imageWindowLevel->UpdateWholeExtent();

    this->qvtkWidget_ul->GetRenderWindow()->Render();
    this->qvtkWidget_ur->GetRenderWindow()->Render();
    this->qvtkWidget_ll->GetRenderWindow()->Render();
    this->qvtkWidget_lr->GetRenderWindow()->Render();
}

void OrthoViewer::on_buttonMaximize_ul_clicked(bool checked)
{
	static bool isMax = false;
	if(!isMax)
	{
		this->buttonMaximize_ul->setText("-");

		this->qvtkWidget_ll->hide();
		this->buttonMaximize_ll->hide();
		this->qvtkWidget_ur->hide();
		this->buttonMaximize_ur->hide();
		this->qvtkWidget_lr->hide();
		this->buttonMaximize_lr->hide();
		isMax = true;
	}
	else
	{
		this->buttonMaximize_ul->setText("+");
		this->qvtkWidget_ll->show();
		this->buttonMaximize_ll->show();
		this->qvtkWidget_ur->show();
		this->buttonMaximize_ur->show();
		this->qvtkWidget_lr->show();
		this->buttonMaximize_lr->show();
		isMax = false;
	}
}

void OrthoViewer::on_buttonMaximize_ur_clicked(bool checked)
{
	static bool isMax = false;
	if(!isMax)
	{
		this->buttonMaximize_ur->setText("-");

		this->qvtkWidget_ll->hide();
		this->buttonMaximize_ll->hide();
		this->qvtkWidget_ul->hide();
		this->buttonMaximize_ul->hide();
		this->qvtkWidget_lr->hide();
		this->buttonMaximize_lr->hide();
		isMax = true;
	}
	else
	{
		this->buttonMaximize_ur->setText("+");
		this->qvtkWidget_ll->show();
		this->buttonMaximize_ll->show();
		this->qvtkWidget_ul->show();
		this->buttonMaximize_ul->show();
		this->qvtkWidget_lr->show();
		this->buttonMaximize_lr->show();
		isMax = false;
	}
}

void OrthoViewer::on_buttonMaximize_ll_clicked(bool checked)
{
	static bool isMax = false;
	if(!isMax)
	{
		this->buttonMaximize_ll->setText("-");

		this->qvtkWidget_ul->hide();
		this->buttonMaximize_ul->hide();
		this->qvtkWidget_ur->hide();
		this->buttonMaximize_ur->hide();
		this->qvtkWidget_lr->hide();
		this->buttonMaximize_lr->hide();
		isMax = true;
	}
	else
	{
		this->buttonMaximize_ll->setText("+");
		this->qvtkWidget_ul->show();
		this->buttonMaximize_ul->show();
		this->qvtkWidget_ur->show();
		this->buttonMaximize_ur->show();
		this->qvtkWidget_lr->show();
		this->buttonMaximize_lr->show();
		isMax = false;
	}
}

void OrthoViewer::on_buttonMaximize_lr_clicked(bool checked)
{
	static bool isMax = false;
	if(!isMax)
	{
		this->buttonMaximize_lr->setText("-");

		this->qvtkWidget_ll->hide();
		this->buttonMaximize_ll->hide();
		this->qvtkWidget_ur->hide();
		this->buttonMaximize_ur->hide();
		this->qvtkWidget_ul->hide();
		this->buttonMaximize_ul->hide();
		isMax = true;
	}
	else
	{
		this->buttonMaximize_lr->setText("+");
		this->qvtkWidget_ll->show();
		this->buttonMaximize_ll->show();
		this->qvtkWidget_ur->show();
		this->buttonMaximize_ur->show();
		this->qvtkWidget_ul->show();
		this->buttonMaximize_ul->show();
		isMax = false;
	}
}

void OrthoViewer::on_actionFullScreen_triggered(bool checked)
{
	if(checked)
		this->showFullScreen();
	else
		this->showNormal();


}