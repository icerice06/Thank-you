import cv2
import mediapipe as mp
import time
import numpy as np

thres = 0.45  # Threshold to detect object
nms_threshold = 0.2
cap = cv2.VideoCapture()
cap.set(3, 1280)
cap.set(4, 720)
cap.set(10, 150)

classNames = []
classFile = 'coco.names'
with open(classFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'

net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

cap = cv2.VideoCapture(0)
pTime = 0
cTime = 0

mpDraw = mp.solutions.drawing_utils
mpFaceMesh = mp.solutions.face_mesh
faceMesh = mpFaceMesh.FaceMesh(max_num_faces=2)
drawSpec = mpDraw.DrawingSpec(thickness=1, circle_radius=2)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDrawHand = mp.solutions.drawing_utils

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    classIds, confs, bbox = net.detect(img, confThreshold=thres)
    bbox = list(bbox)
    confs = list(np.array(confs).reshape(1, -1)[0])
    confs = list(map(float, confs))
    indices = cv2.dnn.NMSBoxes(bbox, confs, thres, nms_threshold)

    results = faceMesh.process(imgRGB)

    resultsHand = hands.process(imgRGB)

    for i in indices:
            box = bbox[i]
            # colors = np.random.uniform(0, 255, size=(len(box), 3))

            x, y, w, h = box[0], box[1], box[2], box[3]
            cv2.rectangle(img, (x, y), (x + w, h + y), color=(0, 255, 0), thickness=2)
            cv2.putText(img, classNames[classIds[i] - 1].upper(), (box[0] + 10, box[1] + 30),
                        cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
            print("Objects Ids: ", classIds)

    # if resultsHand.multi_hand_landmarks:
    #     for handLms in resultsHand.multi_hand_landmarks:
    #         for id, lm in enumerate(handLms.landmark):
    #             print(id, lm)
    #             h, w, c = img.shape
    #             cx, cy = int(lm.x * w), int(lm.y * h)

    #             cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

    #         mpDrawHand.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # if results.multi_face_landmarks:
    #     for faceLms in results.multi_face_landmarks:
    #         mpDraw.draw_landmarks(img, faceLms, mpFaceMesh.FACE_CONNECTIONS,
    #                               drawSpec, drawSpec)
    #         for id, lm in enumerate(faceLms.landmark):
    #             # print(lm)
    #             ih, iw, ic = img.shape
    #             x, y = int(lm.x * iw), int(lm.y * ih)
    #             print("Face id: ", id, x, y)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    # img = cv2.flip(img, 1)
    cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN,
                3, (255, 0, 0), 3)
    cv2.imshow('image', img)
    key = cv2.waitKey(1)

    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()