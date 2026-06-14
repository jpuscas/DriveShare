import datetime
import uuid
import pickle
import os

class UserSession:
    """Singleton pattern to manage the user's session securely."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserSession, cls).__new__(cls)
            cls._instance.current_user = None
        return cls._instance

    def login(self, user):
        self.current_user = user
        # Log the login event to the user's calendar (Green for owner/general events)
        user.log_event("Logged in", "green")
        Database.save()  # Save state on login

    def logout(self):
        self.current_user = None

    def is_logged_in(self):
        return self.current_user is not None

    def get_user(self):
        return self.current_user


class User:
    """Represents a User in the DriveShare system."""
    def __init__(self, username, password, email, sq1, sq2, sq3, display_name=""):
        self.username = username
        self.password = password
        self.email = email
        self.security_answers = [sq1, sq2, sq3]
        self.messages = [] 
        self.balance = 1000.0  # Simulated starting balance
        self.rental_history = []
        self.listed_cars = []
        
        # If no display name is provided, fallback to title-casing the username
        self.display_name = display_name if display_name else username.title()
        
        # Calendar events tracking
        self.creation_date = datetime.date.today()
        self.calendar_events = {}  # Format: {date_object: [{"text": description, "color": red/green}]}
        
        # Initial logs and welcome email
        self.log_event("Account Created", "green", self.creation_date)
        self.receive_message(
            "Welcome to DriveShare!", 
            "Thank you for joining DriveShare.\nWe are excited to have you.\n\n- DriveShare Team"
        )

    def get_display_name(self):
        """Fetches the explicitly formatted name (e.g., 'Kenneth Cook')."""
        name = getattr(self, 'display_name', self.username.title())
        return name if name else self.username.title()

    def receive_message(self, subject, body):
        """Stores a message dictionary for the structured Inbox."""
        msg = {
            "id": str(uuid.uuid4()), # Gives every email a unique ID for UI handling
            "subject": subject,
            "body": body,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.messages.insert(0, msg) # Insert at beginning so newest is always first
        Database.save() # Persist whenever a message is received

    def log_event(self, text, color, date_obj=None):
        """Logs a color-coded event to the user's calendar."""
        if date_obj is None:
            date_obj = datetime.date.today()
            
        if date_obj not in self.calendar_events:
            self.calendar_events[date_obj] = []
            
        self.calendar_events[date_obj].append({"text": text, "color": color})
        Database.save()

    def remove_event(self, partial_text, date_obj):
        """Removes a specific event from the calendar (used for early cancellations)."""
        if date_obj in self.calendar_events:
            self.calendar_events[date_obj] = [
                ev for ev in self.calendar_events[date_obj] 
                if partial_text not in ev["text"]
            ]
            Database.save()


class Car:
    """Represents a Car listing."""
    def __init__(self):
        self.id = str(uuid.uuid4())  # Hidden unique ID to fix listbox indexing
        self.model = ""
        self.year = ""
        self.mileage = 0
        self.location = "Dearborn"
        self.price = 0.0
        self.owner = None
        self.is_available = True
        self.watchers = []
        self.max_days = 14  # Max rental duration limit
        
        # Explicit tracking for active rentals
        self.current_renter = None
        self.return_date = None

    def __str__(self):
        return f"{self.year} {self.model} - {self.location} (${self.price}/day)"


class CarBuilder:
    """Builder pattern to construct car listing objects cleanly."""
    def __init__(self):
        self.reset()

    def reset(self):
        """Creates a fresh, unique Car object in memory."""
        self.car = Car()

    def set_model(self, model):
        self.car.model = model
        return self

    def set_year(self, year):
        self.car.year = year
        return self

    def set_mileage(self, mileage):
        self.car.mileage = mileage
        return self

    def set_location(self, location):
        self.car.location = location
        return self

    def set_price(self, price):
        self.car.price = price
        return self

    def set_owner(self, owner):
        self.car.owner = owner
        return self

    def build(self):
        """Returns the built car and immediately resets for the next one."""
        built_car = self.car
        self.reset()  
        return built_car


class Database:
    """Mock Database handling runtime state and local file persistence."""
    users = {}
    cars = []
    cities = [] 
    
    _FILE_NAME = "driveshare_data.pkl"

    @classmethod
    def save(cls):
        """Saves current memory to a local file so logins and cars are remembered."""
        with open(cls._FILE_NAME, "wb") as f:
            pickle.dump({
                "users": cls.users,
                "cars": cls.cars,
                "cities": cls.cities
            }, f)

    @classmethod
    def load(cls):
        """Loads memory from local file if it exists."""
        if os.path.exists(cls._FILE_NAME):
            try:
                with open(cls._FILE_NAME, "rb") as f:
                    data = pickle.load(f)
                    cls.users = data.get("users", {})
                    cls.cars = data.get("cars", [])
                    cls.cities = data.get("cities", [])
                return True
            except:
                return False # Failsafe if pickle is corrupted
        return False