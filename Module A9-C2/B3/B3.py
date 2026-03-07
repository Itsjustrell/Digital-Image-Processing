import sys
import cv2
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi


class ShowImage(QMainWindow):
    def __init__(self):
        super(ShowImage, self).__init__()
        loadUi("B3.ui", self)
        self.image = None
        self.processed_image = None
        self.preview_windows = []

        self.loadbutton.clicked.connect(self.loadClicked)
        self.saveButton.clicked.connect(self.saveClicked)

        self.actionZoomIn2x.triggered.connect(lambda: self.zoom_in(2))
        self.actionZoomIn3x.triggered.connect(lambda: self.zoom_in(3))
        self.actionZoomIn4x.triggered.connect(lambda: self.zoom_in(4))

        self.actionZoomOutHalf.triggered.connect(lambda: self.zoom_out(0.50))
        self.actionZoomOutQuarter.triggered.connect(lambda: self.zoom_out(0.25))
        self.actionZoomOutThreeQuarter.triggered.connect(lambda: self.zoom_out(0.75))

        self.actionSkewedImage.triggered.connect(self.skewed_image)

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

    def _show_resize_result(self, title, result):
        self.processed_image = result
        preview = QtWidgets.QDialog(self)
        preview.setWindowTitle(title)
        preview.resize(960, 540)

        label = QtWidgets.QLabel(preview)
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        label.setGeometry(10, 10, 940, 520)
        label.setScaledContents(True)

        if len(result.shape) == 2:
            qformat = QImage.Format_Grayscale8
        elif result.shape[2] == 4:
            qformat = QImage.Format_RGBA8888
        else:
            qformat = QImage.Format_RGB888

        qimg = QImage(
            result.data,
            result.shape[1],
            result.shape[0],
            result.strides[0],
            qformat,
        )
        if qformat in (QImage.Format_RGB888, QImage.Format_RGBA8888):
            qimg = qimg.rgbSwapped()

        label.setPixmap(QPixmap.fromImage(qimg))
        preview.show()
        self.preview_windows.append(preview)

    def zoom_in(self, scale):
        if not self._require_image():
            return

        resize_img = cv2.resize(
            self.image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )
        self._show_resize_result(f"Zoom In {scale}x", resize_img)

    def zoom_out(self, scale):
        if not self._require_image():
            return

        resize_img = cv2.resize(self.image, None, fx=scale, fy=scale)
        self._show_resize_result(f"Zoom Out {scale}", resize_img)

    @pyqtSlot()
    def skewed_image(self):
        if not self._require_image():
            return

        resize_img = cv2.resize(self.image, (900, 400), interpolation=cv2.INTER_AREA)
        self._show_resize_result("Skewed Image 900x400", resize_img)

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
    window.setWindowTitle("PRAKTEK B3 - RESIZE")
    window.show()
    sys.exit(app.exec_())
