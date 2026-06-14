import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import re
import datetime
import calendar
import random
import math
from models import UserSession, User, CarBuilder, Database
from patterns import build_security_chain, PaymentProxy, CarNotifier, RenterObserver

def theme(root):
    style = ttk.Style(root)
    style.theme_use('clam')
    
    backgroundColor = "#f8f9fa"
    primary = "#2980b9"
    primaryHover = "#3498db"
    textColor = "#2c3e50"
    
    root.configure(bg=backgroundColor)
    
    style.configure("TFrame", background=backgroundColor)
    
    #Strictly bind to named fonts so the zoom engine catches them all
    style.configure("TLabel", background=backgroundColor, foreground=textColor, font="TkDefaultFont")
    style.configure("Header.TLabel", font="TkHeadingFont", foreground=primary)
    
    style.configure("TButton",
                    font="TkDefaultFont", 
                    background=primary, 
                    foreground="white", 
                    borderwidth=0, 
                    padding=10)
    style.map("TButton", background=[("active", primaryHover)])
    
    #Inputs and Dropdowns
    style.configure("TCombobox", padding=5, font="TkDefaultFont")
    style.configure("TEntry", padding=5, font="TkDefaultFont", fieldbackground="white")
    
    #Clean Notebook Tabs
    style.configure("TNotebook", background=backgroundColor, borderwidth=0)
    style.configure("TNotebook.Tab", font="TkDefaultFont", padding=[15, 8], background="#e9ecef", foreground=textColor, borderwidth=0)
    style.map("TNotebook.Tab", background=[("selected", primary)], foreground=[("selected", "white")])
    
    #Professional Treeview
    style.configure("Treeview", font="TkTextFont", rowheight=30, background="white", fieldbackground="white", borderwidth=0)
    style.configure("Treeview.Heading", font="TkDefaultFont", background="#e9ecef", foreground=textColor, padding=5)


class Mediator:
    def chooseFrame(self, sender, event, data=None): pass

class DriveShareMediator(Mediator):
    #Concrete Mediator managing UI frame transitions and interactions.
    def __init__(self, root):
        self.root = root
        theme(self.root)
        self.frames = {}
        self.current_frame = None
        self.on_frame_change = None 

    def addFrame(self, name, frame):
        self.frames[name] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def chooseFrame(self, sender, event, data=None):
        if event == "GO_TO_REGISTER":
            self.showFrame("RegisterFrame")
        elif event == "GO_TO_LOGIN":
            self.showFrame("LoginFrame")
        elif event == "LOGIN_SUCCESS":
            self.frames["DashboardFrame"].refresh_ui()
            self.showFrame("DashboardFrame")
        elif event == "LOGOUT":
            UserSession().logout()
            self.showFrame("LoginFrame")

    def showFrame(self, name):
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()
            self.current_frame = frame
            if self.on_frame_change:
                self.on_frame_change()


class LoginFrame(ttk.Frame):
    def __init__(self, parent, mediator):
        super().__init__(parent, padding=40)
        self.mediator = mediator
        # Center the frame content perfectly
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.build_ui()

    def build_ui(self):
        container = ttk.Frame(self)
        container.grid(row=1, column=0)
        
        ttk.Label(container, text="DriveShare", style="Header.TLabel").pack(pady=(0, 20))
        
        ttk.Label(container, text="Username:").pack(anchor="w")
        self.user_entry = ttk.Entry(container, width=30)
        self.user_entry.pack(pady=5)
        
        ttk.Label(container, text="Password:").pack(anchor="w")
        self.pass_entry = ttk.Entry(container, show="*", width=30)
        self.pass_entry.pack(pady=5)
        
        ttk.Button(container, text="Login", command=self.login, width=28).pack(pady=(20, 10))
        ttk.Button(container, text="Register New Account", command=lambda: self.mediator.chooseFrame(self, "GO_TO_REGISTER"), width=28).pack(pady=5)
        
        forgot_lbl = tk.Label(container, text="Forgot Password?", fg="#3498db", bg="#f8f9fa", cursor="hand2", font="TkDefaultFont")
        forgot_lbl.pack(pady=15)
        forgot_lbl.bind("<Button-1>", lambda e: self.recover_password())

    def login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        user = Database.users.get(username)
        
        if user and user.password == password:
            UserSession().login(user)
            self.mediator.chooseFrame(self, "LOGIN_SUCCESS")
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def recover_password(self):
        username = self.user_entry.get().strip()
        user = Database.users.get(username)
        if not user:
            messagebox.showerror("Error", "Enter a valid username first to recover password.")
            return
            
        ans1 = simpledialog.askstring("Security", "Favorite color?")
        ans2 = simpledialog.askstring("Security", "Pet's name?")
        ans3 = simpledialog.askstring("Security", "Birth city?")
        
        chain = build_security_chain()
        if chain.handle(user, [ans1 or "", ans2 or "", ans3 or ""]):
            messagebox.showinfo("Success", f"Verification passed! Your password is: {user.password}")
            user.log_event("Password recovered", "green")
            Database.save()  
        else:
            messagebox.showerror("Failed", "Security answers incorrect.")


