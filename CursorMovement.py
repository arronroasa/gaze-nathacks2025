import pyautogui
import time


class CursorMover():
    def __init__(self, move_distance):
        self.__move_distance = move_distance

        # Failsafe: Move mouse to top-left corner to stop the script.
        pyautogui.FAILSAFE = True
        print("Mouse controller script started. Move mouse to top-left corner to stop.")

    def move_mouse(self, x_signal, y_signal, ):
        try:
            x_move = 0
            y_move = 0


            # --- X-Axis Logic ---
            # Signal 1 (Left) maps to negative x_move
            if x_signal == 1:
                # Move Left
                x_move = -self.__move_distance
            # Signal 0 (Right) maps to positive x_move
            elif x_signal == -1:
                # Move Right
                x_move = self.__move_distance
            # Any other integer input (like 2, -1, etc.) is ignored, x_move remains 0.

            # Signal 1 (Up) maps to negative y_move (screen coordinates)
            if y_signal == 1:
                # Move Up
                y_move = -self.__move_distance
            # Signal 0 (Down) maps to positive y_move (screen coordinates)
            elif y_signal == -1: 
                # Move Down
                y_move = self.__move_distance
            # Any other integer input is ignored, y_move remains 0.
            
            # --- Execute Move ---
            if x_move != 0 or y_move != 0:
                print(f"Moving: (x={x_move}, y={y_move})")
                # pyautogui.move takes relative coordinates
                pyautogui.move(x_move, y_move) 
                return True
            else:
                # This will print if the user entered signals other than 1 or 0
                print("No move signal (1 or 0) detected. Mouse not moved.")

            
            print("-" * 20) # Separator for clarity
            return False
            
        except KeyboardInterrupt:
            print('\nScript stopped by failsafe (or manual Ctrl+C).')
        except Exception as e:
            print(f'\nAn unexpected error occured: {e}')
        finally:
            return False
        
    def Click(self):
        pyautogui.leftClick()
    