import datetime
import random
from connection import engine, Base, SessionLocal
from models import Account, Contact, Opportunity, Interaction

# Create all tables in the database
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # Check if we already have data
    if db.query(Account).count() > 0:
        print("Database already seeded!")
        db.close()
        return

    print("Seeding database with Enterprise CRM data...")
    
    industries = ["Technology", "Healthcare", "Finance", "Manufacturing", "Retail"]
    regions = ["North America", "Europe", "Asia Pacific", "Latin America"]
    
    accounts = []
    # Create Accounts
    for i in range(1, 21):
        account = Account(
            name=f"Enterprise Corp {i}",
            industry=random.choice(industries),
            annual_revenue=round(random.uniform(1000000, 50000000), 2),
            region=random.choice(regions)
        )
        db.add(account)
        accounts.append(account)
    
    db.commit()
    
    # Create Contacts & Opportunities
    stages = ["Prospecting", "Qualification", "Proposal", "Closed Won", "Closed Lost"]
    
    for account in accounts:
        # 1-3 Contacts per account
        for j in range(random.randint(1, 3)):
            contact = Contact(
                first_name=f"FirstName{account.id}_{j}",
                last_name=f"LastName{account.id}_{j}",
                email=f"contact{account.id}_{j}@enterprisecorp{account.id}.com",
                title=random.choice(["CEO", "CTO", "VP of Sales", "IT Director"]),
                account_id=account.id
            )
            db.add(contact)
        
        # 1-4 Opportunities per account
        for k in range(random.randint(1, 4)):
            stage = random.choice(stages)
            opp = Opportunity(
                name=f"Q{random.randint(1,4)} Licensing Deal - {account.name}",
                amount=round(random.uniform(10000, 500000), 2),
                stage=stage,
                close_date=datetime.datetime.now() + datetime.timedelta(days=random.randint(-180, 180)),
                account_id=account.id
            )
            db.add(opp)
            db.flush() # flush to get opp.id
            
            # 1-5 Interactions per opportunity
            for _ in range(random.randint(1, 5)):
                interaction = Interaction(
                    type=random.choice(["Email", "Call", "Meeting", "Demo"]),
                    notes="Discussed pricing and timeline.",
                    date=opp.close_date - datetime.timedelta(days=random.randint(1, 30)),
                    opportunity_id=opp.id
                )
                db.add(interaction)

    db.commit()
    db.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
