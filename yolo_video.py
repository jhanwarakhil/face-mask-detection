# USAGE
# python yolo_video.py --input videos/<>.mp4 --output output/airport_output.avi --yolo yolo-mask

# import the necessary packages
import numpy as np
import argparse
import imutils
import time
import cv2
import os

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", type=str, default="",
        help="path to (optional) input video file")
ap.add_argument("-o", "--output", type=str, default="",
        help="path to (optional) output video file")
ap.add_argument("-y", "--yolo", required=True,
        help="base path to YOLO directory")
ap.add_argument("-c", "--confidence", type=float, default=0.1,
        help="minimum probability to filter weak detections")
ap.add_argument("-t", "--threshold", type=float, default=0.3,
        help="threshold when applyong non-maxima suppression")
args = vars(ap.parse_args())

# load the COCO class labels our YOLO model was trained on
labelsPath = os.path.sep.join([args["yolo"], "yolo.names"])
LABELS = open(labelsPath).read().strip().split("\n")

# derive the paths to the YOLO weights and model configuration
weightsPath = os.path.sep.join([args["yolo"], "yolov3_custom_train_3000.weights"])
configPath = os.path.sep.join([args["yolo"], "yolov3_custom_train.cfg"])

# load our YOLO object detector trained on COCO dataset (80 classes)
# and determine only the *output* layer names that we need from YOLO
print("[INFO] loading YOLO from disk...")
net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# initialize the video stream, pointer to output video file, and
# frame dimensions
vs = cv2.VideoCapture(args["input"] if args["input"] else 0)
writer = None
(W, H) = (None, None)

# loop over frames from the video file stream
while True:
        # read the next frame from the file
        (grabbed, frame) = vs.read()

        # if the frame was not grabbed, then we have reached the end
        # of the stream
        if not grabbed:
                break

        # if the frame dimensions are empty, grab them
        if W is None or H is None:
                (H, W) = frame.shape[:2]

        # construct a blob from the input frame and then perform a forward
        # pass of the YOLO object detector, giving us our bounding boxes
        # and associated probabilities
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                swapRB=True, crop=False)
        net.setInput(blob)
        start = time.time()
        layerOutputs = net.forward(ln)
        end = time.time()

        # initialize our lists of detected bounding boxes, confidences,
        # and class IDs, respectively
        boxes = []
        confidences = []
        classIDs = []

        # loop over each of the layer outputs
        for output in layerOutputs:
                # loop over each of the detections
                for detection in output:
                        # extract the class ID and confidence (i.e., probability)
                        # of the current object detection
                        scores = detection[5:]
                        classID = np.argmax(scores)
                        confidence = scores[classID]

                        # filter out weak predictions by ensuring the detected
                        # probability is greater than the minimum probability
                        if confidence > args["confidence"]:
                                # scale the bounding box coordinates back relative to
                                # the size of the image, keeping in mind that YOLO
                                # actually returns the center (x, y)-coordinates of
                                # the bounding box followed by the boxes' width and
                                # height
                                box = detection[0:4] * np.array([W, H, W, H])
                                (centerX, centerY, width, height) = box.astype("int")

                                # use the center (x, y)-coordinates to derive the top
                                # and and left corner of the bounding box
                                x = int(centerX - (width / 2))
                                y = int(centerY - (height / 2))

                                # update our list of bounding box coordinates,
                                # confidences, and class IDs
                                boxes.append([x, y, int(width), int(height)])
                                confidences.append(float(confidence))
                                classIDs.append(classID)

        # apply non-maxima suppression to suppress weak, overlapping
        # bounding boxes
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],
                args["threshold"])

        # ensure at least one detection exists
        if len(idxs) > 0:
                # loop over the indexes we are keeping
                for i in idxs.flatten():
                        # extract the bounding box coordinates
                        (x, y) = (boxes[i][0], boxes[i][1])
                        (w, h) = (boxes[i][2], boxes[i][3])
                        
                        # draw a bounding box rectangle and label on the frame
                        label=LABELS[classIDs[i]]
                        color=(0,255,0) if label == "Mask" else (0,0,255) 
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        text = "{}".format(LABELS[classIDs[i]])
            
                        cv2.putText(frame, text, (x, y - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
                break    
       # check if the video writer is None
        if writer is None:
                # initialize our video writer
                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                writer = cv2.VideoWriter(args["output"], fourcc, 30,
                        (frame.shape[1], frame.shape[0]), True)

                

        # write the output frame to disk
        writer.write(frame)

# release the file pointers
print("[INFO] cleaning up...")
writer.release()
vs.release()
