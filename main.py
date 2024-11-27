import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import re
import threading
import cv2
from PIL import Image, ImageTk


def compress_video(input_file, output_file, progress_var, codec='h263', ffmpeg_path='ffmpeg', filters=None, fps=None,
                   bitrate=None):
    available_resolutions = ['128x96', '176x144', '352x288', '704x576', '1408x1152']

    probe_command = [ffmpeg_path, '-i', input_file, '-vframes', '1', '-c:v', 'png', '-f', 'null', '-']
    probe_result = subprocess.run(probe_command, capture_output=True, text=True)
    if probe_result.returncode != 0:
        messagebox.showerror("Error", "Error getting video information.")
        return

    resolution_match = re.search(r' (\d+)x(\d+)[,\s]', probe_result.stderr)
    if resolution_match:
        input_resolution = tuple(map(int, resolution_match.groups()))
    else:
        messagebox.showerror("Error", "Video resolution information not found.")
        return

    closest_resolution = min(available_resolutions,
                             key=lambda x: abs(int(x.split('x')[0]) - input_resolution[0]) +
                                           abs(int(x.split('x')[1]) - input_resolution[1]))

    filter_string = ''
    if filters:
        filter_string = ','.join(filters)

    command = [
        ffmpeg_path,
        '-i', input_file,
        '-c:v', codec,
        '-b:v', bitrate,
        '-c:a', 'aac',
        '-b:a', '128k',
        '-s', closest_resolution,
    ]

    if filter_string:
        command.extend(['-vf', filter_string])

    if fps:
        command.extend(['-r', fps])

    command.append(output_file)

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    total_duration = None
    for line in process.stderr:
        if 'Duration' in line:
            match = re.search(r'Duration: (\d+):(\d+):(\d+)', line)
            if match:
                hours, minutes, seconds = map(int, match.groups())
                total_duration = hours * 3600 + minutes * 60 + seconds
        elif 'time=' in line and total_duration:
            match = re.search(r'time=(\d+):(\d+):(\d+)', line)
            if match:
                hours, minutes, seconds = map(int, match.groups())
                current_time = hours * 3600 + minutes * 60 + seconds
                progress = (current_time / total_duration) * 100
                progress_var.set(progress)
                root.update_idletasks()

    process.wait()
    if process.returncode == 0:
        messagebox.showinfo("Success", f"Video successfully compressed: {output_file}")
    else:
        messagebox.showerror("Error", "An error occurred during compression.")
    root.destroy()


def browse_file():
    filename = filedialog.askopenfilename(filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*")))
    if filename:
        entry_input_file.delete(0, tk.END)
        entry_input_file.insert(0, filename)
        output_file = re.sub(r'\.mp4$', '_compressed.avi', filename)
        entry_output_file.delete(0, tk.END)
        entry_output_file.insert(0, output_file)
        play_video(filename, lbl_video)


def start_compression():
    input_file = entry_input_file.get()
    output_file = entry_output_file.get()
    if not input_file or not output_file:
        messagebox.showerror("Error", "Please select input and output files.")
        return

    filters = []
    if var_grayscale.get():
        filters.append('format=gray')
    if var_contrast.get():
        contrast_value = scale_contrast.get() / 100.0
        filters.append(f'eq=contrast={contrast_value}')
    if var_brightness.get():
        brightness_value = scale_brightness.get() / 100.0 - 0.5
        filters.append(f'eq=brightness={brightness_value}')
    if var_saturation.get():
        saturation_value = scale_saturation.get() / 100.0
        filters.append(f'eq=saturation={saturation_value}')
    if var_rotate.get():
        rotate_value = rotate_angle.get()
        filters.append(f'rotate={rotate_value}*PI/180')

    progress_var.set(0)
    fps = entry_fps.get() if entry_fps.get().isdigit() else None
    bitrate = f'{entry_bitrate.get()}k' if entry_bitrate.get().isdigit() else '1000k'

    threading.Thread(target=compress_video, args=(
    input_file, output_file, progress_var, 'h263', entry_ffmpeg_path.get(), filters, fps, bitrate)).start()


def play_video(input_file, lbl_video):
    def update_frame():
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
        frame = apply_filters(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = resize_to_aspect_ratio(frame, 640, 360)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)
        lbl_video.after(10, update_frame)

    def apply_filters(frame):
        if var_grayscale.get():
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        if var_contrast.get():
            contrast_value = (scale_contrast.get() - 50) / 50.0
            frame = cv2.convertScaleAbs(frame, alpha=0-contrast_value, beta=0)
        if var_brightness.get():
            brightness_value = scale_brightness.get() - 50
            frame = cv2.convertScaleAbs(frame, alpha=1, beta=brightness_value)
        if var_saturation.get():
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv[..., 1] = hsv[..., 1] * (scale_saturation.get() / 100.0)
            frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        if var_rotate.get():
            height, width = frame.shape[:2]
            center = (width / 2, height / 2)
            angle = rotate_angle.get()
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            frame = cv2.warpAffine(frame, M, (width, height))
        return frame

    def resize_to_aspect_ratio(frame, max_width, max_height):
        h, w = frame.shape[:2]
        aspect_ratio = w / h

        if w > h:
            new_w = max_width
            new_h = int(max_width / aspect_ratio)
        else:
            new_h = max_height
            new_w = int(max_height * aspect_ratio)

        return cv2.resize(frame, (new_w, new_h))

    cap = cv2.VideoCapture(input_file)
    update_frame()


def toggle_contrast():
    if var_contrast.get():
        scale_contrast.configure(state=tk.NORMAL)
    else:
        scale_contrast.configure(state=tk.DISABLED)


def toggle_brightness():
    if var_brightness.get():
        scale_brightness.configure(state=tk.NORMAL)
    else:
        scale_brightness.configure(state=tk.DISABLED)


def toggle_saturation():
    if var_saturation.get():
        scale_saturation.configure(state=tk.NORMAL)
    else:
        scale_saturation.configure(state=tk.DISABLED)


def toggle_rotate():
    if var_rotate.get():
        rotate_angle.configure(state=tk.NORMAL)
    else:
        rotate_angle.configure(state=tk.DISABLED)


root = tk.Tk()
root.title("Video Compressor with Filters")

video_frame = tk.Frame(root, width=640, height=360)
video_frame.grid(row=0, column=1, padx=5, pady=5)
video_frame.grid_propagate(False)

lbl_video = tk.Label(video_frame)
lbl_video.pack(fill=tk.BOTH, expand=True)

filter_frame = tk.Frame(root)
filter_frame.grid(row=0, column=0, padx=5, pady=5)

tk.Label(root, text="FFmpeg Path:").grid(row=1, column=0, sticky=tk.W)
entry_ffmpeg_path = tk.Entry(root, width=50)
entry_ffmpeg_path.grid(row=1, column=1, padx=5, pady=5)
entry_ffmpeg_path.insert(0, "C:/Users/Petar/Downloads/ffmpeg-7.0-full_build/bin/ffmpeg.exe")

tk.Label(root, text="Input File:").grid(row=2, column=0, sticky=tk.W)
entry_input_file = tk.Entry(root, width=50)
entry_input_file.grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_file).grid(row=2, column=2, padx=5, pady=5)

