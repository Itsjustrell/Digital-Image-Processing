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
        super(ShowImage, self).__init__()
        loadUi("C1.ui", self)
        self.img1 = None
        self.img2 = None
        self.result_image = None

        self.loadbutton.clicked.connect(self.load_pair)
        self.saveButton.clicked.connect(self.save_result)

        self.actionPenjumlahan.triggered.connect(self.op_add)
        self.actionPengurangan.triggered.connect(self.op_subtract)
        self.actionPerkalian.triggered.connect(self.op_multiply)
        self.actionPembagian.triggered.connect(self.op_divide)

    def _image_paths(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "img1.jpg"), os.path.join(base_dir, "img2.jpg")

    @pyqtSlot()
    def load_pair(self):
        path1, path2 = self._image_paths()
        img1 = cv2.imread(path1, 0)
        img2 = cv2.imread(path2, 0)

        if img1 is None or img2 is None:
            QtWidgets.QMessageBox.warning(
                self,
                "Load Image",
                f"Pastikan file ada:\n{path1}\n{path2}",
            )
            return

        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]), interpolation=cv2.INTER_AREA)

        self.img1 = img1
        self.img2 = img2
        self.result_image = None
        self.displayImage(self.img1, window=1)
        self.imglabel_2.clear()

    def _require_pair(self):
        if self.img1 is None or self.img2 is None:
            self.load_pair()
        if self.img1 is None or self.img2 is None:
            return False
        return True

    def _show_result(self, result):
        self.result_image = np.clip(result, 0, 255).astype(np.uint8)
        self.displayImage(self.result_image, window=2)

    @pyqtSlot()
    def op_add(self):
        if not self._require_pair():
            return
        add_img = self.img1.astype(np.int16) + self.img2.astype(np.int16)
        self._show_result(add_img)

    @pyqtSlot()
    def op_subtract(self):
        if not self._require_pair():
            return
        subtract = self.img1.astype(np.int16) - self.img2.astype(np.int16)
        self._show_result(subtract)

    @pyqtSlot()
    def op_multiply(self):
        if not self._require_pair():
            return
        multiply = self.img1.astype(np.float32) * self.img2.astype(np.float32) / 255.0
        self._show_result(multiply)

    @pyqtSlot()
    def op_divide(self):
        if not self._require_pair():
            return
        img2_safe = np.where(self.img2 == 0, 1, self.img2)
        divide = self.img1.astype(np.float32) / img2_safe.astype(np.float32) * 255.0
        self._show_result(divide)

    @pyqtSlot()
    def save_result(self):
        if self.result_image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Belum ada hasil operasi untuk disimpan.")
            return

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "PNG (*.png);;JPG (*.jpg *.jpeg);;BMP (*.bmp);;All Files (*)",
        )
        if not filename:
            return

        if cv2.imwrite(filename, self.result_image):
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
    window.setWindowTitle("PRAKTEK C1 - OPERASI ARITMATIKA")
    window.show()
    sys.exit(app.exec_())
