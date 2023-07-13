// QT includes
#include <qapplication.h>
#include "OrthoViewer.h"


int main( int argc, char** argv )
{
  // QT Stuff
  QApplication app( argc, argv );

  OrthoViewer mainwindow;
  mainwindow.show();

  return app.exec();
}