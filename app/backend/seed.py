"""
seed.py — Seeds the database with default accounts and demo fleet data.

Safe to run multiple times — checks for existing records before inserting.
Called automatically on app startup from main.py.

Default manager login:
  username: manager
  password: FleetManager2024!

Demo data includes 10 realistic trucks for RDT Inc. with varied
maintenance statuses (green/yellow/red) to showcase the dashboard.
"""

from datetime import date, timedelta
from sqlalchemy.orm import Session
from models import User, Truck, MaintenanceItem, IncidentReport, MileageLog, BriefingSettings
from models import MAINTENANCE_ITEM_TYPES, DEFAULT_INTERVALS
from auth import hash_password


def seed_users(db: Session):
    """Create the default manager account if it doesn't already exist."""
    if db.query(User).filter(User.username == "manager").first():
        return  # already seeded

    manager = User(
        username="manager",
        hashed_password=hash_password("FleetManager2024!"),
        full_name="Fleet Manager",
        role="manager",
    )
    db.add(manager)
    db.commit()
    print("✓ Seeded default manager account (username: manager)")


def seed_demo_fleet(db: Session):
    """
    Seed 10 demo trucks representing the RDT Inc. fleet.
    Each truck gets 9 maintenance item rows with realistic service history
    designed to show a mix of green, yellow, and red statuses on the dashboard.
    """
    if db.query(Truck).count() > 0:
        return  # fleet already seeded

    today = date.today()

    # Demo truck data — realistic makes/models for Utah waste management
    trucks_data = [
        {"number": "T-01", "make": "Mack",        "model": "LR Series",   "year": 2019, "type": "Garbage Truck",  "mileage": 87450},
        {"number": "T-02", "make": "Mack",        "model": "LR Series",   "year": 2020, "type": "Garbage Truck",  "mileage": 74200},
        {"number": "T-03", "make": "Peterbilt",   "model": "520",         "year": 2018, "type": "Garbage Truck",  "mileage": 112300},
        {"number": "T-04", "make": "Peterbilt",   "model": "520",         "year": 2021, "type": "Roll-Off",       "mileage": 56780},
        {"number": "T-05", "make": "Kenworth",    "model": "T880",        "year": 2017, "type": "Roll-Off",       "mileage": 134500},
        {"number": "T-06", "make": "Kenworth",    "model": "T880",        "year": 2022, "type": "Garbage Truck",  "mileage": 38900},
        {"number": "T-07", "make": "Mack",        "model": "TerraPro",    "year": 2019, "type": "Recycling",      "mileage": 95600},
        {"number": "T-08", "make": "International","model": "HV Series",  "year": 2020, "type": "Compactor",      "mileage": 68100},
        {"number": "T-09", "make": "Ford",        "model": "F-750",       "year": 2021, "type": "Service Truck",  "mileage": 44300},
        {"number": "T-10", "make": "Mack",        "model": "LR Series",   "year": 2023, "type": "Garbage Truck",  "mileage": 21500},
    ]

    # Maintenance history designed to create a mix of statuses:
    # - T-01, T-03, T-05: Some RED items (overdue) — will trigger dashboard alerts
    # - T-02, T-07: Some YELLOW items (due soon)
    # - T-06, T-10: Mostly GREEN (newer trucks, recently serviced)
    # Format: {item_type: (days_ago_serviced, mileage_ago_serviced)}
    # None means never serviced (shows as yellow)
    service_history = {
        "T-01": {
            "oil_change":           (200, 5200),   # RED — overdue by time and miles
            "transmission_fluid":   (400, 28000),  # YELLOW — due soon
            "brake_fluid":          (600, None),   # RED — overdue by time
            "coolant":              (300, 25000),  # GREEN
            "power_steering_fluid": (700, 45000),  # GREEN
            "wheel_alignment":      (380, 11500),  # YELLOW
            "brake_pads":           (500, 19000),  # YELLOW
            "tire_wear":            (200, 9800),   # YELLOW — due soon
            "windshield_wipers":    (400, None),   # GREEN
        },
        "T-02": {
            "oil_change":           (140, 4500),   # YELLOW
            "transmission_fluid":   (200, 20000),  # GREEN
            "brake_fluid":          (400, None),   # GREEN
            "coolant":              (350, 22000),  # GREEN
            "power_steering_fluid": (500, 40000),  # GREEN
            "wheel_alignment":      (300, 10000),  # GREEN
            "brake_pads":           (180, 17000),  # YELLOW
            "tire_wear":            (155, 9000),   # YELLOW
            "windshield_wipers":    (200, None),   # GREEN
        },
        "T-03": {
            "oil_change":           (210, 5100),   # RED
            "transmission_fluid":   (800, 31000),  # RED — overdue
            "brake_fluid":          (750, None),   # RED — overdue
            "coolant":              (750, 31000),  # RED — overdue
            "power_steering_fluid": (600, 44000),  # GREEN
            "wheel_alignment":      (400, 12500),  # RED — over mileage
            "brake_pads":           (300, 18000),  # YELLOW
            "tire_wear":            (190, 9600),   # YELLOW
            "windshield_wipers":    (380, None),   # GREEN
        },
        "T-04": {
            "oil_change":           (90, 4200),    # GREEN
            "transmission_fluid":   (300, 18000),  # GREEN
            "brake_fluid":          (300, None),   # GREEN
            "coolant":              (300, 18000),  # GREEN
            "power_steering_fluid": (400, 32000),  # GREEN
            "wheel_alignment":      (200, 9000),   # GREEN
            "brake_pads":           (200, 13000),  # GREEN
            "tire_wear":            (100, 5000),   # GREEN
            "windshield_wipers":    (200, None),   # GREEN
        },
        "T-05": {
            "oil_change":           (195, 5050),   # RED — just over
            "transmission_fluid":   (740, 30200),  # RED — just over
            "brake_fluid":          (740, None),   # RED
            "coolant":              (400, 28000),  # GREEN
            "power_steering_fluid": (800, 51000),  # RED — over mileage
            "wheel_alignment":      (370, 12100),  # RED
            "brake_pads":           (730, 20100),  # RED
            "tire_wear":            (185, 9800),   # YELLOW
            "windshield_wipers":    (370, None),   # GREEN
        },
        "T-06": {
            "oil_change":           (60, 3000),    # GREEN
            "transmission_fluid":   (200, 12000),  # GREEN
            "brake_fluid":          (200, None),   # GREEN
            "coolant":              (200, 12000),  # GREEN
            "power_steering_fluid": (200, 15000),  # GREEN
            "wheel_alignment":      (150, 6000),   # GREEN
            "brake_pads":           (150, 8000),   # GREEN
            "tire_wear":            (80, 3500),    # GREEN
            "windshield_wipers":    (150, None),   # GREEN
        },
        "T-07": {
            "oil_change":           (160, 4700),   # YELLOW
            "transmission_fluid":   (350, 24000),  # GREEN
            "brake_fluid":          (350, None),   # GREEN
            "coolant":              (350, 24000),  # GREEN
            "power_steering_fluid": (500, 40000),  # GREEN
            "wheel_alignment":      (310, 10500),  # YELLOW
            "brake_pads":           (600, 19500),  # YELLOW
            "tire_wear":            (165, 8700),   # YELLOW
            "windshield_wipers":    (310, None),   # GREEN
        },
        "T-08": {
            "oil_change":           (100, 4000),   # GREEN
            "transmission_fluid":   (250, 16000),  # GREEN
            "brake_fluid":          (250, None),   # GREEN
            "coolant":              (250, 16000),  # GREEN
            "power_steering_fluid": (400, 30000),  # GREEN
            "wheel_alignment":      (200, 8000),   # GREEN
            "brake_pads":           (200, 12000),  # GREEN
            "tire_wear":            (120, 6000),   # GREEN
            "windshield_wipers":    (200, None),   # GREEN
        },
        "T-09": {
            "oil_change":           (170, 4800),   # YELLOW
            "transmission_fluid":   (300, 20000),  # GREEN
            "brake_fluid":          (300, None),   # GREEN
            "coolant":              (300, 20000),  # GREEN
            "power_steering_fluid": (400, 28000),  # GREEN
            "wheel_alignment":      (340, 11000),  # YELLOW
            "brake_pads":           (340, 17500),  # YELLOW
            "tire_wear":            (175, 9200),   # YELLOW
            "windshield_wipers":    (340, None),   # GREEN
        },
        "T-10": {
            "oil_change":           (45, 2000),    # GREEN
            "transmission_fluid":   (100, 7000),   # GREEN
            "brake_fluid":          (100, None),   # GREEN
            "coolant":              (100, 7000),   # GREEN
            "power_steering_fluid": (100, 8000),   # GREEN
            "wheel_alignment":      (100, 5000),   # GREEN
            "brake_pads":           (100, 5000),   # GREEN
            "tire_wear":            (60, 3000),    # GREEN
            "windshield_wipers":    (100, None),   # GREEN
        },
    }

    created_trucks = {}
    for t in trucks_data:
        truck = Truck(
            truck_number=t["number"],
            make=t["make"],
            model=t["model"],
            year=t["year"],
            truck_type=t["type"],
            current_mileage=t["mileage"],
        )
        db.add(truck)
        db.flush()  # get the truck.id before creating maintenance items
        created_trucks[t["number"]] = truck

        # Create all 9 maintenance item rows for this truck
        history = service_history.get(t["number"], {})
        for item_type in MAINTENANCE_ITEM_TYPES:
            defaults = DEFAULT_INTERVALS[item_type]
            service = history.get(item_type)

            last_date = None
            last_mileage = None
            if service:
                days_ago, mileage_ago = service
                last_date = today - timedelta(days=days_ago)
                if mileage_ago is not None:
                    last_mileage = max(0, t["mileage"] - mileage_ago)

            item = MaintenanceItem(
                truck_id=truck.id,
                item_type=item_type,
                last_service_mileage=last_mileage,
                last_service_date=last_date,
                interval_miles=defaults["miles"],
                interval_days=defaults["days"],
            )
            db.add(item)

    db.flush()

    # Seed demo incidents — a mix of severities and statuses
    incidents_data = [
        {
            "truck_number": "T-03",
            "driver_name": "Mike Rodriguez",
            "days_ago": 2,
            "description": "Brake pedal feels soft and requires extra pressure. Noticed this starting yesterday morning on the Vernal route.",
            "severity": "high",
            "status": "open",
        },
        {
            "truck_number": "T-01",
            "driver_name": "James Cooper",
            "days_ago": 1,
            "description": "Check engine light came on during the afternoon route. No loss of power but light is still on.",
            "severity": "medium",
            "status": "open",
        },
        {
            "truck_number": "T-05",
            "driver_name": "David Torres",
            "days_ago": 3,
            "description": "Hydraulic lift is making a grinding noise when raising the bin. Gets worse when cold.",
            "severity": "high",
            "status": "in_review",
        },
        {
            "truck_number": "T-07",
            "driver_name": "Carlos Mendez",
            "days_ago": 5,
            "description": "Driver side mirror is cracked — difficult to see clearly in low light.",
            "severity": "low",
            "status": "open",
        },
        {
            "truck_number": "T-02",
            "driver_name": "James Cooper",
            "days_ago": 7,
            "description": "Air conditioning not working. Not a safety issue but uncomfortable on long routes in the heat.",
            "severity": "low",
            "status": "open",
        },
        {
            "truck_number": "T-09",
            "driver_name": "Brian Walsh",
            "days_ago": 10,
            "description": "Windshield wiper on driver side is leaving streaks. Needs replacement.",
            "severity": "low",
            "status": "resolved",
        },
    ]

    for inc in incidents_data:
        truck = created_trucks.get(inc["truck_number"])
        if not truck:
            continue
        incident = IncidentReport(
            truck_id=truck.id,
            driver_name=inc["driver_name"],
            incident_date=today - timedelta(days=inc["days_ago"]),
            description=inc["description"],
            severity=inc["severity"],
            status=inc["status"],
        )
        db.add(incident)

    # Seed a few recent mileage log entries
    mileage_entries = [
        ("T-01", 87450, "jcooper"),
        ("T-02", 74200, "jcooper"),
        ("T-03", 112300, "mrodriguez"),
        ("T-05", 134500, "dtorres"),
        ("T-06", 38900, "cmendez"),
    ]
    for truck_num, mileage, driver in mileage_entries:
        truck = created_trucks.get(truck_num)
        if truck:
            log = MileageLog(
                truck_id=truck.id,
                reported_mileage=mileage,
                reported_by=driver,
            )
            db.add(log)

    db.commit()
    print(f"✓ Seeded {len(trucks_data)} demo trucks with maintenance history and incidents")


