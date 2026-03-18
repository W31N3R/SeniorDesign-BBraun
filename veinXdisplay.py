import tkinter as tk
from tkinter import Label, Button, IntVar, StringVar, Scale, OptionMenu
import cv2
from PIL import Image, ImageTk
import socket

#set up socket
HOST = "127.0.0.1" # Localhost
PORT = 65432 # Port to listen on (non-privileged ports are > 1023)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Use UDP for simplicity

def send_signal(control_name, value):
    """Send a signal to the receiver."""
    message = f"{control_name}:{value}"
    sock.sendto(message.encode(), (HOST, PORT))
    print(f"Sent signal: {message}")


# Control Functions
def control_action_1(value):
    print(f"Control 1 selected: {value}")
    send_signal("Needle Length", value)  # Send the selected needle length to the receiver

#slider for Control 2 (Zoom)
def control_action_2(value):
    print(f"Zoom set to: {value}")
    send_signal("Zoom", value)  # Send the zoom value to the receiver

#slider for Control 4 (Sharpness)
def control_action_4(value):
    print(f"Sharpness set to: {value}")
    send_signal("Sharpness", value)  # Send the sharpness value to the receiver
    
#slider for Control 5 (Contrast)
def control_action_5(value):
    print(f"Contrast set to: {value}")
    send_signal("Contrast", value)  # Send the contrast value to the receiver

# Toggle Button for Control 3
def toggle_control_3():
    state = control_var_3.get()
    if state:
        control_3_button.config(text="Equilibrium: Off", bg="firebrick2")  # Set to "Off" appearance
        control_var_3.set(0)  # Turn off
        send_signal("CLAHE", "Off") # Send the signal to turn off the needle
    else:
        control_3_button.config(text="Equilibrium: On", bg="limegreen")  # Set to "On" appearance
        control_var_3.set(1)  # Turn on
        send_signal("CLAHE", "On")  # Send the signal to turn on the needle
    print(f"Control 3 {'On' if control_var_3.get() else 'Off'}")

# Main Application Window
root = tk.Tk()
root.title("Vein Viewer UI")
root.geometry("1280x800")
root.attributes('-fullscreen', True)

# Video Display
video_label = Label(root)
video_label.pack(fill="both", expand=True)  # Make the video label fill the entire window

# Overlay Controls
control_frame = tk.Frame(root, bg="white", highlightbackground="black", highlightthickness=1)
control_frame.place(relx=0.7375, rely=0.1, relwidth=0.25, relheight=0.85) # Position controls on the right side
#                                    also change the else in def toggle controls (line156)

# Create individual frames for each control to ensure even spacing
def create_control_section(parent, label_text, widget):
    frame = tk.Frame(parent, bg="white")
    frame.pack(fill="x", pady=12)  # Add padding for even spacing
    label = Label(frame, text=label_text, font=("Arial", 30), bg="white", fg="black")
    label.pack()
    widget.pack()
    return frame

# Dropdown Menu for Control 1
control_var_1 = StringVar(value="1.0 Inch")
control_1_widget = OptionMenu(control_frame, control_var_1, "1.0 Inch", "1.25 Inch", "1.5 Inch", "2.0 Inch", "2.5 Inch", command=control_action_1)
control_1_widget.config(font=("Arial", 30), width=25)  # Increased font size and width
menu = control_1_widget["menu"]  # Configure the dropdown menu options
menu.config(font=("Arial", 30))  # Set font size for the dropdown options
create_control_section(control_frame, "Needle Length", control_1_widget)

# Scale for Control 2 (Zoom)
control_var_2 = IntVar(value=1)  # Default value is 1x zoom
zoom_scale = Scale(
    control_frame,
    from_=1,
    to=5,
    resolution=0.1,
    orient="horizontal",
    variable=control_var_2,
    command=control_action_2,
    length=300,
    font=("Arial", 24)  # Set font size for the number above the slider
)
create_control_section(control_frame, "Zoom", zoom_scale)

# Scale for Control 4 (Sharpness)
control_var_4 = IntVar(value=1)  # Default value is 1? can change
sharp_scale = Scale(
    control_frame,
    from_=0,
    to=2,
    resolution=0.1,
    orient="horizontal",
    variable=control_var_4,
    command=control_action_4,
    length=300,
    font=("Arial", 24)  # Set font size for the number above the slider
)
create_control_section(control_frame, "Sharpness", sharp_scale)

# Scale for Control 5 (Contrast)
control_var_5 = IntVar(value=1)  # Default value is 1? can change
contrast_scale = Scale(
    control_frame,
    from_=0.5,
    to=2,
    resolution=0.1,
    orient="horizontal",
    variable=control_var_5,
    command=control_action_5,
    length=300,
    font=("Arial", 24)  # Set font size for the number above the slider
)
create_control_section(control_frame, "Contrast", contrast_scale)

