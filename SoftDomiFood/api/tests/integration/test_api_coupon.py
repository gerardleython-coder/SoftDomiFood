import requests
import json

# Primero hacer login para obtener el token
login_url = "http://localhost:5000/api/auth/login"
login_data = {
    "email": "Admin@sofka.com",
    "password": "Admin123"
}

print("1. Iniciando sesión como admin...")
try:
    login_response = requests.post(login_url, json=login_data)
    print(f"   Status: {login_response.status_code}")
    print(f"   Response: {login_response.text[:200]}")
    
    if login_response.status_code == 200:
        token = login_response.json()["token"]
        print(f"   ✓ Token obtenido: {token[:50]}...")
        
        # Ahora intentar crear un cupón
        coupon_url = "http://localhost:5000/api/admin/coupons"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        coupon_data = {
            "code": "APITEST20",
            "description": "Test desde Python",
            "discountType": "PERCENTAGE",
            "amount": None,
            "percentage": 20,
            "validFrom": None,
            "validTo": None,
            "maxUses": None,
            "perUserLimit": None,
            "applicableUserId": None,
            "isActive": True
        }
        
        print("\n2. Creando cupón...")
        print(f"   Datos: {json.dumps(coupon_data, indent=2)}")
        
        coupon_response = requests.post(coupon_url, headers=headers, json=coupon_data)
        print(f"\n   Status: {coupon_response.status_code}")
        print(f"   Response Headers: {dict(coupon_response.headers)}")
        print(f"   Response Body: {coupon_response.text}")
        
        if coupon_response.status_code == 200:
            print("\n   ✓ Cupón creado exitosamente!")
        else:
            print(f"\n   ✗ Error al crear cupón!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
