from PyQt5.QtCore import QTimer, QPoint, QElapsedTimer, Qt
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve


from PyQt5.QtCore import QObject, QTimer, QPoint
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

class NotificationManager(QObject):  # Inherit from QObject
    def __init__(self, parent):
        super().__init__(parent)  # Call the QObject constructor
        self.parent = parent
        self.notifications = []  # Stores active notifications
        self.max_notifications = 3  # Maximum number of stacked notifications
        self.notification_height = 100  # Increased height
        self.notification_width = 450  # Increased width
        self.notification_spacing = 15  # Spacing between notifications
        self.notifications_visible = False

        # Calculate base_y correctly (below the title bar)
        title_bar_height = self.parent.title_bar.height()  # Get the title bar height
        self.base_y = title_bar_height + 70  # Increased padding (20 + 50)

        # Timer for checking notifications
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.check_notifications)
        self.hide_timer.start(200)  # Check frequently

        # Connect to the parent window's state change event
        self.parent.installEventFilter(self)  # Install an event filter to monitor window state changes

    def eventFilter(self, obj, event):
        """Event filter to handle window state changes (minimize/restore)."""
        if obj == self.parent and event.type() == event.WindowStateChange:
            if self.parent.isMinimized():
                # Hide all notifications when the main window is minimized
                self.toggle_notifications_visibility(False)
            else:
                # Show all notifications when the main window is restored
                self.toggle_notifications_visibility(True)
        return super().eventFilter(obj, event)

    # Rest of your methods remain unchanged...

    def show_notification(self, message, type="info"):
        """Shows a new notification and manages the stack of existing ones"""
        if not self.parent.dev_mode:
            return  # Only show notifications in Dev Mode

        # If we already have max notifications, remove the oldest one instantly
        if len(self.notifications) >= self.max_notifications:
            oldest = self.notifications.pop()  # Remove the LAST one (oldest)
            oldest.deleteLater()  # Instantly remove the oldest notification

        # Create the new notification
        notification = NotificationWidget(self.parent, message, type, self)

        # Calculate position relative to the main window
        main_window_pos = self.parent.mapToGlobal(QPoint(0, 0))  # Get the main window's top-left corner
        notification_x = main_window_pos.x() + 20  # Add some padding
        notification_y = main_window_pos.y() + self.base_y  # Use base_y for vertical position

        # Set initial position off-screen to the left
        notification.setGeometry(-self.notification_width, notification_y, 
                                self.notification_width, self.notification_height)

        # Insert new notification at the FRONT of the list (so it stays on top)
        self.notifications.insert(0, notification)

        # Update positions of all notifications
        self.update_notification_positions()

        # Make it visible
        notification.show()

        # Slide it in
        notification.slide_in()

    def update_notification_positions(self):
        """Updates the positions of all notifications to maintain the stack"""
        y_offset = self.base_y  # Start from base Y position
        spacing = self.notification_spacing  # Use the defined spacing

        for i, notification in enumerate(self.notifications):
            target_y = y_offset + (i * (self.notification_height + spacing))
            notification.move_to(target_y)

    def check_notifications(self):
        """Checks for notifications that need to be removed"""
        # Get list of notifications that have been shown for more than 5 seconds
        to_remove = [n for n in self.notifications if n.should_remove()]

        # Remove them properly
        for notification in to_remove:
            print(f"Removing old notification: {notification.message}")  # Debugging
            self.notifications.remove(notification)
            notification.deleteLater()

        # Ensure correct spacing after removing old ones
        if to_remove:
            self.update_notification_positions()

    def toggle_notifications_visibility(self, visible):
        self.notifications_visible = visible  # Update state
        """Toggles visibility of all notifications based on Dev Mode"""
        for notification in self.notifications:
            notification.setVisible(visible)

