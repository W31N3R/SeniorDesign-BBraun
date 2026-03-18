import tkinter as tk
from tkinter import Label, Button, IntVar, StringVar, Scale, OptionMenu
import cv2
from PIL import Image, ImageTk

# Video Stream Setup
def update_video_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.config(image=imgtk)
        video_label.image = imgtk
    video_label.after(10, update_video_frame)

# Control Functions
def control_action_1(value):
    print(f"Control 1 selected: {value}")

# Toggle Button for Control 2
def toggle_control_2():
    state = control_var_2.get()
    if state:
        control_2_button.config(text="Depth: On", bg="limegreen")
        control_var_2.set(0)  # Turn off
    else:
        control_2_button.config(text="Depth: Off", bg="firebrick2")
        control_var_2.set(1)  # Turn on
    print(f"Control 2 {'On' if control_var_2.get() else 'Off'}")

def control_action_3(value):
    print(f"Contrast set to: {value}")

# Toggle Button for Control 4
def toggle_control_4():
    state = control_var_4.get()
    if state:
        control_4_button.config(text="Needle: On", bg="limegreen")
        control_var_4.set(0)  # Turn off
    else:
        control_4_button.config(text="Needle: Off", bg="firebrick2")
        control_var_4.set(1)  # Turn on
    print(f"Control 4 {'On' if control_var_4.get() else 'Off'}")

# Main Application Window
root = tk.Tk()
root.title("Vein Viewer UI")
root.geometry("800x480")

# Static Text Bar (Left Aligned)
header_label = Label(root, text="  B-Braun: Vein X", font=("Arial", 16), anchor="w")
header_label.pack(side="top", fill="x")

# Video Display
video_label = Label(root)
video_label.pack(side="left", expand=True)

# Control Buttons
control_frame = tk.Frame(root)
control_frame.pack(side="right", fill="y", expand=True)

# Create individual frames for each control to ensure even spacing
def create_control_section(parent, label_text, widget, row):
    label = Label(parent, text=label_text, font=("Arial", 12))
    label.grid(row=row * 2, column=0, pady=(20, 5), sticky="n")  # Add space before the label
    widget.grid(row=row * 2 + 1, column=0, pady=(0, 20), sticky="n")  # Add space after the widget

# Dropdown Menu for Control 1
control_var_1 = StringVar(value="1 inch")
control_1_widget = OptionMenu(control_frame, control_var_1, "1 inch", "1.5 inches", "2 inches", command=control_action_1)
create_control_section(control_frame, "Length", control_1_widget, row=0)

# Toggle Button for Control 2
control_var_2 = IntVar(value=0)  # Default state is Off
control_2_button = Button(control_frame, text="Depth: Off", bg="firebrick2", command=toggle_control_2)
create_control_section(control_frame, "Show Depth", control_2_button, row=1)

# Scale for Control 3 (Contrast)
control_var_3 = IntVar(value=50)  # Default value is 50
contrast_scale = Scale(control_frame, from_=0, to=100, resolution=5, orient="horizontal", variable=control_var_3, command=control_action_3)
create_control_section(control_frame, "Contrast", contrast_scale, row=2)

# Toggle Button for Control 4
control_var_4 = IntVar(value=0)  # Default state is Off
control_4_button = Button(control_frame, text="Needle: Off", bg="firebrick2", command=toggle_control_4)
create_control_section(control_frame, "Show Needle", control_4_button, row=3)

# Start Video Stream
cap = cv2.VideoCapture(0)
update_video_frame()

# Run the Application
root.mainloop()
cap.release()
cv2.destroyAllWindows()
