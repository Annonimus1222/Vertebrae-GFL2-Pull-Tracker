# Comparación de Archivos: `main_compilation.py` vs `main.py`

## Diferencias Principales

### 1. **Gestión de Rutas y Empaquetado**
- **`main_compilation.py`**: Diseñado para empaquetado con PyInstaller
  -  Incluye función `resource_path()` para compatibilidad con EXE
  -  Maneja correctamente la carpeta temporal `_MEIPASS`
  -  Incluye función `load_json_data()` para carga segura de archivos

- **`main.py`**: Para desarrollo normal
  - ❌ No incluye funciones de manejo de rutas para empaquetado
  - ❌ Usa importaciones directas sin compatibilidad EXE

### 2. **Función `resource_path()` (SOLO en compilation)**
```python
# main_compilation.py - EXCLUSIVO
def resource_path(relative_path):
    """Obtiene la ruta correcta para los archivos tanto en desarrollo como en el EXE"""
    try:
        # PyInstaller crea una carpeta temporal en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)
```

### 3. **Función `load_json_data()` (SOLO en compilation)**
```python
# main_compilation.py - EXCLUSIVO
def load_json_data(filename):
    """Carga archivos JSON desde la ubicación correcta"""
    try:
        # Primero intenta cargar como EXE
        if getattr(sys, 'frozen', False):
            path = resource_path(filename)
        else:
            # En desarrollo
            path = filename
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {filename}")
        print(f"Buscando en: {path}")
        return {}
    except Exception as e:
        print(f"Error cargando {filename}: {e}")
        return {}
```

### 4. **Importación de Módulos**
- **`main_compilation.py`**:
  ```python
  import sys  #  Importación adicional para empaquetado
  from gacha_api import (...)
  ```

- **`main.py`**:
  ```python
  from gacha_api import (...)  # ❌ Sin importación de sys
  ```

## Funcionalidad Idéntica

### Características Comunes (AMBOS archivos):
-  Interfaz gráfica completa con Tkinter
-  Sistema de pestañas (Importar, Historial, Estadísticas)
-  Gestión de configuración
-  Sistema de importación con progreso
-  Filtros avanzados para el historial
-  Gráficos de pastel para estadísticas
-  Sistema de backup inteligente
-  Localización multi-idioma
-  Barra de estado informativa
-  Menús contextuales
-  Sistema de ayuda integrado

### Estructura de Clases Idéntica:
- `GachaTrackerGUI` con los mismos métodos:
  - `setup_ui()`, `create_menu()`, `setup_import_tab()`, etc.
  - `start_import()`, `run_import()`, `load_history()`, etc.
  - `apply_filters()`, `create_pie_chart()`, `update_stats_display()`, etc.

### Flujo de la Aplicación Idéntico:
- Inicialización automática de datos
- Carga de historial al iniciar
- Sistema de importación en hilos separados
- Actualización en tiempo real de la interfaz
- Manejo de errores y mensajes al usuario

## Propósito de Cada Versión

### `main_compilation.py`
- **Uso**: Para distribución final como ejecutable
- **Característica**: Compatible con PyInstaller
- **Ventaja**: Funciona tanto como script como EXE empaquetado
- **Requisito**: Necesita `gacha_api_compile.py` como módulo

### `main.py`
- **Uso**: Para desarrollo y testing
- **Característica**: Rutas simples de desarrollo
- **Ventaja**: Más fácil de debuggear y modificar
- **Requisito**: Usa `gacha_api_dev.py` como módulo

## Conclusión
Ambos archivos proporcionan **exactamente la misma funcionalidad** de interfaz gráfica, pero `main_compilation.py` está optimizado para empaquetado mientras que `main.py` es para desarrollo. Las diferencias son mínimas y se centran únicamente en la compatibilidad con PyInstaller.

**Para usuarios finales**: Usar `main_compilation.py` con `gacha_api_compile.py`
**Para desarrolladores**: Pueden usar cualquiera de los dos, pero `main.py` es más simple para desarrollo

El programa se compila con el siguiente comando. Requiere pyinstaller y antes de eso pip si no están instalados

```bash
pyinstaller --onefile --windowed --noconfirm --clean ^
--add-data "config.json;." ^
--add-data "data/*.json;data/" ^
--add-data "localizations/*.json;localizations/" ^
--add-data "Lenna.ico;." ^
--icon "Lenna.ico" ^
--name "Vertebrae EN" ^
main_compilation.py
```