class NotificationWidget(QWidget):
    def __init__(self, parent, message, type, manager):
        super().__init__(None)  # Set parent to None to make it an independent window
        self.parent = parent
        self.manager = manager
        self.message = message
        self.type = type
        self.create_time = QElapsedTimer()
        self.create_time.start()  # Use this to track how long notification has been shown
        self.animation = None  # Initialize the animation attribute

        # Set up the UI
        self.init_ui()

    def init_ui(self):
        """Set up the notification UI"""
        self.setFixedSize(self.manager.notification_width, self.manager.notification_height)

        # Make the widget background fully transparent
        self.setAttribute(Qt.WA_TranslucentBackground)  # 🔥 Key change
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)  # Stay on top

        # Add a frame to hold the notification content
        self.frame = QFrame(self)
        self.frame.setGeometry(0, 0, self.width(), self.height())
        self.frame.setStyleSheet(f"""
            background-color: {self.get_background_color()};
            border-radius: 15px;
            border: 2px solid {self.get_border_color()};
            padding: 15px;
        """)

        # Add message label inside the frame
        self.label = QLabel(self.frame)
        self.label.setWordWrap(True)

        self.label.setStyleSheet("""
            background: rgba(255, 255, 255, 0.15);  /* More visible glass effect */
            color: white;
            padding: 20px;  /* Increased padding for better spacing */
            border-radius: 14px;  /* Slightly rounder edges */
            font-size: 18px;  /* Bigger font */
            font-weight: 600;  /* Thicker, bolder font */
        """)

        self.setMinimumSize(320, 80)  # Increase notification box size

        self.setGraphicsEffect(QGraphicsDropShadowEffect(self))
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)  # More blur for a softer shadow
        shadow.setXOffset(0)
        shadow.setYOffset(5)  # Slightly more depth
        shadow.setColor(QColor(0, 0, 0, 100))  # Darker shadow
        self.setGraphicsEffect(shadow)


        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label.setWordWrap(True)
        self.label.setText(self.message)
        self.label.setGeometry(15, 15, 420, 70)  # Adjusted geometry for bigger size

        # Bring the notification to the front
        self.raise_()  # 🔥 Key change
        self.show()  # Ensure the notification is shown

    def get_background_color(self):  # Fixed typo here
        """Get background color based on notification type"""
        colors = {
            "info": "rgba(30, 30, 30, 230)",  # Dark gray
            "warning": "rgba(255, 193, 7, 230)",  # Amber
            "error": "rgba(244, 67, 54, 230)"  # Red
        }
        return colors.get(self.type, "rgba(30, 30, 30, 230)")

    def get_border_color(self):
        """Get border color based on notification type"""
        colors = {
            "info": "#444",
            "warning": "#FFA000",
            "error": "#D32F2F"
        }
        return colors.get(self.type, "#444")

    def get_text_color(self):
        """Get text color based on notification type"""
        colors = {
            "info": "white",
            "warning": "black",
            "error": "white"
        }
        return colors.get(self.type, "white")

    def slide_in(self):
        """Animates the notification sliding in from the left"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)

        # Get the main window's position
        main_window_pos = self.parent.mapToGlobal(QPoint(0, 0))
        notification_x = main_window_pos.x() + 20  # Add some padding
        notification_y = main_window_pos.y() + self.manager.base_y  # Use base_y for vertical position

        # Starting geometry (slightly off-screen to the left)
        start_geom = QRect(notification_x - 50, notification_y, self.width(), self.height())  # Start 50px off-screen
        end_geom = QRect(notification_x, notification_y, self.width(), self.height())

        self.animation.setStartValue(start_geom)
        self.animation.setEndValue(end_geom)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def move_to(self, y):
        """Moves the notification to a new Y position with animation"""
        if self.animation and self.animation.state() == QPropertyAnimation.Running:
            self.animation.stop()

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)

        # Get the main window's position
        main_window_pos = self.parent.mapToGlobal(QPoint(0, 0))
        notification_x = main_window_pos.x() + 20  # Add some padding
        notification_y = main_window_pos.y() + y  # Use the provided Y offset

        # Create geometries for the animation
        start_geom = self.geometry()
        end_geom = QRect(notification_x, notification_y, self.width(), self.height())

        self.animation.setStartValue(start_geom)
        self.animation.setEndValue(end_geom)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def should_remove(self):
        """Determines if it's time for this notification to be removed"""
        # Remove after 5 seconds
        return self.create_time.elapsed() >= 5000