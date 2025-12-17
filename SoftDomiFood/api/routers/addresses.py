from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from routers.auth import get_current_user
from services.database_service import create_address, get_user_addresses, get_address_by_id
from services.address_validation_service import get_validation_service, AddressValidationError

router = APIRouter()

class AddressCreate(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str = Field(..., alias="zipCode")  # Acepta zipCode del frontend
    country: str = "Colombia"
    is_default: bool = Field(default=False, alias="isDefault")  # Acepta isDefault del frontend
    instructions: Optional[str] = None

    class Config:
        # Permite usar tanto snake_case como camelCase en el JSON
        populate_by_name = True  # Pydantic v2 - permite usar tanto el alias como el nombre del campo

@router.post("/addresses", status_code=status.HTTP_201_CREATED)
async def create_user_address(
    address: AddressCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Crear nueva dirección para el usuario con validación automática.

    Implementa HU-03:
    - Valida formato automáticamente (Código Postal, Ciudad, Calle)
    - Si hay inconsistencias, genera advertencias claras
    - Permite continuar bajo responsabilidad del usuario
    """
    try:
        # Validar que los campos requeridos no estén vacíos (validación básica previa)
        if not address.street or not address.street.strip():
            raise HTTPException(status_code=422, detail="El campo 'street' (calle) es requerido")
        if not address.city or not address.city.strip():
            raise HTTPException(status_code=422, detail="El campo 'city' (ciudad) es requerido")
        if not address.state or not address.state.strip():
            raise HTTPException(status_code=422, detail="El campo 'state' (departamento) es requerido")
        if not address.zip_code or not address.zip_code.strip():
            raise HTTPException(status_code=422, detail="El campo 'zip_code' (código postal) es requerido")

        # HU-03 Criterio 1: Validación automática de formato
        validation_service = get_validation_service()

        try:
            validation_result = validation_service.validate_or_raise(
                street=address.street.strip(),
                city=address.city.strip(),
                state=address.state.strip(),
                zip_code=address.zip_code.strip(),
                country=address.country
            )
        except AddressValidationError as e:
            # HU-03 Criterio 2: Mensaje claro cuando hay errores
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Error de validación en la dirección",
                    "errors": [
                        {
                            "field": result.field,
                            "message": result.message
                        }
                        for result in e.validation_results
                    ]
                }
            )

        # Crear la dirección (HU-03 Criterio 3: se guarda en historial)
        new_address = await create_address(
            user_id=current_user["userId"],
            street=address.street.strip(),
            city=address.city.strip(),
            state=address.state.strip(),
            zip_code=address.zip_code.strip(),
            country=address.country.strip() if address.country else "Colombia",
            is_default=address.is_default,
            instructions=address.instructions.strip() if address.instructions else None
        )

        if not new_address:
            raise HTTPException(status_code=500, detail="Error creating address")

        # HU-03 Criterio 2: Incluir advertencias en la respuesta si existen
        response = {
            "message": "Address created successfully",
            "address": new_address
        }

        if validation_result.get("has_warnings"):
            response["warnings"] = validation_result["warnings"]
            response["message"] = "Address created successfully with warnings"

        return response

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating address: {str(e)}")

@router.get("/addresses")
async def get_addresses(
    current_user: dict = Depends(get_current_user)
):
    """Obtener todas las direcciones del usuario"""
    addresses = await get_user_addresses(current_user["userId"])
    return {"addresses": addresses}

@router.get("/addresses/{address_id}")
async def get_address(
    address_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtener dirección por ID"""
    address = await get_address_by_id(address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    # Verificar que la dirección pertenece al usuario
    if address["userId"] != current_user["userId"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return {"address": address}
