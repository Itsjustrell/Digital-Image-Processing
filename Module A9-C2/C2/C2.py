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
        loadUi("C2.ui", self)
        self.img1 = None
        self.img2 = None
        self.result_image = None

        self.loadbutton.clicked.connect(self.load_pair)
        self.saveButton.clicked.connect(self.save_result)

        self.actionAND.triggered.connect(self.op_and)
        self.actionOR.triggered.connect(self.op_or)
        self.actionXOR.triggered.connect(self.op_xor)

    def _image_paths(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "img1.jpg"), os.path.join(base_dir, "img2.jpg")

    @pyqtSlot()
    def load_pair(self):
        path1, path2 = self._image_paths()
        img1 = cv2.imread(path1, 1)
        img2 = cv2.imread(path2, 1)

        if img1 is None or img2 is None:
            QtWidgets.QMessageBox.warning(
                self,
                "Load Image",
                f"Pastikan file ada:\n{path1}\n{path2}",
            )
            return

        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]), interpolation=cv2.INTER_AREA)

        self.img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
        self.img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        self.result_image = None

        self.displayImage(self.img1, window=1)
        self.imglabel_2.clear()

    def _require_pair(self):
        if self.img1 is None or self.img2 is None:
            self.load_pair()
        return self.img1 is not None and self.img2 is not None

    def _show_result(self, op_name, result):
        self.result_image = np.ascontiguousarray(result)
        self.displayImage(self.result_image, window=2)
        self.show_analysis(op_name, self.img1, self.result_image)

    def show_analysis(self, op_name, before, after):
        diff = cv2.absdiff(before, after)
        changed_pixels = int(np.count_nonzero(np.any(diff != 0, axis=2)))
        total_pixels = before.shape[0] * before.shape[1]
        changed_percent = (changed_pixels / total_pixels) * 100.0 if total_pixels else 0.0
        mean_before = float(np.mean(before))
        mean_after = float(np.mean(after))

        QtWidgets.QMessageBox.information(
            self,
            f"Analisis {op_name}",
            (
                f"Total piksel: {total_pixels}\n"
                f"Piksel berubah: {changed_pixels} ({changed_percent:.2f}%)\n"
                f"Rata-rata intensitas sebelum: {mean_before:.2f}\n"
                f"Rata-rata intensitas sesudah: {mean_after:.2f}"
            ),
        )

    @pyqtSlot()
    def op_and(self):
        if not self._require_pair():
            return
        op_and = cv2.bitwise_and(self.img1, self.img2)
        self._show_result("AND", op_and)

    @pyqtSlot()
    def op_or(self):
        if not self._require_pair():
            return
        op_or = cv2.bitwise_or(self.img1, self.img2)
        self._show_result("OR", op_or)

    @pyqtSlot()
    def op_xor(self):
        if not self._require_pair():
            return
        op_xor = cv2.bitwise_xor(self.img1, self.img2)
        self._show_result("XOR", op_xor)

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

        image_bgr = cv2.cvtColor(self.result_image, cv2.COLOR_RGB2BGR)
        if cv2.imwrite(filename, image_bgr):
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

        target_label = self.imglabel if window == 1 else self.imglabel_2
        target_label.setPixmap(QPixmap.fromImage(qimg))
        target_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        target_label.setScaledContents(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ShowImage()
    window.setWindowTitle("PRAKTEK C2 - OPERASI BOOLEAN")
    window.show()
    sys.exit(app.exec_())
