#!/usr/bin/env python3
"""Script para actualizar todos los tests E2E para usar SAMPLE_USER en vez de sample_user."""
import re
from pathlib import Path

# Archivos a actualizar
test_files = [
    "tests/e2e/test_favorites_flow.py",
    "tests/e2e/test_order_with_address_flow.py",
    "tests/e2e/test_user_login_flow.py",
    "tests/e2e/test_user_registration_flow.py"
]

base_dir = Path(__file__).parent

for test_file in test_files:
    file_path = base_dir / test_file

    if not file_path.exists():
        print(f"⚠️  Archivo no encontrado: {file_path}")
        continue

    content = file_path.read_text(encoding='utf-8')
    original_content = content

    # 1. Asegurar que tiene los imports
    if "from tests.fixtures.data import SAMPLE_USER" not in content:
        # Agregar después de "from httpx import AsyncClient"
        content = content.replace(
            "from httpx import AsyncClient",
            "from httpx import AsyncClient\nfrom tests.fixtures.data import SAMPLE_USER, SAMPLE_ADMIN"
        )

    # 2. Remover parámetro sample_user de las firmas de funciones
    content = re.sub(
        r',\s*sample_user,',
        ',',
        content
    )
    content = re.sub(
        r',\s*sample_user\s*\)',
        ')',
        content
    )

    # 3. Reemplazar sample_user["email"] con SAMPLE_USER["email"]
    content = content.replace('sample_user["email"]', 'SAMPLE_USER["email"]')

    # 4. Reemplazar sample_user["password"] con SAMPLE_USER["password"]
    content = content.replace('sample_user["password"]', 'SAMPLE_USER["password"]')

    # 5. Reemplazar sample_user["name"] con SAMPLE_USER["name"]
    content = content.replace('sample_user["name"]', 'SAMPLE_USER["name"]')

    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ Actualizado: {test_file}")
    else:
        print(f"ℹ️  Sin cambios: {test_file}")

print("\n✅ Actualización completada")
