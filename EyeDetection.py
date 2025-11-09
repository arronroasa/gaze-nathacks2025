import cv2
from collections import deque

class EyeDetector():
    # Callback function for trackbars
    def nothing(self, x):
        pass

    def __init__(self, max_cx, min_cx, max_cy, min_cy):
        # Initialize webcam
        self.__cap = cv2.VideoCapture(0)
        self.__eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.__face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Create a window with trackbars for adjustable horizontal/vertical center zones
        # cv2.namedWindow("Controls")
        # cv2.createTrackbar("Center Min X (%)", "Controls", 45, 100, self.nothing)
        # cv2.createTrackbar("Center Max X (%)", "Controls", 55, 100, self.nothing)
        # cv2.createTrackbar("Center Min Y (%)", "Controls", 45, 100, self.nothing)
        # cv2.createTrackbar("Center Max Y (%)", "Controls", 55, 100, self.nothing)

        self.__center_min_x = min_cx
        self.__center_min_y = min_cy
        self.__center_max_x = max_cx
        self.__center_max_y = max_cy

        # Deques to store last N pupil positions for smoothing
        N = 5
        self.__cx_history = deque(maxlen=N)
        self.__cy_history = deque(maxlen=N)

    def get_eye_detection(self):
        ret, frame = self.__cap.read()
        if not ret:
            return False

        # Flip frame horizontally so LEFT/RIGHT matches user's perspective
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Read thresholds from trackbars
        # center_min_x = cv2.getTrackbarPos("Center Min X (%)", "Controls") / 100.0
        # center_max_x = cv2.getTrackbarPos("Center Max X (%)", "Controls") / 100.0
        # center_min_y = cv2.getTrackbarPos("Center Min Y (%)", "Controls") / 100.0
        # center_max_y = cv2.getTrackbarPos("Center Max Y (%)", "Controls") / 100.0

        faces = self.__face_cascade.detectMultiScale(gray, 1.3, 5)

        x_dir = 0
        y_dir = 0
        
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            # roi_color = frame[y:y+h, x:x+w]
            
            eyes = self.__eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                eye_gray = roi_gray[ey:ey+eh, ex:ex+ew]
                # eye_color = roi_color[ey:ey+eh, ex:ex+ew]
                
                # Preprocessing
                blurred = cv2.GaussianBlur(eye_gray, (3, 3), 0)
                thresh = cv2.adaptiveThreshold(
                    blurred, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY_INV, 11, 3
                )
                
                # Find contours
                contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                contours = [c for c in contours if cv2.contourArea(c) > 30]
                contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
                
                # Draw the CENTER zone rectangle inside the eye
                # top_left = (int(ew * center_min_x), int(eh * center_min_y))
                # bottom_right = (int(ew * center_max_x), int(eh * center_max_y))
                # cv2.rectangle(eye_color, top_left, bottom_right, (0, 255, 255), 1)  # yellow rectangle

                if contours:
                    (cx, cy), radius = cv2.minEnclosingCircle(contours[0])
                    
                    # Add to history for smoothing
                    self.__cx_history.append(cx)
                    self.__cy_history.append(cy)
                    
                    smooth_cx = sum(self.__cx_history) / len(self.__cx_history)
                    smooth_cy = sum(self.__cy_history) / len(self.__cy_history)

                    # Adjust horizontal position for flipped frame
                    smooth_cx_flipped = ew - smooth_cx
                    
                    # cv2.circle(eye_color, (int(smooth_cx), int(smooth_cy)), int(radius), (255, 0, 0), 2)

                    # Normalized pupil positions
                    rel_cx = smooth_cx_flipped / ew
                    rel_cy = smooth_cy / eh

                    # Horizontal direction
                    if rel_cx < self.__center_min_x:
                        horiz = 'LEFT'
                    elif rel_cx > self.__center_max_x:
                        horiz = 'RIGHT'
                    else:
                        horiz = 'CENTER'

                    # Vertical direction
                    if rel_cy < self.__center_min_y:
                        vert = 'UP'
                    elif rel_cy > self.__center_max_y:
                        vert = 'DOWN'
                    else:
                        vert = 'CENTER'

                    # Combine directions
                    if horiz == 'CENTER' and vert == 'CENTER':
                        direction = 'CENTER'
                    elif horiz != 'CENTER' and vert == 'CENTER':
                        direction = horiz
                        if horiz == 'LEFT':
                            x_dir = -1
                        elif horiz == 'RIGHT':
                            x_dir = 1
                    elif horiz == 'CENTER' and vert != 'CENTER':
                        direction = vert
                        if vert == 'UP':
                            x_dir = 1
                        elif vert == 'DOWN':
                            x_dir = -1
                    else:
                        direction = vert + '-' + horiz  # e.g., UP-LEFT
                        if direction == 'UP-LEFT':
                            x_dir = -1
                            y_dir = 1
                        elif vert == 'UP-RIGHT':
                            x_dir = 1
                            y_dir = 1
                        elif vert == 'DOWN-LEFT':
                            x_dir = -1
                            y_dir = -1
                        elif vert == 'DOWN-RIGHT':
                            x_dir = 1
                            y_dir =-1

                    # Color pupil circle based on CENTER zone
                    # if direction == 'CENTER':
                    #     circle_color = (0, 255, 0)  # green
                    # else:
                    #     circle_color = (0, 0, 255)  # red

        return [x_dir, y_dir]

        #             cv2.circle(eye_color, (int(smooth_cx), int(smooth_cy)), int(radius), circle_color, 2)
        #             cv2.putText(frame, direction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        #             print(direction)
                    
                    # cv2.imshow('Pupil Direction', frame)
                    
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #     break
        
    def __del__(self):
        self.__cap.release()
        # cv2.destroyAllWindows()
        # cv2.destroyWindow("Controls")
