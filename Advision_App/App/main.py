import time
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ui import SplashScreen, MainWindow
from constants import AV_SPLASH
import cv2
from deepface import DeepFace
import numpy as np

def main():
    start_time = time.time()
    print("Starting application...")

    # Create the application
    app = QApplication(sys.argv)
    print(f"QApplication created: {time.time() - start_time:.2f} seconds")

    # Show the splash screen immediately
    splash_start_time = time.time()
    splash = SplashScreen(AV_SPLASH)
    splash.show()
    print(f"Splash screen displayed: {time.time() - splash_start_time:.2f} seconds")

    # Force the event loop to process the splash screen immediately
    QApplication.processEvents()

    # Initialize the webcam
    webcam_start_time = time.time()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend (Windows)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set width to 640px
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set height to 480px
    if not cap.isOpened():
        print("Failed to open webcam")
        sys.exit()
    print(f"Webcam initialized: {time.time() - webcam_start_time:.2f} seconds")

    # Preload the model (in the main thread)
    model_start_time = time.time()
    try:
        # Perform a dummy analysis to load the model
        dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)  # Create a dummy frame
        DeepFace.analyze(dummy_frame, actions=['age', 'gender'], enforce_detection=False)
        print(f"Model preloaded: {time.time() - model_start_time:.2f} seconds")
    except Exception as e:
        print(f"Error preloading model: {e}")

    # Perform initial detection (in the main thread)
    detection_start_time = time.time()
    try:
        # Grab a single frame for initial detection
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame during startup detection")
        else:
            # Resize the frame to reduce processing time
            resized_frame = cv2.resize(frame, (320, 240))  # Smaller frame size

            # Perform a quick analysis to warm up the model
            DeepFace.analyze(resized_frame, actions=['age', 'gender'], enforce_detection=False)
            print(f"Initial detection completed: {time.time() - detection_start_time:.2f} seconds")
    except Exception as e:
        print(f"Error during initial detection: {e}")

    # Create the main window with the pre-initialized webcam
    window_start_time = time.time()
    window = MainWindow(cap)  # Pass the webcam object here
    print(f"Main window created: {time.time() - window_start_time:.2f} seconds")

    # Close the splash screen and show the main window
    splash.finish(window)  # Close the splash screen and transfer focus to the main window
    window.show()

    # Start the application event loop
    print(f"Application ready: {time.time() - start_time:.2f} seconds")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()