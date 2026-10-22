"""Service layer handling business logic and database transactions for addresses."""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models import Address
from app.schemas import AddressCreate, AddressUpdate

logger = get_logger(__name__)


class AddressService:
    """Handles operational logic for the Address model."""

    @staticmethod
    def create_address(db: Session, address_in: AddressCreate) -> Address:
        """Creates a new address record.

        Args:
            db: The asynchronous database session dependency.
            address_in: The validated Pydantic schema containing the new address
                details.

        Returns:
            The newly created and committed Address database model instance.

        Raises:
            ValueError: If the database model field validation rules or physical
                geographic coordinate constraints fail.
        """
        try:
            db_address = Address(**address_in.model_dump())
            db.add(db_address)
            db.commit()
            db.refresh(db_address)
            logger.info("Successfully created address ID: %s", db_address.id)
            return db_address
        except ValueError as err:
            db.rollback()
            logger.exception("Validation failed during address creation: %s", err)
            raise ValueError(f"Validation failed: {err}") from err
        except IntegrityError as err:
            db.rollback()
            logger.critical("Database integrity error on address creation!", exc_info=True)
            raise ValueError("Database integrity constraint violated.") from err

    @staticmethod
    def get_address_by_id(db: Session, address_id: int) -> Address | None:
        """Retrieves a single address by its primary key ID.

        Args:
            db: The asynchronous database session dependency.
            address_id: The unique primary key integer of the address to retrieve.

        Returns:
            The matched Address database model instance, or None if no record
            associated with the given ID exists.
        """
        result = db.execute(select(Address).where(Address.id == address_id))
        return result.scalars().first()

    @staticmethod
    def get_addresses(
        db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[Address]:
        """Retrieves a paginated list of address entries.

       Args:
           db: The asynchronous database session dependency.
           skip: The number of initial address records to skip for pagination.
               Defaults to 0.
           limit: The maximum number of address records to return in the
               response batch. Defaults to 100.

       Returns:
           A sequence containing the fetched Address database model instances.
       """
        result = db.execute(select(Address).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    def update_address(
        db: Session, db_address: Address, address_in: AddressUpdate
    ) -> Address:
        """Updates an existing address using partial data.

        Args:
            db: The asynchronous database session dependency.
            db_address: The current Address model instance retrieved from the
                database.
            address_in: The Pydantic schema containing the fields to update.

        Returns:
            The updated and committed Address database model instance.

        Raises:
            ValueError: If any updated field values violate the model's geometric
                or text constraint validations.
        """
        update_data = address_in.model_dump(exclude_unset=True)

        try:
            for field, value in update_data.items():
                setattr(db_address, field, value)
            db.commit()
            db.refresh(db_address)
            logger.info("Successfully updated the address with the ID: %s", db_address.id)
            return db_address
        except ValueError as err:
            db.rollback()
            logger.exception("Validation failed during address updating: %s", err)
            raise ValueError(f"Update validation failed: {err}") from err

    @staticmethod
    def delete_address(db: Session, db_address: Address) -> None:
        """Removes an address record from the database.

        Args:
            db: The asynchronous database session dependency.
            db_address: The Address database model instance to be removed.
        """
        db.delete(db_address)
        db.commit()
