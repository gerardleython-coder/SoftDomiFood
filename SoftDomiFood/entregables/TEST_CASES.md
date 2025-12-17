## Casos de Prueba

A continuación se presentan los **Casos de Prueba**, generados **exactamente en el formato solicitado (ID, Descripción, Pasos, Datos de Entrada, Resultado Esperado)**.

👉 **La sección "Pasos" ha sido expresada en lenguaje Gherkin (Dado (Given) / Cuando (When) / Entonces (Then))**, manteniendo **el mismo número de casos de prueba que criterios de aceptación por cada HU**, de acuerdo con el documento proporcionado.

---

### HU-001 – Registrarse como cliente

**TC-HU001-01**

**Descripción:** Validar el registro exitoso de un cliente con email y contraseña válidos.

**Pasos (Gherkin):**
```

Dado (Given) el usuario se encuentra en la pantalla de registro
Y (And) el email no existe previamente en el sistema
Cuando (When) el usuario ingresa un email válido y una contraseña válida
Y (And) envía el formulario de registro
Entonces (Then) la cuenta es creada exitosamente
Y (And) el usuario puede iniciar sesión en el sistema
```

**Datos de Entrada:**
- Email: usuario_nuevo@correo.com
- Contraseña: Prueba@123456

**Resultado Esperado:**
- La cuenta es creada exitosamente.
- El usuario puede iniciar sesión en el sistema.

---

**TC-HU001-02**

**Descripción:** Validar el mensaje de error al intentar registrarse con un email ya existente.

**Pasos (Gherkin):**
```

Dado (Given) el usuario se encuentra en la pantalla de registro
Y (And) el email ya existe en el sistema
Cuando (When) el usuario ingresa el email existente y una contraseña válida
Y (And) envía el formulario de registro
Entonces (Then) el sistema muestra un mensaje indicando que el email ya está en uso
Y (And) la cuenta no es creada
```

**Datos de Entrada:**
- Email: usuario_existente@correo.com
- Contraseña: Prueba@123456

**Resultado Esperado:**
- El sistema informa que el email ya está en uso.
- No se crea la cuenta.

---

### HU-002 – Iniciar sesión como cliente/administrador

**TC-HU002-01**

**Descripción:** Validar el inicio de sesión con credenciales válidas.

**Pasos (Gherkin):**
```

Dado (Given) el usuario se encuentra en la pantalla de inicio de sesión
Y (And) las credenciales ingresadas son válidas
Cuando (When) el usuario envía el formulario de inicio de sesión
Entonces (Then) el usuario accede al sistema
Y (And) es redirigido a su panel correspondiente
```

**Datos de Entrada:**
- Usuario: cliente@correo.com
- Contraseña: Valida@123456

**Resultado Esperado:**
- El usuario accede al sistema.
- Es redirigido a su panel correspondiente.

---

**TC-HU002-02**

**Descripción:** Validar el mensaje de error al iniciar sesión con credenciales inválidas.

**Pasos (Gherkin):**
```

Dado (Given) el usuario se encuentra en la pantalla de inicio de sesión
Y (And) las credenciales ingresadas son inválidas
Cuando (When) el usuario envía el formulario de inicio de sesión
Entonces (Then) el sistema muestra un mensaje de error
Y (And) no se permite el acceso al sistema
```

**Datos de Entrada:**
- Usuario: cliente@correo.com
- Contraseña: Incorrecta123

**Resultado Esperado:**
- El sistema muestra un mensaje de error.
- No se permite el acceso.

---

**TC-HU002-03**

**Descripción:** Validar el acceso al panel administrativo cuando el usuario es administrador.

**Pasos (Gherkin):**
```

Dado (Given) el usuario se encuentra en la pantalla de inicio de sesión
Y (And) el usuario tiene rol de administrador
Cuando (When) el usuario ingresa credenciales válidas de administrador
Y (And) envía el formulario
Entonces (Then) el sistema permite el acceso
Y (And) redirige al panel administrativo
```

**Datos de Entrada:**
- Usuario: admin@correo.com
- Contraseña: Admin@123456

**Resultado Esperado:**
- El usuario accede al panel administrativo.

---

### HU-003 – Visualizar el menú de productos

**TC-HU003-01**

**Descripción:** Validar la visualización del listado de productos en el menú.