tk.Label(root, text="Output File:").grid(row=3, column=0, sticky=tk.W)
entry_output_file = tk.Entry(root, width=50)
entry_output_file.grid(row=3, column=1, padx=5, pady=5)

var_grayscale = tk.BooleanVar()
tk.Checkbutton(filter_frame, text="Grayscale", variable=var_grayscale).grid(row=0, column=0, sticky=tk.W)

var_contrast = tk.BooleanVar()
chk_contrast = tk.Checkbutton(filter_frame, text="Contrast", variable=var_contrast, command=toggle_contrast)
chk_contrast.grid(row=1, column=0, sticky=tk.W)

tk.Label(filter_frame, text="Contrast Level:").grid(row=1, column=1, sticky=tk.W)
scale_contrast = tk.Scale(filter_frame, from_=0, to=50, orient=tk.HORIZONTAL, state=tk.DISABLED)
scale_contrast.set(50)
scale_contrast.grid(row=1, column=2, padx=5, pady=5)

var_brightness = tk.BooleanVar()
chk_brightness = tk.Checkbutton(filter_frame, text="Brightness", variable=var_brightness, command=toggle_brightness)
chk_brightness.grid(row=2, column=0, sticky=tk.W)

tk.Label(filter_frame, text="Brightness Level:").grid(row=2, column=1, sticky=tk.W)
scale_brightness = tk.Scale(filter_frame, from_=50, to=100, orient=tk.HORIZONTAL, state=tk.DISABLED)
scale_brightness.set(50)
scale_brightness.grid(row=2, column=2, padx=5, pady=5)

var_saturation = tk.BooleanVar()
chk_saturation = tk.Checkbutton(filter_frame, text="Saturation", variable=var_saturation, command=toggle_saturation)
chk_saturation.grid(row=3, column=0, sticky=tk.W)

tk.Label(filter_frame, text="Saturation Level:").grid(row=3, column=1, sticky=tk.W)
scale_saturation = tk.Scale(filter_frame, from_=0, to=100, orient=tk.HORIZONTAL, state=tk.DISABLED)
scale_saturation.set(100)
scale_saturation.grid(row=3, column=2, padx=5, pady=5)

var_rotate = tk.BooleanVar()
chk_rotate = tk.Checkbutton(filter_frame, text="Rotate", variable=var_rotate, command=toggle_rotate)
chk_rotate.grid(row=4, column=0, sticky=tk.W)

tk.Label(filter_frame, text="Rotate Angle:").grid(row=4, column=1, sticky=tk.W)
rotate_angle = tk.Scale(filter_frame, from_=0, to=360, orient=tk.HORIZONTAL, state=tk.DISABLED)
rotate_angle.set(0)
rotate_angle.grid(row=4, column=2, padx=5, pady=5)

tk.Label(root, text="FPS:").grid(row=5, column=0, sticky=tk.W)
entry_fps = tk.Entry(root, width=10)
entry_fps.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

tk.Label(root, text="Bitrate (kbps):").grid(row=6, column=0, sticky=tk.W)
entry_bitrate = tk.Entry(root, width=10)
entry_bitrate.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)

tk.Button(root, text="Start Compression", command=start_compression).grid(row=7, column=0, columnspan=3, pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.grid(row=8, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)

root.mainloop()
