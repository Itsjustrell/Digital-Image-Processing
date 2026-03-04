import os
import sys

import cv2
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi


class ShowImage(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "A7.ui")
        loadUi(ui_path, self)

        self.image = None
        self.output_image = None

        self.loadbutton.clicked.connect(self.loadClicked)
        self.actionNegative.triggered.connect(self.negativeClicked)
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
    def negativeClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # 1. Tentukan nilai konstanta maximum_intensity.
        maximum_intensity = 255

        h, w = img.shape[:2]
        for i in range(h):
            for j in range(w):
                # 2. Baca nilai array piksel.
                a = int(img[i, j])
                # 3. Terapkan Persamaan (7): f'(x,y) = 255 - f(x,y).
                b = maximum_intensity - a
                img[i, j] = b

        self.output_image = img

        # 4. Display image.
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
    window.setWindowTitle("A7 - Negative Image")
    window.show()
    sys.exit(app.exec_())
