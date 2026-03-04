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
        ui_path = os.path.join(os.path.dirname(__file__), "A6.ui")
        loadUi(ui_path, self)

        self.image = None
        self.output_image = None

        self.loadbutton.clicked.connect(self.loadClicked)
        self.actionContrastStretching.triggered.connect(self.contrastStretchingClicked)
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
        self.output_image = None
        self.displayImage(self.image, window=1)

    @pyqtSlot()
    def contrastStretchingClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # 1. Konstanta 8-bit.
        max_pixel = 255
        min_pixel = 0

        rmin = int(np.min(img))
        rmax = int(np.max(img))

        h, w = img.shape[:2]
        for i in range(h):
            for j in range(w):
                # 2. Baca nilai array piksel.
                a = int(img[i, j])

                # 3-4. Clipping awal terhadap batas minimum dan maksimum.
                if a > max_pixel:
                    a = max_pixel
                elif a < min_pixel:
                    a = min_pixel

                # 5. Terapkan Persamaan (6).
                if rmax == rmin:
                    b = a
                else:
                    b = ((a - rmin) / (rmax - rmin)) * (max_pixel - min_pixel) + min_pixel

                img[i, j] = int(np.clip(round(b), min_pixel, max_pixel))

        self.output_image = img

        # 6. Tampilkan hasil.
        self.displayImage(self.output_image, window=2)

    @pyqtSlot()
    def saveClicked(self):
        image_to_save = self.output_image if self.output_image is not None else self.image
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
    window.setWindowTitle("A6 - Contrast Stretching")
    window.show()
    sys.exit(app.exec_())
