import serial, time
import Bleh, CursorMovement, EyeDetection

testing = False

ser = serial.Serial('COM3', 19200, timeout=1)
time.sleep(2)

serial_listener = Bleh.Serial_Listener(19200, 69/67, ser)
cursor_mover = CursorMovement.CursorMover(67)
eye_detector = EyeDetection.EyeDetector(0.69, 0.67, 0.69, 0.67)

def test():
    print("Beginning Testing Function...    ")

    should_click = False

    # Testing Arduino Connection
    print("Testing Arduino Listener...")
    try:
        should_click = serial_listener.get_click()
        print("Arduino Listener Output:", should_click)
        print("Arduino Successful.")
    except Exception as e:
        print(f"Arduino Listener Failed: {e}")

    # Testing Eye Detector
    print("Testing Eye Detector...")
    try:
        dir = eye_detector.get_eye_detection()
        print("Eye Detector Output:", dir)
        print("Eye Detector Working.")
    except Exception as e:
        print(f"Eye Detector Failed: {e}")

    # Testing Mouse Mover
    print("Testing Mouse Mover...")
    try:
        print("Mouse Mover Output:", cursor_mover.move_mouse(dir[0], dir[1]))
        print("Mouse Mover Working.")
    except Exception as e:
        print(f"Mouse Mover Failed: {e}")

    if (should_click == True):
        cursor_mover.Click()

def main():
    print("Beginning Main Program...")
    while(True):
        dir = eye_detector.get_eye_detection()
        cursor_mover.move_mouse(0, 0)
        if (serial_listener.get_click()):
            print("CLICKED")
            cursor_mover.Click()

if (__name__ == "__main__"):
    if (testing):
        for _ in range(10):
            test()
    else:
        main()