def seed_demo_drivers(db: Session):
    """Create a few demo driver accounts for the pitch demo."""
    demo_drivers = [
        {"username": "jcooper",    "full_name": "James Cooper",   "password": "Driver2024!"},
        {"username": "mrodriguez", "full_name": "Mike Rodriguez",  "password": "Driver2024!"},
        {"username": "dtorres",    "full_name": "David Torres",    "password": "Driver2024!"},
        {"username": "cmendez",    "full_name": "Carlos Mendez",   "password": "Driver2024!"},
        {"username": "bwalsh",     "full_name": "Brian Walsh",     "password": "Driver2024!"},
    ]
    for d in demo_drivers:
        if not db.query(User).filter(User.username == d["username"]).first():
            user = User(
                username=d["username"],
                hashed_password=hash_password(d["password"]),
                full_name=d["full_name"],
                role="driver",
            )
            db.add(user)
    db.commit()
    print("✓ Seeded demo driver accounts")


def seed_briefing_settings(db: Session):
    """Create the default BriefingSettings row if it doesn't already exist."""
    if db.query(BriefingSettings).first():
        return
    settings = BriefingSettings(enabled=False, send_time="05:30", email_address="")
    db.add(settings)
    db.commit()


def run_all_seeds(db: Session):
    """Run all seed functions in order. Called from main.py on startup."""
    seed_users(db)
    seed_demo_drivers(db)
    seed_demo_fleet(db)
    seed_briefing_settings(db)
