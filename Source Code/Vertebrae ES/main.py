import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
import math
import json
import os

# Importar nuestro módulo funcional
from gacha_api import (
    SimpleGachaBackup, get_all_pages_for_type, get_banner_name, 
    get_item_name, get_item_type, DataManager, SERVERS, 
    get_server_display_name, ConfigManager, LocalizationManager, _
)

class GachaTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(_("ui.title"))
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        # Sistema de backup
        self.backup = SimpleGachaBackup()
        self.is_importing = False
        
        # Cargar datos al inicio
        self.data_manager = DataManager()
        self.dolls_data = self.data_manager.load_dolls()
        self.weapons_data = self.data_manager.load_weapons()
        self.mbox_data = self.data_manager.load_mbox()
        
        # Cargar idioma desde configuración
        self.current_language = ConfigManager.get_setting('default_language', 'ES')
        LocalizationManager.set_language(self.current_language)
        
        # Datos para filtros
        self.all_records = []
        self.current_stats = None
        
        self.setup_ui()
        self.create_menu()
        self.update_status_bar()
        
        # Cargar historial automáticamente después de que la interfaz esté lista
        self.root.after(500, self.auto_load_data)
        
    def auto_load_data(self):
        """Carga automáticamente el historial y estadísticas al iniciar"""
        try:
            self.load_history()
            self.update_stats_display()
            print("✅ Historial y estadísticas cargados automáticamente")
        except Exception as e:
            print(f"❌ Error cargando datos automáticamente: {e}")
    
    def create_menu(self):
        """Crea la barra de menú"""
        menubar = tk.Menu(self.root)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=_("ui.settings"), command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label=_("ui.exit"), command=self.root.quit)
        menubar.add_cascade(label=_("ui.file_menu"), menu=file_menu)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=_("ui.about"), command=self.show_about)
        menubar.add_cascade(label=_("ui.help_menu"), menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def show_settings(self):
        """Muestra la ventana de configuración"""
        self.create_settings_window()
    
    def show_about(self):
        """Muestra información acerca de la aplicación"""
        messagebox.showinfo(_("ui.about"), "Vertebrae - Girl's Frontline 2 Pull Tracker\n\nVersión 0.1\nCreado con Python y Tkinter")
    
    def create_settings_window(self):
        """Crea la ventana de configuración"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title(_("ui.settings") + " - Vertebrae")
        settings_window.geometry("500x350")
        settings_window.resizable(True, True)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Centrar ventana
        settings_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - settings_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - settings_window.winfo_height()) // 2
        settings_window.geometry(f"+{x}+{y}")
        
        # Cargar configuración actual
        config = ConfigManager.load_config()
        settings = config['settings']
        
        # Variables de control
        page_limit_var = tk.StringVar(value=str(settings['page_limit']))
        timeout_var = tk.StringVar(value=str(settings['request_timeout']))
        retries_var = tk.StringVar(value=str(settings['max_retries']))
        language_var = tk.StringVar(value=settings['default_language'])
        theme_var = tk.StringVar(value=settings['theme'])
        
        # Frame principal con scroll
        main_frame = ttk.Frame(settings_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_frame, text=_("ui.settings") + " - Vertebrae", 
                  font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Configuración de API
        api_frame = ttk.LabelFrame(main_frame, text="Configuración de API", padding=10)
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Límite de páginas
        ttk.Label(api_frame, text="Límite de páginas:").grid(row=0, column=0, sticky=tk.W, pady=2)
        page_entry = ttk.Entry(api_frame, textvariable=page_limit_var, width=15)
        page_entry.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        ttk.Label(api_frame, text="-1 = Sin límite. 1 página = 6 pulls").grid(row=0, column=2, sticky=tk.W, padx=(5,0))
        
        # Timeout
        ttk.Label(api_frame, text="Timeout (segundos):").grid(row=1, column=0, sticky=tk.W, pady=2)
        timeout_spinbox = ttk.Spinbox(api_frame, from_=5, to=60, textvariable=timeout_var, width=10)
        timeout_spinbox.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Intentos
        ttk.Label(api_frame, text="Máximo de reintentos:").grid(row=2, column=0, sticky=tk.W, pady=2)
        retries_spinbox = ttk.Spinbox(api_frame, from_=1, to=10, textvariable=retries_var, width=10)
        retries_spinbox.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Configuración de Aplicación
        app_frame = ttk.LabelFrame(main_frame, text="Configuración de Aplicación", padding=10)
        app_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Idioma
        ttk.Label(app_frame, text="Idioma (Work in Progress):").grid(row=0, column=0, sticky=tk.W, pady=2)
        language_combo = ttk.Combobox(app_frame, textvariable=language_var, 
                                     values=["ES", "EN"], state="readonly", width=10)
        language_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Tema
        ttk.Label(app_frame, text="Tema (Placeholder):").grid(row=1, column=0, sticky=tk.W, pady=2)
        theme_combo = ttk.Combobox(app_frame, textvariable=theme_var, 
                                  values=["Sistema", "Blanco", "Oscuro"], state="readonly", width=10)
        theme_combo.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        def save_settings():
            """Guarda la configuración"""
            try:
                # Validar límite de páginas
                page_limit_str = page_limit_var.get().strip()
                if page_limit_str == "-1":
                    page_limit = -1
                else:
                    page_limit = int(page_limit_str)
                    if page_limit < 1:
                        messagebox.showerror("Error", "El Límite de páginas debe ser -1 (sin límite) o un número positivo")
                        return
                
                new_settings = {
                    'page_limit': page_limit,
                    'request_timeout': int(timeout_var.get()),
                    'max_retries': int(retries_var.get()),
                    'default_language': language_var.get(),
                    'theme': theme_var.get()
                }
                
                # Aplicar tema inmediatamente
                old_theme = ConfigManager.get_setting('theme')
                if theme_var.get() != old_theme:
                    self.change_theme(theme_var.get())
                
                # Guardar configuración
                config['settings'] = new_settings
                ConfigManager._config = config
                if ConfigManager.save_config():
                    # Actualizar idioma si cambió
                    if language_var.get() != self.current_language:
                        self.current_language = language_var.get()
                        LocalizationManager.set_language(self.current_language)
                        self.refresh_ui_texts()
                        messagebox.showinfo("Éxito", "Opciones guardadas. Reinicia la app para aplicar los cambios de idioma.")
                        settings_window.destroy()
                        self.root.after(1000, self.restart_app)
                    else:
                        messagebox.showinfo("Éxito", "Opciones guardadas")
                        settings_window.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo guardar los cambios")
                    
            except ValueError as e:
                messagebox.showerror("Error", "Por favor introduce un valor válido\n-1 = Sin límite\nNúmero positivo = Limite específico")
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando: {str(e)}")
        
        def reset_settings():
            """Restablece configuración por defecto"""
            if messagebox.askyesno("Confirmar", "Reiniciar los valores por defecto?"):
                default_config = {
                    "version": 1,
                    "settings": {
                        "page_limit": 50,
                        "request_timeout": 20,
                        "max_retries": 3,
                        "default_language": "ES",
                        "theme": "system"
                    }
                }
                ConfigManager._config = default_config
                ConfigManager.save_config()
                messagebox.showinfo("Éxito", "Opciones reiniciadas a los valores por defecto")
                settings_window.destroy()
        
        ttk.Button(button_frame, text="Guardar", command=save_settings).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Por defecto", command=reset_settings).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cancelar", command=settings_window.destroy).pack(side=tk.RIGHT, padx=(0, 10))
        
        return settings_window
    
    def change_theme(self, theme):
        """Cambia el tema de la aplicación"""
        # Implementación del cambio de tema
        pass
    
    def restart_app(self):
        """Reinicia la aplicación"""
        # Implementación del reinicio
        pass
    
    def refresh_ui_texts(self):
        """Actualiza todos los textos de la interfaz cuando cambia el idioma"""
        # Actualizar título de la ventana
        self.root.title(_("ui.title"))
        
        # Actualizar textos de pestañas
        self.notebook.tab(0, text=_("ui.import_tab"))
        self.notebook.tab(1, text=_("ui.history_tab"))
        self.notebook.tab(2, text=_("ui.stats_tab"))
        
        # Actualizar barra de menú
        self.create_menu()
        
        # Actualizar barra de estado
        self.update_status_bar()
        
        # Recargar datos para actualizar nombres traducidos
        self.load_history()
        self.update_stats_display()
    
    def setup_ui(self):
        """Configura la interfaz principal con pestañas"""
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))
        
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        header_frame = ttk.Frame(main_container)
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        title_label = ttk.Label(header_frame, text=_("ui.title"), 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, sticky='w')
        
        help_btn = ttk.Button(header_frame, text="?", width=3, 
                             command=self.show_help, style='Help.TButton')
        help_btn.grid(row=0, column=1, sticky='e', padx=(10, 0))
        
        style.configure('Help.TButton', font=('Arial', 12, 'bold'))
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=1, column=0, sticky='nsew')
        
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        self.setup_import_tab()
        self.setup_history_tab()
        self.setup_stats_tab()
        
        self.setup_status_bar()
        
        self.root.bind('<Configure>', self.on_window_resize)
        
    def show_help(self):
        """Muestra información de ayuda al usuario"""
        help_text = """🎮 **GUÍA RÁPIDA - VERTEBRAE GACHA TRACKER**

**📥 IMPORTACIÓN DE DATOS:**
• Obtén tu token desde el juego usando Fiddler Classic
• Introduce tu email y selecciona tu servidor
• Si juegas en Haoplay y no sabes cúal es tu región exacta, prueba una a una. No tendrás que volver a introducir tus datos por hacer esto
• Haz click en \"🚀 Iniciar Importación\"

**📥 TUTORIAL DE FIDDLER:**
Paso 1: Descarga e instala Fiddler Classic: https://www.telerik.com/download/fiddler (Puedes mentir en la encuesta **guiño guiño**)
Paso 2: Ejecuta el programa
Paso 3: Ejecuta Girls Frontline 2
Paso 4: En la sección de banners, toca "Detalles". No importa en qué banner lo hagas
Paso 5: Vuelve a Fiddler, y en la lista de la izquierda, busca una entrada que comienza con "https://gf2-gacha-record". Haz click sobre ella
Paso 5.5: Si no encuentras la entrada, espera un poco. A veces puede ser lento
Paso 6: Busca el botón "Headers", en la parte superior del programa. Haz click sobre él
Paso 7: En la lista debajo de la barra de herramientas, busca una entrada llamada "Authorization". Click derecho, "Copy values only". Ese es tu token. Puedes pegarlo en este programa, removiendo la parte de "Authorization:" y el espacio. Deja solo el token largo

**📜 FUNCIONES: HISTORIAL**
• Filtra por banner, rareza o nombre de item
• Usa la búsqueda para encontrar items específicos
• Los datos no se duplican (En teoria :p)

**📊 FUNCIONES: ESTADÍSTICAS:**
• Distribución visual de tus tiradas por banner
• Total de tiradas y multis detectadas
• Rango temporal de tus pulls

**💡 CONSEJOS:**
• El token expira cada 24h más o menos - renuévalo cuando sea necesario
• Una vez hechas las tiradas, los datos tardan una hora aprox. en estar disponibles para su importación. Esto es una limitación del juego
• Solo se pueden importar tiradas de menos de 6 meses de antiguedad. Si quieres conservar tu historial, empieza cuando antes
• Los datos se guardan localmente en el archivo backup.json

**🛠️ COMENTARIOS:**
• Este programa no recoge, almacena ni envía datos a ningún lugar fuera de tu PC, exceptuando a los servidores de Girls Frontline 2 (duh)
• Dado que usa el mismo método de obtención de historial que el propio juego, no existe riesgo real de baneo
• Aún así, por mi seguridad, NO me hago responsable de las consecuencias causadas por ningún uso que le des a este programa
• Vertebrae es un programa en desarrollo. Nuevas funciones y mejoras serán (quizás) añadidas en el futuro
• Si tienes un error, una pregunta, o crees que puedes ayudar, dilo a través de github; te estaré agradecido si lo haces

¿Necesitas más ayuda? Visita la documentación del proyecto.

⚠️  **IMPORTANTE**: Este proyecto no está afiliado, respaldado ni autorizado 
por Sunborn Network Technology Co., MICA Team, o "Girl's Frontline 2: Exilium". 
Es un proyecto de un fan para fans
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Ayuda - Vertebrae Gacha Tracker")
        help_window.geometry("600x500")
        help_window.minsize(500, 400)
        help_window.transient(self.root)
        help_window.grab_set()
        
        main_frame = ttk.Frame(help_window, padding=15)
        main_frame.pack(fill='both', expand=True)
        
        title_label = ttk.Label(main_frame, text="🎮 Guía de Usuario", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 15))
        
        help_text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                                    font=('Arial', 10), 
                                                    padx=10, pady=10,
                                                    height=20)
        help_text_widget.pack(fill='both', expand=True)
        help_text_widget.insert('1.0', help_text)
        help_text_widget.config(state='disabled')
        
        ttk.Button(main_frame, text="Cerrar", 
                  command=help_window.destroy).pack(pady=(15, 0))
        
        help_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (help_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (help_window.winfo_height() // 2)
        help_window.geometry(f"+{x}+{y}")
        
    def on_window_resize(self, event):
        """Se ejecuta cuando se redimensiona la ventana"""
        if (hasattr(self, 'current_stats') and self.current_stats and 
            self.notebook.tab(self.notebook.select(), "text") == _("ui.stats_tab")):
            if hasattr(self, '_resize_after_id'):
                self.root.after_cancel(self._resize_after_id)
            self._resize_after_id = self.root.after(200, self.redraw_pie_chart)
        
    def redraw_pie_chart(self):
        """Redibuja el gráfico de pastel con las estadísticas actuales"""
        if self.current_stats:
            self.create_pie_chart(self.current_stats)
        
    def on_tab_changed(self, event):
        """Se ejecuta cuando se cambia de pestaña"""
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        
        if current_tab == _("ui.history_tab"):
            if hasattr(self, 'all_records'):
                filtered_count = len(self.history_tree.get_children())
                total_count = len(self.all_records)
                if filtered_count == total_count:
                    self.status_label.config(text=_(f"messages.showing_all").format(count=total_count))
                else:
                    self.status_label.config(text=_(f"messages.filtered").format(filtered=filtered_count, total=total_count))
        elif current_tab == _("ui.stats_tab"):
            if hasattr(self, 'current_stats') and self.current_stats:
                self.root.after(100, lambda: self.create_pie_chart(self.current_stats))
        else:
            self.update_status_bar()
        
    def setup_import_tab(self):
        """Pestaña de importación de datos""" 
        self.import_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.import_tab, text=_("ui.import_tab"))
        
        self.import_tab.grid_rowconfigure(1, weight=1)
        self.import_tab.grid_columnconfigure(0, weight=1)
        
        title_label = ttk.Label(self.import_tab, text=_("ui.import_title"), 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        
        config_frame = ttk.LabelFrame(self.import_tab, text=_("ui.account_data"), padding=15)
        config_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 10))
        
        config_frame.grid_rowconfigure(0, weight=0)
        config_frame.grid_rowconfigure(1, weight=0)
        config_frame.grid_rowconfigure(2, weight=0)
        config_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(config_frame, text=_("ui.auth_token"), font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='nw', pady=8)
        self.token_entry = scrolledtext.ScrolledText(config_frame, height=4, font=('Consolas', 9))
        self.token_entry.grid(row=0, column=1, padx=10, pady=8, sticky='ew')
        
        ttk.Label(config_frame, text=_("ui.email"), font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='nw', pady=8)
        self.email_entry = ttk.Entry(config_frame, font=('Arial', 10))
        self.email_entry.grid(row=1, column=1, padx=10, pady=8, sticky='ew')
        
        ttk.Label(config_frame, text=_("ui.server"), font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='nw', pady=8)
        
        server_names = [config["name"] for config in SERVERS.values()]
        self.server_combobox = ttk.Combobox(config_frame, values=server_names, width=30, font=('Arial', 10))
        self.server_combobox.set("Darkwinter (US/EU)")
        self.server_combobox.grid(row=2, column=1, padx=10, pady=8, sticky='w')
        
        bottom_frame = ttk.Frame(self.import_tab)
        bottom_frame.grid(row=2, column=0, sticky='nsew', pady=(0, 10))
        
        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(1, weight=0)
        bottom_frame.grid_columnconfigure(0, weight=1)
        
        progress_frame = ttk.LabelFrame(bottom_frame, text=_("ui.import_progress"), padding=15)
        progress_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        
        progress_frame.grid_rowconfigure(1, weight=1)
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        self.import_log = scrolledtext.ScrolledText(progress_frame, height=8, state='disabled', 
                                                   font=('Consolas', 9), wrap=tk.WORD)
        self.import_log.grid(row=1, column=0, sticky='nsew')
        
        button_frame = ttk.Frame(bottom_frame)
        button_frame.grid(row=1, column=0, sticky='ew', pady=10)
        
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=0)
        button_frame.grid_columnconfigure(2, weight=0)
        button_frame.grid_columnconfigure(3, weight=0)
        button_frame.grid_columnconfigure(4, weight=1)
        
        self.import_btn = ttk.Button(button_frame, text=_("ui.start_import"), 
                                   command=self.start_import)
        self.import_btn.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text=_("ui.view_stats"), 
                  command=self.show_stats).grid(row=0, column=2, padx=5)
        
        ttk.Button(button_frame, text=_("ui.clear_log"), 
                  command=self.clear_log).grid(row=0, column=3, padx=5)
        
    def setup_history_tab(self):
        """Pestaña de historial de tiradas"""
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text=_("ui.history_tab"))
        
        self.history_tab.grid_rowconfigure(1, weight=1)
        self.history_tab.grid_columnconfigure(0, weight=1)
        
        controls_frame = ttk.Frame(self.history_tab)
        controls_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        # FILTRO POR BANNER
        ttk.Label(controls_frame, text=_("ui.banner_filter")).pack(side='left', padx=(0, 5))
        self.banner_filter = ttk.Combobox(controls_frame, 
                                         values=[_("filters.all"), _("banners.characters"), _("banners.weapons"), 
                                                _("banners.permanent"), _("banners.beginner"), _("banners.mystery_box"), 
                                                _("banners.special"), _("banners.event")], 
                                         width=12)
        self.banner_filter.set(_("filters.all"))
        self.banner_filter.pack(side='left', padx=(0, 15))
        self.banner_filter.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # FILTRO POR TIPO
        ttk.Label(controls_frame, text=_("ui.type_filter")).pack(side='left', padx=(0, 5))
        self.type_filter = ttk.Combobox(controls_frame, 
                                       values=[_("filters.all"), _("filters.characters"), _("filters.weapons"), _("filters.items")], 
                                       width=8)
        self.type_filter.set(_("filters.all"))
        self.type_filter.pack(side='left', padx=(0, 15))
        self.type_filter.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # FILTRO POR RAREZA
        ttk.Label(controls_frame, text=_("ui.rarity_filter")).pack(side='left', padx=(0, 5))
        self.rarity_filter = ttk.Combobox(controls_frame, 
                                         values=[_("filters.all_rarities"), _("filters.3_star"), _("filters.4_star"), _("filters.5_star")], 
                                         width=8)
        self.rarity_filter.set(_("filters.all_rarities"))
        self.rarity_filter.pack(side='left', padx=(0, 15))
        self.rarity_filter.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Búsqueda por texto
        ttk.Label(controls_frame, text=_("ui.search")).pack(side='left', padx=(0, 5))
        self.search_entry = ttk.Entry(controls_frame, width=20)
        self.search_entry.pack(side='left', padx=(0, 15))
        self.search_entry.bind('<KeyRelease>', self.apply_filters)
        
        # Botones
        ttk.Button(controls_frame, text=_("ui.refresh"), command=self.load_history).pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text=_("ui.clear_filters"), command=self.clear_filters).pack(side='left')
        
        tree_frame = ttk.Frame(self.history_tab)
        tree_frame.grid(row=1, column=0, sticky='nsew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(1, weight=0)
        
        columns = ('Fecha', 'Hora', _("ui.banner_filter"), 'Item', _("ui.type_filter"), _("ui.rarity_filter"))
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=25)
        
        column_widths = {'Fecha': 100, 'Hora': 80, _("ui.banner_filter"): 120, 'Item': 250, _("ui.type_filter"): 80, _("ui.rarity_filter"): 70}
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=column_widths.get(col, 100))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
    def setup_stats_tab(self):
        """Pestaña de estadísticas"""
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text=_("ui.stats_tab"))
        
        self.stats_tab.grid_rowconfigure(0, weight=1)
        self.stats_tab.grid_columnconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self.stats_tab)
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        text_frame = ttk.LabelFrame(main_frame, text=_("ui.detailed_stats"), padding=10)
        text_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        self.stats_text = scrolledtext.ScrolledText(text_frame, height=20, state='disabled', 
                                                   font=('Arial', 9), wrap=tk.WORD)
        self.stats_text.grid(row=0, column=0, sticky='nsew')
        
        graph_frame = ttk.LabelFrame(main_frame, text=_("ui.banner_distribution"), padding=10)
        graph_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
        graph_frame.grid_rowconfigure(0, weight=1)
        graph_frame.grid_rowconfigure(1, weight=0)
        graph_frame.grid_columnconfigure(0, weight=1)
        
        self.graph_container = ttk.Frame(graph_frame)
        self.graph_container.grid(row=0, column=0, sticky='nsew')
        
        self.graph_container.grid_rowconfigure(0, weight=1)
        self.graph_container.grid_columnconfigure(0, weight=1)
        
        self.pie_canvas = tk.Canvas(self.graph_container, bg='white', highlightthickness=1, 
                                   highlightbackground='#cccccc')
        self.pie_canvas.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        self.legend_frame = ttk.Frame(graph_frame)
        self.legend_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=(0, 5))
        self.legend_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Button(main_frame, text=_("ui.update_stats"), 
                  command=self.update_stats_display).grid(row=1, column=0, columnspan=2, pady=10)
        
    def setup_status_bar(self):
        """Barra de estado inferior"""
        self.status_frame = ttk.Frame(self.root, relief='sunken', padding=5)
        self.status_frame.pack(fill='x', side='bottom')
        
        self.status_label = ttk.Label(self.status_frame, text=_("ui.ready"))
        self.status_label.pack(side='left', padx=5)
        
        stats = self.backup.get_statistics()
        self.record_count_label = ttk.Label(self.status_frame, text=_(f"ui.pulls").format(count=stats['total_records']))
        self.record_count_label.pack(side='right', padx=5)
        
    def get_rarity_display(self, rarity):
        """Convierte número de rareza a solo estrellas"""
        return "★" * rarity
        
    def get_server_code_from_name(self, display_name):
        """Obtiene el código del servidor a partir del nombre para mostrar"""
        for code, config in SERVERS.items():
            if config["name"] == display_name:
                return code
        return "darkwinter"
        
    def get_item_type_display(self, item_id):
        """Determina el tipo de item basado en los diccionarios"""
        if item_id in self.dolls_data:
            return _("filters.characters")
        elif item_id in self.weapons_data:
            return _("filters.weapons")
        elif item_id in self.mbox_data:
            return _("filters.items")
        else:
            return "Desconocido"
        
    def apply_filters(self, event=None):
        """Aplica los filtros de búsqueda, banner, tipo y rareza"""
        if not self.all_records:
            return
            
        search_text = self.search_entry.get().lower()
        selected_banner = self.banner_filter.get()
        selected_type = self.type_filter.get()
        selected_rarity = self.rarity_filter.get()
        
        # Limpiar tabla actual
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        filtered_count = 0
        for record in self.all_records:
            # Obtener información del registro
            banner_name = get_banner_name(record['pool_id'])
            item_name, rarity = get_item_name(record['item'])
            item_type = self.get_item_type_display(record['item'])
            rarity_display = self.get_rarity_display(rarity)
            
            # FILTRO POR BANNER
            if selected_banner != _("filters.all"):
                # Manejar caso especial de "Promocional" vs "Personajes"
                if selected_banner == _("banners.characters"):
                    # Para filtro "Personajes", mostrar tanto "Promocional" como "Personajes"
                    if banner_name not in [_("banners.promotional"), _("banners.characters")]:
                        continue
                elif selected_banner != banner_name:
                    continue
                        
            # FILTRO POR TIPO
            if selected_type != _("filters.all"):
                if selected_type == _("filters.characters") and item_type != _("filters.characters"):
                    continue
                elif selected_type == _("filters.weapons") and item_type != _("filters.weapons"):
                    continue
                elif selected_type == _("filters.items") and item_type != _("filters.items"):
                    continue
                
            # FILTRO POR RAREZA
            if selected_rarity != _("filters.all_rarities"):
                rarity_map = {_("filters.3_star"): 3, _("filters.4_star"): 4, _("filters.5_star"): 5}
                target_rarity = rarity_map.get(selected_rarity)
                if rarity != target_rarity:
                    continue
                
            # Filtrar por búsqueda de texto
            if search_text and search_text not in item_name.lower():
                continue
                
            # Si pasa los filtros, agregar a la tabla
            dt = datetime.fromtimestamp(record['time'])
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M:%S")
            
            self.history_tree.insert('', 'end', values=(
                date_str, time_str, banner_name, item_name, item_type, rarity_display
            ))
            filtered_count += 1
            
        # Actualizar barra de estado
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab == _("ui.history_tab"):
            total_count = len(self.all_records)
            if filtered_count == total_count:
                self.status_label.config(text=_(f"messages.showing_all").format(count=total_count))
            else:
                self.status_label.config(text=_(f"messages.filtered").format(filtered=filtered_count, total=total_count))
        
    def clear_filters(self):
        """Limpia todos los filtros y muestra todos los registros"""
        self.search_entry.delete(0, 'end')
        self.banner_filter.set(_("filters.all"))
        self.type_filter.set(_("filters.all"))
        self.rarity_filter.set(_("filters.all_rarities"))
        self.apply_filters()
        
    def _draw_no_data_message(self):
        """Dibuja mensaje de no datos en el canvas"""
        canvas_width = self.pie_canvas.winfo_width()
        canvas_height = self.pie_canvas.winfo_height()
        
        if canvas_width > 10 and canvas_height > 10:
            self.pie_canvas.delete("all")
            self.pie_canvas.create_text(
                canvas_width // 2, canvas_height // 2,
                text=_(f"messages.no_data"), 
                font=('Arial', 12), fill='gray', justify='center'
            )
        
    def create_pie_chart(self, stats):
        """Crea un gráfico de pastel usando tkinter Canvas"""
        self.pie_canvas.delete("all")
        for widget in self.legend_frame.winfo_children():
            widget.destroy()
            
        if not stats['banners'] or stats['total_records'] == 0:
            self.root.after(100, self._draw_no_data_message)
            return
        
        banner_groups = {}
        for banner_id, count in stats['banners'].items():
            banner_name = get_banner_name(banner_id)
            if banner_name in banner_groups:
                banner_groups[banner_name] += count
            else:
                banner_groups[banner_name] = count
        
        banners = list(banner_groups.keys())
        counts = list(banner_groups.values())
        total = sum(counts)
        
        self.pie_canvas.update_idletasks()
        canvas_width = self.pie_canvas.winfo_width()
        canvas_height = self.pie_canvas.winfo_height()
        
        if canvas_width < 50 or canvas_height < 50:
            container_width = self.graph_container.winfo_width()
            container_height = self.graph_container.winfo_height()
            
            if container_width > 50 and container_height > 50:
                canvas_width = container_width - 20
                canvas_height = container_height - 20
            else:
                canvas_width = 200
                canvas_height = 200
        
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        radius = min(center_x, center_y) - 30
        
        if radius < 10:
            radius = min(canvas_width, canvas_height) // 3
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
        
        if len(banners) == 1:
            banner_name = banners[0]
            count = counts[0]
            
            self.pie_canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill=colors[0], outline='white', width=2
            )
            
            font_size = max(10, min(14, radius // 10))
            self.pie_canvas.create_text(
                center_x, center_y,
                text=f"100%\n{banner_name}",
                font=('Arial', font_size, 'bold'),
                fill='white',
                justify='center'
            )
            
        else:
            start_angle = 0
            for i, count in enumerate(counts):
                percentage = (count / total) * 100
                angle = 360 * (count / total)
                
                if angle > 0:
                    self.pie_canvas.create_arc(
                        center_x - radius, center_y - radius,
                        center_x + radius, center_y + radius,
                        start=start_angle, extent=angle,
                        fill=colors[i % len(colors)], 
                        outline='white', 
                        width=1,
                        style=tk.PIESLICE
                    )
                    
                    if angle > 15 and radius > 30:
                        mid_angle = start_angle + angle / 2
                        mid_angle_rad = math.radians(mid_angle)
                        label_x = center_x + (radius * 0.7) * math.cos(mid_angle_rad)
                        label_y = center_y + (radius * 0.7) * math.sin(mid_angle_rad)
                        
                        font_size = max(8, min(12, radius // 15))
                        self.pie_canvas.create_text(
                            label_x, label_y, 
                            text=f"{percentage:.1f}%", 
                            font=('Arial', font_size, 'bold'), 
                            fill='white'
                        )
                    
                    start_angle += angle
        
        for i, (banner, count) in enumerate(zip(banners, counts)):
            percentage = (count / total) * 100
            
            legend_item_frame = ttk.Frame(self.legend_frame)
            legend_item_frame.pack(fill='x', padx=5, pady=1)
            
            color_canvas = tk.Canvas(legend_item_frame, width=16, height=16, highlightthickness=0)
            color_canvas.pack(side='left', padx=(0, 5))
            color_canvas.create_rectangle(2, 2, 14, 14, fill=colors[i % len(colors)], outline='#666666')
            
            legend_text = f"{banner}: {count} ({percentage:.1f}%)"
            legend_label = ttk.Label(legend_item_frame, text=legend_text, font=('Arial', 8))
            legend_label.pack(side='left', fill='x', expand=True)
        
        self.pie_canvas.update_idletasks()
        
    def log_message(self, message):
        """Agrega mensaje al log de importación"""
        self.import_log.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.import_log.insert('end', f"[{timestamp}] {message}\n")
        self.import_log.see('end')
        self.import_log.config(state='disabled')
        self.root.update_idletasks()
        
    def clear_log(self):
        """Limpia el log de importación"""
        self.import_log.config(state='normal')
        self.import_log.delete('1.0', 'end')
        self.import_log.config(state='disabled')
        
    def start_import(self):
        """Inicia la importación en un hilo separado"""
        if self.is_importing:
            messagebox.showwarning("Importación en curso", "Ya hay una importación en progreso.")
            return
            
        token = self.token_entry.get('1.0', 'end').strip()
        email = self.email_entry.get().strip()
        server_display_name = self.server_combobox.get()
        
        server_code = self.get_server_code_from_name(server_display_name)
        
        if not token or not email:
            messagebox.showerror("Error", "Token y email son obligatorios.")
            return
            
        self.is_importing = True
        self.import_btn.config(state='disabled')
        self.progress_bar.start()
        self.clear_log()
        
        thread = threading.Thread(target=self.run_import, args=(token, email, server_code))
        thread.daemon = True
        thread.start()
        
    def run_import(self, token, email, server_code):
        """Ejecuta la importación (en hilo separado)"""
        try:
            server_display_name = get_server_display_name(server_code)
            
            self.log_message(_("messages.import_started"))
            self.log_message(f"Email: {email}")
            self.log_message(f"Servidor: {server_display_name}")
            self.log_message(f"Código de servidor: {server_code}")
            
            # Mostrar configuración actual
            page_limit = ConfigManager.get_setting('page_limit', 50)
            if page_limit == -1:
                self.log_message(f"⚡ Configuración: MODO SIN LÍMITE de páginas")
            else:
                self.log_message(f"⚡ Configuración: Límite de {page_limit} páginas")
            
            stats = self.backup.get_statistics()
            self.log_message(f"📊 ESTADO ACTUAL: {stats['total_records']} tiradas, {stats['multi_count']} multis")
            
            type_ids_to_check = ['1', '3', '4', '5', '8']
            all_new_raw_records = []
            
            for type_id in type_ids_to_check:
                self.log_message(f"🎯 Obteniendo type_id {type_id}...")
                records = get_all_pages_for_type(token, email, type_id, server_code, self.log_message)
                if records:
                    all_new_raw_records.extend(records)
                    self.log_message(f"   ✅ {len(records)} tiradas obtenidas")
                else:
                    self.log_message(f"   ℹ️  Sin datos")
            
            if all_new_raw_records:
                added_count = self.backup.add_new_records(all_new_raw_records)
                
                self.log_message(f"\n📊 RESULTADO FINAL:")
                self.log_message(f"   Tiradas del servidor: {len(all_new_raw_records)}")
                self.log_message(f"   Nuevas tiradas agregadas: {added_count}")
                self.log_message(f"   Duplicados omitidos: {len(all_new_raw_records) - added_count}")
                
                self.root.after(0, self.on_import_success, added_count)
                
            else:
                self.log_message(_("messages.no_new_data"))
                self.root.after(0, self.on_import_finished)
                
        except Exception as e:
            self.log_message(f"❌ ERROR: {str(e)}")
            self.root.after(0, self.on_import_error, str(e))
            
    def on_import_success(self, added_count):
        """Cuando la importación termina exitosamente"""
        self.progress_bar.stop()
        self.import_btn.config(state='normal')
        self.is_importing = False
        
        self.update_status_bar()
        self.load_history()
        self.update_stats_display()
        
        self.status_label.config(text=_(f"messages.import_success").format(count=added_count))
        messagebox.showinfo("Importación Exitosa", 
                          f"Se agregaron {added_count} nuevas tiradas al historial.")
        
    def on_import_finished(self):
        """Cuando la importación termina sin nuevos datos"""
        self.progress_bar.stop()
        self.import_btn.config(state='normal')
        self.is_importing = False
        self.update_status_bar()
        self.status_label.config(text=_("messages.import_finished"))
        
    def on_import_error(self, error_msg):
        """Cuando ocurre un error en la importación"""
        self.progress_bar.stop()
        self.import_btn.config(state='normal')
        self.is_importing = False
        self.status_label.config(text=_("messages.import_error"))
        messagebox.showerror("Error de Importación", f"Ocurrió un error:\n{error_msg}")
        
    def update_status_bar(self):
        """Actualiza la barra de estado con información actual"""
        stats = self.backup.get_statistics()
        self.record_count_label.config(text=_(f"ui.pulls").format(count=stats['total_records']))
        self.status_label.config(text=_("ui.ready"))
        
    def load_history(self):
        """Carga el historial en la tabla"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        try:
            records = self.backup.get_all_records()
            self.all_records = records.copy()
            
            records.sort(key=lambda x: x['time'], reverse=True)
            
            for record in records[:1000]:
                dt = datetime.fromtimestamp(record['time'])
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M:%S")
                banner_name = get_banner_name(record['pool_id'])
                item_name, rarity = get_item_name(record['item'])
                item_type = self.get_item_type_display(record['item'])
                rarity_display = self.get_rarity_display(rarity)
                
                self.history_tree.insert('', 'end', values=(
                    date_str, time_str, banner_name, item_name, item_type, rarity_display
                ))
            
            self.update_status_bar()
            
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            if current_tab == _("ui.history_tab"):
                total_count = len(records)
                self.status_label.config(text=_(f"messages.showing_all").format(count=total_count))
            
        except Exception as e:
            print(f"Error cargando historial: {e}")
            
    def update_stats_display(self):
        """Actualiza la pestaña de estadísticas"""
        stats = self.backup.get_statistics()
        self.current_stats = stats
        
        banner_groups = {}
        for banner_id, count in stats['banners'].items():
            banner_name = get_banner_name(banner_id)
            if banner_name in banner_groups:
                banner_groups[banner_name] += count
            else:
                banner_groups[banner_name] = count
        
        stats_text = f"""📊 ESTADÍSTICAS DEL HISTORIAL

• Total de tiradas: {stats['total_records']}
• Multis detectadas: {stats['multi_count']}
• Última actualización: {stats.get('last_update', 'N/A')}

"""
        
        if stats['total_records'] > 0:
            stats_text += f"• Rango temporal: {stats.get('oldest', 'N/A')} - {stats.get('newest', 'N/A')}\n\n"
        
        stats_text += "🎯 DISTRIBUCIÓN POR BANNER:\n"
        
        if banner_groups:
            total_tiradas = stats['total_records']
            for banner_name, count in banner_groups.items():
                porcentaje = (count / total_tiradas) * 100 if total_tiradas > 0 else 0
                stats_text += f"   • {banner_name}: {count} tiradas ({porcentaje:.1f}%)\n"
        else:
            stats_text += "   No hay datos de banners\n"
            
        self.stats_text.config(state='normal')
        self.stats_text.delete('1.0', 'end')
        self.stats_text.insert('1.0', stats_text)
        self.stats_text.config(state='disabled')
        
        self.root.after(100, lambda: self.create_pie_chart(stats))
        
    def show_stats(self):
        """Muestra estadísticas rápidas en un messagebox"""
        stats = self.backup.get_statistics()
        
        banner_groups = {}
        for banner_id, count in stats['banners'].items():
            banner_name = get_banner_name(banner_id)
            if banner_name in banner_groups:
                banner_groups[banner_name] += count
            else:
                banner_groups[banner_name] = count
        
        stats_text = f"📊 ESTADÍSTICAS RÁPIDAS\n\n"
        stats_text += f"Total de tiradas: {stats['total_records']}\n"
        stats_text += f"Multis detectadas: {stats['multi_count']}\n"
        
        if banner_groups:
            stats_text += f"\nDistribución:\n"
            for banner_name, count in list(banner_groups.items())[:5]:
                stats_text += f"• {banner_name}: {count}\n"
            
        messagebox.showinfo("Estadísticas", stats_text)

def main():
    root = tk.Tk()
    app = GachaTrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()