**Pasos (Gherkin):**
```

Dado (Given) el usuario se encuentra en la página principal
Cuando (When) navega a la sección de menú
Entonces (Then) el sistema muestra el listado de productos
Y (And) cada producto incluye nombre, descripción y precio
```

**Datos de Entrada:**
- N/A

**Resultado Esperado:**
- Se muestra la lista de productos con nombre, descripción y precio.

---

**TC-HU003-02**

**Descripción:** Validar la carga eficiente de productos al hacer scroll.

**Pasos (Gherkin):**
```

Dado (Given) el usuario se encuentra en el menú de productos
Cuando (When) realiza desplazamiento hacia abajo
Entonces (Then) los productos se cargan progresivamente
Y (And) no se percibe degradación del rendimiento
```

**Datos de Entrada:**
- N/A

**Resultado Esperado:**
- Los productos se cargan de forma progresiva sin afectar el rendimiento.

---

### HU-004 – Agregar productos al carrito

**TC-HU004-01**

**Descripción:** Validar que un producto se agrega al carrito.

**Pasos (Gherkin):**
```

Dado (Given) el usuario visualiza un producto disponible
Cuando (When) selecciona la opción "Agregar al carrito"
Entonces (Then) el producto se añade al carrito
Y (And) el total del carrito se actualiza
```

**Datos de Entrada:**
- Producto seleccionado

**Resultado Esperado:**
- El producto se añade al carrito.
- El total del carrito se actualiza.

---

**TC-HU004-02**

**Descripción:** Validar el incremento de cantidad al agregar un producto existente en el carrito.

**Pasos (Gherkin):**
```

Dado (Given) el producto ya existe en el carrito
Cuando (When) el usuario agrega nuevamente el mismo producto
Entonces (Then) la cantidad del producto se incrementa correctamente
```

**Datos de Entrada:**
- Producto ya existente en el carrito

**Resultado Esperado:**
- La cantidad del producto se incrementa correctamente.

---

### HU-005 – Gestionar productos favoritos

**TC-HU005-01**

**Descripción:** Validar que un producto se añade a favoritos.

**Pasos (Gherkin):**
```

Dado (Given) el usuario visualiza un producto
Cuando (When) selecciona la opción de marcar como favorito
Entonces (Then) el producto se añade a la lista de favoritos
```

**Datos de Entrada:**
- Producto seleccionado

**Resultado Esperado:**
- El producto se añade a la lista de favoritos.

---

**TC-HU005-02**

**Descripción:** Validar la eliminación de un producto de favoritos.

**Pasos (Gherkin):**
```

Dado (Given) el producto se encuentra marcado como favorito
Cuando (When) el usuario elimina el producto de favoritos
Entonces (Then) el producto desaparece de la lista de favoritos
```

**Datos de Entrada:**
- Producto marcado como favorito

**Resultado Esperado:**
- El producto se elimina de la lista de favoritos.

---

**TC-HU005-03**

**Descripción:** Validar la visualización de la lista de favoritos.

**Pasos (Gherkin):**
```

Dado (Given) el usuario accede a la sección de favoritos
Entonces (Then) el sistema muestra todos los productos marcados como favoritos
```

**Datos de Entrada:**
- N/A

**Resultado Esperado:**
- Se muestran todos los productos marcados como favoritos.

---

### HU-006 – Crear un pedido con dirección de entrega

**TC-HU006-01**

**Descripción:** Validar la creación de un pedido con una dirección existente.

**Pasos (Gherkin):**
```

Dado (Given) el usuario tiene productos en el carrito
Y (And) el usuario posee direcciones registradas
Cuando (When) selecciona una dirección existente y confirma el pedido
Entonces (Then) el pedido se registra correctamente con la dirección seleccionada
```

**Datos de Entrada:**
- Dirección registrada

**Resultado Esperado:**
- El pedido se registra con la dirección seleccionada.

---

**TC-HU006-02**

**Descripción:** Validar la adición de una nueva dirección durante el checkout.

**Pasos (Gherkin):**
```

Dado (Given) el usuario no tiene direcciones registradas
Cuando (When) ingresa una nueva dirección válida durante el checkout
Y (And) confirma el pedido
Entonces (Then) la nueva dirección se guarda
Y (And) el pedido se registra correctamente con la nueva dirección
```

**Datos de Entrada:**
- Nueva dirección válida

**Resultado Esperado:**
- La nueva dirección se guarda.
- El pedido se registra correctamente con la nueva dirección.

