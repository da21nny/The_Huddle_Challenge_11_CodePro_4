# El Chat Indestructible - Testing Fest Challenge

## 📋 Descripción del Proyecto

**El Chat Indestructible** es una aplicación de chat en tiempo real con arquitectura cliente-servidor desarrollada en Python. El proyecto demuestra buenas prácticas de testing incluidas pruebas unitarias, pruebas de integración, test-driven development (TDD) y validación de robustez ante desconexiones inesperadas.

El servidor maneja múltiples conexiones simultáneas mediante threading, mientras que los clientes pueden conectarse, enviar y recibir mensajes en tiempo real. El sistema es resistente a fallos de red y desconexiones abruptas.

---

## 🏗️ Arquitectura del Proyecto

### Componentes Principales

```
┌─────────────────────────────────────────────┐
│         ARQUITECTURA DEL SISTEMA             │
├─────────────────────────────────────────────┤
│                                              │
│  ┌──────────────┐    ┌──────────────┐      │
│  │   Cliente 1  │    │   Cliente 2  │      │
│  │  (socket)    │    │  (socket)    │      │
│  └──────┬───────┘    └──────┬───────┘      │
│         │                    │               │
│         └────────┬───────────┘               │
│                  │ TCP/IP                    │
│          ┌───────▼────────┐                 │
│          │     SERVIDOR   │                 │
│          │  (puerto 5000)  │                 │
│          │                 │                 │
│          │ ┌─────────────┐ │                 │
│          │ │  Diccionario│ │                 │
│          │ │   clientes  │ │                 │
│          │ └─────────────┘ │                 │
│          │                 │                 │
│          │ ┌─────────────┐ │                 │
│          │ │   Threads   │ │                 │
│          │ │   handler   │ │                 │
│          │ └─────────────┘ │                 │
│          │                 │                 │
│          │ ┌─────────────┐ │                 │
│          │ │  Broadcast  │ │                 │
│          │ │   sistema   │ │                 │
│          │ └─────────────┘ │                 │
│          └─────────────────┘                 │
│                                              │
└─────────────────────────────────────────────┘
```

### Flujo de Datos

1. **Cliente → Servidor**: El cliente envía nickname + mensajes
2. **Servidor**: Procesa, valida y distribuye mensajes
3. **Servidor → Broadcast**: Envía a todos los clientes excepto el remitente
4. **Manejo de desconexiones**: Se detectan automáticamente y se notifica a otros clientes

---

## 🛠️ Tecnología Usada

| Componente | Versión | Propósito |
|-----------|---------|----------|
| **Python** | 3.14+ | Lenguaje de programación |
| **Socket** | stdlib | Comunicación TCP/IP |
| **Threading** | stdlib | Manejo de múltiples clientes |
| **pytest** | latest | Framework de testing |
| **unittest.mock** | stdlib | Mocking para tests unitarios |

### Características Técnicas

- **Protocolo**: TCP/IP con sockets
- **Concurrencia**: Threading con locks (RLock) para sincronización
- **Comunicación**: Mensajes codificados en UTF-8
- **Validación**: Mensajes entre 1-500 caracteres
- **Resiliencia**: Manejo de errores de socket y desconexiones

---

## 📁 Estructura del Proyecto

```
The_Huddle_Challenge_11_CodePro_4/
├── README.md                    # Este archivo
├── requirements.txt             # Dependencias Python
├── src/
│   ├── __init__.py
│   ├── server.py               # Servidor TCP/IP
│   └── client.py               # Cliente interactivo
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Configuración de pytest (fixtures)
│   ├── test_unit.py            # Pruebas unitarias
│   ├── test_tdd.py             # Pruebas TDD
│   ├── test_integration.py     # Pruebas de integración
│   └── test_disconnect.py      # Pruebas de desconexión
└── docs/
    └── challenge.txt            # Especificación del reto
```

---

## 🚀 Guía de Instalación y Ejecución

### Requisitos Previos

- **Python 3.14+** instalado
- **pip** (gestor de paquetes)
- Terminal/CMD disponible

---

### 🪟 Windows

#### 1. **Clonar o descargar el proyecto**

```powershell
cd Documents\VSCode
```

#### 2. **Crear entorno virtual**

```powershell
python -m venv .venv
```

#### 3. **Activar entorno virtual**

```powershell
.\.venv\Scripts\Activate.ps1
```

Si hay problema de ejecución, ejecuta:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4. **Instalar dependencias**

```powershell
pip install -r requirements.txt
```

#### 5. **Ejecutar pruebas**

```powershell
# Todas las pruebas
python -m pytest tests/ -v

# Pruebas específicas
python -m pytest tests/test_unit.py -v
python -m pytest tests/test_tdd.py -v
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_disconnect.py -v
```

#### 6. **Ejecutar el servidor**

```powershell
python src/server.py
```

Verás:
```
[+] Servidor iniciado en 127.0.0.1:5000
[*] Esperando conexiones...
```

#### 7. **Ejecutar clientes (en otra terminal)**

```powershell
# Terminal 2
.\.venv\Scripts\Activate.ps1
python src/client.py

# Terminal 3
.\.venv\Scripts\Activate.ps1
python src/client.py
```

Ingresa un nickname y comienza a chatear.

---

### 🐧 Linux

#### 1. **Clonar o descargar el proyecto**

```bash
cd Documents/VSCode/The_Huddle_Challenge_11_CodePro_4
```

#### 2. **Crear entorno virtual**

```bash
python3 -m venv .venv
```

#### 3. **Activar entorno virtual**

