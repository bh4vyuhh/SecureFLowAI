import os
import random
import pandas as pd
from faker import Faker
from tqdm import tqdm

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

OUT_DIR = "./ai-service/data/raw/synthetic_dlp"
OUT_FILE = os.path.join(OUT_DIR, "synthetic_data.csv")

NUM_RECORDS_PER_CLASS = 5000

def generate_public():
    """Generates Public (Non-Sensitive) data"""
    templates = [
        "Company Newsletter: Welcome to {month}! We are excited to announce our new {catch_phrase}. Join us in the cafeteria for {food}.",
        "Press Release: {company} today announced {catch_phrase}. For more information, visit our website.",
        "Event Reminder: The {event_name} will take place on {date} at {time} in the main conference room. All staff are welcome.",
        "Cafeteria Menu: Today's special is {food}. Enjoy a healthy meal at the {company} campus.",
        "Generic Update: Please remember to fill out your weekly timesheets by {day}.",
    ]
    
    template = random.choice(templates)
    return template.format(
        month=fake.month_name(),
        catch_phrase=fake.bs(),
        food=fake.word(),
        company=fake.company(),
        event_name=fake.catch_phrase(),
        date=fake.date_this_year(),
        time=fake.time(),
        day=fake.day_of_week()
    )

def generate_confidential():
    """Generates Confidential (Internal corporate sensitive, no explicit PII) data"""
    templates = [
        "INTERNAL MEMO: Q{quarter} Earnings projection looks {adjective}. We expect a revenue of ${amount}M. Do not share outside the finance department.",
        "Strategic Initiative: Project {project} will launch next month. Target market is {market}. Competitor analysis shows we have a {percent}% advantage.",
        "Performance Review: Employee ID {emp_id} showed {adjective} performance this quarter. Recommended for a {percent}% bonus.",
        "Meeting Notes (CONFIDENTIAL): Discussed restructuring the {department} division. We will be reallocating {amount} budget from Q1.",
        "NDA Protected: The proprietary algorithm yields a {percent}% efficiency increase over legacy systems. Trade secret classification applies.",
    ]
    
    template = random.choice(templates)
    return template.format(
        quarter=random.randint(1,4),
        adjective=random.choice(["strong", "weak", "exceptional", "subpar", "concerning"]),
        amount=random.randint(10, 999),
        project=fake.catch_phrase().title(),
        market=fake.job(),
        percent=random.randint(5, 95),
        emp_id=fake.ean8(),
        department=fake.job()
    )

def generate_restricted():
    """Generates Restricted (PII, PHI, PCI, API Keys, Top Secret) data"""
    templates = [
        "Customer Profile: Name: {name}, SSN: {ssn}, Credit Card: {credit_card}, CVV: {cvv}, Address: {address}",
        "Patient Diagnosis: Patient Name {name}, DOB: {dob}. Diagnosed with {condition}. Prescribed {medication}. Health Insurance ID: {ssn}.",
        "System Credentials: DB_URI=postgres://{username}:{password}@{domain}:5432/prod_db, API_KEY={api_key}",
        "Wire Transfer Log: Initiated transfer of ${amount} from Account {acct1} to Account {acct2}. Beneficiary: {name}, Routing Number: {routing}.",
        "TOP SECRET CLEARANCE: Operative {name} deployed to {country}. Passport number {passport}. Emergency contact phone: {phone}.",
    ]
    
    template = random.choice(templates)
    return template.format(
        name=fake.name(),
        ssn=fake.ssn(),
        credit_card=fake.credit_card_number(),
        cvv=fake.credit_card_security_code(),
        address=fake.address().replace("\n", ", "),
        dob=fake.date_of_birth(),
        condition=random.choice(["Type 2 Diabetes", "Hypertension", "Asthma", "Arrhythmia", "Chronic Bronchitis"]),
        medication=random.choice(["Lisinopril", "Albuterol", "Metformin", "Atorvastatin"]),
        username=fake.user_name(),
        password=fake.password(),
        domain=fake.domain_name(),
        api_key=fake.sha256(),
        amount=random.randint(1000, 500000),
        acct1=fake.bban(),
        acct2=fake.bban(),
        routing=fake.aba(),
        country=fake.country(),
        passport=fake.ssn(),
        phone=fake.phone_number()
    )

def main():
    print(f"Generating synthetic DLP datasets ({NUM_RECORDS_PER_CLASS} per class)...")
    os.makedirs(OUT_DIR, exist_ok=True)
    
    records = []
    
    print("Generating Public...")
    for _ in tqdm(range(NUM_RECORDS_PER_CLASS)):
        records.append({"text": generate_public(), "label": "Public", "source": "synthetic"})
        
    print("Generating Confidential...")
    for _ in tqdm(range(NUM_RECORDS_PER_CLASS)):
        records.append({"text": generate_confidential(), "label": "Confidential", "source": "synthetic"})
        
    print("Generating Restricted...")
    for _ in tqdm(range(NUM_RECORDS_PER_CLASS)):
        records.append({"text": generate_restricted(), "label": "Restricted", "source": "synthetic"})
        
    df = pd.DataFrame(records)
    df.to_csv(OUT_FILE, index=False)
    
    print(f"\n[SUCCESS] Generated {len(df)} synthetic records and saved to {OUT_FILE}")

if __name__ == "__main__":
    main()
