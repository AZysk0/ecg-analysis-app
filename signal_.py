import numpy as np
import neurokit2 as nk
import pywt


class Signal:

    def __init__(self):
        self.vector = None
        self.time = None
        self.peaks = None

    def simulate_ecg(self, duration: int, rate: int, noise: float):
        self.time = np.arange(0, duration, 1 / rate)
        self.vector = nk.ecg_simulate(duration=duration,
                                      sampling_rate=rate,
                                      noise=noise)

    def signal_to_txt(self, path: str):
        stacked = np.vstack((self.time, self.vector))
        print(stacked.shape, type(stacked))
        np.savetxt(path, stacked)

    def signal_from_txt(self, path: str):
        temp = np.loadtxt(path)
        self.time = temp[0, :]
        self.vector = temp[1, :]

    def signal_detect_peaks(self):  # детекція інтервалів ЕКГ
        rate = int(1 / (self.time[1] - self.time[0]))
        _, rpeaks = nk.ecg_peaks(self.vector, sampling_rate=rate)
        _, waves_peak = nk.ecg_delineate(self.vector, rpeaks
                                         , sampling_rate=rate, method="peak")
        plot = nk.events_plot([waves_peak['ECG_T_Peaks'],
                               waves_peak['ECG_P_Peaks'],
                               waves_peak['ECG_Q_Peaks'],
                               waves_peak['ECG_S_Peaks']], self.vector)

    # якісь вейвлет функції додати
    def signal_transform_fft(self):  # перетворення Фур'є
        raise NotImplementedError

    def signal_transform_dct(self):  # дискретне косинусне перетворення
        raise NotImplementedError
