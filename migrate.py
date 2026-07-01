import os
import shutil

OLD_SRC = r"C:\Users\AfrinBanu\AgentsToolkitProjects\SQL_analytics_Agent\sql_analytics_agent\src"
NEW_SRC = r"C:\Users\AfrinBanu\AgentsToolkitProjects\AIsql_analytics_agent\src"

directories = [
    "database",
    "api",
    "services"
]

def migrate():
    for d in directories:
        os.makedirs(os.path.join(NEW_SRC, d), exist_ok=True)
        with open(os.path.join(NEW_SRC, d, "__init__.py"), "w") as f:
            pass
            
    # 1. Move connection.py
    with open(os.path.join(OLD_SRC, r"database\postgres\connection.py"), "r") as f:
        content = f.read()
    with open(os.path.join(NEW_SRC, r"database\connection.py"), "w") as f:
        f.write(content)
        
    # 2. Move models.py
    with open(os.path.join(OLD_SRC, r"database\postgres\models.py"), "r") as f:
        content = f.read()
    content = content.replace("from src.database.postgres.connection", "from src.database.connection")
    with open(os.path.join(NEW_SRC, r"database\models.py"), "w") as f:
        f.write(content)
        
    # 3. Move seed_db.py
    with open(os.path.join(OLD_SRC, r"database\postgres\seed_db.py"), "r") as f:
        content = f.read()
    content = content.replace("from src.database.postgres.models", "from src.database.models")
    content = content.replace("from src.database.postgres.connection", "from src.database.connection")
    with open(os.path.join(NEW_SRC, r"database\seed_db.py"), "w") as f:
        f.write(content)

    # 4. Move schemas.py
    with open(os.path.join(OLD_SRC, r"api\routers\schemas.py"), "r") as f:
        content = f.read()
    with open(os.path.join(NEW_SRC, r"api\schemas.py"), "w") as f:
        f.write(content)

    # 5. Move tools.py (agents.py -> tools.py)
    with open(os.path.join(OLD_SRC, r"api\routers\agents.py"), "r") as f:
        content = f.read()
    content = content.replace("from src.database.postgres.connection", "from src.database.connection")
    content = content.replace("from src.api.routers.schemas", "from src.api.schemas")
    with open(os.path.join(NEW_SRC, r"api\tools.py"), "w") as f:
        f.write(content)

    print("Migration complete!")

if __name__ == "__main__":
    migrate()
