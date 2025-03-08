import os
import cv2
import threading
from tkinter import Label, Button, StringVar, Toplevel, Tk, SUNKEN
from datetime import datetime

FONT = ('Helvetica', '16')

class DataInputWindow:
    def __init__(self, root, vidname, font):
        self.root = root
        self.font = FONT
        self.root.title("Input data for recording")
        self.root.attributes('-fullscreen', True)
        self.root.option_add("*Font", self.font)
        self.fname = vidname

        # Buttons to open number selection windows
        self.shot_type  = StringVar(value="")
        self.carry = StringVar(value="")
        self.total = StringVar(value="")

        Button(root, text="Select Shot Shape", command=lambda: self.open_shot_window(self.shot_type)).grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        Button(root, text="Enter number for Carry (Yds)", command=lambda: self.open_number_window(self.carry)).grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        Button(root, text="Enter number for Total (Yds)", command=lambda: self.open_number_window(self.total)).grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        # Label to show the combined number
        self.shot_label = Label(root, text="Selected Shot: ")
        self.shot_label.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        self.result_label = Label(root, text="Selected Number: ")
        self.result_label.grid(row=4, column=0, sticky="nsew", padx=5, pady=5)

        # Confirm button
        Button(root, text="Confirm", command=self.success_close).grid(row=5, column=0, sticky="nsew", padx=5, pady=5)
        Button(root, text="Cancel", command=self.cancel_close).grid(row=6, column=0, sticky="nsew", padx=5, pady=5)

        for i in range(7):
            self.root.grid_rowconfigure(i, weight=1)
        for j in range(1):
            self.root.grid_columnconfigure(j, weight=1)
            
    def open_shot_window(self, shot_var):
        shot_window = Toplevel(self.root)
        shot_window.title("Select Shot Shape")
        shot_window.attributes('-fullscreen', True)
        shot_window.option_add("*Font", self.font)

        shot_types = (
            'Pull Hook', 'Hook', 'Pull',
            'Fade', 'Straight', 'Draw',
            'Push', 'Slice', 'Push Slice'
        )
        
        label = Label(shot_window, text="")
        label.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        
        def update_shotvar(shot):
            label.config(text=shot)
        
        def confirm_selection():
            shot_var.set(label["text"])
            shot_window.destroy()
            self.update_shot_label()

        # Shot buttons - 3x3 grid
        for i, shot in enumerate(shot_types):
            Button(
                shot_window, text=shot, 
                command=lambda shot=shot: update_shotvar(shot)
            ).grid(
                row=i // 3 + 1, column=i % 3, sticky="nsew",
                padx=5, pady=5
            )
            

        # Confirm selection button
        Button(shot_window, text="Confirm", command=confirm_selection).grid(row=4, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        for i in range(5):
            shot_window.grid_rowconfigure(i, weight=1)
        for j in range(3):
            shot_window.grid_columnconfigure(j, weight=1)

    def open_number_window(self, num_var):
        """Opens a new window for selecting up to 3 digits."""
        num_window = Toplevel(self.root)
        num_window.title("Select Numbers")
        num_window.attributes('-fullscreen', True)
        num_window.option_add("*Font", self.font)

        selected_digits = []

        def add_digit(digit):
            """Add digit to the list (up to 3 digits)."""
            if len(selected_digits) < 3:
                selected_digits.append(str(digit))
                label.config(text="".join(selected_digits))

        def confirm_selection():
            """Store the selected number as a string and close the window."""
            num_var.set("".join(selected_digits))
            num_window.destroy()
            self.update_metrics()

        label = Label(num_window, text="")
        label.grid(row=0, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)

        # Number buttons
        for i in range(10):  # 0-9 buttons
            Button(num_window, text=str(i), command=lambda i=i: add_digit(i)).grid(row=i//5 + 2, column=i%5, sticky="nsew", padx=5, pady=5)

        # Confirm selection button
        Button(num_window, text="Confirm", command=confirm_selection).grid(row=4, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)

        for i in range(5):
            num_window.grid_rowconfigure(i, weight=1)
        for j in range(5):
            num_window.grid_columnconfigure(j, weight=1)

    def success_close(self):
        """Combine the selected numbers and display the result."""
        data = [self.fname, self.shot_type.get(), self.carry.get(), self.total.get(), '\n']
        newline = ','.join(data)
        with open('data.csv', 'a') as f:
            f.write(newline)
        self.root.destroy()

    def cancel_close(self):
        self.root.destroy()

    def update_metrics(self):
        """Update the displayed number when selections change."""
        self.result_label.config(text=f"Carry and Total (Yds): {self.carry.get()}, {self.total.get()}")
        
    def update_shot_label(self):
        self.shot_label.config(text=f"Shot Shape: {self.shot_type.get()}")

class FullscreenButtonApp:
    def __init__(self, root):
        self.root = root
        self.font = FONT
        self.root.title("Fullscreen Button Grid")
        self.root.attributes('-fullscreen', True)  # Open in fullscreen mode
        self.root.bind("q", self.exit_fullscreen)  # Exit fullscreen on 'q' key
        self.root.option_add("*Font", self.font)

        self.button_configs = (
            (1280, 800, 120), (1280, 720, 120), (1024, 768, 120), (800, 600, 120),
            (640, 480, 210), (640, 400, 210), (320, 240, 420), (160, 120, 640)
        )
        self.button_texts = [f'{w}x{h}, {fps} FPS' for w, h, fps in self.button_configs]
        self.vidname = ''
        self.recording = False
        self.out = None
        self.cap = None
        self.recording_thread = None  # Thread for recording
        self.stop_event = threading.Event()  # Event to signal when to stop
        self.create_widgets()

        if not os.path.exists('recordings'):
            os.mkdir('recordings')
        os.chdir('recordings')
        if not os.path.exists('data.csv'):
            headers = ','.join(['filename', 'shot type', 'carry', 'total'])
            with open('data.csv', 'w') as f:
                f.write(headers + '\n')


    def create_widgets(self):
        self.status_var = StringVar()
        self.status_var.set("Ready")
        status_label = Label(
            self.root, textvariable=self.status_var, relief=SUNKEN,
            padx=5, pady=5)
        status_label.grid(row=0, column=0, columnspan=2, sticky="nsew")

        for i in range(4):  # Creating 4 rows with 2 buttons each
            for j in range(2):
                index = i * 2 + j
                label = self.button_texts[index]
                btn = Button(self.root, text=label,
                    command=lambda idx=index: self.start_recording(idx))
                btn.grid(row=i+1, column=j, sticky="nsew", padx=5, pady=5)

        # Stop Recording Button
        stop_button = Button(self.root, text="Stop Recording",
            command=self.stop_recording, bg='red')
        stop_button.grid(row=5, column=0, sticky="nsew", padx=5, pady=5)

        # Full-width Exit Button
        exit_button = Button(self.root, text="Exit",
            command=self.close_app)
        exit_button.grid(row=5, column=1, sticky="nsew", padx=5, pady=5)

        # Configure row and column weights
        for i in range(6):
            self.root.grid_rowconfigure(i, weight=1)
        for j in range(2):
            self.root.grid_columnconfigure(j, weight=1)

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

    def start_recording(self, index):
        if self.recording:
            return  # Ignore if already recording

        w, h, fps = self.button_configs[index]
        label = self.button_texts[index]
        self.update_status(f"Starting recording: {label}")
        # working with AVI, now works with mp4
        gst_pipeline = (
            f"v4l2src ! image/jpeg, width={w}, height={h}, framerate={fps}/1 "
            "! jpegdec ! videoconvert ! video/x-raw, format=BGR "
            "! appsink drop=true"
        )
        self.cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

        if not self.cap.isOpened():
            self.update_status("Failed to open video source")
            return

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        now = datetime.now()
        dt_time = now.strftime("%Y%m%d-%H%M")
        self.vidname = f'{dt_time}_{w}x{h}_{fps}FPS.mp4'
        self.out = cv2.VideoWriter(self.vidname, fourcc, fps, (w, h))
        self.recording = True
        self.stop_event.clear()  # Reset stop event

        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self.record_video)
        self.recording_thread.start()

    def record_video(self):
        while self.recording and not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)
            else:
                break  # Stop if the camera feed is lost
        self.stop_recording()  # Ensure cleanup when stopping

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.stop_event.set()  # Signal the thread to stop
            if self.recording_thread:
                self.recording_thread.join()  # Wait for the thread to finish
            if self.cap:
                self.cap.release()
            if self.out:
                self.out.release()
            self.update_status("Recording stopped")
            self.open_stop_recording_window()

    def open_stop_recording_window(self):
        if self.vidname:
            stop_window = Toplevel()
            self.data_window = DataInputWindow(stop_window, self.vidname, self.font)
        else:
            self.update_status("No recent video file to record data for")

    def exit_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', False)

    def close_app(self):
        self.stop_recording()
        self.root.quit()

if __name__ == "__main__":
    root = Tk()
    app = FullscreenButtonApp(root)
    root.mainloop()
