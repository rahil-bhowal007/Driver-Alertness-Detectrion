from scipy.spatial import distance as dist

from imutils import face_utils

import numpy as np
import playsound

import imutils
import time
import dlib
import cv2
def eye_aspect_ratio(eye):
   
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])

   
    ear = (A + B) / (2.0 * C)

    return ear
def mouth_aspect_ratio(mouth):
    A = dist.euclidean(mouth[5], mouth[8])
    B = dist.euclidean(mouth[1], mouth[11])	
    C = dist.euclidean(mouth[0], mouth[6])
    mar=(A + B) / (2.0 * C)
    return mar
 

EYE_AR_THRESH = 0.28
EYE_AR_CONSEC_FRAMES = 30
MOUTH_AR_THRESH = 0.4
COUNTER_MOUTH=0
COUNTER_BLINK=0
COUNTER_FRAMES_MOUTH=0

COUNTER = 0


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


vs = cv2.VideoCapture(0)
#time.sleep(1.0)

while True:

    __, frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

   
    rects = detector(gray, 0)

    for rect in rects:
        
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        jaw=shape[48:61]

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        ear = (leftEAR + rightEAR) / 2.0
        mar = mouth_aspect_ratio(jaw)

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        jawHull = cv2.convexHull(jaw)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [jawHull], -1, (0, 255, 0), 1)

        if COUNTER_BLINK > 25 or COUNTER_MOUTH > 2:
            cv2.putText(frame, "Send Alert!", (200, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            playsound.playsound("audience.wav")
        if ear < EYE_AR_THRESH:
                    COUNTER += 1
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        cv2.putText(frame, "Sleeping Driver!", (200, 80),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        playsound.playsound("alarm.wav")
        else:
            if COUNTER>2:
                COUNTER_BLINK=+1
            COUNTER=0
                
        if mar >= MOUTH_AR_THRESH:
            COUNTER_FRAMES_MOUTH += 1
            cv2.putText(frame, "Sleeping Driver!", (200, 80),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            playsound.playsound("alarm.wav")
        else:
            if COUNTER_FRAMES_MOUTH > 5:
                COUNTER_MOUTH += 1
      
            COUNTER_FRAMES_MOUTH = 0
        if COUNTER_BLINK > 25 or COUNTER_MOUTH > 2:
            cv2.putText(frame, "Send Alert!", (200, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "MAR: {:.2f}".format(mar), (100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255, 255), 2)
 
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(10) & 0xFF

    if key == 27:
        break

cv2.destroyAllWindows()

