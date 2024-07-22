import tkinter as tk
from tkinter import font as tkfont
import cv2
from PIL import Image, ImageTk
import numpy as np


class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera Background UI")

        # Set the window to full screen
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", self.toggle_fullscreen)  # Bind Escape key to toggle full screen

        # Define canvas dimensions based on full screen size
        self.canvas_width = root.winfo_screenwidth()
        self.canvas_height = root.winfo_screenheight()

        # Create a canvas to display the video feed
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Set the background color of the root window
        self.root.configure(bg='black')

        self.video_source = 0  # Use the default camera
        self.vid = cv2.VideoCapture(self.video_source)

        # Set camera resolution to the highest possible
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # Define font for buttons
        self.button_font = tkfont.Font(family="Arial", size=16, weight="bold")

        # Define button properties
        self.button_width = 300
        self.button_height = 50
        self.spacing = 20  # Spacing between buttons

        # Add buttons with improved design
        self.buttons = {
            "Mirror Try On": self.button_action,
            "My Wardrobe": self.button_action,
            "Fashionista": self.button_action,
            "Shop": self.button_action,
            "Imagine": self.button_action,
            "Friends": self.button_action
        }

        self.create_buttons()
        self.update_button_positions()

        # Start the video update loop
        self.update_video()

    def toggle_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
        return "break"

    def create_buttons(self):
        self.button_widgets = {}
        for text, command in self.buttons.items():
            button = tk.Button(
                self.root,
                text=text,
                font=self.button_font,
                bg="#4CAF50",  # Green background color
                fg="white",  # White text color
                width=self.button_width // 10,  # Width based on characters
                relief=tk.RAISED,
                borderwidth=2,
                command=command
            )
            self.button_widgets[text] = button

    def update_video(self):
        ret, frame = self.vid.read()
        if ret:
            # Convert frame to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Crop and resize frame to maintain aspect ratio
            frame = self.crop_and_resize_frame(frame)

            # Convert the frame to a PhotoImage
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            # Update the canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.imgtk = imgtk

        self.root.after(10, self.update_video)

    def crop_and_resize_frame(self, frame):
        target_width = 768
        target_height = 1024

        # Get frame dimensions
        frame_height, frame_width, _ = frame.shape

        # Calculate aspect ratios
        frame_aspect = frame_width / frame_height
        target_aspect = target_width / target_height

        # Create a black background frame
        black_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)

        if frame_aspect > target_aspect:
            # Frame is wider than target, crop the width
            new_width = int(frame_height * target_aspect)
            x_start = (frame_width - new_width) // 2
            cropped_frame = frame[:, x_start:x_start + new_width]
            # Resize cropped frame to target dimensions
            resized_frame = cv2.resize(cropped_frame, (target_width, target_height))
            # Place resized frame onto black background
            black_frame = resized_frame
        else:
            # Frame is taller than target, crop the height
            new_height = int(frame_width / target_aspect)
            y_start = (frame_height - new_height) // 2
            cropped_frame = frame[y_start:y_start + new_height, :]
            # Resize cropped frame to target dimensions
            resized_frame = cv2.resize(cropped_frame, (target_width, target_height))
            # Place resized frame onto black background
            black_frame = resized_frame

        return black_frame

    def update_button_positions(self):
        # Calculate total height of buttons and spacing
        total_buttons_height = len(self.buttons) * self.button_height + (len(self.buttons) - 1) * self.spacing

        # Center buttons vertically and horizontally
        start_x = (self.canvas_width - self.button_width) // 2
        start_y = (self.canvas_height - total_buttons_height) // 2

        for idx, (text, button) in enumerate(self.button_widgets.items()):
            button.place(
                x=start_x,
                y=start_y + idx * (self.button_height + self.spacing)
            )

    def button_action(self):
        print("Button clicked")

    def __del__(self):
        self.vid.release()


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
