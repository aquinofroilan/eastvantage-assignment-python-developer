"""HTTP routes for address resources."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies.db import get_db
from app.schemas import AddressCreate, AddressResponse, AddressUpdate
from app.services import AddressService

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post(
    "",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_address(
    address_in: AddressCreate, db: Session = Depends(get_db)
) -> AddressResponse:
    """Create a new address.

    Args:
        address_in: Address data to validate and persist.
        db: Database session provided for the request.

    Returns:
        The newly created address.

    Raises:
        HTTPException: If the address data violates a validation constraint.
    """
    try:
        return AddressService.create_address(db, address_in)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err


@router.get("", response_model=list[AddressResponse])
def get_addresses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[AddressResponse]:
    """Retrieve a paginated list of addresses.

    Args:
        skip: Number of addresses to skip.
        limit: Maximum number of addresses to return.
        db: Database session provided for the request.

    Returns:
        The requested addresses.
    """
    return list(AddressService.get_addresses(db, skip=skip, limit=limit))


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(address_id: int, db: Session = Depends(get_db)) -> AddressResponse:
    """Retrieve an address by its ID.

    Args:
        address_id: ID of the address to retrieve.
        db: Database session provided for the request.

    Returns:
        The requested address.

    Raises:
        HTTPException: If no address exists with the given ID.
    """
    address = AddressService.get_address_by_id(db, address_id)
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )
    return address


@router.patch("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    address_in: AddressUpdate,
    db: Session = Depends(get_db),
) -> AddressResponse:
    """Partially update an existing address.

    Args:
        address_id: ID of the address to update.
        address_in: Address fields to update.
        db: Database session provided for the request.

    Returns:
        The updated address.

    Raises:
        HTTPException: If the address does not exist or the update is invalid.
    """
    address = AddressService.get_address_by_id(db, address_id)
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )

    try:
        return AddressService.update_address(db, address, address_in)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: int, db: Session = Depends(get_db)) -> None:
    """Delete an address by its ID.

    Args:
        address_id: ID of the address to delete.
        db: Database session provided for the request.

    Raises:
        HTTPException: If no address exists with the given ID.
    """
    address = AddressService.get_address_by_id(db, address_id)
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )
    AddressService.delete_address(db, address)
