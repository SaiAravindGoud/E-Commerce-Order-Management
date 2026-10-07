from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.address import Address
from app.models.user import User
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate


router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"],
)


def set_default_address(
    db: Session,
    customer_id: int,
    address_id: int,
):
    addresses = db.scalars(
        select(Address).where(
            Address.customer_id == customer_id
        )
    ).all()

    for address in addresses:
        address.is_default = address.id == address_id


@router.post(
    "",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = Address(
        customer_id=current_user.id,
        full_name=address_data.full_name,
        phone=address_data.phone,
        address_line=address_data.address_line,
        city=address_data.city,
        state=address_data.state,
        pincode=address_data.pincode,
        is_default=address_data.is_default,
    )

    db.add(address)
    db.flush()

    if address.is_default:
        set_default_address(
            db,
            current_user.id,
            address.id,
        )

    db.commit()
    db.refresh(address)

    return address


@router.get(
    "",
    response_model=list[AddressResponse],
)
def get_my_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    addresses = db.scalars(
        select(Address)
        .where(Address.customer_id == current_user.id)
        .order_by(Address.id.desc())
    ).all()

    return addresses


@router.get(
    "/{address_id}",
    response_model=AddressResponse,
)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = db.scalar(
        select(Address).where(
            Address.id == address_id,
            Address.customer_id == current_user.id,
        )
    )

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    return address


@router.put(
    "/{address_id}",
    response_model=AddressResponse,
)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = db.scalar(
        select(Address).where(
            Address.id == address_id,
            Address.customer_id == current_user.id,
        )
    )

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    address.full_name = address_data.full_name
    address.phone = address_data.phone
    address.address_line = address_data.address_line
    address.city = address_data.city
    address.state = address_data.state
    address.pincode = address_data.pincode

    if address_data.is_default:
        set_default_address(
            db,
            current_user.id,
            address.id,
        )
    else:
        address.is_default = False

    db.commit()
    db.refresh(address)

    return address


@router.delete(
    "/{address_id}",
)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = db.scalar(
        select(Address).where(
            Address.id == address_id,
            Address.customer_id == current_user.id,
        )
    )

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    if address.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the default address",
        )

    db.delete(address)
    db.commit()

    return {
        "message": "Address deleted successfully",
        "address_id": address_id,
    }


@router.put(
    "/{address_id}/default",
    response_model=AddressResponse,
)
def make_default_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = db.scalar(
        select(Address).where(
            Address.id == address_id,
            Address.customer_id == current_user.id,
        )
    )

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    set_default_address(
        db,
        current_user.id,
        address.id,
    )

    db.commit()
    db.refresh(address)

    return address