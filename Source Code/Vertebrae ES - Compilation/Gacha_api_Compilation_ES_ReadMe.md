# Comparación de Archivos: `gacha_api.py` (Código usado para compilar) vs `gacha_api.py` (Código usado para debuggear)

## Diferencias Principales

### 1. **Gestión de Rutas y Empaquetado**
- **`gacha_api_compile.py`**: Diseñado para empaquetado con PyInstaller
  - Usa `resource_path()` para rutas compatibles con EXE
  - Maneja correctamente la carpeta temporal `_MEIPASS`
  - Solo crea carpetas en modo desarrollo

- **`gacha_api.py`**: Para desarrollo normal
  - Usa rutas directas con `os.path.join()`
  - Siempre crea carpetas `data` y `localizations` (De no existir ya)

### 2. **Inicialización de Directorios**
```python
# gacha_api_compile.py (empaquetado)
if not getattr(sys, 'frozen', False):
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOCALIZATIONS_DIR, exist_ok=True)

# gacha_api.py (desarrollo)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOCALIZATIONS_DIR, exist_ok=True)
```

### 3. **Función `resource_path()`**
- **Solo en `gacha_api_compile.py`**:
```python
def resource_path(relative_path):
    """Obtiene la ruta correcta para archivos en desarrollo y EXE"""
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
```

### 4. **Rutas de Archivos de Datos**
- **`gacha_api_compile.py`**: Usa `resource_path()`
  ```python
  dolls_path = resource_path('data/dolls.json')
  ```

- **`gacha_api.py`**: Usa rutas directas
  ```python
  dolls_path = os.path.join(DATA_DIR, 'dolls.json')
  ```

## Propósito de Cada Versión

### `gacha_api_compile.py`
- **Uso**: Para distribución final como ejecutable. Esta version no se ejecuta de no estar compilada en un exe
- **Característica**: Compatible con PyInstaller

### `gacha_api.py` 
- **Uso**: Para desarrollo y testing
- **Rutas simples de desarrollo**
- **Ventaja**: Más fácil de debuggear y modificar

Ambos archivos proporcionan la misma funcionalidad completa del tracker de gacha, pero `gacha_api_compile.py` está optimizado para empaquetado en .exe, mientras que `gacha_api.py` es más adecuado para desarrollo. Los usuarios finales deben usar la versión compilada del código, mientras que los desarrolladores pueden usar cualquiera de las dos según sus necesidades.