# Toggle Button for Control 3
control_var_3 = IntVar(value=0)  # Default state is Off
control_3_button = Button(
    control_frame,
    text="Equilibrium: Off",  # Match the initial state
    bg="firebrick2",  # Match the initial state
    font=("Arial", 30),
    command=toggle_control_3
)
create_control_section(control_frame, "Toggle CLAHE", control_3_button)

# Variable to track the visibility of the control frame
controls_visible = True

# Function to toggle the visibility of the control frame
def toggle_controls():
    global controls_visible
    if controls_visible:
        control_frame.place_forget()  # Hide the controls
        toggle_button.config(text="Show Controls")  # Update button text
    else:
        control_frame.place(relx=0.7375, rely=0.1, relwidth=0.25, relheight=0.85)  # Show the contrls
        toggle_button.config(text="Hide Controls")  # Update button text
    controls_visible = not controls_visible  # Toggle the state

# Add a button to the top bar to toggle controls
toggle_button = Button(root, text="Hide Controls", font=("Arial", 32), command=toggle_controls, fg="white", bg="black")
toggle_button.place(relx=0.75, rely=0.025, relwidth=0.225, relheight=0.075)  # Position the button at the top-left corner
# Start Video Stream
cap = cv2.VideoCapture(0)
# Start QR Detector
qr_detector = cv2.QRCodeDetector()

qr_data = None  # This will store the QR code contents


def update_video_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (1280, 800))  # Resize the huframe to match the screen resolution
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.config(image=imgtk)
        video_label.image = imgtk
        
        # Detect and decode the QR code
        data, bbox, _ = qr_detector.detectAndDecode(frame)
        # If a QR code is detected and decoded
        if bbox is not None and data:
            qr_data = data
            print(f"QR Code Data: {qr_data}")
            
            # Update Control 1 based on QR code data
            if qr_data.lower() == "1.0 Inch":
                control_var_1.set("1.0 Inch")
                control_action_1("1.0 Inch")  # Trigger the control action
            elif qr_data.lower() == "1.25 Inch":
                control_var_1.set("1.25 Inch")
                control_action_1("1.25 Inch")  # Trigger the control action
            elif qr_data.lower() == "1.5 Inch":
                control_var_1.set("1.5 Inch")
                control_action_1("1.5 Inch")  # Trigger the control action
            elif qr_data.lower() == "2.0 Inch":
                control_var_1.set("2.0 Inch")
                control_action_1("2.0 Inch")  # Trigger the control action
            elif qr_data.lower() == "2.5 Inch":
                control_var_1.set("2.5 Inch")
                control_action_1("2.5 Inch")  # Trigger the control action

            
            # Draw a box around the QR code
            for i in range(len(bbox)):
                pt1 = tuple(bbox[i][0])
                pt2 = tuple(bbox[(i + 1) % len(bbox)][0])
                cv2.line(frame, pt1, pt2, (0, 255, 0), 2)


    video_label.after(10, update_video_frame)

update_video_frame()

# Run the Application
root.mainloop()
cap.release()
cv2.destroyAllWindows()
sock.close() # Close the socket when done

#edits
#4/1/25
# Jacob  - changed resolution to 1280x800 and started to increase the button size
# Tested the touchscreen with the Beetronics BEE7TS7M/U1 screen and it worked as a touchscreen and as a video streaming!
# Jacob  - change window to be borderless and fullscreen so users can't click out of the window
# Blaine - Button did not visibly toggle, but the output did on very first click
# Gunner - is it possible to have the video take up the whole area, and the controls on top of the video?
# Riley  - changed to a drop down menu to show all buttons, and hide all of them
# Jacob  - two-click principle? unsure
#completed - borderless, fullscreen window, fullscreen camera, and button to hide/show controls, and control size

#4/13/25
# Jacob - added socket code to send the control values to the receiver (Camera)
# Jacob - changed control sizes and still changing them

#4/16/25
# Jacob - Increased all sizes
# Jacob - added a second file that will take a picture of the sizing after 5 seconds

#4/22/25
# Addis - change the show needle tip control to slider for zoom from 1x to 5x
# Add controls - zoom 1x to 5x, sharpness 0 to 2, toggle CLAHE "contrast equilibruim"
# Remove controls - show needle tip, 
# Change controls - contrast 0.5 to 2, gauge selector is now controlled by qr code reader
# Use open cv for the qr code instead of zed2

#4/24/25
# Jacob - added QR code reader to camera stream
# Jacob - using https://www.the-qrcode-generator.com/

#4/28/25
# Jacob - changed all controls to new camera controls
# Jacob - resized to fit all 5 controls
# Jacob - added code to read the QR code and change the gauge length

#4/30/25
# Jacob - change 20 gauge and 22 gauge to 1.0 inch, 1.25 inch, 1.5 inch, 2.0 inch, 2.5 inch
# Jacob - changed, along with QR code reading