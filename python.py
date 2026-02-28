import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QColorDialog, QFileDialog
)
from PyQt6.QtGui import QPainter, QColor, QPen, QImage
from PyQt6.QtCore import Qt

class PixelEditor(QWidget):
    def __init__(self, size=16, scale=24):
        super().__init__()
        self.size = size
        self.scale = scale
        self.canvas_px = size * scale

        self.setFixedSize(self.canvas_px + 180, self.canvas_px)
        self.setWindowTitle("pixel.hua 编辑器")

        self.image = QImage(
            self.size, self.size,
            QImage.Format.Format_ARGB32
        )
        self.image.fill(QColor(0, 0, 0, 0))

        self.color = QColor(0, 0, 0, 255)
        self.mode = "brush"

        y = 10
        QPushButton("颜色", self, clicked=self.pick_color)\
            .move(self.canvas_px + 10, y)
        y += 40
        QPushButton("画笔", self, clicked=lambda: self.set_mode("brush"))\
            .move(self.canvas_px + 10, y)
        y += 40
        QPushButton("透明橡皮", self, clicked=lambda: self.set_mode("eraser"))\
            .move(self.canvas_px + 10, y)
        y += 40
        QPushButton("保存 PNG", self, clicked=self.save_png)\
            .move(self.canvas_px + 10, y)
        y += 40
        QPushButton("保存 .hua", self, clicked=self.save_hua)\
            .move(self.canvas_px + 10, y)
        y += 40
        QPushButton("打开 .hua", self, clicked=self.load_hua)\
            .move(self.canvas_px + 10, y)

    def set_mode(self, m):
        self.mode = m

    def pick_color(self):
        c = QColorDialog.getColor(self.color)
        if c.isValid():
            self.color = c

    # ===== 鼠标 =====
    def mousePressEvent(self, e):
        self.apply_pixel(e)

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.MouseButton.LeftButton:
            self.apply_pixel(e)

    def apply_pixel(self, e):
        x = int(e.position().x() // self.scale)
        y = int(e.position().y() // self.scale)
        if 0 <= x < self.size and 0 <= y < self.size:
            if self.mode == "brush":
                self.image.setPixelColor(x, y, self.color)
            else:
                self.image.setPixelColor(x, y, QColor(0, 0, 0, 0))
            self.update()

    def paintEvent(self, e):
        p = QPainter(self)

        p.fillRect(0, 0, self.canvas_px, self.canvas_px, QColor(30, 30, 30))

        for y in range(self.size):
            for x in range(self.size):
                c = self.image.pixelColor(x, y)
                if c.alpha() == 0:
                    p.fillRect(
                        x*self.scale, y*self.scale,
                        self.scale, self.scale,
                        QColor(0, 255, 0)
                    )
                else:
                    p.fillRect(
                        x*self.scale, y*self.scale,
                        self.scale, self.scale,
                        c
                    )

        p.setPen(QPen(QColor(0, 0, 0, 60)))
        for i in range(self.size + 1):
            p.drawLine(i*self.scale, 0, i*self.scale, self.canvas_px)
            p.drawLine(0, i*self.scale, self.canvas_px, i*self.scale)

    def save_png(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "保存 PNG", "", "PNG (*.png)"
        )
        if path:
            self.image.save(path)

    def save_hua(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "保存 .hua", "", "HUA (*.hua)"
        )
        if not path:
            return

        pixels = []
        for y in range(self.size):
            for x in range(self.size):
                c = self.image.pixelColor(x, y)
                pixels.append([c.red(), c.green(), c.blue(), c.alpha()])

        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "version": 1,
                "size": self.size,
                "pixels": pixels
            }, f)

    def load_hua(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "打开 .hua", "", "HUA (*.hua)"
        )
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("size") != self.size:
            return

        i = 0
        for y in range(self.size):
            for x in range(self.size):
                r, g, b, a = data["pixels"][i]
                self.image.setPixelColor(x, y, QColor(r, g, b, a))
                i += 1

        self.update()

if __name__ == "__main__":
    app = QApplication([])
    w = PixelEditor()
    w.show()
    app.exec()
