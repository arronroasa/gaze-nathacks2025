import time

class Serial_Listener():
    def __init__(self, baud_rate, thres, ser):
        self.__delay = time.time()
        self.__baud_rate = baud_rate
        self.__thres = thres
        self.__ser = ser
        # time.sleep(2)
        
    def is_float(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
    def get_click(self):
        for _ in range(10):
            avg = 0
            if self.__ser.in_waiting:
                line = self.__ser.readline().decode('utf-8').strip()
                if (self.is_float(line)):
                    avg += float(line)
                else:
                    print(line)
            time.sleep(1/self.__baud_rate)

        if ((avg/10 > self.__thres) and (time.time()-self.__delay > 0.5S)):
            print(f"BLINKED with EMG VALUE: {avg/10}")
            self.__delay = time.time()
            return True
        return False

