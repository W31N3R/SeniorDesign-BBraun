import cv2, numpy as np, torch, torchvision, matplotlib, asyncio, time, math, os
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from models.common import DetectMultiBackend
from utils.general import LOGGER, Profile, xywh2xyxy, clean_str
from utils.torch_utils import select_device
from utils.dataloaders import LoadImages
from timeit import default_timer as timer from threading import Thread
from pathlib import Path
from pynput import keyboard
# Calibrated for 1ft 3/16in
# Vein visualization window dimensions relative to the ZED perspective (right camera, 640x640 center crop)
vein_vis_x_offset = 57
vein_vis_width = 150
vein_vis_y_offset = 275
vein_vis_height = 120
# Initialize other global variables
last_successful_coords = None
exit_loop = False
# Initialize variables used throughout the program with a focus on projector_image
def initializeVariables():
    global vein_vis_height
    global vein_vis_width
    global vein_vis_x_offset
    global vein_vis_y_offset
    f = 0
    lost = 0
    inference_times = []
    inputData = "stream"
    # Define the image that respresents the DLPDLCR4710EVM projection (1920x1080)
    base_image = np.zeros((1080, 1920, 3), np.uint8)
    # Create image that represents the ZED 2 perspective (right camera 640x640 center crop)
    
    projector_image = np.zeros((640, 640, 3), np.uint8)
    # Make blue for development purposes
    projector_image[:, :, 0] = 255
    # # Make the vein visualization window red for development purposes
    # projector_image[0 + vein_vis_y_offset:vein_vis_y_offset + vein_vis_height, 0 + vein_vis_x_offset:vein_vis_x_offset + vein_vis_width, 0] = 0
    # projector_image[0 + vein_vis_y_offset:vein_vis_y_offset + vein_vis_height, 0 + vein_vis_x_offset:vein_vis_x_offset + vein_vis_width, 2] = 255
    # Define new height for the projector image for tuning
    # proj_crop_y = 640 will align the bottom edges of the base image and projector image
    # Decreasing this value will move the vein visualization window downwards on the final projection (might need to find a better way to do this)
    proj_crop_y = 640 - 0
    projector_image = projector_image[0:proj_crop_y, :, :]
    # Define the center coordinates of the vein visualisation window (for scaling at this point)
    center_y = (2*vein_vis_y_offset + vein_vis_height) // 2
    center_x = (2*vein_vis_x_offset + vein_vis_width) // 2
    # Define the offsets for the projector image in relation to the base image
    x_offset = (1920 // 2) - (640 // 2) + 235
    coor    y_offset = 1080 - proj_crop_y
    # Define the scale factor for the projector image, and intialize parameters for place_and_scale
    offset = (x_offset, y_offset)
    scale_factor = 3.65
    center = (320, 320)
    # Creating list of "projecotr information" because this is used to tune the location and size of the viewport
    projection_info = [offset, scale_factor, center]
    
    return f, lost, inference_times, projector_image, inputData, base_image, projection_info
    # Save a histogram of inference times (at the moment this is used to track frame speed)
def saveHistogram(inference_times):
    plt.hist(inference_times, bins=100)
    plt.xlabel('Inference Time (s)')
    plt.ylabel('Frequency')
    plt.title('Histogram of Inference Times')
    plt.savefig('histogram.png')
# Print inference time data (at the moment this is used to track frame speed)
def printTimes(inference_times):
    avg_inference_speed = np.mean(inference_times)
    print(f"Average: {avg_inference_speed}ms, Median: 
    {np.median(inference_times)}ms., Std Dev: {np.std(inference_times)}ms., Variance: 
    {np.var(inference_times)}ms, Max: {np.max(inference_times)}ms, Min: 
    {np.min(inference_times)}ms.")
    saveHistogram(inference_times)
# Get the center point of a box provided by a model result
def getMidpoint(coords):
    return (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2
# Calculate the constant values based on the model results
def getConstants(triangleResults, squareResults):
    if not (squareResults.shape[0] > 1 and triangleResults.shape[0] >= 1):
        return 0, 0, 0, 0, 0, 0, 0
    x_t, y_t = getMidpoint(triangleResults[0])
    x_s1, y_s1 = getMidpoint(squareResults[0])
    x_s2, y_s2 = getMidpoint(squareResults[1])
    return x_t, y_t, x_s1, y_s1, x_s2, y_s2, 100
# Get the center point of the two squares on the tracker
def getCenterPoint(x1, y1, x2, y2):
    return (x1 + x2) / 2, (y1 + y2) / 2

# Calculate the needle coordinates based on both model results
def calculateNeedleCoord(x_t, y_t, x_s1, y_s1, x_s2, y_s2, d):
    if not (x_t and y_t and x_s1 and y_s1 and x_s2 and y_s2):
        return 0, 0
    x_m, y_m = getCenterPoint(x_s1, y_s1, x_s2, y_s2)
    slope = (y_m - y_t) / (x_m - x_t)
    delta_x = -d / np.sqrt(1 + slope**2)
    return (x_t + delta_x, y_t + delta_x * slope)
    vali
# Function provided by Yolov5 for getting frames (edited)
class LoadStreams:
# YOLOv5 streamloader, i.e. `python detect.py --source 'rtsp://example.com/media.mp4' # RTSP, RTMP, HTTP streams`
def __init__(self, sources="file.streams", img_size=640, stride=32, auto=True, transforms=None, vid_stride=1):
    torch.backends.cudnn.benchmark = True # faster for fixed-size inference
    self.mode = "stream"
    self.img_size = img_size
    self.stride = stride
    self.vid_stride = vid_stride # video frame-rate stride
    sources = Path(sources).read_text().rsplit() if os.path.isfile(sources) else [sources]
    n = len(sources)
    self.sources = [clean_str(x) for x in sources] # clean source names for later
    self.imgs, self.fps, self.frames, self.threads = [None] * n, [0] * n, [0]
    * n, [None] * n
    for i, s in enumerate(sources): # index, source
        # Start thread to read frames from video stream
        st = f"{i + 1}/{n}: {s}... "
        s = eval(s) if s.isnumeric() else s # i.e. s = '0' local webcam
        cap = cv2.VideoCapture(s)
        assert cap.isOpened(), f"{st}Failed to open {s}"
        w = 2560
        h = 720
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        fps = cap.get(cv2.CAP_PROP_FPS) # warning: may return 0 or nan
        self.frames[i] = max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 0) or float("inf") # infinite stream fallback
        self.fps[i] = max((fps if math.isfinite(fps) else 0) % 100, 0) or 30 # 30 FPS fallback _, self.imgs[i] = cap.read() # guarantee first frame
        self.threads[i] = Thread(target=self.update, args=([i, cap, s]),daemon=True)
        LOGGER.info(f"{st} Success ({self.frames[i]} frames {w}x{h} at {self.fps[i]:.2f} FPS)")
        self.threads[i].start()
    LOGGER.info("") # newline
    # check for common shapes
    s = np.stack([x.shape for x in self.imgs])
    self.rect = np.unique(s, axis=0).shape[0] == 1 # rect inference if all shapes equal
    self.auto = auto and self.rect
    self.transforms = transforms # optional
    if not self.rect:
        LOGGER.warning("WARNING ⚠️ Stream shapes differ. For optimal performance supply similarly-shaped streams.")
def update(self, i, cap, stream):
    """Reads frames from stream `i`, updating imgs array; handles stream 
    reopening on signal loss."""
    n, f = 0, self.frames[i] # frame number, frame array
    while cap.isOpened() and n < f:
        n += 1
        cap.grab() # .read() = .grab() followed by .retrieve()
        if n % self.vid_stride == 0:
            success, im = cap.retrieve()
            if success:
                self.imgs[i] = im
            else:
                LOGGER.warning("WARNING ⚠️ Video stream unresponsive, please check your IP camera connection.")
                self.imgs[i] = np.zeros_like(self.imgs[i])
                cap.open(stream) # re-open stream if signal was lost
        time.sleep(0.0) # wait time
def __iter__(self):
    """Resets and returns the iterator for iterating over video frames or images in a dataset."""
    self.count = -1
    return self
def __next__(self):
    """Iterates over video frames or images, halting on thread stop or 'q' 
    key press, raising `StopIteration` when
    done.
    """
    self.count += 1
    if not all(x.is_alive() for x in self.threads) or cv2.waitKey(1) ==
        ord("q"): # q to quit
        cv2.destroyAllWindows()
        raise StopIteration
    im0 = self.imgs.copy()
    if self.transforms:
        im = np.stack([self.transforms(x) for x in im0]) # transforms
    else:
        im = np.stack([x for x in im0])
        im = im[..., ::-1].transpose((0, 3, 1, 2)) # BGR to RGB, BHWC to BCHW
        im = np.ascontiguousarray(im) # contiguous
    return self.sources, im, im0, None, ""
def __len__(self):
    """Returns the number of sources in the dataset, supporting up to 32 
    streams at 30 FPS over 30 years."""
    return len(self.sources) # 1E12 frames = 32 streams at 30 FPS for 30 
    years
# Load and warmup the quare and triangle models, set device to GPU
def loadModels():
    device = select_device("0")
    square_model = DetectMultiBackend("C:/Users/tobyw/OneDrive/Desktop/workspace/yolov5/data_square_640x640-center-crop_v1_noWeight.pt", device=device, dnn=False, data="./square_model_640x640-center-crop_v1/data.yaml", fp16=False)
    stride_square, names_square, pt_square = square_model.stride, square_model.names, square_model.pt
    triangle_model = DetectMultiBackend("C:/Users/tobyw/OneDrive/Desktop/workspace/yolov5/data_triangle_640x640-center-crop_v1_noWeight.pt", device=device, dnn=False, data="./triangle_model_640x640-center-crop_v1/data.yaml", fp16=False)
    stride_triangle, names_triangle, pt_triangle = triangle_model.stride, triangle_model.names, triangle_model.pt

    imgsz = [640, 640]
    batchsz = 1

    square_model.warmup(imgsz=(1 if pt_square or square_model.triton else batchsz, 3, *imgsz)) # warmup
    triangle_model.warmup(imgsz=(1 if pt_triangle or triangle_model.triton else batchsz, 3, *imgsz)) # warmup
    seen, windows, dt = 0, [], (Profile(device=device), Profile(device=device), Profile(device=device))
    model_1 = [square_model, 2, 0.25, 0.6]
    model_2 = [triangle_model, 1, 0.25, 0.6]
    print(f"Img size: {imgsz}, Stride: {stride_square}, PT: {pt_square}")
    return model_1, model_2, imgsz, dt, stride_square, pt_square

# Load the data for inference (either a video or a live capture)
def loadData(str, imgsz, stride_square, pt_square):
    if str == "vid":
        dataset = LoadImages("C:/Users/tobyw/OneDrive/Desktop/workspace/yolov5/testVideos/subset_2_left_640x640-crop.mp4", img_size=imgsz, stride=stride_square, auto=pt_square, vid_stride=1)
    else:
        dataset = LoadStreams("0", img_size=imgsz, stride=stride_square, auto=pt_square, vid_stride=1)
    return dataset
# Set cv2 display properties
def loadDisplay():
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
# Non maximum supression for model predictions provided by Yolov5 (edited)
def non_max_suppression(
    prediction,
    model2,
    conf_thres=0.25,
    iou_thres=0.45,
    classes=None,
    agnostic=False,
    max_det=300,
    nm=0, # number of masks
):
    """
    Non-Maximum Suppression (NMS) on inference results to reject overlapping 
    detections.
    Returns:
    list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """
    # Checks
    assert 0 <= conf_thres <= 1, f"Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0"
    assert 0 <= iou_thres <= 1, f"Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0"
    if isinstance(prediction, (list, tuple)): # YOLOv5 model in validation model, output = (inference_out, loss_out)
        prediction = prediction[0] # select only inference output
    nc = prediction.shape[2] - nm - 5 # number of classes
    xc = prediction[..., 4] > conf_thres # candidates
    
    # Settings
    # min_wh = 2 # (pixels) minimum box width and height
    max_wh = 7680 # (pixels) maximum box width and height
    max_nms = 30000 # maximum number of boxes into torchvision.ops.nms()
    t = time.time()
    mi = 5 + nc # mask start index
    output = [torch.zeros((0, 6 + nm), device=prediction.device)]
    x = prediction[xc] # confidence
    # Compute conf
    x[:, 5:] *= x[:, 4:5] # conf = obj_conf * cls_conf
    # Box/Mask
    box = xywh2xyxy(x[:, :4]) # center_x, center_y, width, height) to (x1, y1, x2, y2)
    mask = x[:, mi:] # zero columns if no masks
    conf, j = x[:, 5:mi].max(1, keepdim=True)
    x = torch.cat((box, conf, j.float(), mask), 1)[conf.view(-1) > conf_thres]
    # Check shape
    n = x.shape[0] # number of boxes
    if not n: # no boxes
        return output
    x = x[x[:, 4].argsort(descending=True)[:max_nms]] # sort by confidence and remove excess boxes
    # Batched NMS
    c = x[:, 5:6] * (0 if agnostic else max_wh) # classes
    boxes, scores = x[:, :4] + c, x[:, 4] # boxes (offset by class), scores
    i = torchvision.ops.nms(boxes, scores, iou_thres) # NMS
    i = i[:max_det] # limit detections
    # Only take highest conf for triangle model
    if model2:
        if len(i) > 0:
            output[0] = x[i[0]].unsqueeze(0) # take only the box with the highest score
        else:
            output[0] = None
        return output
        output[0] = x[i]
        return output
# Pull coordinates from prediction objects
def processPredictions(pred):
    det = pred[0].cpu().numpy()[::-1]
    return det[:, :4]
# Inference function for detecting squares and triangles
def inference(img, dt, classes, model_1, model_2):
    pred_1, pred_2 = None, None
    with dt[0]:
        img = torch.from_numpy(img).to(model_1[0].device)
        img = img.half() if model_1[0].fp16 and model_2[0].fp16 else img.float() # uint8 to fp16/32
        img /= 255 # 0 - 255 to 0.0 - 1.0
        if len(img.shape) == 3:
            img = img[None] # expand for batch dim
    # Inference
    with dt[1]:
        pred_1 = model_1[0](img, False, False)
        pred_2 = model_2[0](img, False, False)
    # NMS
    with dt[2]:
        pred_1 = non_max_suppression(pred_1, False, model_1[2], model_1[3],classes, True, model_1[1])
        pred_2 = non_max_suppression(pred_2, True, model_2[2], model_2[3],classes, True, model_2[1])
    return processPredictions(pred_1), processPredictions(pred_2)
# Draw the needle tip on the image
def drawCircle(projector_image, x, y):
    if x != 0 and y != 0:
        return cv2.circle(projector_image, (int(x), int(y)), 2, (255, 255, 255),
    -1)
    else:
        return projector_image
# Helper function for center cropping an image
def center_crop(img, inputData):
    if inputData == "vid":
        _, w, h = img.shape
    else:
        _, _, w, h = img.shape
    crop_w = min(w, 640)
    crop_h = min(h, 640)
    mid_x, mid_y = w // 2, h // 2
    crop_w_next, crop_h_next = crop_w // 2, crop_h // 2
    if inputData == "vid":
        img = img[:, mid_x - crop_w_next:mid_x + crop_w_next, mid_y - crop_h_next:mid_y + crop_h_next]
    else:
        img = img[:, :, mid_x - crop_w_next:mid_x + crop_w_next, mid_y - crop_h_next:mid_y + crop_h_next]
    return img
# Check if the predicted needle tip is within the viewport
def NeedleInView(x, y):
    global vein_vis_height
    global vein_vis_width
    global vein_vis_x_offset
    global vein_vis_y_offset
    # For production
    # if y > 0 + vein_vis_y_offset and y < vein_vis_y_offset + vein_vis_height and x > 0 + vein_vis_x_offset and x < vein_vis_x_offset + vein_vis_width:
    # return True
    # return False
    # For dev
    return True
# Place an image on another image and scale it from a specified center point
def place_and_scale(smaller_image, larger_image, offset, scale_factor, center):
    # Define a transformation matrix for scaling with the specific center point
    M = cv2.getRotationMatrix2D(center, 0, scale_factor)
    # Apply the transformation to the smaller image
    transformed_image = cv2.warpAffine(smaller_image, M, (smaller_image.shape[1],smaller_image.shape[0]))
    # Place the transformed smaller image on the larger image at the offset
    larger_image[offset[1]:offset[1]+transformed_image.shape[0], offset[0]:offset[0]+transformed_image.shape[1]] = transformed_image
    # Crop the larger image to its original size
    cropped_image = larger_image[0:larger_image.shape[0],0:larger_image.shape[1]]
    return cropped_image

# Process each frame by running inference and returning the display
async def processFrame(frame, model_1, model_2, dt, projector_image, input_data, base_image, projection_info):
    global last_successful_coords
    global vein_vis_height
    global vein_vis_width
    global vein_vis_x_offset
    global vein_vis_y_offset
    # Create asycio event loop
    loop = asyncio.get_event_loop()
    # Crop the recieved frame (ZED stream or uncropped video)
    frame = frame[:, :, :, 1280:2560]
    frame = center_crop(frame, input_data)
    # Create inference task for timeout implementation
    inference_task = loop.run_in_executor(None, inference, frame, dt, None, model_1, model_2)
    try:
        # Run inference on the frame asynchronously with a 33ms timeout
        square_results, triangle_results = await asyncio.wait_for(inference_task,
        timeout=0.03333)
        # Calculate constants based on inference results
        x_t, y_t, x_s1, y_s1, x_s2, y_s2, d = getConstants(triangle_results, square_results)
        # Calculate the needle coordinates based on constants
        x_n, y_n = calculateNeedleCoord(x_t, y_t, x_s1, y_s1, x_s2, y_s2, d)
        x_n, y_n = 640 - x_n - 215, 640 - y_n + 53
        # x_n, y_n = x_n - 110, y_n + 75
        # Set the vein visualisation region back to red (switch to black for production)
        # projector_image[0 + vein_vis_y_offset:vein_vis_y_offset + 
        vein_vis_height, 0 + vein_vis_x_offset:vein_vis_x_offset + vein_vis_width, 2] = 255
        # Tesitng real time coloring outside of vein visualsation (purely debugging)
        projector_image[:, :, :] = 0
        projector_image[320, 320, 2] = 255
        # Check if the needle tip is within the vein visualisation region
        if NeedleInView(x_n, y_n):
            # Store results for lost frames
            last_successful_coords = (x_n, y_n)
            # Draw the needle tip
            drawCircle(projector_image, x_n, y_n)
        return 0, place_and_scale(projector_image, base_image, projection_info[0], projection_info[1], projection_info[2])
    except Exception as e:
        # Print to see if timeout occurs
        print(f"Inference failed with error: {e}")
        # Cancel the async task
        inference_task.cancel()
        # Check if we have a previous prediction
        if last_successful_coords is not None:
            x_n, y_n = last_successful_coords
        else:
            x_n, y_n = 0, 0
        # Set the vein visualisation region back to red (switch to black for production)
        # projector_image[0 + vein_vis_y_offset:vein_vis_y_offset + vein_vis_height, 0 + vein_vis_x_offset:vein_vis_x_offset + vein_vis_width, 2] = 255
        projector_image[:, :, :] = 0
        projector_image[320, 320, 2] = 255
        # Draw the circle
        drawCircle(projector_image, x_n, y_n)
        return 1, place_and_scale(projector_image, base_image, projection_info[0], projection_info[1], projection_info[2])
        # Function required for keyboard listener to raise new flag
def on_press(key):
    global exit_loop
    if key == keyboard.Key.esc or key.char == 'q':
        exit_loop = True
    # Main 
async def main():
    global exit_loop
    # Create keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    # Initialize all variables
    f, lost, inference_times, blank_image, input_data, base_image, projection_info = initializeVariables()
    # Load/Warmup the square and triangle models
    model_1, model_2, imgsz, dt, stride_square, pt_square = loadModels()
    # Load the input data (either stream or video)
    dataset = loadData(input_data, imgsz, stride_square, pt_square)
    # Set cv2 display properties
    loadDisplay()
    # Loop pulling frames from video capture or file
    for path, frame, im0s, vid_cap, s in dataset:
        # Start timmer for timing each frame
        start = timer()
        fullstart = start
        # Check for keyboard flag
        # Check for keyboard flag
        if exit_loop:
            break
        # Get the display results and the timeout flag (run inference on frame and process results)
        timeout, projector_image = await processFrame(frame, model_1, model_2, dt, blank_image, input_data, base_image, projection_info)
        # Display cv2 image
        cv2.imshow("image", projector_image)
        # End the timer
        end = timer()
        # Not being timed due to its long execution time on Windows (13ms), reportedly faster on Ubuntu
        cv2.waitKey(5)
        
        # Record frame speed
        inference_speed = end - fullstart
        # Check the timeout flag
        if timeout == 1:
            # Add to the lost frame count
            lost += 1
            # Print the time it took for the frame to be processed
            print(f"Frame {f} took {inference_speed*1000}ms to process.")
        # Update the list of inference times
        inference_times.append(inference_speed*1000)
        # Increment the frame count
        f += 1
    # Stop listening for keyboard events
    listener.stop()
    # Print inference time information (statistics)
    printTimes(inference_times)
    # Print percentage of frames lost
    print(f"{lost / f * 100}% of frames lost.")
    # Close display
    cv2.destroyAllWindows()
if __name__ == "__main__":
    # Use asyncio for timeout implementation
    asyncio.run(main())
