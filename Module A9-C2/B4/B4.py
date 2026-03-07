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
        loadUi("B4.ui", self)
        self.image = None
        self.processed_image = None

        self.loadbutton.clicked.connect(self.loadClicked)
        self.saveButton.clicked.connect(self.saveClicked)
        self.actionCrop.triggered.connect(self.crop_image)

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
        self.processed_image = None
        self.displayImage(self.image, window=1)
        self.displayImage(self.image, window=2)

    def _require_image(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return False
        return True

    @pyqtSlot()
    def crop_image(self):
        if not self._require_image():
            return

        h, w = self.image.shape[:2]
        start_row, ok = QtWidgets.QInputDialog.getInt(self, "Crop", f"Start row (0-{h - 1}):", 0, 0, h - 1)
        if not ok:
            return
        end_row, ok = QtWidgets.QInputDialog.getInt(self, "Crop", f"End row ({start_row + 1}-{h}):", h, start_row + 1, h)
        if not ok:
            return
        start_col, ok = QtWidgets.QInputDialog.getInt(self, "Crop", f"Start col (0-{w - 1}):", 0, 0, w - 1)
        if not ok:
            return
        end_col, ok = QtWidgets.QInputDialog.getInt(self, "Crop", f"End col ({start_col + 1}-{w}):", w, start_col + 1, w)
        if not ok:
            return

        crop_img = self.image[start_row:end_row, start_col:end_col]
        if crop_img.size == 0:
            QtWidgets.QMessageBox.warning(self, "Crop", "Koordinat crop tidak valid.")
            return

        self.processed_image = crop_img
        self.displayImage(crop_img, window=2)

    @pyqtSlot()
    def saveClicked(self):
        image_to_save = self.processed_image if self.processed_image is not None else self.image
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
        image = np.ascontiguousarray(image)

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
    window.setWindowTitle("PRAKTEK B4 - CROP IMAGE")
    window.show()
    sys.exit(app.exec_())
