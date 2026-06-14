import datetime

# --- OBSERVER PATTERN ---
class RenterObserver:
    """Observer interface for renters receiving notifications."""
    def __init__(self, user):
        self.user = user

    def update(self, subject, message):
        """Passes the notification payload directly to the user's Inbox logic."""
        self.user.receive_message(subject, message)


class CarNotifier:
    """Subject in the Observer pattern to notify renters of changes to watched cars."""
    @staticmethod
    def add_watcher(car, observer):
        # Prevent duplicate watcher entries
        if observer not in car.watchers:
            car.watchers.append(observer)

    @staticmethod
    def notify_watchers(car, subject, message):
        """Iterates through all watching users and fires their update method."""
        for observer in car.watchers:
            observer.update(subject, f"Update on {car.year} {car.model}: {message}")


# --- PROXY PATTERN ---
class PaymentSystem:
    """Interface for the Payment System"""
    def processPayment(self, amount, payer, payee, car, duration_days):
        raise NotImplementedError


class RealPaymentSystem(PaymentSystem):
    """The real payment processor that handles the actual transaction and side-effects."""
    def processPayment(self, amount, payer, payee, car, duration_days):
        #transfer funds from payer to payee
        payer.balance -= amount
        payee.balance += amount
        
        payer_name = payer.get_display_name()
        payee_name = payee.get_display_name()
        
        # 2. Dispatch digital receipts to the Inbox
        # Host Notification: Explicitly states the car is rented and for how long
        payee.receive_message(
            "Vehicle Rented Successfully",
            f"Great news! Your {car.model} was successfully rented by {payer_name} for {duration_days} days.\n"
            f"A payment of ${amount:.2f} has been added to your balance."
        )
        
        # Renter Notification: Confirms booking and payment sent
        payer.receive_message(
            "Payment Sent & Booking Confirmed",
            f"Payment of ${amount:.2f} sent to {payee_name} for {car.model}.\nBooking confirmed for {duration_days} days."
        )
        
        # 3. Update active Car Status
        car.current_renter = payer
        today = datetime.date.today()
        drop_off_date = today + datetime.timedelta(days=duration_days)
        car.return_date = drop_off_date
        
        # 4. Log rigorous Calendar Events for both parties
        # Renter logging: Last day to drop off (Red)
        payer.log_event(f"Drop off {car.model} by today", "red", drop_off_date)
        
        # Owner logging: Rented out today (Green), Expected Return Date (Green)
        payee.log_event(f"Rented out {car.model} to {payer_name}", "green", today)
        payee.log_event(f"Expected return: {car.model} from {payer_name}", "green", drop_off_date)
        
        return True


class PaymentProxy(PaymentSystem):
    """Proxy pattern to simulate secure payment interactions and verify funds before acting."""
    def __init__(self):
        self.real_system = RealPaymentSystem()

    def processPayment(self, amount, payer, payee, car, duration_days):
        # Acts as the security gatekeeper before hitting the real processing logic
        if payer.balance >= amount:
            return self.real_system.processPayment(amount, payer, payee, car, duration_days)
        else:
            payer.receive_message("Payment Failed", f"Insufficient funds to book the {car.model}.")
            return False


# --- CHAIN OF RESPONSIBILITY PATTERN ---
class SecurityQuestionHandler:
    """Base Handler for Chain of Responsibility."""
    def __init__(self, next_handler=None):
        self.next_handler = next_handler

    def handle(self, user, answers):
        if self.next_handler:
            return self.next_handler.handle(user, answers)
        return True


class Question1Handler(SecurityQuestionHandler):
    def handle(self, user, answers):
        # .strip() cleanly sanitizes the input so trailing spaces don't fail a user
        if user.security_answers[0].lower().strip() == answers[0].lower().strip():
            return super().handle(user, answers)
        return False


class Question2Handler(SecurityQuestionHandler):
    def handle(self, user, answers):
        if user.security_answers[1].lower().strip() == answers[1].lower().strip():
            return super().handle(user, answers)
        return False


class Question3Handler(SecurityQuestionHandler):
    def handle(self, user, answers):
        if user.security_answers[2].lower().strip() == answers[2].lower().strip():
            return super().handle(user, answers)
        return False


def build_security_chain():
    """Builds the chain of 3 security questions."""
    q3 = Question3Handler()
    q2 = Question2Handler(q3)
    q1 = Question1Handler(q2)
    return q1