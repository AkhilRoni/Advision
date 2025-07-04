from PyQt5.QtWidgets import (
    QMainWindow, QSplashScreen, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy,
    QApplication, QFrame
)
from PyQt5.QtGui import QPixmap, QIcon, QColor
from PyQt5.QtCore import Qt, QTimer, QUrl, QPoint, QPropertyAnimation, QRect, QParallelAnimationGroup, QEasingCurve
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from constants import AV_ICON, AV_WINDOW_ICON, AV_SPLASH, DEFAULT_AD_PATH
from detection_logic import detect_age_gender, analyze_frame, detect_mood, MoodDetector,start_initial_detection,detect_faces
from ad_manager import get_ad_path, get_next_ad_path, log_played_ad, update_log_fin, get_general_ad,get_all_general_ads,bin_age_to_group
import cv2
import sys
from PyQt5.QtCore import QElapsedTimer,QCoreApplication
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from notif_manager import NotificationManager,NotificationWidget
from PyQt5.QtWidgets import QComboBox, QLineEdit



class MainWindow(QMainWindow):
    def __init__(self, cap):
        super().__init__()
        self.cap = cap  # Use the pre-initialized webcam
        self.setup_ui()
        self.setup_media_player()
        self.setup_title_bar()

        # Initialize Dev Mode Panel
        self.setup_dev_mode_panel()

        # Initialize Notification System
        self.notification_manager = NotificationManager(self)

        # Initialize mood detection and ad priority
        self.age_group = None
        self.gender = None
        self.mood_detector = MoodDetector(threshold=2)  # Set threshold to 2 frames
        self.is_mood_detection_running = True

        self.initial_mood = None
        self.final_mood = None
        self.switched_ad = False
        self.button_pressed = False

        self.current_ad_priority = 1  # Start with priority 1
        self.current_log_id = None
        self.dev_mode = False  # Initially OFF

        self.is_detection_running = False  

        self.start_y = 80

        self.notifications = []  # ✅ Store all notifications

        self.is_muted = True  # Start in muted state

        self.dragging = False

        # Add a QTimer for mood detection
        self.mood_detection_timer = QTimer(self)
        self.mood_detection_timer.timeout.connect(self.start_mood_detection)

        self.is_app_fully_loaded = False  # Start as False
        QTimer.singleShot(5000, lambda: setattr(self, "is_app_fully_loaded", True))  # Set to True after 5 sec

        # Add a flag to track general ad playback
        self.is_playing_general_ad = False  # Start with False

        # Start initial detection
        start_initial_detection(self)
    def setup_ui(self):
        self.setWindowTitle("AdVision")
        self.setWindowIcon(QIcon(AV_WINDOW_ICON))
        self.setGeometry(550, 200, 1600, 1200)  # Larger window size
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Set black background for the main window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1C1C1C;
                color: white;
                font-family: 'Segoe UI', sans-serif;
            }
            QVideoWidget {
                border: 1px solid #555;
                border-radius: 5px;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setFixedSize(1550, 873)

        video_layout = QHBoxLayout()
        video_layout.addStretch()  # Push video to center
        video_layout.addWidget(self.video_widget, alignment=Qt.AlignCenter)  # Align Center
        video_layout.addStretch()

        # Add the video layout to the main layout
        main_layout.addLayout(video_layout)

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Dev Mode Button (Left Side)
        self.dev_mode_button = QPushButton("DEV MODE")
        self.dev_mode_button.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    color: #00E5FF;
                    border-radius: 15px;
                    padding: 15px 30px;
                    font-size: 22px;
                    font-weight: 600;
                    border: 2px solid #333;
                    
                }
                QPushButton:hover {
                    background-color: #444;
                    border: 2px solid #00B8D4;
                }
                QPushButton:pressed {
                    background-color: #222;
                    border: 2px solid #008BA3;
                }
            """)
        
        #
        button_layout.addWidget(self.dev_mode_button)

        # Start Detection Button (Right Side)
        self.detect_button = QPushButton("Detect Face")
        self.detect_button.setStyleSheet("""
            QPushButton {
                background-color: #00C853;
                color: white;
                border-radius: 15px;
                padding: 15px 30px;
                font-size: 22px;
                font-weight: 600;
                text-transform: uppercase;
                border: 2px solid #00C853;
            }
            QPushButton:hover {
                background-color: #009624;
                border: 2px solid #009624;
            }
            QPushButton:pressed {
                background-color: #00701A;
                border: 2px solid #00701A;
            }
        """)
        button_layout.addWidget(self.detect_button)
        self.detect_button.clicked.connect(self.start_detection)
        self.dev_mode_button.clicked.connect(self.toggle_dev_mode)

        # Add button layout to main layout
        main_layout.addLayout(button_layout)

    def setup_dev_mode_panel(self):
        # Create the hidden panel
        self.dev_panel = QFrame()
        self.dev_panel.setStyleSheet("""
            background-color: #222;
            border-top: 2px solid #444;
        """)
        self.dev_panel.setMaximumHeight(0)  # Initially hidden

        # Layout for the panel
        self.dev_panel_layout = QVBoxLayout(self.dev_panel)  # Changed to QVBoxLayout for multiple rows
        self.dev_panel_layout.setContentsMargins(10, 10, 10, 10)
        self.dev_panel_layout.setSpacing(10)

        # First row of buttons
        first_row_layout = QHBoxLayout()
        self.mute_button = QPushButton("🔊 Unmute")
        self.mute_button.clicked.connect(self.toggle_mute)

        self.next_ad_button = QPushButton("⏭️ Next General Ad")
        self.next_ad_button.clicked.connect(self.play_next_general_ad)

        self.close_button_2 = QPushButton("❌ Close App")
        self.close_button_2.clicked.connect(self.close)

        self.notif_button = QPushButton("🚫 Notifications")
        self.notif_button.clicked.connect(self.toggle_notifications)

        for btn in [self.mute_button, self.next_ad_button, self.close_button_2, self.notif_button]:
            btn.setFixedHeight(60)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #444;
                    color: white;
                    border-radius: 10px;
                    font-size: 18px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #666;
                }
            """)

        first_row_layout.addWidget(self.mute_button)
        first_row_layout.addWidget(self.close_button_2)
        first_row_layout.addWidget(self.notif_button)
        first_row_layout.addWidget(self.next_ad_button)

        # Add the first row to the panel
        self.dev_panel_layout.addLayout(first_row_layout)

        # Second row for manual age/gender selection---------------------------------
        # Second row for manual age/gender selection
        second_row_layout = QHBoxLayout()

        # Leftmost: "Custom Input" Button (non-clickable)
        self.custom_input_button = QPushButton("Custom Input")
        self.custom_input_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 10px;
                font-size: 18px;
                font-weight: 600;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #666;  /* Slightly lighter on hover */
            }
            QPushButton:pressed {
                background-color: #444;  /* No change on press */
            }
        """)
        self.custom_input_button.setFixedHeight(60)
        self.custom_input_button.setEnabled(False)  # Make it non-clickable
        second_row_layout.addWidget(self.custom_input_button, stretch=1)  # Equal stretch

        # Middle Left: Age Textbox (right-aligned text)
        self.age_textbox = QLineEdit()
        self.age_textbox.setPlaceholderText("Enter Age")
        self.age_textbox.setStyleSheet("""
            QLineEdit {
                background-color: #444;
                color: white;
                border-radius: 10px;
                font-size: 18px;
                padding: 8px;
                text-align: right;  /* Right-align the text */
            }
            QLineEdit:hover {
                background-color: #666;
            }
        """)
        self.age_textbox.setFixedHeight(60)
        second_row_layout.addWidget(self.age_textbox, stretch=1)  # Equal stretch

        # Middle Right: Gender Dropdown (bigger and better-looking)
        self.gender_dropdown = QComboBox()
        self.gender_dropdown.addItems(["Male", "Female"])
        self.gender_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #444;
                color: white;
                border-radius: 10px;
                font-size: 18px;
                padding: 8px;
                min-width: 100px;  /* Make it wider */
            }
            QComboBox:hover {
                background-color: #666;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: #666;
                border-left-style: solid;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QComboBox::down-arrow {
                image: url(none);  /* Remove default arrow */
            }
            QComboBox QAbstractItemView {
                background-color: #444;  /* Dropdown menu background */
                color: white;  /* Dropdown menu text color */
                selection-background-color: #666;  /* Highlight color */
                font-size: 18px;  /* Bigger font for dropdown items */
                padding: 8px;  /* Padding for dropdown items */
            }
        """)
        self.gender_dropdown.setFixedHeight(60)
        second_row_layout.addWidget(self.gender_dropdown, stretch=1)  # Equal stretch

        # Rightmost: Show Ad Button
        self.show_ad_button = QPushButton("Show Ad")
        self.show_ad_button.clicked.connect(self.show_ad_manually)
        self.show_ad_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 10px;
                font-size: 18px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        self.show_ad_button.setFixedHeight(60)
        second_row_layout.addWidget(self.show_ad_button, stretch=1)  # Equal stretch

        # Add the second row to the panel
        self.dev_panel_layout.addLayout(second_row_layout)
        #------------------------------------------------------------
        self.centralWidget().layout().addWidget(self.dev_panel)
        self.dev_panel_anim = QPropertyAnimation(self.dev_panel, b"maximumHeight")
        self.dev_panel_anim.setDuration(300)
    from PyQt5.QtWidgets import QGraphicsDropShadowEffect

    from PyQt5.QtGui import QIcon, QPixmap

    from PyQt5.QtWidgets import QGraphicsDropShadowEffect
    from PyQt5.QtGui import QColor

    def toggle_dev_mode(self):
        if not self.dev_mode:
            # Enable Dev Mode
            self.dev_panel_anim.setStartValue(0)
            self.dev_panel_anim.setEndValue(230)  # Expand panel
            self.notification_manager.toggle_notifications_visibility(True)  # Show notifications

            # Add glowing effect to the button
            glow_effect = QGraphicsDropShadowEffect(self.dev_mode_button)
            glow_effect.setColor(QColor(0, 229, 255, 150))  # Cyan glow color with transparency
            glow_effect.setBlurRadius(20)  # How blurry the glow is
            glow_effect.setOffset(0, 0)  # No offset (glow surrounds the button)
            self.dev_mode_button.setGraphicsEffect(glow_effect)

            # Button styling for active mode (Glowing cyan)
            self.dev_mode_button.setStyleSheet("""
                QPushButton {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00E5FF, stop:1 #00B8D4);  /* Cyan gradient */
                    color: #333;
                    border-radius: 15px;
                    padding: 15px 30px;
                    font-size: 22px;
                    font-weight: 600;
                    border: 2px solid #00E5FF;
                }
                QPushButton:hover {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00B8D4, stop:1 #008BA3);  /* Darker cyan gradient */
                    border: 2px solid #00B8D4;
                }
                QPushButton:pressed {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                        stop:0 #008BA3, stop:1 #006073);  /* Even darker cyan gradient */
                    border: 2px solid #008BA3;
                }
            """)
            #self.dev_mode_button.setIcon(QIcon(QPixmap("icons/laptop_dark.png")))  # Dark laptop icon
        else:
            # Disable Dev Mode
            self.dev_panel_anim.setStartValue(230)
            self.dev_panel_anim.setEndValue(0)  # Collapse panel
            self.notification_manager.toggle_notifications_visibility(False)  # Hide notifications

            # Remove glowing effect
            self.dev_mode_button.setGraphicsEffect(None)

            # Button styling for inactive mode (Dark grey with cyan text)
            self.dev_mode_button.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    color: #00E5FF;
                    border-radius: 15px;
                    padding: 15px 30px;
                    font-size: 22px;
                    font-weight: 600;
                    border: 2px solid #333;
                }
                QPushButton:hover {
                    background-color: #444;
                    border: 2px solid #00B8D4;
                }
                QPushButton:pressed {
                    background-color: #222;
                    border: 2px solid #008BA3;
                }
            """)
            #self.dev_mode_button.setIcon(QIcon(QPixmap("icons/laptop_glow.png")))  # Glowing laptop icon

        self.dev_panel_anim.start()
        self.dev_mode = not self.dev_mode

    def changeEvent(self, event):
        """Override changeEvent to handle window state changes (minimize/restore)."""
        if event.type() == event.WindowStateChange:
            if self.isMinimized():
                # Hide all notifications when the main window is minimized
                self.notification_manager.toggle_notifications_visibility(False)
            else:
                # Show all notifications when the main window is restored
                self.notification_manager.toggle_notifications_visibility(True)
        super().changeEvent(event)

    # Example usage of notifications
    def log_message(self, message, type="info"):
        colors = {
            "info": "white",
            "warning": "yellow",
            "error": "red"
        }
        self.notification_manager.show_notification(message, colors.get(type, "white"))


    def toggle_notifications(self):
        if not self.notification_manager.notifications_visible:
            self.notification_manager.toggle_notifications_visibility(True)
            self.notif_button.setText("🔔 Notifications")  # Hide text
        else:
            self.notification_manager.toggle_notifications_visibility(False)
            self.notif_button.setText("🚫 Notifications")  # Crossed-out circle + text




    # Rest of your existing methods...
    def setup_media_player(self):
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        self.media_player.setMuted(True)
        self.is_muted = True

        # Play the initial general ad
        self.play_video(get_general_ad())

        # Connect the mediaStatusChanged signal to handle video looping and mood detection
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)

    def setup_title_bar(self):
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet(""" 
            background-color: #333;
            border-radius: 10px;
            height: 90px;
        """)
        title_layout = QHBoxLayout(self.title_bar)

        # Icon
        self.icon_label = QLabel(self.title_bar)
        self.icon_label.setPixmap(QPixmap(AV_ICON).scaled(40, 40, Qt.KeepAspectRatio))
        title_layout.addWidget(self.icon_label)

        # Spacer to push the title to the center
        title_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Title
        title_label = QLabel("AdVision", self.title_bar)
        title_label.setStyleSheet(""" 
            color: white;
            font-size: 32px;
            font-weight: 600;
            text-align: center;
        """)
        title_layout.addWidget(title_label)

        # Spacer to push the buttons to the right
        title_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Minimize button
        self.minimize_button = QPushButton("–", self.title_bar)
        self.minimize_button.setStyleSheet(""" 
            QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                font-size: 36px;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #FF9500;
            }
            QPushButton:pressed {
                background-color: #D47800;
            }
        """)
        self.minimize_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.minimize_button)

        # Close button
        self.close_button = QPushButton("×", self.title_bar)
        self.close_button.setStyleSheet(""" 
            QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                font-size: 36px;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #FF3B30;
            }
            QPushButton:pressed {
                background-color: #D02B20;
            }
        """)
        self.close_button.clicked.connect(self.close)
        title_layout.addWidget(self.close_button)

        # Set the title bar as the menu widget
        self.setMenuWidget(self.title_bar)

    def mousePressEvent(self, event):
        """ Allow dragging only when clicking on the title bar """
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self.dragging = True
            self.offset = event.pos()


    def mouseMoveEvent(self, event):
        """ Move the window when dragging the title bar """
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        """ Stop dragging when releasing the mouse button """
        self.dragging = False




    def play_video(self, ad_path):
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(ad_path)))
        self.media_player.play()

        # Set the flag to indicate whether a general ad is playing
        self.is_playing_general_ad = ad_path in get_all_general_ads()  # Check if the ad is a general ad

    




    def handle_media_status(self, status):
        if not self.is_app_fully_loaded:  # Prevents handling media events too early
            print("🚨 Media status event ignored! App is still loading.")
            return

        # Only handle the "EndOfMedia" status when an ad is playing
        if status == QMediaPlayer.EndOfMedia:
            print("🎬 Ad fully played. Checking if it was accepted...")

            if self.is_playing_general_ad:  # If a general ad was playing
                print("🎥 General ad finished. Playing the next general ad.")
                general_ad_path = get_general_ad()
                self.play_video(general_ad_path)  # Play the next general ad

                # Stop mood detection during general ad playback
                self.is_mood_detection_running = False
                self.mood_detection_timer.stop()

                if self.button_pressed == False:
                    QTimer.singleShot(10000, self.check_for_face_before_restart)

                return  # Skip the rest of the logic for general ads

            if not self.switched_ad:  # Ad was NOT switched due to a mood change
                print("✅ Ad was watched fully ")

                # Update log with 'Happy' final mood (only for age/gender-specific ads)
                if self.age_group and self.gender:  # Only log if age and gender are detected
                    self.log_message("😁 Ad Accepted")
                    update_log_fin(
                        ad_priority=self.current_ad_priority,
                        mainwindow_instance=self,
                        final_mood="happy",
                        switched_ad=False
                    )
                    self.log_message("📝 Log Updated")

                self.button_pressed = False
                # Stop mood detection since ad was accepted
                self.is_mood_detection_running = False

                # 🎥 Play General Ad next
                general_ad_path = get_general_ad()
                self.play_video(general_ad_path)
                self.log_message("🎥 Playing General Ad")

                # 👀 Restart detection after some time (e.g., 10 sec)
                if not self.button_pressed:
                    QTimer.singleShot(10000, self.check_for_face_before_restart)
                else:
                    print("🚫 Detection is already running. Skipping automatic detection.")

            # Reset the flag
            self.is_playing_general_ad = False
        # Start mood detection when the ad starts playing
#        if status == QMediaPlayer.LoadedMedia:
#            if not self.is_mood_detection_running:
#                self.start_mood_detection()
#                self.is_mood_detection_running = True 

    def start_detection(self):
        if self.is_detection_running:
            print("Detection is already running. Ignoring this request.")
            return

        # Set the state to indicate that detection is running
        self.is_detection_running = True
        self.button_pressed = True

        # Stop ongoing mood detection
        self.is_mood_detection_running = False
        self.mood_detection_timer.stop()
        self.current_ad_priority = 1

        # Perform gender and age detection
        self.age_group, self.gender = detect_age_gender(self.cap)
        ad_deets = get_ad_path(self.age_group, self.gender, 1)
        ad_path = ad_deets[1]
        self.play_video(ad_path)
        self.log_message("Age : " + self.age_group + " " + "Gender: " + self.gender)
        ad_id = ad_deets[0]
        log_played_ad(self, ad_id, self.age_group, self.gender, self.initial_mood, 1)
        print("Current Log ID in MainWindow:", self.current_log_id)

        # Restart mood detection after a delay
        self.is_mood_detection_running = True
        QTimer.singleShot(4000, lambda: self.mood_detection_timer.start(200))  # Start the timer after 4 seconds

        # Reset the state variable after detection is complete
        self.is_detection_running = False  # Reset the state


    def show_ad_manually(self):
        if self.is_detection_running:
            print("Detection is already running. Ignoring this request.")
            return

        # Set the state to indicate that detection is running
        self.is_detection_running = True
        self.button_pressed = True


        gender = self.gender_dropdown.currentText()
        age = int(self.age_textbox.text())
        age_group = bin_age_to_group(age)

        self.gender = gender
        self.age_group = age_group

        # Stop ongoing mood detection
        self.is_mood_detection_running = False
        self.mood_detection_timer.stop()

        self.current_ad_priority = 1
        ad_deets = get_ad_path(age_group, gender, 1)
        ad_path = ad_deets[1]
        self.play_video(ad_path)
        self.log_message("Age : " + age_group + " " + "Gender: " + gender)
        self.log_message("🎞️ Playing Ad for Manual Input" )

        ad_id = ad_deets[0]
        log_played_ad(self, ad_id, age_group, gender, self.initial_mood, 1)
        print("Current Log ID in MainWindow:", self.current_log_id)

        # Restart mood detection after a delay
        self.is_mood_detection_running = True
        QTimer.singleShot(4000, lambda: self.mood_detection_timer.start(200))  # Start the timer after 4 seconds

        # Reset the state variable after detection is complete
        self.is_detection_running = False  # Reset the state

    def start_mood_detection(self):
        # 🔥 Ensure mood detection stays ON

        if not self.is_mood_detection_running:
            print("Mood detection is stopped.")
            return

        # Skip mood detection if a general ad is playing
        if self.is_playing_general_ad:
            print("🚫 Skipping mood detection during general ad playback.")
            return

        # Capture frame safely
        ret, frame = self.cap.read()
        if not ret:
            print("❌ Failed to grab frame for mood detection. Retrying...")
            QTimer.singleShot(1000, self.start_mood_detection)  # Retry after 1 sec
            return

        try:
            # Detect mood
            emotion = detect_mood(frame)
            if emotion:
                print(f"✅ Detected emotion: {emotion}")
                #self.log_message(f"✅ Detected emotion: {emotion}")

                # Update mood history and check if we need to switch ads
                if self.mood_detector.update_mood(emotion):
                    self.final_mood = self.mood_detector.mood_history[-1]
                    self.log_message("😡Negative Mood Detected")
                    self.is_mood_detection_running = False
                    self.switch_to_next_ad()
                    
                    return

        except Exception as e:
            print(f"🚨 Error in mood detection: {e}")

        # Ensure mood detection keeps running
        if self.is_mood_detection_running:
            self.mood_detection_timer.start(200)

    def switch_to_next_ad(self):
        if self.age_group is None or self.gender is None:
            print("❌ Age and gender not detected yet. Using default ad.")
            self.age_group, self.gender = "default", "unknown"

        update_log_fin(self.current_ad_priority, self, self.final_mood, switched_ad=True)

        ## Same Age Group Switching Ads for Mood
        if self.current_ad_priority < 3:
            next_priority = self.current_ad_priority + 1
            next_ad_deets = get_ad_path(self.age_group, self.gender, next_priority)
            next_ad_path = next_ad_deets[1]
            ad_id = next_ad_deets[0]
            self.play_video(next_ad_path)
            self.log_message("🎥 Playing Priority " + str(next_priority) + " Ad")
            print("Ad Id of this ad = ", ad_id)

            # Update the current priority (Cycle 1 → 2 → 3 → back to 1)
            self.current_ad_priority = self.current_ad_priority + 1
            log_played_ad(self, ad_id, self.age_group, self.gender, self.final_mood, self.current_ad_priority)
            print(f"🎥 Switched to priority {self.current_ad_priority} ad: {next_ad_path}")
            self.is_mood_detection_running = True
            self.mood_detection_timer.start(4000)  # Start the timer

        ## Jumping out to General ads
        else:
            self.play_video(get_general_ad())
            self.current_ad_priority = 1
            self.log_message(f"🎥 Switched to default ad")
            self.is_mood_detection_running = False
            self.mood_detection_timer.stop()  # Stop the timer
            QTimer.singleShot(10000, self.check_for_face_before_restart)
            self.button_pressed = False

        # Reset mood history after switching ad
        self.mood_detector.mood_history.clear()


    def check_for_face_before_restart(self):
        if self.button_pressed:
            print("🚫 Detection is already running. Skipping face check.")
            return

        print("🔍 Checking for faces before restarting detection...")
        frame = self.get_camera_frame()
        if frame is not None and detect_faces(frame):  # If a face is detected, restart detection
            self.log_message("✅ Face detected! Restarting detection...")
            self.start_detection()
        else:
            self.log_message("🚫 No face detected. Waiting...")
            QTimer.singleShot(10000, self.check_for_face_before_restart)

    def get_camera_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("🚫 Failed to capture image from webcam.")
            return None
        return frame
    
    def toggle_mute(self):
        """Toggles mute state for the video ads"""
        self.is_muted = not self.is_muted  # Flip mute state

        # Actually mute/unmute the media player
        self.media_player.setMuted(self.is_muted)

        # Change button text based on state
        self.mute_button.setText("🔊 Unmute" if self.is_muted else "🔇 Mute")


    def play_next_general_ad(self):
        # Stop mood detection
        self.is_mood_detection_running = False
        self.mood_detection_timer.stop()

        # Reset the ad priority to 1 (general ad)
        self.current_ad_priority = 1

        # Play the next general ad
        next_ad = get_general_ad()  # Get a new general ad
        self.play_video(next_ad)  # Play it immediately

        # Log the action
        self.log_message("🎥 Playing Next General Ad")

    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()
        super().closeEvent(event)

class SplashScreen(QSplashScreen):
    def __init__(self, image_path):
        pixmap = QPixmap(image_path)
        super().__init__(pixmap)
        self.setMask(pixmap.mask())

    def show_splash(self):
        self.show()
        # Close the splash screen after 2 seconds (or earlier if webcam is ready)
        QTimer.singleShot(4000, self.close)