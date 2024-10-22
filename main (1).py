from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
import sys
from ui import Ui_MainWindow
import logging
from read_data import *

logger = logging.getLogger(__name__)
logging.basicConfig(filename='error.log', filemode='w', level=logging.DEBUG,encoding='utf8')


def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        #Will call default excepthook
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        #Create a critical level log message with info from the except hook.
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(f'Непредвиденная ошибка. Попробуйте запустить программу повторно. В случае повторения ошибки - обратись к разработчику.')
    msg.setWindowTitle("Error")
    msg.exec_()
#Assign the excepthook to the handler
sys.excepthook = handle_unhandled_exception


#Create application
app = QtWidgets.QApplication(sys.argv)

#Create form init UI
MainWindow = QtWidgets.QDialog()
MainWindow.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
MainWindow.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint, True)
ui = Ui_MainWindow()
ui.setupUi(MainWindow)

MainWindow.show()

#Run main loop
sys.exit(app.exec_())
