#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, random
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QInputDialog, QLabel, QFrame, QDesktopWidget, QLineEdit, \
    QTextEdit, QGridLayout, QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, QPoint, QObject, pyqtSlot
from PyQt5.QtGui import *


class Communicate(QObject):
    endofgame = pyqtSignal()


class Controller:
    def __init__(self):
        self.c = Communicate()

    def update_game_state(self, new_x, new_y):
        if game_model.field[new_y][new_x] in 'XO':
            return
        game_model.field[new_y][new_x] = game_model.turn
        self.check_win_condition(new_y, new_x)
        game_viewer.update()
        if game_model.turn == 'X':
            game_model.turn = 'O'
        else:
            game_model.turn = 'X'

    def find_ray_length(self, y, x, dir_y, dir_x):
        ray_length = 0
        ray_end_x = x
        ray_end_y = y
        for i in range(1, game_model.win_length):
            new_x = x + dir_x * i
            new_y = y + dir_y * i
            if new_x > game_model.map_size - 1 or new_y > game_model.map_size - 1 \
                    or new_x < 0 or new_y < 0:
                break
            if game_model.field[new_y][new_x] == game_model.turn:
                ray_length += 1
                ray_end_x = new_x
                ray_end_y = new_y
            else:
                break
        return ray_length, ray_end_y, ray_end_x

    def check_win_condition(self, new_y, new_x):
        dirs_p = ((0, 1), (1, 0), (1, 1), (-1, 1))
        dirs_n = ((0, -1), (-1, 0), (-1, -1), (1, -1))

        for dir_n, dir_p in zip(dirs_n, dirs_p):
            n_length, n_y, n_x = self.find_ray_length(new_y, new_x, dir_n[1], dir_n[0])
            p_length, p_y, p_x = self.find_ray_length(new_y, new_x, dir_p[1], dir_p[0])
            if n_length + p_length >= game_model.win_length - 1:
                game_model.gameover = True
                game_model.end_line0 = n_y, n_x
                game_model.end_line1 = p_y, p_x

                self.c.endofgame.emit()

                return


class GameModel:
    field = []
    end_line0 = []
    end_line1 = []

    def __init__(self, map_size, win_length):
        self.map_size = map_size
        self.turn = 'X'
        self.win_length = win_length
        self.gameover = False
        for i in range(self.map_size):
            self.field.append([])
            for j in range(self.map_size):
                self.field[i].append('_')

    def clear_field(self):
        self.gameover = False
        for i in range(self.map_size):
            for j in range(self.map_size):
                self.field[i][j] = '_'


'''
class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('TikTacToe')
        self.game_viewer = GameViewer(20)
        self.setCentralWidget(self.game_viewer)
        self.game_viewer.show()
        self.show()
'''


class GameViewer(QWidget):
    def __init__(self, cell_pix_size):
        super().__init__()

        self.initUI(cell_pix_size)
        controller.c.endofgame.connect(lambda: self.showwindow())
        self.show()

    def showwindow(self):
        msg = QMessageBox(self)
        msg.setText("Game Over! {} won!".format(game_model.turn))
        msg.setInformativeText("Do you want to start again?")
        msg.setWindowTitle("Game Over")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = msg.exec_()
        if retval == QMessageBox.Yes:
            game_model.clear_field()
        elif retval == QMessageBox.No:
            self.close()

    def initUI(self, cell_pix_size):
        self.cell_pix_size = cell_pix_size
        self.setFixedSize(self.cell_pix_size * game_model.map_size + 1, self.cell_pix_size * game_model.map_size + 1)
        self.setWindowTitle('TikTacToe')

    def mouseReleaseEvent(self, event):
        i = event.pos().y()
        j = event.pos().x()
        controller.update_game_state(int(i / self.cell_pix_size), int(j / self.cell_pix_size))

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.HighQualityAntialiasing)
        map_size = game_model.map_size
        cell_h = self.cell_pix_size
        cell_w = self.cell_pix_size

        self.drawField(qp, cell_h, cell_w, map_size)
        self.drawMarks(qp, cell_h, cell_w, map_size)
        if game_model.gameover:
            self.drawEndline(qp, cell_h, cell_w)
        qp.end()

    def drawField(self, qp, h, w, map_size):
        pen = QPen(Qt.blue, 1, Qt.SolidLine)
        qp.setPen(pen)
        for i in range(map_size + 1):
            qp.drawLine(0, h * i, w * map_size, h * i)
            qp.drawLine(w * i, 0, w * i, h * map_size)

    def drawMarks(self, qp, h, w, map_size):
        for i in range(map_size):
            for j in range(map_size):
                if game_model.field[i][j] == 'X':
                    self.drawX(qp, i, j, h, w)
                elif game_model.field[i][j] == 'O':
                    self.drawO(qp, i, j, h, w)

    def drawEndline(self, qp, h, w):
        pen = QPen(Qt.green, 4, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine((game_model.end_line0[0] + 0.5) * w, (game_model.end_line0[1] + 0.5) * h,
                    (game_model.end_line1[0] + 0.5) * w, (game_model.end_line1[1] + 0.5) * h)

    def drawX(self, qp, x, y, h, w):
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(x * w + 3, y * h + 3, (x + 1) * w - 3, (y + 1) * h - 3)
        qp.drawLine(x * w + 3, (y + 1) * h - 3, (x + 1) * w - 3, y * h + 3)

    def drawO(self, qp, x, y, h, w):
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        qp.setPen(pen)
        center = QPoint((x + 0.5) * w, (y + 0.5) * h)
        qp.drawEllipse(center, w / 2 - 3, h / 2 - 3)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = Controller()
    game_model = GameModel(30, 4)
    game_viewer = GameViewer(26)
    sys.exit(app.exec_())
