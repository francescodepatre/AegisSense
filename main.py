from detection.yolo_inference import YOLODetector
from control.pan_tilt import PanTiltController
import cv2
import datetime
from multiprocessing import Process, Pipe
import os
import time

screen_width = 1280
screen_height = 720

threshold_x_MAX = screen_width - 200
threshold_x_MIN = screen_width - 1000
threshold_y_MAX = screen_height - 200
threshold_y_MIN = screen_height - 500

def follow_mode(pantilt, cx, cy):
    if(cx >= threshold_x_MAX):
        pantilt.move_pan(pantilt.get_pan() + 10)
    elif(cx <= threshold_x_MIN):
        pantilt.move_pan(pantilt.get_pan() - 10)

    if(cy >= threshold_y_MAX):
        pantilt.move_tilt(pantilt.get_tilt() + 10)
    elif(cy <= threshold_y_MIN):
        pantilt.move_tilt(pantilt.get_tilt() - 10)

def hardware_process(conn, main_pipe):
    #creazione del file di log nella cartella logs
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logfile_path = f"logs/logfile_{timestamp}.txt"

    pan_lmts = (0, 180) 
    tilt_lmts = (0, 180)
    commInterface = None

    HardwareSupport = PanTiltController(pan_channel=1, tilt_channel=0, pan_limits=pan_lmts, tilt_limits=tilt_lmts, logf=logfile_path, commInterface=commInterface)
    print("HARDWARE TEST: SUCCESSFUL\n" if HardwareSupport.test_hardware_support() else "HARDWARE TEST: FAILED\n", flush=True)

    main_pipe.send(True)

    while(True):
        msg = conn.recv()
        match msg[0]:
            case "MoveTilt":
                HardwareSupport.move_tilt(msg[1])
            case "MovePan":
                HardwareSupport.move_pan(msg[1])
            case "Shutdown":
                HardwareSupport.shutdown()
                break
            case "research":
                HardwareSupport.research_loop()
            case "getTilt":
                conn.send(HardwareSupport.get_tilt())
            case "getPan":
                conn.send(HardwareSupport.get_pan())
            case "detected":
                
                follow_mode(HardwareSupport,msg[1],msg[2])
                tilt_position = HardwareSupport.get_tilt()
                pan_position = HardwareSupport.get_pan()
                HardwareSupport.move_pan(pan_position)
                HardwareSupport.move_tilt(tilt_position)


def detection_process(conn):

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("MISSING CAMERA PERIPHERAL!")
        return

    detectorAgent = YOLODetector()

    frame_counter = 0

    while(True):

        if conn.poll():
            msg = conn.recv()
            if msg == "Shutdown":
                break

        ret, frame = cap.read()
        frame_counter += 1

        if not ret:
            print("FAILED TO GRAB FRAME")
            break

        
        center, output_frame, detections = detectorAgent.detect(frame, frame_counter)
        

        if detections is None:
            pass
        elif detections == 0:
            conn.send(("research",))
        elif detections == 1:
            conn.send(("detected",center[0],center[1]))
            '''
            conn.send(("detected",))
            if(center[0] > threshold_x_MIN and center[0] < threshold_x_MAX):
                pass
            elif(center[0] < threshold_x_MIN):
                conn.send(("getPan",))
                panPosition = conn.recv()
                msg = ("MovePan", panPosition - 5)
                conn.send(msg)
            elif(center[0] > threshold_x_MAX):
                conn.send(("getPan",))
                panPosition = conn.recv()
                msg = ("MovePan", panPosition[0] + 5)
                conn.send(msg)
        
            if(center[1] > threshold_y_MIN and center[1] < threshold_y_MAX):
                pass
            elif(center[1] < threshold_y_MIN):
                conn.send(("getTilt",))
                tiltPosition = conn.recv()
                msg = ("MoveTilt", tiltPosition - 5)
                conn.send(msg)
            elif(center[1] > threshold_y_MAX):
                conn.send(("getTilt",))
                tiltPosition = conn.recv()
                msg = ("MoveTilt", tiltPosition + 5)
                conn.send(msg)
            '''
            

            time.sleep(0.01)
    cap.release()  
        
def main():

    detect_conn, platform_conn = Pipe()
    main_conn, p1_conn = Pipe()
    p1 = Process(target=hardware_process, args=(platform_conn,p1_conn))
    
    p1.start()

    test_response = main_conn.recv()

    if test_response:
        p2 = Process(target=detection_process, args=(detect_conn,))
        p2.start()
    else:
        p1.close()
        print("HARDWARE TEST FAILED - EXIT")
        return

    try:
        userInput = input("INSERT 'q' TO TERMINATE OPERATION: ")
        if userInput.strip().lower() == 'q':
            detect_conn.send(("Shutdown",))
            platform_conn.send(("Shutdown",))
            time.sleep(3)
            p1.terminate()
            p2.terminate()
            return
    except KeyboardInterrupt:
        print("MANUAL INTERRUPTION!")
        detect_conn.send(("Shutdown",))
        platform_conn.send(("Shutdown",))
        p1.terminate()
        p2.terminate()
        return

if __name__ == "__main__":
    main()