class RegisterFrame(ttk.Frame):
    def __init__(self, parent, mediator):
        super().__init__(parent, padding=40)
        self.mediator = mediator
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.build_ui()

    def build_ui(self):
        container = ttk.Frame(self)
        container.grid(row=1, column=0)
        
        ttk.Label(container, text="Create Account", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        self.entries = {}
        fields = ["Username", "Password", "Email", "Q1: Favorite Color", "Q2: Pet's Name", "Q3: Birth City"]
        for i, field in enumerate(fields):
            ttk.Label(container, text=field).grid(row=i+1, column=0, sticky="e", padx=10, pady=8)
            entry = ttk.Entry(container, show="*" if field == "Password" else "", width=25)
            entry.grid(row=i+1, column=1, pady=8)
            self.entries[field] = entry
            
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="Register", command=self.register, width=15).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Back", command=lambda: self.mediator.chooseFrame(self, "GO_TO_LOGIN"), width=15).grid(row=0, column=1, padx=10)

    def is_valid_email(self, email):
        match = re.match(r"^[^@\.\s]{2,}@[^@\.\s]{2,}\.[a-zA-Z]{2,}$", email)
        return bool(match)

    def register(self):
        vals = {f: self.entries[f].get().strip() for f in self.entries}
        if any(not v for v in vals.values()):
            messagebox.showwarning("Warning", "All fields are required.")
            return
        if vals["Username"] in Database.users:
            messagebox.showerror("Error", "Username already exists.")
            return
        if not self.is_valid_email(vals["Email"]):
            messagebox.showerror("Error", "Invalid email format. E.g., john@gmail.com")
            return

        new_user = User(vals["Username"], vals["Password"], vals["Email"], 
                        vals["Q1: Favorite Color"], vals["Q2: Pet's Name"], vals["Q3: Birth City"], display_name=vals["Username"].title())
        Database.users[new_user.username] = new_user
        Database.save()  
        messagebox.showinfo("Success", "Registration successful! You may now log in.")
        self.mediator.chooseFrame(self, "GO_TO_LOGIN")


