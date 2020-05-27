import pandas
import cv2
from datetime import datetime

first_frame = None
status_list = [None, None]
time = []
df = pandas.DataFrame(columns=['Start', 'End'])

video = cv2.VideoCapture(0)

while True:
	check, frame = video.read()

	# status at the beginning of the recording is set to zero
	status = 0

	# convert the frame to gray scale
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# Converting gray scale image to GaussianBlur so that change can be find easily
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# store the first frame of the video
	if first_frame is None:
		first_frame = gray
		continue

	# diff between first frame and current frame
	diff_frame = cv2.absdiff(first_frame, gray)

	# If difference between first frame and current frame is greater than 30 it will show white color(255)
	thresh_frame = cv2.threshold(diff_frame, 50, 255, cv2.THRESH_BINARY)[1]
	thresh_frame = cv2.dilate(thresh_frame, None, iterations=4)

	# Define the contours, basically adding borders
	(contours, hierarchy) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# Remove noises and shadows, basically keeping only area greater than 1000 px
	for contour in contours:
		if cv2.contourArea(contour) < 10000:
			continue
		status = 1

		(x, y, w, h) = cv2.boundingRect(contour)

		# making rectangle around the moving object
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

	# Appending status
	status_list.append(status)
	status_list = status_list[-2:]

	# appending start time
	if status_list[-1] == 1 and status_list[-2] == 0:
		time.append(datetime.now())

	# appending end time
	if status_list[-1] == 0 and status_list[-2] == 1:
		time.append(datetime.now())

	# displaying image in gray scale
	cv2.imshow("Gray frame", gray)

	# displaying the difference in current time to the static frame(very first)
	cv2.imshow("Difference frame", diff_frame)

	# intensity greater than 1000px will appear
	cv2.imshow("Threshold Frame", thresh_frame)

	# displaying colour frame
	cv2.imshow("colour frame", frame)

	key = cv2.waitKey(1)

	# press "q" to quit
	if key == ord('q'):
		if status == 1:
			time.append(datetime.now())
		break

# Appending time of motion in DataFrame
for i in range(0, len(time), 2):
	df = df.append({"Start": time[i], "End": time[i + 1]}, ignore_index=True)

# write the DataFrame to a csv file
df.to_csv("Times.csv")

video.release() 

# Destroying all the windows 
cv2.destroyAllWindows()