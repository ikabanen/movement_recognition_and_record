import cv2
import time
import pandas
from datetime import datetime
import numpy as np

first_frame = None
status_list = [None, None]
times = []
df = pandas.DataFrame(columns=["Start", "End"])
video = cv2.VideoCapture(0)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
frame_number = 0

while True:
    ret, frame = video.read()
    frame_number += 1
    status = 0
    if not ret:
        print("Can't receive video")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if first_frame is None:
        first_frame = gray
        continue

    delta_frame = cv2.absdiff(first_frame, gray)
    thresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

    (cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in cnts:
        if cv2.contourArea(contour) < 1000:
            continue
        status = 1

        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
    status_list.append(status)
    if status_list[-1] == 1 and status_list[-2] == 0:
        times.append(datetime.now().strftime("%I-%M-%S_%p"))

    if status_list[-1] == 0 and status_list[-2] == 1:
        times.append(datetime.now().strftime("%I-%M-%S_%p"))

    cv2.imshow("Color Frame", frame)
    out.write(frame)

    key = cv2.waitKey(1)

    if key == ord('q'):
        if status == 1:
            times.append(datetime.now().strftime("%I-%M-%S_%p"))
        break
print(status_list)
print(times)

for i in range(0, len(times), 2):
    df = df.append({"Start": times[i], "End": times[i + 1]}, ignore_index=True)
file_name = datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p")
df.to_csv(str(file_name) + ".csv")

video.release()
out.release()
cv2.destroyAllWindows()
