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
        control_var_2.set(0)  # Turn off
    else:
        control_var_2.set(1)  # Turn on
    print(f"Control 2 {'On' if control_var_2.get() else 'Off'}")

def control_action_3(value):
    print(f"Contrast set to: {value}")

# Toggle Button for Control 4
def toggle_control_4():
    state = control_var_4.get()
    if state:
        control_var_4.set(0)  # Turn off
    else:
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

# Create a Menu Bar
menu_bar = tk.Menu(root)

# Control 1 Menu
control_1_menu = tk.Menu(menu_bar, tearoff=0)
control_1_menu.add_command(label="1 inch", command=lambda: control_action_1("1 inch"))
control_1_menu.add_command(label="1.5 inches", command=lambda: control_action_1("1.5 inches"))
control_1_menu.add_command(label="2 inches", command=lambda: control_action_1("2 inches"))
menu_bar.add_cascade(label="Length", menu=control_1_menu)

# Control 2 Menu
control_2_menu = tk.Menu(menu_bar, tearoff=0)
control_2_menu.add_command(label="Toggle Depth", command=toggle_control_2)
menu_bar.add_cascade(label="Show Depth", menu=control_2_menu)

# Control 3 Menu
control_3_menu = tk.Menu(menu_bar, tearoff=0)
for value in range(0, 101, 5):  # Add options for contrast in increments of 5
    control_3_menu.add_command(label=f"Set Contrast to {value}", command=lambda v=value: control_action_3(v))
menu_bar.add_cascade(label="Contrast", menu=control_3_menu)

# Control 4 Menu
control_4_menu = tk.Menu(menu_bar, tearoff=0)
control_4_menu.add_command(label="Toggle Needle", command=toggle_control_4)
menu_bar.add_cascade(label="Show Needle", menu=control_4_menu)

# Add the Menu Bar to the Window
root.config(menu=menu_bar)

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
#completed - borderless, fullscreen window, fullscreen camera, and buttons hidden