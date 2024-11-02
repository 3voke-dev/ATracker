import psutil
import time
from collections import defaultdict
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread


class AppTimeTracker:
    def __init__(self):
        self.app_times = defaultdict(int)  # Словарь для хранения времени работы приложений
        self.last_check_time = time.time()  # Время последней проверки
        self.is_running = True  # Флаг для отслеживания работы трекера
        self.initial_processes = set()  # Множество для хранения начальных процессов

    def track_apps(self):
        # Сохраняем начальные процессы
        self.initial_processes = {proc.name() for proc in psutil.process_iter(['name'])}

        while self.is_running:
            current_time = time.time()
            active_apps = {proc.name(): proc.pid for proc in psutil.process_iter(['name'])}

            # Проверяем только новые приложения, запущенные после старта скрипта
            new_apps = set(active_apps.keys()) - self.initial_processes

            # Обновляем время для новых приложений
            for app in new_apps:
                self.app_times[app] += current_time - self.last_check_time

            self.last_check_time = current_time
            time.sleep(1)  # Задержка в 1 секунду

    def stop_tracking(self):
        self.is_running = False

    def get_report(self):
        report_lines = ["Отчет о времени работы приложений:"]
        for app, time_spent in self.app_times.items():
            hours, remainder = divmod(time_spent, 3600)
            minutes, seconds = divmod(remainder, 60)
            report_lines.append(f"{app}: {int(hours)} ч {int(minutes)} мин {int(seconds)} сек")
        return "\n".join(report_lines)


class AppGUI:
    def __init__(self, tracker):
        self.tracker = tracker

        # Создание основного окна
        self.window = tk.Tk()
        self.window.title("ATracker")

        # Создание текстового поля для отчета
        self.report_area = scrolledtext.ScrolledText(self.window, width=50, height=20)
        self.report_area.pack(pady=10)

        # Создание кнопки для отображения отчета
        self.report_button = tk.Button(self.window, text="Показать отчет", command=self.show_report)
        self.report_button.pack(pady=5)

        # Запуск трекера в отдельном потоке
        self.tracker_thread = Thread(target=self.tracker.track_apps)
        self.tracker_thread.start()

        # Обновление отчета каждую минуту
        self.update_report()

    def show_report(self):
        """Показать отчет о времени работы приложений в текстовом поле."""
        report = self.tracker.get_report()
        self.report_area.delete(1.0, tk.END)  # Очистить текстовое поле
        self.report_area.insert(tk.END, report)  # Вставить новый отчет

    def update_report(self):
        """Обновить отчет каждую минуту."""
        report = self.tracker.get_report()
        self.report_area.delete(1.0, tk.END)  # Очистить текстовое поле
        self.report_area.insert(tk.END, report)  # Вставить новый отчет
        self.window.after(60000, self.update_report)  # Обновлять каждые 60000 мс (1 минута)

    def run(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def on_closing(self):
        self.tracker.stop_tracking()
        self.window.destroy()


if __name__ == "__main__":
    tracker = AppTimeTracker()
    gui = AppGUI(tracker)
    gui.run()