```bash
source .venv/bin/activate
```

#### 4. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

#### 5. **Ejecutar pruebas**

```bash
# Todas las pruebas
python -m pytest tests/ -v

# Pruebas específicas
python -m pytest tests/test_unit.py -v
python -m pytest tests/test_tdd.py -v
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_disconnect.py -v
```

#### 6. **Ejecutar el servidor**

```bash
python src/server.py
```

Verás:
```
[+] Servidor iniciado en 127.0.0.1:5000
[*] Esperando conexiones...
```

#### 7. **Ejecutar clientes (en otras terminales)**

```bash
# Terminal 2
source .venv/bin/activate
python src/client.py

# Terminal 3
source .venv/bin/activate
python src/client.py
```

---

### 🍎 macOS

#### 1. **Clonar o descargar el proyecto**

```bash
cd Documents/VSCode/The_Huddle_Challenge_11_CodePro_4
```

#### 2. **Crear entorno virtual**

```bash
python3 -m venv .venv
```

#### 3. **Activar entorno virtual**

```bash
source .venv/bin/activate
```

#### 4. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

#### 5. **Ejecutar pruebas**

```bash
# Todas las pruebas
python -m pytest tests/ -v

# Pruebas específicas
python -m pytest tests/test_unit.py -v
python -m pytest tests/test_tdd.py -v
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_disconnect.py -v
```

#### 6. **Ejecutar el servidor**

```bash
python src/server.py
```

Verás:
```
[+] Servidor iniciado en 127.0.0.1:5000
[*] Esperando conexiones...
```

#### 7. **Ejecutar clientes (en otras terminales)**

```bash
# Terminal 2
source .venv/bin/activate
python src/client.py

# Terminal 3
source .venv/bin/activate
python src/client.py
```

---

## 🧪 Estrategia de Testing

### Tipos de Pruebas Implementadas

#### 1. **Pruebas Unitarias** (`test_unit.py`)
Validan funciones específicas de forma aislada:
- `check_message()`: Validación de mensajes
- `broadcast()`: Distribución de mensajes
- `remove_client()`: Eliminación de clientes

**Ejemplo**:
```python
def test_empty_message():
    ok, reason = check_message("")
    assert ok is False
    assert "vacio" in reason
```

#### 2. **Test-Driven Development** (`test_tdd.py`)
Sigue el ciclo Rojo-Verde-Refactor:
- **Rojo**: Escribe pruebas que fallan
- **Verde**: Implementa código mínimo
- **Refactor**: Optimiza manteniendo pruebas verdes

#### 3. **Pruebas de Integración** (`test_integration.py`)
Validan la interacción de múltiples componentes:
- Múltiples conexiones simultáneas
- Broadcast a varios clientes
- Orden de mensajes
- Validación de mensajes inválidos

#### 4. **Pruebas de Desconexión** (`test_disconnect.py`)
Verifican robustez ante fallos:
- Desconexión abrupta de un cliente
- Desconexión de múltiples clientes
- El servidor sigue funcionando
- Otros clientes reciben notificaciones

---

## 📊 Cobertura de Pruebas

```
Cobertura aproximada:
├── src/server.py
│   ├── check_message()      ✅ 100%
│   ├── broadcast()          ✅ 100%
│   ├── remove_client()      ✅ 100%
│   ├── handle_client()      ✅ 85%
│   └── accept_loop()        ✅ 85%
│
└── Total: 26 pruebas
    ├── 6 unitarias
    ├── 6 TDD
    ├── 8 integración
    └── 6 desconexión
```

---

## 💡 Conceptos Clave Implementados

### 1. **Concurrencia Thread-Safe**
```python
with clients_lock:
    clients[socket] = nickname
    # Acceso seguro al diccionario compartido
```

### 2. **Broadcast Seguro**
- Envía a todos excepto el remitente
- Maneja errores de socket
- Elimina clientes con fallos

### 3. **Validación de Mensajes**
- No vacíos
- No más de 500 caracteres
- Devuelve mensajes de error descriptivos

### 4. **Manejo de Desconexiones**
- Detecta automáticamente
- Notifica a otros clientes
- Limpia recursos correctamente

---

## 🔧 Troubleshooting

### Puerto en uso
```powershell
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :5000
kill -9 <PID>
```

### Permisos de script (Windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Módulos no encontrados
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📝 Ejemplos de Uso

### Escenario 1: Chat Simple

**Terminal 1 (Servidor)**:
```
$ python src/server.py
[+] Servidor iniciado en 127.0.0.1:5000
```

**Terminal 2 (Cliente Alice)**:
```
$ python src/client.py
Nickname: Alice
[+] Conectado como 'Alice'
> Hola a todos!
```

**Terminal 3 (Cliente Bob)**:
```
$ python src/client.py
Nickname: Bob
[+] Conectado como 'Bob'
** Alice se ha unido al chat **
[Alice]: Hola a todos!
> Hola Alice!
```

### Escenario 2: Pruebas Completas

```bash
# Ejecutar todas las pruebas con output detallado
python -m pytest tests/ -v --tb=short

# Ejecutar solo una categoría
python -m pytest tests/test_integration.py -v

# Con cobertura (si instala coverage)
pip install coverage
coverage run -m pytest tests/
coverage report
```

---

## 📚 Referencias

- [Python Socket Documentation](https://docs.python.org/3/library/socket.html)
- [Threading in Python](https://docs.python.org/3/library/threading.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)

---

## 📄 Licencia

Proyecto educativo - Testing Fest Challenge

## 👨‍💻 Autor

Edgar Vega - Da21nny
