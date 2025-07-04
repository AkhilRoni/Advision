# detection_logic.py
import cv2
from deepface import DeepFace
from collections import Counter,deque
from ad_manager import bin_age_to_group,get_ad_path,log_played_ad
from PyQt5.QtCore import Qt, QTimer


def analyze_frame(frame):
    resized_frame = cv2.resize(frame, (640, 480))
    try:
        result = DeepFace.analyze(resized_frame, actions=['age', 'gender'], enforce_detection=False)
        print("DeepFace result:", result)
        age = result[0]['age']
        gender_prob = result[0]['gender']
        gender = max(gender_prob, key=gender_prob.get)
        return age, gender
    except Exception as e:
        print(f"Error in DeepFace analysis: {e}")
        return None, None

def detect_age_gender(cap, frame_count=5):
    age_predictions = []
    gender_predictions = []

    for _ in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            continue

        age, gender = analyze_frame(frame)
        if age and gender:
            age_predictions.append(age)
            gender_predictions.append(gender)

    age_groups = [bin_age_to_group(age) for age in age_predictions]
    most_common_age_group = Counter(age_groups).most_common(1)[0][0]
    most_common_gender = Counter(gender_predictions).most_common(1)[0][0]
    most_common_gender = "Male" if most_common_gender == "Man" else "Female"

    return most_common_age_group, most_common_gender

def detect_mood(frame):
    try:
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        dominant_emotion = result[0]['dominant_emotion']
        return dominant_emotion
    except Exception as e:
        print(f"Error during mood detection: {e}")
        return None
    
def start_initial_detection(self):
    # Perform initial detection as soon as the webcam is ready
    ret, frame = self.cap.read()
    if not ret:
        print("Failed to grab frame during startup detection")
        return

    try:
        # Perform a quick analysis to warm up the model
        analyze_frame(frame)
        detect_mood(frame)
        print("Initial detection completed. Models are warmed up.")
    except Exception as e:
        print(f"Error during initial detection: {e}")
    
def detect_faces(frame):
    try:
        # Convert frame to RGB (DeepFace needs RGB input)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Analyze frame using DeepFace for face detection only
        faces = DeepFace.extract_faces(rgb_frame, detector_backend='opencv')  

        return len(faces) > 0  # True if faces are detected, False otherwise

    except Exception as e:
        print(f"❌ Face detection error: {e}")
        return False  # In case of error, return False

class MoodDetector:
    def __init__(self, threshold=5):
        self.mood_history = deque(maxlen=threshold)  # Track last N frames
        self.threshold = threshold

    def update_mood(self, emotion):
        self.mood_history.append(emotion)
        mood_counts = Counter(self.mood_history)
        return ((mood_counts['angry'] + mood_counts['sad']) >= self.threshold)