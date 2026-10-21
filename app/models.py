
from sqlalchemy import create_engine, Integer, String, Float
from sqlalchemy.orm import sessionmaker, validates, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models using modern 2.0 style."""
    pass


class Address(Base):
    """
    Represents a physical geographic address entry in the database.
    """
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    street: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    @validates("name", "street", "city", "country")
    def validate_required_fields(self, key, value):
        """Ensures text fields are non-empty strings and strips whitespace."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Field '{key}' cannot be empty or non-string.")
        return value.strip()
    
    @validates("latitude")
    def validate_latitude(self, key: str, value: float) -> float:
        """Validates that latitude coordinates stay within global boundaries."""
        if not -90.0 <= value <= 90.0:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        return value

    @validates("longitude")
    def validate_longitude(self, key: str, value: float) -> float:
        """Validates that longitude coordinates stay within global boundaries."""
        if not -180.0 <= value <= 180.0:
            raise ValueError("Longitude must be between -180 and 180 degrees.")
        return value


# SQLite database
engine = create_engine(
    "sqlite:///addresses.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)
