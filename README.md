# face-mask-detection
It uses customised yolov3 framework trained on masked and non masked images

Dataset:
https://www.kaggle.com/alexandralorenzo/maskdetection

Steps:
1. Train the Model using Goolge colab and get yolo weights
  Refer yolo_mask_train.ipynb
  
2. Copy the generated weights in yolo-mask folder
3. Test 
    Image:
      python yolo_image.py --image images/baggage_claim.jpg --yolo yolo-mask
      
     Video feed/Take input from Webcam
     python yolo_video.py --input videos/<file>.mp4 --output output/output.avi --yolo yolo-mask
     
