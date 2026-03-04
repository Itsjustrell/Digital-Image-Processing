import os
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
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "A8.ui")
        loadUi(ui_path, self)

        self.image = None
        self.gray_image = None
        self.binary_image = None

        self.loadbutton.clicked.connect(self.loadClicked)
        self.actionBinerImage.triggered.connect(self.binaryClicked)
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
        self.gray_image = None
        self.binary_image = None
        self.displayImage(self.image, window=1)

    def gray(self):
        if self.image is None:
            return None
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return self.gray_image

    @pyqtSlot()
    def binaryClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        # 1 & 2. Load image dan ubah ke grayscale
        gray_img = self.gray()
        if gray_img is None:
            return

        # 3. Ambil tinggi dan lebar gambar
        h, w = gray_img.shape

        # Copy supaya tidak merusak gray asli
        binary_img = gray_img.copy()

        # 4. Nested looping (tinggi dulu, lalu lebar)
        for i in range(h):
            for j in range(w):

                # 5. Ambil nilai pixel
                pixel_value = int(binary_img[i, j])

                # 6,7,8. Validasi nilai pixel
                if pixel_value == 180:
                    new_value = 0
                elif pixel_value < 180:
                    new_value = 0
                else:
                    new_value = 255

                # 7. Set nilai pixel
                binary_img[i, j] = new_value

        # Simpan hasil
        self.binary_image = binary_img

        # 9. Tampilkan image
        self.displayImage(self.binary_image, window=2)

    @pyqtSlot()
    def saveClicked(self):
        if self.binary_image is not None:
            image_to_save = self.binary_image
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

        target_label = self.inputwindow if window == 1 else self.outputwindow
        target_label.setPixmap(QPixmap.fromImage(qimg))
        target_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        target_label.setScaledContents(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ShowImage()
    window.setWindowTitle("A8 - Binary Image")
    window.show()
    sys.exit(app.exec_())
