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
        loadUi("A4.ui", self)
        self.image = None
        self.gray_image = None
        self.brightness_image = None

        self.loadbutton.clicked.connect(self.loadClicked)
        self.GrayScaleButton.clicked.connect(self.grayClicked)
        self.saveButton.clicked.connect(self.saveClicked)
        self.actionBrightness.triggered.connect(self.brightnessClicked)

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
        self.gray_image = None
        self.brightness_image = None
        self.displayImage(self.image, window=1)

    @pyqtSlot()
    def grayClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.gray_image = gray
        self.displayImage(self.gray_image, window=2)

    @pyqtSlot()
    def brightnessClicked(self):
        if self.gray_image is None:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "Klik Grayscale dulu untuk menghasilkan image grayscale.",
            )
            return

        # Command Soal 1: Terapkan Persamaan (3), f'(x,y)=f(x,y)+b.
        brightness = 50
        bright = np.clip(self.gray_image.astype(np.int16) + brightness, 0, 255).astype(np.uint8)
        # Command Soal 2: Lakukan clipping ke rentang 0..255.
        # (Clipping sudah dilakukan oleh np.clip di atas.)

        # Command Soal 3: Analisis sebelum/sesudah brightness.
        print("\n=== ANALISIS BRIGHTNESS (A4) ===")
        print(
            f"Sebelum -> min:{int(np.min(self.gray_image))}, "
            f"max:{int(np.max(self.gray_image))}, "
            f"mean:{float(np.mean(self.gray_image)):.2f}"
        )
        print(
            f"Sesudah  -> min:{int(np.min(bright))}, "
            f"max:{int(np.max(bright))}, "
            f"mean:{float(np.mean(bright)):.2f}"
        )

        # Command Soal 4: Display image brightness.
        self.brightness_image = bright
        self.displayImage(self.brightness_image, window=3)

    @pyqtSlot()
    def saveClicked(self):
        if self.brightness_image is not None:
            image_to_save = self.brightness_image
        elif self.gray_image is not None:
            image_to_save = self.gray_image
        else:
            image_to_save = self.image

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

        if window == 1:
            target_label = self.imglabel
        elif window == 2:
            target_label = self.imglabel_2
        else:
            target_label = getattr(self, "imglabel3", None) or getattr(self, "imglabel_3", None)
            if target_label is None:
                QtWidgets.QMessageBox.warning(
                    self,
                    "UI Error",
                    "Label brightness (imglabel3/imglabel_3) tidak ditemukan di A4.ui.",
                )
                return

        target_label.setPixmap(QPixmap.fromImage(qimg))
        target_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        target_label.setScaledContents(True)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ShowImage()
    window.setWindowTitle("Show Image GUI")
    window.show()
    sys.exit(app.exec_())
