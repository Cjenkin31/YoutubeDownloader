import time
import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
from tkinter.ttk import Progressbar, Frame, Label, Entry, Button, Style, Checkbutton
from pytube import YouTube
import threading

class YouTubeDownloader:
    def __init__(self):
        self.setup_window()

    def setup_window(self):
        self.window = tk.Tk()
        self.window.title("YouTube Video Downloader")
        self.window.geometry('600x500')

        self.style = Style(self.window)
        self.configure_styles()

        self.setup_path_frame()
        self.setup_url_frame()
        self.setup_download_button()
        self.setup_progress_bar()
        self.setup_status_labels()
        self.setup_mp3_option()

        self.window.mainloop()

    def configure_styles(self):
        modern_font = ('Arial', 10)
        self.style.configure('TButton', font=modern_font, padding=5)
        self.style.configure('TLabel', font=modern_font, padding=5)
        self.style.configure('TProgressbar', thickness=20)

    def setup_path_frame(self):
        self.path_frame = Frame(self.window, padding="3 3 12 12")
        self.path_frame.pack(fill='x', expand=True)

        Label(self.path_frame, text="Download Path:").pack(side='left', padx=(0, 10))

        self.path_entry = Entry(self.path_frame, textvariable=tk.StringVar(), width=50)
        self.path_entry.pack(side='left', expand=True, fill='x')

        path_button = Button(self.path_frame, text="Browse", command=self.select_path)
        path_button.pack(side='left', padx=(5, 0))

    def setup_url_frame(self):
        url_frame = Frame(self.window, padding="3 3 12 12")
        url_frame.pack(fill='x', expand=True)

        Label(url_frame, text="Enter YouTube URLs (one per line):").pack(side='top', fill='x')

        self.url_input = tk.Text(url_frame, height=6, width=50)
        self.url_input.pack(fill='x', expand=True)

    def setup_download_button(self):
        download_button = Button(self.window, text="Download", command=self.start_download)
        download_button.pack(pady=10)

    def setup_progress_bar(self):
        self.progress = Progressbar(self.window, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill='x', expand=True, pady=10)

    def setup_status_labels(self):
        self.current_video_label = Label(self.window, text="Currently Downloading: None")
        self.current_video_label.pack()

        self.eta_label = Label(self.window, text="ETA: --")
        self.eta_label.pack()

        self.speed_label = Label(self.window, text="Speed: --")
        self.speed_label.pack()

    def setup_mp3_option(self):
        self.mp3_var = tk.BooleanVar()
        mp3_checkbutton = Checkbutton(self.window, text="Download as MP3 (audio only)", variable=self.mp3_var)
        mp3_checkbutton.pack()

    def select_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def start_download(self):
        input_text = self.url_input.get("1.0", "end-1c").strip()
        urls = [url for url in input_text.split("\n") if url.strip()]
        download_path = self.path_entry.get()
        download_as_mp3 = self.mp3_var.get()

        if not download_path:
            messagebox.showwarning("Warning", "Please select a download path before downloading.")
            return

        if not urls:
            messagebox.showwarning("Warning", "Please provide YouTube URLs.")
            return

        download_thread = threading.Thread(target=self.download_videos, args=(urls, download_path, download_as_mp3))
        download_thread.start()

    def download_videos(self, url_list, save_path, download_as_mp3):
        total_videos = len(url_list)
        for index, url in enumerate(url_list, start=1):
            try:
                yt = YouTube(url)
                yt.register_on_progress_callback(self.show_progress_bar)
                if download_as_mp3:
                    stream = yt.streams.filter(only_audio=True).first()
                else:
                    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

                if stream:
                    self.current_video_label.config(text=f"Currently Downloading [{index}/{total_videos}]: \"{yt.title}\"")
                    stream.download(save_path)
                else:
                    print(f"No suitable stream found for video: {yt.title}")

            except Exception as e:
                error_message = f"Error downloading \"{yt.title}\": {e}"
                print(error_message)
                self.current_video_label.config(text=error_message)

        # After all downloads are attempted, update the label
        self.current_video_label.config(text=f"All downloads finished [{total_videos}/{total_videos}].")

    def show_progress_bar(self, stream, chunk, bytes_remaining):
        download_speed, eta_str = self.calculate_download_stats(stream, bytes_remaining)

        self.progress['value'] = 100 - (bytes_remaining / stream.filesize * 100)
        self.eta_label.config(text=f"ETA: {eta_str}")
        self.speed_label.config(text=f"Speed: {download_speed}")
        self.window.update_idletasks()

    def calculate_download_stats(self, stream, bytes_remaining):
        current_time = time.time()
        if not hasattr(self, 'last_time'):
            self.last_time = current_time
            self.last_bytes = bytes_remaining

        elapsed_time = current_time - self.last_time
        download_speed = (self.last_bytes - bytes_remaining) / elapsed_time if elapsed_time > 0 else 0
        download_speed_str = f"{download_speed / 1024:.2f} KB/s"
        if download_speed / 1024 > 1024:
            download_speed_str = f"{download_speed / 1024 / 1024:.2f} MB/s"

        estimated_time = bytes_remaining / download_speed if download_speed > 0 else 0
        eta_str = f"{int(estimated_time // 60)} min {int(estimated_time % 60)} sec remaining"

        self.last_time, self.last_bytes = current_time, bytes_remaining
        return download_speed_str, eta_str

if __name__ == "__main__":
    YouTubeDownloader()
