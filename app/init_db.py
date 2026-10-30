"""Create local development tables. Run: python -m app.init_db"""

import app.models  # noqa: F401
from app.database import Base, engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("IndexGuard database tables created or already exist.")


if __name__ == "__main__":
    main()
