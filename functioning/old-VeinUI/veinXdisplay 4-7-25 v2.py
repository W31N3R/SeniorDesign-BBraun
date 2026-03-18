import tkinter as tk
from tkinter import Label, Button, IntVar, StringVar, Scale, OptionMenu
import cv2
from PIL import Image, ImageTk

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
root.geometry("1280x800")
root.attributes('-fullscreen', True)

# Video Display
video_label = Label(root)
video_label.pack(fill="both", expand=True)  # Make the video label fill the entire window

# Overlay Controls
control_frame = tk.Frame(root, bg="black", highlightbackground="white", highlightthickness=1)
control_frame.place(relx=0.8, rely=0.1, relwidth=0.18, relheight=0.8)  # Position controls on the right side

# Create individual frames for each control to ensure even spacing
def create_control_section(parent, label_text, widget):
    frame = tk.Frame(parent, bg="black")
    frame.pack(fill="x", pady=10)  # Add padding for even spacing
    label = Label(frame, text=label_text, font=("Arial", 12), bg="black", fg="white")
    label.pack()
    widget.pack()
    return frame

# Dropdown Menu for Control 1
control_var_1 = StringVar(value="1 inch")
control_1_widget = OptionMenu(control_frame, control_var_1, "1 inch", "1.5 inches", "2 inches", command=control_action_1)
create_control_section(control_frame, "Length", control_1_widget)

# Toggle Button for Control 2
control_var_2 = IntVar(value=0)  # Default state is Off
control_2_button = Button(control_frame, text="Depth: Off", bg="firebrick2", command=toggle_control_2)
create_control_section(control_frame, "Show Depth", control_2_button)

# Scale for Control 3 (Contrast)
control_var_3 = IntVar(value=50)  # Default value is 50
contrast_scale = Scale(control_frame, from_=0, to=100, resolution=5, orient="horizontal", variable=control_var_3, command=control_action_3)
create_control_section(control_frame, "Contrast", contrast_scale)

# Toggle Button for Control 4
control_var_4 = IntVar(value=0)  # Default state is Off
control_4_button = Button(control_frame, text="Needle: Off", bg="firebrick2", command=toggle_control_4)
create_control_section(control_frame, "Show Needle", control_4_button)

# Start Video Stream
cap = cv2.VideoCapture(0)

def update_video_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (1280, 800))  # Resize the frame to match the screen resolution
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.config(image=imgtk)
        video_label.image = imgtk
    video_label.after(10, update_video_frame)

update_video_frame()

# Run the Application
root.mainloop()
cap.release()
cv2.destroyAllWindows()

#edits
#4/1/25
# Jacob  - changed resolution to 1280x800 and started to increase the button size
# Tested the touchscreen with the Beetronics BEE7TS7M/U1 screen and it worked as a touchscreen and as a video streaming!
# Jacob  - change window to be borderless and fullscreen so users can't click out of the window
# Blaine - Button did not visibly toggle, but the output did on very first click
# Gunner - is it possible to have the video take up the whole area, and the controls on top of the video?
# Riley  - changed to a drop down menu to show all buttons, and hide all of them
# Jacob  - two-click principle? unsure
#completed - borderless, fullscreen window, fullscreen camera