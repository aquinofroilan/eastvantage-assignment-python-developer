"""
Service layer handling business logic and database transactions for Addresses.
"""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models import Address
from app.schemas import AddressCreate, AddressUpdate

logger = get_logger(__name__)

class AddressService:
    """Handles operational logic for the Address model."""
    
    @staticmethod
    async def create_address(db: AsyncSession, address_in: AddressCreate) -> Address:
        """
        Creates a new address record.

        Raises ValueError if SQLAlchemy model validators fail.
        """
        try:
            # .model_dump() converts Pydantic schema data directly into a dict
            db_address = Address(**address_in.model_dump())
            db.add(db_address)
            await db.commit()
            await db.refresh(db_address)
            logger.info("Successfully created address ID: %s", db_address.id)
            return db_address
        except ValueError as err:
            await db.rollback()
            # Re-raise to let the FastAPI route handler turn it into an HTTP 400
            logger.error("Validation failed during address creation: %s", err, exc_info=True)
            raise ValueError(f"Validation failed: {err}") from err
        except IntegrityError as err:
            await db.rollback()
            logger.critical("Database integrity error on address creation!", exc_info=True)
            raise ValueError("Database integrity constraint violated.") from err
    
    @staticmethod
    async def get_address_by_id(db: AsyncSession, address_id: int) -> Address | None:
        """Retrieves a single address by its primary key ID."""
        result = await db.execute(select(Address).where(Address.id == address_id))
        return result.scalars().first()
    
    @staticmethod
    async def get_addresses(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[Address]:
        """Retrieves a paginated list of address entries."""
        result = await db.execute(select(Address).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def update_address(
        db: AsyncSession, db_address: Address, address_in: AddressUpdate
    ) -> Address:
        """
            Updates an existing address using partial data.
    
            Raises ValueError if updated data violates field validators.
        """
        # Convert schema input into a dict, ignoring explicitly unset values
        update_data = address_in.model_dump(exclude_unset=True)
        
        try:
            for field, value in update_data.items():
                setattr(db_address, field, value)
            
            await db.commit()
            await db.refresh(db_address)
            logger.info("Successfully updated the address with the ID: %s", db_address.id)
            return db_address
        except ValueError as err:
            await db.rollback()
            logger.error("Validation failed during address updating: %s", err, exc_info=True)
            raise ValueError(f"Update validation failed: {err}") from err
    
    @staticmethod
    async def delete_address(db: AsyncSession, db_address: Address) -> None:
        """Removes an address record from the database."""
        await db.delete(db_address)
        await db.commit()
