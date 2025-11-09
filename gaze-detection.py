import cv2
import torch
import numpy as np
from threading import Thread
from l2cs import Pipeline # installed package

# ----------------------------
# CONFIG
# ----------------------------
# These values are now constants for the pinhole model.
HEIGHT_OF_HUMAN_FACE = 250 # mm (S_actual: Approximate actual height of a human face)

# *** ACTION REQUIRED: CALIBRATE THIS VALUE ***
# Replace the guess (700) with your actual calibrated Focal Length in Pixels (F).
FOCAL_LENGTH_PIXELS = 700 

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
WEIGHTS_PATH = "models/L2CSNet_gaze360.pkl" # Make sure this path is correct

# Initialize L2CS-Net pipeline
gaze_pipeline = Pipeline(weights=WEIGHTS_PATH, arch="ResNet50", device=DEVICE)

# OpenCV face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# ----------------------------
# THREADING FOR WEBCAM (Unchanged)
# ----------------------------
class WebcamStream:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        Thread(target=self.update, daemon=True).start()

    def update(self):
        while not self.stopped:
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.stopped = True
        self.cap.release()


# ----------------------------
# FUNCTIONS (Unchanged)
# ----------------------------
def detect_face(frame, scale_factor=0.5):
    small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return None
    
    # Use the largest face found, assuming it's the main user
    # Note: Using faces[0] is still a simplification, but maintained from original.
    x, y, w, h = [int(f / scale_factor) for f in faces[0]]
    
    face_crop = frame[y:y+h, x:x+w]
    face_crop = cv2.resize(face_crop, (224, 224)) # resize for L2CS-Net
    return face_crop, (x, y, w, h)


def draw_gaze(frame, bbox, yaw, pitch):
    x, y, w, h = bbox
    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    arrow_length = w # Arrow length based on bbox width
    
    # Standard 3D vector calculation for the arrow projection
    dx = arrow_length * np.sin(yaw) * np.cos(pitch)
    dy = -arrow_length * np.sin(pitch) * np.cos(yaw) # Corrected to project based on cos(yaw) as well
    
    cv2.arrowedLine(
        frame,
        (x + w // 2, y + h // 2),
        (int(x + w // 2 + dy), int(y + h // 2 + dx)),
        (0, 0, 255),
        2,
        cv2.LINE_AA,
        tipLength=0.2,
    )

    label = f"Yaw: {np.degrees(yaw):.2f}, Pitch: {np.degrees(pitch):.2f}"
    cv2.putText(frame, label, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return frame


# ----------------------------
# MAIN LOOP
# ----------------------------
def main():
    vs = WebcamStream(0)

    frame_count = 0
    skip_frames = 2
    last_yaw, last_pitch, last_bbox = 0, 0, None

    alpha = 0.3 # smoothing factor
    neutral_yaw, neutral_pitch = None, None # neutral gaze calibration

    while True:
        ret, frame = vs.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1) # mirror for natural webcam view
        frame_count += 1

        if frame_count % skip_frames == 0:
            face_crop_info = detect_face(frame)
            if face_crop_info is not None:
                face_crop, bbox = face_crop_info
                gaze_result = gaze_pipeline.step(face_crop)
                yaw = gaze_result.yaw.item()
                pitch = gaze_result.pitch.item()

                # Correct yaw for mirrored webcam
                yaw = -yaw

                # Capture neutral gaze on first valid detection
                if neutral_yaw is None:
                    neutral_yaw = yaw
                    neutral_pitch = pitch

                # Offset by neutral gaze
                yaw -= neutral_yaw
                pitch -= neutral_pitch

                # Exponential smoothing
                last_yaw = alpha * yaw + (1 - alpha) * last_yaw
                last_pitch = alpha * pitch + (1 - alpha) * last_pitch
                last_bbox = bbox

        if last_bbox is not None:
            frame = draw_gaze(frame, last_bbox, last_yaw, last_pitch)

            # --- DYNAMIC DISTANCE ESTIMATION ---
            face_height_pixels = last_bbox[3]
            
            # D_actual = (S_actual * F) / S_pixel
            # Calculate dynamic distance for optional display (in mm)
            dynamic_distance_mm = (HEIGHT_OF_HUMAN_FACE * FOCAL_LENGTH_PIXELS) / face_height_pixels
            
            # --- IMPROVED GAZE MAPPING TO SCREEN COORDINATES ---
            # The D_actual cancels out in the pixel projection:
            # dx_pixels = D_actual * tan(yaw) * (F / D_actual) = F * tan(yaw)
            
            # --- MODIFIED GAZE MAPPING TO SCREEN COORDINATES ---
            img_h, img_w = frame.shape[:2]

            # 1. Calculate pixel offsets (Swap and Negate Horizontal)
            # Horizontal offset (X-axis) now comes from Pitch (last_pitch), and is negated for flip.
            # Vertical offset (Y-axis) now comes from Yaw (last_yaw).
            dx_pixels_corrected = -FOCAL_LENGTH_PIXELS * np.tan(last_pitch)
            dy_pixels_corrected = FOCAL_LENGTH_PIXELS * np.tan(last_yaw)

            # 2. Calculate target screen coordinates based on frame center
            center_x = img_w / 2
            center_y = img_h / 2

            # Apply corrected offsets to their respective axes
            target_x = center_x + dx_pixels_corrected
            target_y = center_y + dy_pixels_corrected

            # 3. Draw the gaze point
            if np.isfinite(target_x) and np.isfinite(target_y):
                gaze_x = int(np.clip(target_x, 0, img_w - 1))
                gaze_y = int(np.clip(target_y, 0, img_h - 1))
                
                # Use standard OpenCV (X, Y) order
                gaze_point = (gaze_x, gaze_y) 
                
                cv2.circle(frame, gaze_point, 15, (0, 0, 255), -1)
            # ...
            
            # Optional: Display estimated distance
            label_dist = f"Distance: {dynamic_distance_mm/1000:.2f} m"
            cv2.putText(frame, label_dist, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            gaze_coords = (gaze_x/img_w, gaze_y/img_h)
            print(gaze_coords)

        cv2.imshow("L2CS-Net Gaze Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    vs.stop()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()