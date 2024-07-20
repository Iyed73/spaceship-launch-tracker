from enum import Enum


class EventCategory(Enum):
    NEW_LAUNCH = "new launch"
    LAUNCH_UPDATE = "update launch"
    LAUNCH_DELETE = "delete launch"
    REMINDER = "reminder"
