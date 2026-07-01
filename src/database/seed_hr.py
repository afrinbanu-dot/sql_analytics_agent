import datetime
import random
from connection import engine, Base, SessionLocal
from models import Department, Employee, TimeOff

# Create all tables in the database (this will create the new HR tables)
Base.metadata.create_all(bind=engine)

def seed_hr_data():
    db = SessionLocal()
    
    # Check if we already have HR data
    if db.query(Department).count() > 0:
        print("HR Database already seeded!")
        db.close()
        return

    print("Seeding database with HR (Workday) data...")
    
    departments_data = [
        ("Engineering", 5000000.00),
        ("Sales", 3000000.00),
        ("Human Resources", 1000000.00),
        ("Marketing", 2000000.00)
    ]
    
    departments = []
    # Create Departments
    for name, budget in departments_data:
        dept = Department(name=name, budget=budget)
        db.add(dept)
        departments.append(dept)
    
    db.commit()
    
    # Create Employees & TimeOff
    roles = {
        "Engineering": ["Software Engineer", "Senior Engineer", "Engineering Manager", "QA Tester"],
        "Sales": ["Account Executive", "Sales Development Rep", "VP of Sales"],
        "Human Resources": ["HR Business Partner", "Recruiter", "HR Director"],
        "Marketing": ["Marketing Manager", "Content Strategist", "SEO Specialist"]
    }
    
    pto_types = ["Vacation", "Sick", "Parental"]
    pto_statuses = ["Approved", "Pending", "Rejected"]
    
    for dept in departments:
        # 10-30 employees per department
        num_employees = random.randint(10, 30)
        for i in range(num_employees):
            role = random.choice(roles[dept.name])
            base_salary = 60000
            if "Senior" in role or "Manager" in role:
                base_salary = random.randint(100000, 160000)
            elif "VP" in role or "Director" in role:
                base_salary = random.randint(150000, 250000)
            else:
                base_salary = random.randint(60000, 110000)
                
            emp = Employee(
                first_name=f"Emp{dept.id}_{i}",
                last_name=f"LastName{dept.id}_{i}",
                email=f"emp{dept.id}_{i}@enterprisecorp.com",
                role=role,
                salary=float(base_salary),
                hire_date=datetime.datetime.now() - datetime.timedelta(days=random.randint(10, 1500)),
                department_id=dept.id
            )
            db.add(emp)
            db.flush() # get emp.id
            
            # 0-3 PTO requests per employee
            for _ in range(random.randint(0, 3)):
                pto = TimeOff(
                    employee_id=emp.id,
                    type=random.choice(pto_types),
                    days=random.randint(1, 14),
                    status=random.choice(pto_statuses)
                )
                db.add(pto)

    db.commit()
    db.close()
    print("HR Database seeded successfully!")

if __name__ == "__main__":
    seed_hr_data()
