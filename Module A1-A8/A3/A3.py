import sys
import cv2
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi


class ShowImage(QMainWindow):
    def __init__(self):
        super(ShowImage, self).__init__()
        loadUi("A3.ui", self)
        self.image = None
        self.gray_image = None

        self.loadbutton.clicked.connect(self.loadClicked)
        self.GrayScaleButton.clicked.connect(self.grayClicked)
        self.saveButton.clicked.connect(self.saveClicked)

    @pyqtSlot()
    def loadClicked(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)",
        )
        if not filename:
            return
        self.loadImage(filename)

    def loadImage(self, filename):
        self.image = cv2.imread(filename)
        if self.image is None:
            QtWidgets.QMessageBox.warning(self, "Load Image", f"Gagal membuka: {filename}")
            return
        self.displayImage(self.image, window=1)

    @pyqtSlot()
    def grayClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        # Command Soal 1: Konversi RGB/BGR ke grayscale manual (Persamaan 2).
        # BGR -> Grayscale dengan formula luminance manual.
        blue = self.image[:, :, 0]
        green = self.image[:, :, 1]
        red = self.image[:, :, 2]
        gray = np.clip(0.114 * blue + 0.587 * green + 0.299 * red, 0, 255).astype(np.uint8)

        self.gray_image = gray
        # Command Soal 2: Tampilkan matriks piksel citra keabuan.
        print("\n=== MATRIX PIXEL GRAYSCALE (A3) ===")
        print(self.gray_image)
        # Command Soal 3: Display hasil grayscale pada label hasil.
        self.displayImage(self.gray_image, window=2)

    @pyqtSlot()
    def saveClicked(self):
        image_to_save = self.gray_image if self.gray_image is not None else self.image
        if image_to_save is None:
            QtWidgets.QMessageBox.information(self, "Info", "Tidak ada image untuk disimpan.")
            return

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "PNG (*.png);;JPG (*.jpg *.jpeg);;BMP (*.bmp);;All Files (*)",
        )
        if not filename:
            return

        if cv2.imwrite(filename, image_to_save):
            QtWidgets.QMessageBox.information(self, "Save Image", f"Berhasil simpan: {filename}")
        else:
            QtWidgets.QMessageBox.warning(self, "Save Image", f"Gagal simpan: {filename}")

    def displayImage(self, image, window=1):
        if image is None:
            return

        if len(image.shape) == 2:
            qformat = QImage.Format_Grayscale8
        elif image.shape[2] == 4:
            qformat = QImage.Format_RGBA8888
        else:
            qformat = QImage.Format_RGB888

        qimg = QImage(
            image.data,
            image.shape[1],
            image.shape[0],
            image.strides[0],
            qformat,
        )

        if qformat in (QImage.Format_RGB888, QImage.Format_RGBA8888):
            qimg = qimg.rgbSwapped()

        target_label = self.imglabel if window == 1 else self.imglabel_2
        target_label.setPixmap(QPixmap.fromImage(qimg))
        target_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        target_label.setScaledContents(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ShowImage()
    window.setWindowTitle("Show Image GUI")
    window.show()
    sys.exit(app.exec_())
