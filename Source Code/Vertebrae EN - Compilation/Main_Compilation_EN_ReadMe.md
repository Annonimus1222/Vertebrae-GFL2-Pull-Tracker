Here's a clear comparison of the differences between `main.py` and `main_compile.py`:

## Key Differences

### 1. **PyInstaller Compatibility**
- **main.py**: Standard file paths
- **main_compile.py**: Implements `resource_path()` function for PyInstaller, using `sys._MEIPASS` for bundled executables

### 2. **Application Icon Handling**
- **main.py**: No icon loading code
- **main_compile.py**: Added icon loading with PyInstaller compatibility (This is broken, tho, as i used "icon.ico" as the file name instead of "Lenna.ico" :/
  ```python
  try:
      if getattr(sys, 'frozen', False):
          icon_path = resource_path('icon.ico')
      else:
          icon_path = 'icon.ico'
      
      if os.path.exists(icon_path):
          self.root.iconbitmap(icon_path)
  ```

### 3. **Settings Window Size**
- **main.py**: `settings_window.geometry("500x350")`
- **main_compile.py**: `settings_window.geometry("500x400")` (Taller, to accommodate new elements)

### 4. **Language Options Order**
- **main.py**: `values=["ES", "EN"]` (Spanish first)
- **main_compile.py**: `values=["EN", "ES"]` (English first)

### 5. **Language Selection Labels**
- **main.py**: "Language (Work in Progress):" and "Theme (Placeholder):"
- **main_compile.py**: Cleaner labels "Language:" and "Theme:" with status indicators in separate columns

### 6. **Settings Reset Button Text**
- **main.py**: "Default"
- **main_compile.py**: "Reset to Default" (more descriptive)

### 7. **Success Messages**
- **main.py**: "Options saved" / "Options reset to default values"
- **main_compile.py**: "Settings saved successfully" / "Settings reset to default values"

### 8. **Error Messages**
- **main.py**: "Error saving: {str(e)}"
- **main_compile.py**: "Error saving settings: {str(e)}" (more specific)

### 9. **Language Change Behavior** (It's some practice, for when i merge both versions)
- **main.py**: Attempts to restart application after language change
- **main_compile.py**: Asks user to restart manually instead of auto-restart

### 10. **Removed Methods**
- **main.py**: Contains `restart_app()` method (placeholder)
- **main_compile.py**: Removed `restart_app()` method entirely

### 11. **Import Statements**
- **main_compile.py**: Added `import sys` for PyInstaller detection
- **main.py**: No `sys` import needed

## Functional Impact

### **For End Users:**
- **main_compile.py** provides the executable packaging support
- Improved settings window layout with clearer labels
- More descriptive button texts and messages
- Manual restart requirement for language changes (more user-friendly)

### **For Developers:**
- **main_compile.py** is ready for PyInstaller packaging with proper resource handling (And a lot of spagghetti code, unfortunately. Do you like pasta?)
- **main.py** would still works, but it cannot be compiled into the .exe file while maintaining it fully funtionable

## Core Functionality Preservation

Both versions maintain identical:
- Three-tab interface (Import, History, Statistics)
- Data import functionality with all servers
- Filtering and search capabilities  
- Pie chart visualization
- Backup system integration
- Multi-pull detection
- Localization system

The differences are primarily focused on the **deployment readiness**, to make it a standalone app and **user experience improvements** rather than core functionality changes.

The app is compiled using this command. It requieres pyinstall and pip before installing that, if you don't have neither

```bash
pyinstaller --onefile --windowed --noconfirm --clean ^
--add-data "config.json;." ^
--add-data "data/*.json;data/" ^
--add-data "localizations/*.json;localizations/" ^
--add-data "Lenna.ico;." ^
--icon "Lenna.ico" ^
--name "Vertebrae EN" ^
main_compile.py
```