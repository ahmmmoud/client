import tkinter as tk
from tkinter import font as tkfont, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import os

import try_on

Path_Images_Folder = './my_wardrobe'

class CameraApp:
    received_image = False
    frame_counter = 0
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
            "Mirror Try On": self.show_try_on,
            "My Wardrobe": self.show_image_list,
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
        if not self.received_image:
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
                img.save("./my_model/captured_image.jpg", "JPEG")
        else:
            self.frame_counter += 1
            if self.frame_counter > 100:
                self.received_image = False
                self.frame_counter = 0
            # Show a static image
            static_image_path = "./try_on/response.jpg"
            if os.path.exists(static_image_path):
                img = Image.open(static_image_path)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.canvas.imgtk = imgtk
            else:
                print(f"Static image not found at {static_image_path}")

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

    def show_try_on(self):
        res = try_on.invoke_image()
        self.received_image = True


    def show_image_list(self):
        # Create a new window for the image list
        image_window = tk.Toplevel(self.root)
        image_window.title("My Wardrobe")
        image_window.geometry("800x600")  # Size of the image window

        # Create a frame for scrolling images
        frame = tk.Frame(image_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas and scrollbar for image scrolling
        canvas = tk.Canvas(frame, bg='black')
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create an image container frame inside the canvas
        image_container = tk.Frame(canvas, bg='black')
        canvas.create_window((0, 0), window=image_container, anchor="nw")

        # Load images from folder
        image_folder = 'my_wardrobe'  # Change this to the path of your image folder
        images = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

        # Define image size and padding
        image_size = (150, 150)
        padding = 10
        columns = 5  # Number of images per row

        x = padding
        y = padding

        for idx, image_file in enumerate(images):
            image_path = os.path.join(image_folder, image_file)
            img = Image.open(image_path).resize(image_size)  # Resize images as needed
            img_tk = ImageTk.PhotoImage(img)

            # Create a clickable label for each image
            label = tk.Label(image_container, image=img_tk, bg='black')
            label.image = img_tk  # Keep a reference to avoid garbage collection
            label.grid(row=idx // columns, column=idx % columns, padx=padding, pady=padding)

            # Bind the label click event
            label.bind("<Button-1>", lambda e, path=image_path: self.show_image_popup(path))

        # Update scroll region
        image_container.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def show_image_popup(self, image_path):
        # Create a popup window with actions
        popup = tk.Toplevel(self.root)
        popup.title("Image Actions")
        popup.geometry("300x200")

        # Load the selected image
        img = Image.open(image_path)
        img_tk = ImageTk.PhotoImage(img.resize((150, 150)))  # Resize for display

        # Display the selected image in the popup
        img_label = tk.Label(popup, image=img_tk)
        img_label.image = img_tk  # Keep a reference to avoid garbage collection
        img_label.pack()

        # Add action buttons
        actions_frame = tk.Frame(popup)
        actions_frame.pack(pady=10)

        tk.Button(actions_frame, text="Action 1", command=lambda: self.perform_action("Action 1", image_path)).pack(
            pady=5)
        tk.Button(actions_frame, text="Action 2", command=lambda: self.perform_action("Action 2", image_path)).pack(
            pady=5)
        tk.Button(actions_frame, text="Action 3", command=lambda: self.perform_action("Action 3", image_path)).pack(
            pady=5)

    def perform_action(self, action, image_path):
        # Example action handler
        messagebox.showinfo("Action Performed", f"You selected {action} for {os.path.basename(image_path)}")

    def __del__(self):
        self.vid.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()