"""
Datos de prueba determinísticos para tests
"""


# Usuario de prueba estándar (debe coincidir con seed_data.py)
SAMPLE_USER = {
    "email": "cliente1@example.com",
    "password": "cliente123",
    "name": "Juan Pérez",
    "phone": "3001234567"
}

# Usuario admin de prueba (no existe por defecto en seed, pero se puede crear si es necesario)
SAMPLE_ADMIN = {
    "email": "admin.test@example.com",
    "password": "AdminTest123!",
    "name": "Admin Test User",
    "role": "ADMIN"
}

# Productos de prueba
SAMPLE_PRODUCTS = [
    {
        "name": "Salchipapa Básica",
        "description": "Salchipapa tradicional con papas fritas y salchicha",
        "price": 15000.0,
        "category": "SALCHIPAPAS",
        "isAvailable": True,
        "image": "https://example.com/salchipapa-basica.jpg"
    },
    {
        "name": "Coca Cola 350ml",
        "description": "Bebida gaseosa Coca Cola",
        "price": 3000.0,
        "category": "BEBIDAS",
        "isAvailable": True,
        "image": "https://example.com/coca-cola.jpg"
    },
    {
        "name": "Salsa de Ajo",
        "description": "Salsa adicional de ajo",
        "price": 1500.0,
        "category": "ADICIONALES",
        "isAvailable": True,
        "image": "https://example.com/salsa-ajo.jpg"
    },
    {
        "name": "Combo Familiar",
        "description": "2 Salchipapas + 2 Bebidas",
        "price": 35000.0,
        "category": "COMBOS",
        "isAvailable": True,
        "image": "https://example.com/combo-familiar.jpg"
    }
]

# Dirección de prueba
SAMPLE_ADDRESS = {
    "street": "Calle 123 #45-67",
    "city": "Bogotá",
    "state": "Cundinamarca",
    "zipCode": "110111",
    "country": "Colombia",
    "isDefault": True,
    "instructions": "Casa azul, timbre en la puerta principal"
}

# Cupón de prueba - Porcentaje
SAMPLE_COUPON_PERCENTAGE = {
    "code": "TEST20",
    "description": "Cupón de prueba 20% descuento",
    "discountType": "PERCENTAGE",
    "percentage": 20.0,
    "isActive": True,
    "maxUses": 100,
    "perUserLimit": 3
}

# Cupón de prueba - Monto fijo
SAMPLE_COUPON_AMOUNT = {
    "code": "SAVE5000",
    "description": "Cupón de prueba $5000 descuento",
    "discountType": "AMOUNT",
    "amount": 5000.0,
    "isActive": True,
    "maxUses": 50,
    "perUserLimit": 1
}

# Orden de prueba básica
SAMPLE_ORDER = {
    "paymentMethod": "CASH",
    "notes": "Sin salsas picantes"
}
