Contributors
1. Idris Kabir - Data models, Database persistence (Pickle), Builder pattern, Dynamic Calendar.
2. Zaid Kabir - Business logic, Proxy/Observer/Chain patterns, Rent/Host interactive logic.
3. Jason Puscas - Application bootstrapper, Universal Zoom Engine, Mediator router, Dummy data, Flat UI styling.

Project Files:
1. patterns.py
2. ui.py
3. model.py
4. main_driveshare.pyw

How to use:
1. clone the repo to your IDE
2. run "python main_driveshare.pyw" in your terminal

Functions/Features

User Registration and Authentication:
Users can register on DriveShare using email and password authentication.
During registration, users must set three security questions (with answers).

Car Listing and Management (Owner):
Car owners can list their vehicles for short-term rental, providing details such as car model, year, mileage, availability calendar, pick up location and rental pricing.
Owners have the ability to manage their car listings, including updating availability and price
The system must prevent the same car from being rented by more than one renter for overlapping dates/times.

Search and Booking (Renter):
Renters can search for available cars based on location, date, and other preferences (your choice).
Renters can “watch” desired cars and receive notification when the car becomes available and/or rental prices drop to meet renter-defined specifications
Implement a booking system allowing renters to reserve a car for a specific period.

Messaging and Communication:
DriveShare includes a messaging system to facilitate communication between car owners and renters.
Send notifications for booking requests, confirmations, and important updates via email or in-app messages.

Payment:
Allow renters to make payment (A real payment is not required. A payment button with amount is enough, clicking on the button will change the balance and send notification to both owner and renter)

Implementation

User Authentication and Encryption:
Implements the Singleton pattern to manage the user's session securely.

Observer Pattern for Booking Notifications:
Applies the Observer pattern to notify renters if their watched cars meet their expectations.

Mediator Pattern for UI Components:
Implements the Mediator pattern to manage communication between different UI components, creating a cohesive and user-friendly interface.

Builder Pattern for Car Listing Creation:
Uses the Builder pattern to construct car listing objects with optional/variable attributes cleanly

Proxy Pattern for Payment Integration:
Uses the Proxy pattern to simulate secure interaction between DriveShare and the payment system.

Chain of Responsibility for Password Recovery:
Applies the Chain of Responsibility pattern to create a secure process (using three security questions to build the chain) for recovering a forgotten password.
