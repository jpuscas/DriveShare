import random
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

from models import Database, User, CarBuilder
from ui import Mediator, DriveShareMediator, LoginFrame, RegisterFrame, DashboardFrame



def SetDummyData():
#List of Ddummy Cities
    dummyCities = {
        "Dearborn", "Rochester Hills", "Bloomfield Hills", "Birmingham", "Troy", "Ann Arbor"
    }
    Database.cities = sorted(list(set(dummyCities)))
    dummyRenterAccount = User("Renter", "password", "Renter@gmail.com", "Red", "Buddy", "Rochester Hills", "Renter")
    Database.users[dummyRenterAccount.username] = dummyRenterAccount

#List of dummy cars
    dummyCars = [
        ("Ford Bronco", "2022"), ("Ford Bronco", "2024"), ("Ford Mustang", "2025"), ("Ford F150", "2020"),
        ("Kia Soul ", "2019"), ("Honda Civic", "2010"), ("Honda Accord", "2018"), ("Subaru Forester", "2021"),
        ("Subaru WRX", "2017"), ("Jeep Wrangler", "2016"), ("Mazda 3", "2022"), ("Mazda CX5", "2020")
    ]
#List of dummy owners
    dummyOwners = [
        "John James", "James Smith", "David Jones", "Albert Einstein", "Lionel Messi", "Cristiano Ronaldo",
        "Ryan Reynolds", "Tom Brady", "Cade Cunningham", " Lebron James", "Buzz Lightyear", "Christian Pulisic"
    ]
#Creating dummy car owners
    Users = []
    for name in dummyOwners:
        user = User(
            username=name.replace(" ", "").lower(),
            password="password",
            email=f"{name.split()[0].lower()}@gmail.com",
            sq1="purple",
            sq2="bear",
            sq3="detroit",
            display_name=name
        )
        user.balance = random.randint(100, 5000)
        Users.append(user)
        Database.users[user.username] = user

#Building five random cars per city with random price and mileage
    builder = CarBuilder()
    CarsList = []
    for city in dummyCities:
        OwnersList = random.sample(Users, 5)
        SelectedCarsList = random.sample(dummyCars, 5)
        for i in range(5):
            model, year = SelectedCarsList[i]
            car = (builder.set_owner(OwnersList[i])
                .set_model(model)
                .set_year(year)
                .set_price(round(random.uniform(40.0, 100.0), 2))
                .set_location(city)
                .set_mileage(int(random.uniform(0, 50000)))
                .build()
            )
            car.max_days = random.randint(1, 15)
            car.is_available = False
            CarsList.append(car)
            OwnersList[i].listed_cars.append(car)
            Database.cars.append(car)

#randomly setting the availability of the cars we built
        for car in random.sample(CarsList, 3):
            car.is_available = True

    Database.save()

#The main function for the app that the runnable main function uses
class DriveShareApp:
    def __init__(self):
        #use dummyData if Database has nothing
        if not Database.load():
            SetDummyData()

        self.TKSetUp()
#Attempting to set the frames to mediator
        try:
            mediator = DriveShareMediator(self.root)
            mediator.addFrame("LoginFrame", LoginFrame(self.root, mediator))
            mediator.addFrame("RegisterFrame", RegisterFrame(self.root, mediator))
            mediator.addFrame("DashboardFrame", DashboardFrame(self.root, mediator))
        except Exception:
            print("Something went wrong setting up Frames")
#Calling the magnifier
        try:
            self.setMagnifier()
            mediator.on_frame_change = self.magnifier_frame.lift
        except Exception:
            print("Something went wrong setting up Magnifier")
#Taking to LoginFrame as that is the first place the app should take you
        try:
            mediator.showFrame("LoginFrame")
        except Exception:
            print("Something went wrong showing frame")

#Setting the magnifier for the zoom functionality
    def setMagnifier(self):
        self.magnifier_frame = tk.Frame(
            self.root,
            bg="#ffffff",
            relief="flat",
            borderwidth=1,
            highlightbackground="#dcdde1",
            highlightthickness=1
        )
        self.magnifier_frame.place(
            relx=0.01,
            rely=0.98,
            anchor='sw'
        )
#Setting the label for the zoom functionality
        ttk.Label(
            self.magnifier_frame,
            text="Zoom",
            font="TkDefaultFont",
            background="#ffffff",
        ).pack(
            side="left",
            padx=(5, 5),
            pady=(5, 5)
        )
#setting the button for zoom in
        tk.Button(
            self.magnifier_frame,
            text="+",
            width=3,
            bg="#e9ecef",
            relief="flat",
            cursor="hand2",
            command=self.zoomIn
        ).pack(
            side="left",
            padx=(2, 10),
            pady=5
        )
#Setting the button for zoom out
        tk.Button(
            self.magnifier_frame,
            text="-",
            width=3,
            bg="#e9ecef",
            relief="flat",
            cursor="hand2",
            command=self.zoomOut
        ).pack(
            side="left",
            padx=2,
            pady=5
        )

#Deciding the new zoomed in size
    def zoomIn(self):
        #go through each font and scale up
        currentSize = self.fonts["default"].cget("size")
        if currentSize <= self.base_size + 8:
            self.applyZoom(currentSize + 1)

#Deciding the new zoomed out size
    def zoomOut(self):
        # go through each font and scale down
        currentSize = self.fonts["default"].cget("size")
        if currentSize >= max(8, self.base_size - 3):
            self.applyZoom(currentSize - 1)

#Doing the action of zoom
    def applyZoom(self, new_size):
        for name, f in self.fonts.items():
            if name == "heading":
                f.configure(size=new_size + 6)
            else:
                f.configure(size=new_size)

#Setup for the TKinter
    def TKSetUp(self):
        self.root = tk.Tk()
        self.root.title("DriveShare - Peer-to-Peer Car Rental")
        self.root.geometry("1100x800")

        # App Background (bg)
        self.root.configure(bg="#f8f9fa")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Setting Fonts
        self.fonts = {
            "default": tkfont.nametofont("TkDefaultFont"),
            "text": tkfont.nametofont("TkTextFont"),
            "fixed": tkfont.nametofont("TkFixedFont"),
            "heading": tkfont.nametofont("TkHeadingFont"),
            "menu": tkfont.nametofont("TkMenuFont"),
            "caption": tkfont.nametofont("TkCaptionFont"),
            "smallcaption": tkfont.nametofont("TkSmallCaptionFont"),
            "icon": tkfont.nametofont("TkIconFont"),
            "tooltip": tkfont.nametofont("TkTooltipFont")
        }

        self.base_size = 10
        for name, f in self.fonts.items():
            if name == "heading":
                f.configure(size=self.base_size + 6, family="Segoe UI", weight="bold")
            else:
                f.configure(size=self.base_size, family="Segoe UI")
        return self

    def run(self):
        self.root.mainloop()

#Runnable Main app function
if __name__ == "__main__":
    app = DriveShareApp()
    app.run()