class DashboardFrame(ttk.Frame):
    def __init__(self, parent, mediator):
        super().__init__(parent, padding=10)
        self.mediator = mediator
        
        # Header area for dynamic stretching and Clock
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(self.header_frame, text="DriveShare Dashboard", style="Header.TLabel").pack(side="left", padx=10)
        
        # Custom Canvas Analog Clock
        self.clock_canvas = tk.Canvas(self.header_frame, width=70, height=70, bg="#f8f9fa", highlightthickness=0)
        self.clock_canvas.pack(side="right", padx=10)
        self.draw_analog_clock()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Tab Frames
        self.rent_tab = ttk.Frame(self.notebook, padding=15)
        self.host_tab = ttk.Frame(self.notebook, padding=15)
        self.manage_tab = ttk.Frame(self.notebook, padding=15)
        self.inbox_tab = ttk.Frame(self.notebook, padding=15)
        self.calendar_tab = ttk.Frame(self.notebook, padding=15)

        self.notebook.add(self.rent_tab, text="Rent a Car")
        self.notebook.add(self.host_tab, text="Host a Car")
        self.notebook.add(self.manage_tab, text="Manage Listings")
        self.notebook.add(self.inbox_tab, text="Inbox & Profile")
        self.notebook.add(self.calendar_tab, text="Dynamic Calendar")

        self.build_host_tab()
        self.build_rent_tab()
        self.build_manage_tab()
        
        ttk.Button(self, text="Log Out Securely", command=lambda: self.mediator.chooseFrame(self, "LOGOUT")).pack(pady=15)

    def draw_analog_clock(self):
        """Native drawing of an analog clock using math (12hr format)."""
        self.clock_canvas.delete("all")
        
        cx, cy, r = 35, 35, 30
        self.clock_canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#bdc3c7", width=2, fill="white")
        
        # Tick marks
        for i in range(12):
            angle = math.radians(i * 30)
            inner_r = r - 5
            self.clock_canvas.create_line(cx + inner_r*math.cos(angle), cy + inner_r*math.sin(angle),
                                          cx + r*math.cos(angle), cy + r*math.sin(angle), fill="#bdc3c7")
        
        now = datetime.datetime.now()
        
        sec_angle = math.radians(now.second * 6 - 90)
        min_angle = math.radians(now.minute * 6 - 90)
        hour_angle = math.radians((now.hour % 12) * 30 + (now.minute / 2) - 90)
        
        # Draw Hands
        hx, hy = cx + r * 0.5 * math.cos(hour_angle), cy + r * 0.5 * math.sin(hour_angle)
        self.clock_canvas.create_line(cx, cy, hx, hy, width=3, fill="#2c3e50")
        
        mx, my = cx + r * 0.75 * math.cos(min_angle), cy + r * 0.75 * math.sin(min_angle)
        self.clock_canvas.create_line(cx, cy, mx, my, width=2, fill="#34495e")
        
        sx, sy = cx + r * 0.85 * math.cos(sec_angle), cy + r * 0.85 * math.sin(sec_angle)
        self.clock_canvas.create_line(cx, cy, sx, sy, width=1, fill="#e74c3c")
        
        # Center dot
        self.clock_canvas.create_oval(cx-2, cy-2, cx+2, cy+2, fill="#2c3e50")
        
        self.after(1000, self.draw_analog_clock)

    def refresh_ui(self):
        if Database.cities and hasattr(self, 'city_combo'):
            if not self.city_combo.get():
                self.city_combo['values'] = Database.cities
                self.city_combo.set("Dearborn")
            if not self.filter_city.get():
                self.filter_city['values'] = Database.cities
                self.filter_city.set("Dearborn")
            
        self.refresh_rent_tab()
        self.refresh_inbox()
        self.refresh_manage_tab()
        self.refresh_calendar()

    # --- MANAGE LISTINGS TAB ---
    def build_manage_tab(self):
        self.manage_tab.grid_rowconfigure(1, weight=1)
        self.manage_tab.grid_columnconfigure(0, weight=1)
        
        ttk.Label(self.manage_tab, text="Your Hosted Vehicles", style="Header.TLabel").grid(row=0, column=0, pady=(0,10))
        
        self.manage_listbox = tk.Listbox(self.manage_tab, font="TkTextFont", bg="white", relief="flat", borderwidth=1, highlightbackground="#dcdde1")
        self.manage_listbox.grid(row=1, column=0, sticky="nsew", pady=5)
        
        f = ttk.Frame(self.manage_tab)
        f.grid(row=2, column=0, pady=15)
        ttk.Label(f, text="New Price ($):").grid(row=0, column=0)
        self.update_price_entry = ttk.Entry(f, width=10)
        self.update_price_entry.grid(row=0, column=1, padx=10)
        ttk.Button(f, text="Update Price", command=self.update_price).grid(row=0, column=2, padx=5)
        ttk.Button(f, text="Toggle Availability", command=self.toggle_avail).grid(row=0, column=3, padx=5)

    def refresh_manage_tab(self):
        self.manage_listbox.delete(0, tk.END)
        user = UserSession().get_user()
        if not user: return
        for i, car in enumerate(user.listed_cars):
            status = "Available" if car.is_available else "Unavailable / Rented"
            self.manage_listbox.insert(tk.END, f"{i + 1}: {car.model} ({car.location}) | ${car.price}/day | {status}")

    def update_price(self):
        selection = self.manage_listbox.curselection()
        if not selection: return
        user = UserSession().get_user()
        car = user.listed_cars[selection[0]]
        try:
            new_p = float(self.update_price_entry.get())
            car.price = new_p
            CarNotifier.notify_watchers(car, "Price Drop", f"Price updated to ${new_p}")
            Database.save() 
            messagebox.showinfo("Updated", f"Price updated to ${new_p}")
            self.refresh_manage_tab()
            self.refresh_rent_tab()
        except ValueError:
            messagebox.showerror("Error", "Invalid price entered.")

    def toggle_avail(self):
        selection = self.manage_listbox.curselection()
        if not selection: return
        user = UserSession().get_user()
        car = user.listed_cars[selection[0]]
        
        # 100% Guaranteed Fee Trigger: Triggers ANY time an unavailable car is pulled back early
        if not car.is_available:
            confirm = messagebox.askyesno(
                "Cancellation Warning",
                f"WARNING: The {car.model} is currently marked as rented/unavailable.\n\n"
                "Canceling this active rental early will incur a Customer Inconvenience DriveShare Platform Fee of $89.99.\n\n"
                "Do you wish to proceed and cancel the rental?"
            )
            if confirm:
                # Issue the exact requested Penalty Charge
                user.balance -= 89.99
                user.receive_message("Penalty Charge", "Customer Inconvenience Fee Initiated: -$89.99 for early cancellation.")
                user.remove_event("Expected return", car.return_date)
                
                # Notify Renter (if there was an actual user booked)
                if car.current_renter:
                    car.current_renter.receive_message("Rental Canceled", f"The owner canceled your rental for the {car.model}.")
                
                # Reset Status
                car.current_renter = None
                car.return_date = None
                car.is_available = True
                CarNotifier.notify_watchers(car, "Car Available", f"{car.model} is now available again!")
                
                Database.save()
                self.refresh_manage_tab()
                self.refresh_rent_tab()
                self.refresh_calendar()
                self.refresh_inbox()
            return

        # Simulating a Rental: Toggling to Unavailable
        car.is_available = False
        days = car.max_days
        today = datetime.date.today()
        return_date = today + datetime.timedelta(days=days)
        car.return_date = return_date
        
        # Log to calendar and simulate the exact Host Notification Email requested!
        user.log_event(f"Marked {car.model} unavailable", "green", today)
        user.log_event(f"Expected return for {car.model}", "green", return_date)
        user.receive_message("Vehicle Rented Successfully", f"Great news! Your {car.model} was successfully rented out for {days} days.")

        Database.save()  
        self.refresh_manage_tab()
        self.refresh_rent_tab()
        self.refresh_calendar()
        self.refresh_inbox()

    # --- HOST TAB ---
    def build_host_tab(self):
        self.host_tab.grid_columnconfigure(0, weight=1)
        self.host_tab.grid_columnconfigure(3, weight=1)
        
        container = ttk.Frame(self.host_tab)
        container.grid(row=0, column=1, pady=20)
        
        ttk.Label(container, text="List Your Vehicle", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0,20))
        
        self.host_entries = {}
        fields = ["Make/Model", "Year", "Mileage", "Price per Day ($)"]
        for i, field in enumerate(fields):
            ttk.Label(container, text=field).grid(row=i+1, column=0, sticky="e", padx=10, pady=10)
            ent = ttk.Entry(container, width=30)
            ent.grid(row=i+1, column=1, pady=10)
            self.host_entries[field] = ent
        
        ttk.Label(container, text="City").grid(row=5, column=0, sticky="e", padx=10, pady=10)
        self.city_combo = ttk.Combobox(container, values=[], state="readonly", width=28)
        self.city_combo.grid(row=5, column=1, pady=10)

        ttk.Label(container, text="Max Duration (Days)").grid(row=6, column=0, sticky="e", padx=10, pady=10)
        self.days_combo = ttk.Combobox(container, values=list(range(1, 15)), state="readonly", width=28)
        self.days_combo.set("14")
        self.days_combo.grid(row=6, column=1, pady=10)

        ttk.Button(container, text="Publish Listing", command=self.list_car, width=35).grid(row=7, column=0, columnspan=2, pady=30)

    def list_car(self):
        user = UserSession().get_user()
        try:
            builder = CarBuilder()
            car = (builder.set_model(self.host_entries["Make/Model"].get())
                          .set_year(self.host_entries["Year"].get())
                          .set_mileage(int(self.host_entries["Mileage"].get()))
                          .set_location(self.city_combo.get())
                          .set_price(float(self.host_entries["Price per Day ($)"].get()))
                          .set_owner(user)
                          .build())
            car.max_days = int(self.days_combo.get())
            Database.cars.append(car)
            user.listed_cars.append(car)
            
            user.receive_message("Listing Created", f"You Hosted a Car on DriveShare!\n{car.model} is now live.")
            CarNotifier.notify_watchers(car, "New Car Listed", "Now available for rent!")
            
            Database.save()  
            messagebox.showinfo("Success", "Car listed successfully!")
            self.refresh_rent_tab()
            self.refresh_manage_tab()
            self.refresh_inbox()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")

    # --- RENT TAB ---
    def build_rent_tab(self):
        self.visible_cars = []  
        self.rent_tab.grid_rowconfigure(1, weight=1)
        self.rent_tab.grid_columnconfigure(0, weight=1)
        
        f_top = ttk.Frame(self.rent_tab)
        f_top.grid(row=0, column=0, pady=10)
        
        ttk.Label(f_top, text="Filter by City:").grid(row=0, column=0, padx=5)
        self.filter_city = ttk.Combobox(f_top, values=[], state="readonly", width=25)
        self.filter_city.grid(row=0, column=1, padx=5)
        self.filter_city.bind("<<ComboboxSelected>>", lambda e: self.refresh_rent_tab(shuffle=False))

        ttk.Label(f_top, text="City Starts With:").grid(row=0, column=2, padx=15)
        alpha = [chr(i) for i in range(65, 91)]
        self.alpha_combo = ttk.Combobox(f_top, values=alpha, state="readonly", width=5)
        self.alpha_combo.grid(row=0, column=3, padx=5)
        self.alpha_combo.bind("<<ComboboxSelected>>", self.filter_by_alpha)

        # Configured to use TkTextFont so Zoom Engine controls it directly
        self.car_listbox = tk.Listbox(self.rent_tab, font="TkTextFont", bg="white", relief="flat", borderwidth=1, highlightbackground="#dcdde1")
        self.car_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        btn_frame = ttk.Frame(self.rent_tab)
        btn_frame.grid(row=2, column=0, pady=15)
        ttk.Button(btn_frame, text="Book Selected Vehicle", command=self.book_car).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Watch Car (Notify Me)", command=self.watch_car).grid(row=0, column=1, padx=10)
        ttk.Button(btn_frame, text="Refresh Listings", command=lambda: self.refresh_rent_tab(shuffle=True)).grid(row=0, column=2, padx=10)

    def filter_by_alpha(self, event):
        letter = self.alpha_combo.get()
        filtered = [c for c in Database.cities if c.startswith(letter)]
        self.filter_city['values'] = filtered
        if filtered: 
            self.filter_city.set(filtered[0])
        else:
            self.filter_city.set("")  
        self.refresh_rent_tab(shuffle=False)

    def refresh_rent_tab(self, shuffle=False):
        city_filter = self.filter_city.get()
        user = UserSession().get_user()
        
        if not city_filter or not user:
            self.car_listbox.delete(0, tk.END)
            self.visible_cars = []
            return

        city_cars = [c for c in Database.cars if c.location == city_filter]
        
        if shuffle and random.random() < 0.3:
            # Smart shuffle strictly ignores cars owned by user OR actively rented out
            shuffle_pool = [c for c in city_cars if c.owner != user and c.current_renter is None]
            if len(shuffle_pool) > 0:
                for c in shuffle_pool: 
                    c.is_available = False
                new_avail = random.sample(shuffle_pool, min(int(len(shuffle_pool) * 0.66), len(shuffle_pool)))
                for c in new_avail: 
                    c.is_available = True
                    CarNotifier.notify_watchers(c, "Car Now Available", f"{c.model} is ready for rent!")
                Database.save()  

        self.car_listbox.delete(0, tk.END)
        self.visible_cars = city_cars  
        
        for i, car in enumerate(self.visible_cars):
            status = "Available" if car.is_available else "Unavailable"
            self.car_listbox.insert(tk.END, f"{i + 1}: {car} [Max: {car.max_days} Days] - [{status}]")

    def book_car(self):
        selection = self.car_listbox.curselection()
        if not selection: return
        
        idx = selection[0]
        car = self.visible_cars[idx]
        user = UserSession().get_user()

        if not car.is_available:
            messagebox.showerror("Unavailable", "This car is already rented.")
            return
        if car.owner == user:
            messagebox.showerror("Error", "You cannot rent your own car.")
            return

        days = simpledialog.askinteger("Booking Duration", f"How many days? (Max {car.max_days})", minvalue=1, maxvalue=car.max_days)
        if not days: return  

        total_price = car.price * days
        proxy = PaymentProxy()
        
        if proxy.processPayment(total_price, user, car.owner, car, days):
            car.is_available = False
            user.rental_history.append(car)
            Database.save()  
            messagebox.showinfo("Success", f"Booked {car.model} for {days} days!\nTotal: ${total_price:.2f}")
            self.refresh_rent_tab()
            self.refresh_calendar()
            self.refresh_inbox()

    def watch_car(self):
        selection = self.car_listbox.curselection()
        if not selection: return
        car = self.visible_cars[selection[0]]
        user = UserSession().get_user()
        observer = RenterObserver(user)
        CarNotifier.add_watcher(car, observer)
        Database.save() 
        messagebox.showinfo("Watching", f"You will receive notifications for the {car.model}.")

    # --- INBOX TAB ---
    def refresh_inbox(self):
        for widget in self.inbox_tab.winfo_children(): widget.destroy()
        user = UserSession().get_user()
        if not user: return

        self.inbox_tab.grid_rowconfigure(2, weight=1)
        self.inbox_tab.grid_columnconfigure(0, weight=1)

        # Profile Header
        header_text = f"Logged in as: {user.get_display_name()}    |    {user.email}    |    Wallet: ${user.balance:.2f}"
        ttk.Label(self.inbox_tab, text=header_text, style="Header.TLabel").grid(row=0, column=0, pady=10, sticky="w")
        
        # Professional App Treeview 
        columns = ("date", "subject")
        self.inbox_tree = ttk.Treeview(self.inbox_tab, columns=columns, show="headings", style="Treeview")
        self.inbox_tree.heading("date", text="Date Received")
        self.inbox_tree.heading("subject", text="Subject Line")
        self.inbox_tree.column("date", width=180, anchor="center")
        self.inbox_tree.column("subject", width=600)
        self.inbox_tree.grid(row=2, column=0, sticky="nsew", pady=5)

        for msg in user.messages:
            self.inbox_tree.insert("", tk.END, values=(msg['date'], msg['subject']))

        btn_frame = ttk.Frame(self.inbox_tab)
        btn_frame.grid(row=3, column=0, pady=15)
        ttk.Button(btn_frame, text="Read Selected Message", command=self.open_email).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Refresh Inbox", command=self.refresh_inbox).grid(row=0, column=1, padx=10)

    def open_email(self):
        selected = self.inbox_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a message to read.")
            return
            
        item = self.inbox_tree.item(selected[0])
        subject_clicked = item['values'][1]
        date_clicked = item['values'][0]
        
        user = UserSession().get_user()
        msg_obj = next((m for m in user.messages if m['subject'] == subject_clicked and m['date'] == date_clicked), None)
        if not msg_obj: return

        win = tk.Toplevel(self)
        win.title(msg_obj['subject'])
        win.geometry("550x400")
        win.configure(bg="#f8f9fa")
        
        ttk.Label(win, text=f"From: DriveShare\nDate: {msg_obj['date']}\nSubject: {msg_obj['subject']}", style="Header.TLabel").pack(anchor="w", padx=20, pady=15)
        
        txt = tk.Text(win, wrap="word", width=60, height=12, bg="white", relief="flat", font="TkTextFont", padx=10, pady=10)
        txt.insert("1.0", msg_obj['body'])
        txt.config(state="disabled")
        txt.pack(padx=20, pady=10, fill="both", expand=True)

    # --- DYNAMIC CALENDAR TAB ---
    def refresh_calendar(self):
        for widget in self.calendar_tab.winfo_children(): widget.destroy()
        user = UserSession().get_user()
        if not user: return
        
        self.calendar_tab.grid_rowconfigure(1, weight=1)
        self.calendar_tab.grid_columnconfigure(0, weight=1)

        f_top = ttk.Frame(self.calendar_tab)
        f_top.grid(row=0, column=0, pady=10)

        ttk.Label(f_top, text="Select Month:").grid(row=0, column=0, padx=5)
        
        start_date = user.creation_date.replace(day=1)
        months = []
        for i in range(12):
            m = (start_date.month + i - 1) % 12 + 1
            y = start_date.year + (start_date.month + i - 1) // 12
            months.append(f"{y}-{m:02d}")

        self.cal_month_combo = ttk.Combobox(f_top, values=months, state="readonly", width=15)
        self.cal_month_combo.set(datetime.date.today().strftime("%Y-%m"))
        self.cal_month_combo.grid(row=0, column=1, padx=5)
        self.cal_month_combo.bind("<<ComboboxSelected>>", lambda e: self.draw_calendar_grid())

        self.cal_grid_frame = ttk.Frame(self.calendar_tab)
        self.cal_grid_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.draw_calendar_grid()

    def open_calendar_day(self, curr_date):
        user = UserSession().get_user()
        events = user.calendar_events.get(curr_date, [])
        win = tk.Toplevel(self)
        win.title(f"Details for {curr_date}")
        win.geometry("350x250")
        win.configure(bg="#f8f9fa")
        if not events:
            ttk.Label(win, text="No events for this day.").pack(pady=20)
        else:
            for ev in events:
                ttk.Label(win, text=ev['text'], foreground=ev['color']).pack(anchor="w", padx=20, pady=10)

    def draw_calendar_grid(self):
        for w in self.cal_grid_frame.winfo_children(): w.destroy()
        user = UserSession().get_user()
        
        sel = self.cal_month_combo.get().split("-")
        y, m = int(sel[0]), int(sel[1])
        
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, d in enumerate(days):
            ttk.Label(self.cal_grid_frame, text=d, font="TkHeadingFont").grid(row=0, column=i, padx=5, pady=5)
            self.cal_grid_frame.grid_columnconfigure(i, weight=1)
            
        cal = calendar.monthcalendar(y, m)
        for r_idx, row in enumerate(cal):
            # Dynamic stretching so the boxes scale smoothly with window/zoom sizes
            self.cal_grid_frame.grid_rowconfigure(r_idx+1, weight=1)
            for c_idx, day in enumerate(row):
                if day == 0: continue
                
                f = tk.Frame(self.cal_grid_frame, borderwidth=1, relief="solid", bg="white")
                f.grid(row=r_idx+1, column=c_idx, padx=2, pady=2, sticky="nsew")
                
                curr_date = datetime.date(y, m, day)
                lbl = tk.Label(f, text=str(day), anchor="nw", bg="white", font="TkDefaultFont")
                lbl.pack(fill="x")
                
                f.bind("<Button-1>", lambda e, d=curr_date: self.open_calendar_day(d))
                lbl.bind("<Button-1>", lambda e, d=curr_date: self.open_calendar_day(d))
                
                if curr_date in user.calendar_events:
                    for ev in user.calendar_events[curr_date]:
                        ev_lbl = tk.Label(f, text=ev["text"], fg=ev["color"], font="TkDefaultFont", bg="white", wraplength=100)
                        ev_lbl.pack(anchor="w")
                        ev_lbl.bind("<Button-1>", lambda e, d=curr_date: self.open_calendar_day(d))