import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QMenu, QAction, QMessageBox, QFormLayout,
                             QLabel, QLineEdit, QPushButton, QDialog, QInputDialog,
                             QFileDialog)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from signal_ import Signal


class Chart(FigureCanvas):

    def __init__(self, parent):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.setParent(parent)

    ###
    def redraw_plot(self, t, v, overlap=False):
        if not overlap:
            self.ax.clear()

        self.ax.plot(t, v)
        self.draw()

    def draw_peaks(self, signal_obj: Signal):
        raise NotImplementedError

    ###
    def save_as_png(self, path):
        self.fig.savefig(path)


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.signal_object = Signal()
        # методи ініціалізації складових вікна
        self._config()
        self._chart()  #
        self._actions()
        self._menubar()
        self._connect_actions()

    ### конфіг методи
    def _actions(self):
        # save submenu
        self.file_save_png = QAction('&PNG', self)  #
        self.file_save_csv = QAction('&TXT', self)  #
        # signal
        self.signal_from_file = QAction('&Open...', self)  #
        self.signal_simulate = QAction('&Simulate', self)  #
        self.signal_detect_peaks = QAction('&ECG Peaks', self)  #
        self.signal_reset_transforms = QAction('&Reset', self)
        # transform submenu
        self.signal_transform_fft = QAction('&FFT', self)  #
        self.signal_transform_dct = QAction('&Discrete Cosine Transform', self)  #
        # help
        self.help_about = QAction('&About', self)  #

    def _menubar(self):
        menubar = self.menuBar()  #
        # menus
        file_menu = QMenu('&File', self)
        file_save_submenu = file_menu.addMenu('&Save as...')
        signal_menu = QMenu('&Signal', self)
        transform_submenu = signal_menu.addMenu('&Transform')
        help_menu = QMenu('&Help', self)
        # додати меню до панелі
        menubar.addMenu(file_menu)
        menubar.addMenu(signal_menu)
        menubar.addMenu(help_menu)
        # призначити дії для них
        file_save_submenu.addAction(self.file_save_png)  #
        file_save_submenu.addAction(self.file_save_csv)  #

        signal_menu.addAction(self.signal_from_file)  #
        signal_menu.addAction(self.signal_simulate)  #
        signal_menu.addAction(self.signal_detect_peaks)  #
        signal_menu.addAction(self.signal_reset_transforms)  #

        transform_submenu.addAction(self.signal_transform_fft)  #
        transform_submenu.addAction(self.signal_transform_dct)  #

        help_menu.addAction(self.help_about)  #

    def _connect_actions(self):
        # save submenu
        self.file_save_png.triggered.connect(self.file_save_image)  #
        self.file_save_csv.triggered.connect(self.file_save_vector)  #
        # signal
        self.signal_from_file.triggered.connect(self.signal_load_from_file)  #
        self.signal_simulate.triggered.connect(self.signal_simulate_dialog_form)  #
        self.signal_detect_peaks.triggered.connect(self.find_ecg_peaks)  # +++
        self.signal_reset_transforms.triggered.connect(self.reset_transforms)
        # transform submenu
        self.signal_transform_fft.triggered.connect(self.signal_transform_fft_func)
        self.signal_transform_dct.triggered.connect(self.signal_transform_dct_func)
        # help
        self.help_about.triggered.connect(self.help_about_msg)  #

    ###
    def _chart(self):
        self.chart = Chart(self)  # FigureCanvas - для графіків в інтерфейсі

    # для завантаження налаштувань з файлу(якщо буду модифікувати цю програму після здачі)
    def _config(self):
        self.resize(640, 480)
        self.setWindowTitle('ECG wavelet tool')

    #==========методи що з'єднані з менюбаром
    ###
    def file_save_image(self):  # зберегти зображення png
        folder = 'saved/'
        # QInputDialog
        path, ok_clicked = QInputDialog.\
            getText(self, 'QInputDialog().getText()'
                    , 'Filename', QLineEdit.Normal)

        if path and ok_clicked:
            self.chart.save_as_png(folder + path + '.png')

    ###
    def file_save_vector(self):  # зберегти вектор в txt файл
        folder = 'saved/'
        path, ok_clicked = QInputDialog()\
            .getText(self, 'QInputDialog().getText()',
                     'Filename', QLineEdit.Normal)

        if path and ok_clicked:
            self.signal_object.signal_to_txt(folder + path + '.txt')

    ###
    def signal_simulate_dialog_form(self):
        self.sim_dialog = QDialog()
        self.sim_dialog.resize(240, 180)

        self.button_sim_simulate = QPushButton('Simulate')
        self.button_sim_simulate.clicked.connect(self.simulate_helper)

        self.button_sim_cancel = QPushButton('Cancel')  #
        self.button_sim_cancel.clicked.connect(self.sim_dialog.close)

        self.input_duration = QLineEdit()
        self.input_rate = QLineEdit()
        self.input_noise = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow('Duration(s)', self.input_duration)
        form_layout.addRow('Rate(Hz)', self.input_rate)
        form_layout.addRow('Noise(mV)', self.input_noise)
        form_layout.addRow(self.button_sim_simulate, self.button_sim_cancel)

        self.sim_dialog.setLayout(form_layout)
        self.sim_dialog.exec_()

    ###
    def simulate_helper(self):  # бере дані з форми і по ним генерує вектор сигналу
        duration = int(self.input_duration.text())
        rate = int(self.input_rate.text())
        noise = float(self.input_noise.text())
        self.signal_object.simulate_ecg(duration, rate, noise)
        self.chart.redraw_plot(self.signal_object.time, self.signal_object.vector)
        self.sim_dialog.close()

    ###
    def signal_load_from_file(self):
        # filename: tuple
        filename = QFileDialog\
            .getOpenFileName(self, 'Open File', '',
                             'Text Files(*.txt);;CSV Files(*.csv)')

        if len(filename[0]) != 0:
            self.signal_object.signal_from_txt(filename[0])
            self.chart.redraw_plot(self.signal_object.time, self.signal_object.vector)

    # ???
    def find_ecg_peaks(self):
        # як скопіювати значення осей на іншу фігуру?
        self.signal_object.signal_detect_peaks()
        plt.show()

    def reset_transforms(self):
        self.chart.redraw_plot(self.signal_object.time,
                               self.signal_object.main_signal)

    #========= вейвлет методи
    def signal_transform_fft_func(self):
        self.signal_object.signal_transform_fft()
        self.chart.redraw_plot(self.signal_object.time,
                               self.signal_object.vector,
                               overlap=True)

    def signal_transform_dct_func(self):
        self.signal_object.signal_transform_dct()
        self.chart.redraw_plot(self.signal_object.time,
                               self.signal_object.vector,
                               overlap=True)


    def signal_some_wavelet_func(self):
        raise NotImplementedError
    #=========

    ###
    @staticmethod
    def help_about_msg():  # вспливає повідомлення
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("ECG wavelet transform tool")
        msg.exec_()


def run():
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    run()
