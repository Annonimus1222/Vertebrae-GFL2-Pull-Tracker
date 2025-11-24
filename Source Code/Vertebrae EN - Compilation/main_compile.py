import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
import math
import json
import os
import sys

# Import our functional module
from gacha_api_compile import (
    SimpleGachaBackup, get_all_pages_for_type, get_banner_name, 
    get_item_name, get_item_type, DataManager, SERVERS, 
    get_server_display_name, ConfigManager, LocalizationManager, _
)

def resource_path(relative_path):
    """Get the correct path for files in both development and EXE"""
    try:
        # PyInstaller creates a temporary folder in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class GachaTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(_("ui.title"))
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        # Try to load the icon
        try:
            if getattr(sys, 'frozen', False):
                # In the EXE
                icon_path = resource_path('icon.ico')
            else:
                # In development
                icon_path = 'icon.ico'
            
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                print(f"✅ Icon loaded: {icon_path}")
            else:
                print("⚠️  icon.ico file not found")
        except Exception as e:
            print(f"❌ Error loading icon: {e}")
        
        # Backup system
        self.backup = SimpleGachaBackup()
        self.is_importing = False
        
        # Load data at startup
        self.data_manager = DataManager()
        self.dolls_data = self.data_manager.load_dolls()
        self.weapons_data = self.data_manager.load_weapons()
        self.mbox_data = self.data_manager.load_mbox()
        
        # Load language from configuration
        self.current_language = ConfigManager.get_setting('default_language', 'EN')
        LocalizationManager.set_language(self.current_language)
        
        # Data for filters
        self.all_records = []
        self.current_stats = None
        
        self.setup_ui()
        self.create_menu()
        self.update_status_bar()
        
        # Automatically load history after the interface is ready
        self.root.after(500, self.auto_load_data)
        
    def auto_load_data(self):
        """Automatically loads history and statistics on startup"""
        try:
            self.load_history()
            self.update_stats_display()
            print("✅ History and statistics automatically loaded")
        except Exception as e:
            print(f"❌ Error automatically loading data: {e}")
    
    def create_menu(self):
        """Creates the menu bar"""
        menubar = tk.Menu(self.root)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=_("ui.settings"), command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label=_("ui.exit"), command=self.root.quit)
        menubar.add_cascade(label=_("ui.file_menu"), menu=file_menu)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=_("ui.about"), command=self.show_about)
        menubar.add_cascade(label=_("ui.help_menu"), menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def show_settings(self):
        """Shows the settings window"""
        self.create_settings_window()
    
    def show_about(self):
        """Shows information about the application"""
        messagebox.showinfo(_("ui.about"), 
                          "Vertebrae - Girl's Frontline 2 Pull Tracker\n\n"
                          "Version 0.1\n"
                          "Created with Python and Tkinter\n\n")
    
    def create_settings_window(self):
        """Creates the settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title(_("ui.settings") + " - Vertebrae")
        settings_window.geometry("500x400")
        settings_window.resizable(True, True)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center window
        settings_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - settings_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - settings_window.winfo_height()) // 2
        settings_window.geometry(f"+{x}+{y}")
        
        # Load current configuration
        config = ConfigManager.load_config()
        settings = config['settings']
        
        # Control variables
        page_limit_var = tk.StringVar(value=str(settings['page_limit']))
        timeout_var = tk.StringVar(value=str(settings['request_timeout']))
        retries_var = tk.StringVar(value=str(settings['max_retries']))
        language_var = tk.StringVar(value=settings['default_language'])
        theme_var = tk.StringVar(value=settings['theme'])
        
        # Main frame with scroll
        main_frame = ttk.Frame(settings_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        ttk.Label(main_frame, text=_("ui.settings") + " - Vertebrae", 
                  font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # API Configuration
        api_frame = ttk.LabelFrame(main_frame, text="API Configuration", padding=10)
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Page limit
        ttk.Label(api_frame, text="Page limit:").grid(row=0, column=0, sticky=tk.W, pady=2)
        page_entry = ttk.Entry(api_frame, textvariable=page_limit_var, width=15)
        page_entry.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        ttk.Label(api_frame, text="-1 = No limit. 1 page = 6 pulls").grid(row=0, column=2, sticky=tk.W, padx=(5,0))
        
        # Timeout
        ttk.Label(api_frame, text="Timeout (seconds):").grid(row=1, column=0, sticky=tk.W, pady=2)
        timeout_spinbox = ttk.Spinbox(api_frame, from_=5, to=60, textvariable=timeout_var, width=10)
        timeout_spinbox.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Retries
        ttk.Label(api_frame, text="Max retries:").grid(row=2, column=0, sticky=tk.W, pady=2)
        retries_spinbox = ttk.Spinbox(api_frame, from_=1, to=10, textvariable=retries_var, width=10)
        retries_spinbox.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Application Configuration
        app_frame = ttk.LabelFrame(main_frame, text="Application Configuration", padding=10)
        app_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Language
        ttk.Label(app_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, pady=2)
        language_combo = ttk.Combobox(app_frame, textvariable=language_var, 
                                     values=["EN", "ES"], state="readonly", width=10)
        language_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        ttk.Label(app_frame, text="Work in Progress").grid(row=0, column=2, sticky=tk.W, padx=(5,0))
        
        # Theme
        ttk.Label(app_frame, text="Theme:").grid(row=1, column=0, sticky=tk.W, pady=2)
        theme_combo = ttk.Combobox(app_frame, textvariable=theme_var, 
                                  values=["System", "Light", "Dark"], state="readonly", width=10)
        theme_combo.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        ttk.Label(app_frame, text="Placeholder").grid(row=1, column=2, sticky=tk.W, padx=(5,0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        def save_settings():
            """Saves the configuration"""
            try:
                # Validate page limit
                page_limit_str = page_limit_var.get().strip()
                if page_limit_str == "-1":
                    page_limit = -1
                else:
                    page_limit = int(page_limit_str)
                    if page_limit < 1:
                        messagebox.showerror("Error", "Page limit must be -1 (no limit) or a positive number")
                        return
                
                new_settings = {
                    'page_limit': page_limit,
                    'request_timeout': int(timeout_var.get()),
                    'max_retries': int(retries_var.get()),
                    'default_language': language_var.get(),
                    'theme': theme_var.get()
                }
                
                # Apply theme immediately
                old_theme = ConfigManager.get_setting('theme')
                if theme_var.get() != old_theme:
                    self.change_theme(theme_var.get())
                
                # Save configuration
                config['settings'] = new_settings
                ConfigManager._config = config
                if ConfigManager.save_config():
                    # Update language if changed
                    if language_var.get() != self.current_language:
                        self.current_language = language_var.get()
                        LocalizationManager.set_language(self.current_language)
                        self.refresh_ui_texts()
                        messagebox.showinfo("Success", "Settings saved. Please restart the application to apply language changes.")
                        settings_window.destroy()
                    else:
                        messagebox.showinfo("Success", "Settings saved successfully")
                        settings_window.destroy()
                else:
                    messagebox.showerror("Error", "Could not save changes")
                    
            except ValueError as e:
                messagebox.showerror("Error", "Please enter a valid value:\n-1 = No limit\nPositive number = Specific limit")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving settings: {str(e)}")
        
        def reset_settings():
            """Resets to default configuration"""
            if messagebox.askyesno("Confirm", "Reset all settings to default values?"):
                default_config = {
                    "version": 1,
                    "settings": {
                        "page_limit": 50,
                        "request_timeout": 20,
                        "max_retries": 3,
                        "default_language": "EN",
                        "theme": "system"
                    }
                }
                ConfigManager._config = default_config
                ConfigManager.save_config()
                messagebox.showinfo("Success", "Settings reset to default values")
                settings_window.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_settings).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Reset to Default", command=reset_settings).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.RIGHT, padx=(0, 10))
        
        return settings_window
    
    def change_theme(self, theme):
        """Changes the application theme"""
        # Theme change implementation (placeholder)
        print(f"Theme changed to: {theme}")
    
    def refresh_ui_texts(self):
        """Updates all interface texts when language changes"""
        # Update window title
        self.root.title(_("ui.title"))
        
        # Update tab texts
        self.notebook.tab(0, text=_("ui.import_tab"))
        self.notebook.tab(1, text=_("ui.history_tab"))
        self.notebook.tab(2, text=_("ui.stats_tab"))
        
        # Update menu bar
        self.create_menu()
        
        # Update status bar
        self.update_status_bar()
        
        # Reload data to update translated names
        self.load_history()
        self.update_stats_display()
    
    def setup_ui(self):
        """Sets up the main interface with tabs"""
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
        """Shows help information to the user"""
        help_text = """🎮 **QUICK GUIDE - VERTEBRAE GACHA TRACKER**

**📥 DATA IMPORT:**
• Get your token from the game using Fiddler Classic
• Enter your email and select your server
• If you play on Haoplay and don't know your exact region, try them one by one. You won't have to re-enter your data for doing this
• Click on \"🚀 Start Import\"

**📥 FIDDLER TUTORIAL:**
Step 1: Download and install Fiddler Classic: https://www.telerik.com/download/fiddler (You can lie on the survey **wink wink**)
Step 2: Run the program
Step 3: Run Girls Frontline 2
Step 4: In the banners section, tap "Details". It doesn't matter which banner you do it on
Step 5: Return to Fiddler, and in the list on the left, look for an entry that starts with "https://gf2-gacha-record". Click on it
Step 5.5: If you can't find the entry, wait a bit. It can sometimes be slow
Step 6: Look for the "Headers" button at the top of the program. Click on it
Step 7: In the list below the toolbar, look for an entry called "Authorization". Right-click, "Copy values only". That is your token. You can paste it into this program, removing the "Authorization:" part and the space. Keep only the long token

**📜 FUNCTIONS: HISTORY**
• Filter by banner, rarity, or item name
• Use search to find specific items
• Data is not duplicated (In theory :p)

**📊 FUNCTIONS: STATISTICS:**
• Visual distribution of your pulls by banner
• Total pulls and multis detected
• Time range of your pulls

**💡 TIPS:**
• The token expires every 24h or so - renew it when necessary
• Once pulls are made, the data takes about an hour to be available for import. This is a game limitation
• Only pulls less than 6 months old can be imported. If you want to keep your history, start as soon as possible
• Data is saved locally in the backup.json file

**🛠️ COMMENTS:**
• This program does not collect, store, or send data anywhere outside your PC, except to Girls Frontline 2 servers (duh)
• Since it uses the same history retrieval method as the game itself, there is no real risk of ban
• Still, for my safety, I am NOT responsible for consequences caused by any use you make of this program
• Vertebrae is a program under development. New features and improvements will (maybe) be added in the future
• If you have an error, a question, or think you can help, say so through github; I'll be grateful if you do

Need more help? Visit the project documentation.

⚠️ **IMPORTANT**: This project is not affiliated, endorsed, or authorized 
by Sunborn Network Technology Co., MICA Team, or "Girl's Frontline 2: Exilium". 
It is a fan-made project for fans.
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Vertebrae Gacha Tracker")
        help_window.geometry("600x500")
        help_window.minsize(500, 400)
        help_window.transient(self.root)
        help_window.grab_set()
        
        main_frame = ttk.Frame(help_window, padding=15)
        main_frame.pack(fill='both', expand=True)
        
        title_label = ttk.Label(main_frame, text="🎮 User Guide", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 15))
        
        help_text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                                    font=('Arial', 10), 
                                                    padx=10, pady=10,
                                                    height=20)
        help_text_widget.pack(fill='both', expand=True)
        help_text_widget.insert('1.0', help_text)
        help_text_widget.config(state='disabled')
        
        ttk.Button(main_frame, text="Close", 
                  command=help_window.destroy).pack(pady=(15, 0))
        
        help_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (help_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (help_window.winfo_height() // 2)
        help_window.geometry(f"+{x}+{y}")
        
    def on_window_resize(self, event):
        """Executes when the window is resized"""
        if (hasattr(self, 'current_stats') and self.current_stats and 
            self.notebook.tab(self.notebook.select(), "text") == _("ui.stats_tab")):
            if hasattr(self, '_resize_after_id'):
                self.root.after_cancel(self._resize_after_id)
            self._resize_after_id = self.root.after(200, self.redraw_pie_chart)
        
    def redraw_pie_chart(self):
        """Redraws the pie chart with current statistics"""
        if self.current_stats:
            self.create_pie_chart(self.current_stats)
        
    def on_tab_changed(self, event):
        """Executes when switching tabs"""
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        
        if current_tab == _("ui.history_tab"):
            if hasattr(self, 'all_records'):
                filtered_count = len(self.history_tree.get_children())
                total_count = len(self.all_records)
                if filtered_count == total_count:
                    self.status_label.config(text=_("messages.showing_all").format(count=total_count))
                else:
                    self.status_label.config(text=_("messages.filtered").format(filtered=filtered_count, total=total_count))
        elif current_tab == _("ui.stats_tab"):
            if hasattr(self, 'current_stats') and self.current_stats:
                self.root.after(100, lambda: self.create_pie_chart(self.current_stats))
        else:
            self.update_status_bar()
        
    def setup_import_tab(self):
        """Data import tab""" 
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
        """Pull history tab"""
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text=_("ui.history_tab"))
        
        self.history_tab.grid_rowconfigure(1, weight=1)
        self.history_tab.grid_columnconfigure(0, weight=1)
        
        controls_frame = ttk.Frame(self.history_tab)
        controls_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        # BANNER FILTER
        ttk.Label(controls_frame, text=_("ui.banner_filter")).pack(side='left', padx=(0, 5))
        self.banner_filter = ttk.Combobox(controls_frame, 
                                         values=[_("filters.all"), _("banners.characters"), _("banners.weapons"), 
                                                _("banners.permanent"), _("banners.beginner"), _("banners.mystery_box"), 
                                                _("banners.special"), _("banners.event")], 
                                         width=12)
        self.banner_filter.set(_("filters.all"))
        self.banner_filter.pack(side='left', padx=(0, 15))
        self.banner_filter.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # TYPE FILTER
        ttk.Label(controls_frame, text=_("ui.type_filter")).pack(side='left', padx=(0, 5))
        self.type_filter = ttk.Combobox(controls_frame, 
                                       values=[_("filters.all"), _("filters.characters"), _("filters.weapons"), _("filters.items")], 
                                       width=8)
        self.type_filter.set(_("filters.all"))
        self.type_filter.pack(side='left', padx=(0, 15))
        self.type_filter.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # RARITY FILTER
        ttk.Label(controls_frame, text=_("ui.rarity_filter")).pack(side='left', padx=(0, 5))
        self.rarity_filter = ttk.Combobox(controls_frame, 
                                         values=[_("filters.all_rarities"), _("filters.3_star"), _("filters.4_star"), _("filters.5_star")], 
                                         width=8)
        self.rarity_filter.set(_("filters.all_rarities"))
        self.rarity_filter.pack(side='left', padx=(0, 15))
        self.rarity_filter.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Text search
        ttk.Label(controls_frame, text=_("ui.search")).pack(side='left', padx=(0, 5))
        self.search_entry = ttk.Entry(controls_frame, width=20)
        self.search_entry.pack(side='left', padx=(0, 15))
        self.search_entry.bind('<KeyRelease>', self.apply_filters)
        
        # Buttons
        ttk.Button(controls_frame, text=_("ui.refresh"), command=self.load_history).pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text=_("ui.clear_filters"), command=self.clear_filters).pack(side='left')
        
        tree_frame = ttk.Frame(self.history_tab)
        tree_frame.grid(row=1, column=0, sticky='nsew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(1, weight=0)
        
        columns = ('Date', 'Time', _("ui.banner_filter"), 'Item', _("ui.type_filter"), _("ui.rarity_filter"))
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=25)
        
        column_widths = {'Date': 100, 'Time': 80, _("ui.banner_filter"): 120, 'Item': 250, _("ui.type_filter"): 80, _("ui.rarity_filter"): 70}
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=column_widths.get(col, 100))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
    def setup_stats_tab(self):
        """Statistics tab"""
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
        """Bottom status bar"""
        self.status_frame = ttk.Frame(self.root, relief='sunken', padding=5)
        self.status_frame.pack(fill='x', side='bottom')
        
        self.status_label = ttk.Label(self.status_frame, text=_("ui.ready"))
        self.status_label.pack(side='left', padx=5)
        
        stats = self.backup.get_statistics()
        self.record_count_label = ttk.Label(self.status_frame, text=_("ui.pulls").format(count=stats['total_records']))
        self.record_count_label.pack(side='right', padx=5)
        
    def get_rarity_display(self, rarity):
        """Converts rarity number to stars only"""
        return "★" * rarity
        
    def get_server_code_from_name(self, display_name):
        """Gets server code from display name"""
        for code, config in SERVERS.items():
            if config["name"] == display_name:
                return code
        return "darkwinter"
        
    def get_item_type_display(self, item_id):
        """Determines item type based on dictionaries"""
        if item_id in self.dolls_data:
            return _("filters.characters")
        elif item_id in self.weapons_data:
            return _("filters.weapons")
        elif item_id in self.mbox_data:
            return _("filters.items")
        else:
            return "Unknown"
        
    def apply_filters(self, event=None):
        """Applies search, banner, type and rarity filters"""
        if not self.all_records:
            return
            
        search_text = self.search_entry.get().lower()
        selected_banner = self.banner_filter.get()
        selected_type = self.type_filter.get()
        selected_rarity = self.rarity_filter.get()
        
        # Clear current table
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        filtered_count = 0
        for record in self.all_records:
            # Get record information
            banner_name = get_banner_name(record['pool_id'])
            item_name, rarity = get_item_name(record['item'])
            item_type = self.get_item_type_display(record['item'])
            rarity_display = self.get_rarity_display(rarity)
            
            # BANNER FILTER
            if selected_banner != _("filters.all"):
                # Handle special case of "Promotional" vs "Characters"
                if selected_banner == _("banners.characters"):
                    # For "Characters" filter, show both "Promotional" and "Characters"
                    if banner_name not in [_("banners.promotional"), _("banners.characters")]:
                        continue
                elif selected_banner != banner_name:
                    continue
                        
            # TYPE FILTER
            if selected_type != _("filters.all"):
                if selected_type == _("filters.characters") and item_type != _("filters.characters"):
                    continue
                elif selected_type == _("filters.weapons") and item_type != _("filters.weapons"):
                    continue
                elif selected_type == _("filters.items") and item_type != _("filters.items"):
                    continue
                
            # RARITY FILTER
            if selected_rarity != _("filters.all_rarities"):
                rarity_map = {_("filters.3_star"): 3, _("filters.4_star"): 4, _("filters.5_star"): 5}
                target_rarity = rarity_map.get(selected_rarity)
                if rarity != target_rarity:
                    continue
                
            # Filter by text search
            if search_text and search_text not in item_name.lower():
                continue
                
            # If it passes filters, add to table
            dt = datetime.fromtimestamp(record['time'])
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M:%S")
            
            self.history_tree.insert('', 'end', values=(
                date_str, time_str, banner_name, item_name, item_type, rarity_display
            ))
            filtered_count += 1
            
        # Update status bar
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab == _("ui.history_tab"):
            total_count = len(self.all_records)
            if filtered_count == total_count:
                self.status_label.config(text=_("messages.showing_all").format(count=total_count))
            else:
                self.status_label.config(text=_("messages.filtered").format(filtered=filtered_count, total=total_count))
        
    def clear_filters(self):
        """Clears all filters and shows all records"""
        self.search_entry.delete(0, 'end')
        self.banner_filter.set(_("filters.all"))
        self.type_filter.set(_("filters.all"))
        self.rarity_filter.set(_("filters.all_rarities"))
        self.apply_filters()
        
    def _draw_no_data_message(self):
        """Draws no data message on canvas"""
        canvas_width = self.pie_canvas.winfo_width()
        canvas_height = self.pie_canvas.winfo_height()
        
        if canvas_width > 10 and canvas_height > 10:
            self.pie_canvas.delete("all")
            self.pie_canvas.create_text(
                canvas_width // 2, canvas_height // 2,
                text=_("messages.no_data"), 
                font=('Arial', 12), fill='gray', justify='center'
            )
        
    def create_pie_chart(self, stats):
        """Creates a pie chart using tkinter Canvas"""
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
        """Adds message to import log"""
        self.import_log.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.import_log.insert('end', f"[{timestamp}] {message}\n")
        self.import_log.see('end')
        self.import_log.config(state='disabled')
        self.root.update_idletasks()
        
    def clear_log(self):
        """Clears import log"""
        self.import_log.config(state='normal')
        self.import_log.delete('1.0', 'end')
        self.import_log.config(state='disabled')
        
    def start_import(self):
        """Starts import in a separate thread"""
        if self.is_importing:
            messagebox.showwarning("Import in progress", "There is already an import in progress.")
            return
            
        token = self.token_entry.get('1.0', 'end').strip()
        email = self.email_entry.get().strip()
        server_display_name = self.server_combobox.get()
        
        server_code = self.get_server_code_from_name(server_display_name)
        
        if not token or not email:
            messagebox.showerror("Error", "Token and email are required.")
            return
            
        self.is_importing = True
        self.import_btn.config(state='disabled')
        self.progress_bar.start()
        self.clear_log()
        
        thread = threading.Thread(target=self.run_import, args=(token, email, server_code))
        thread.daemon = True
        thread.start()
        
    def run_import(self, token, email, server_code):
        """Runs import (in separate thread)"""
        try:
            server_display_name = get_server_display_name(server_code)
            
            self.log_message(_("messages.import_started"))
            self.log_message(f"Email: {email}")
            self.log_message(f"Server: {server_display_name}")
            self.log_message(f"Server code: {server_code}")
            
            # Show current configuration
            page_limit = ConfigManager.get_setting('page_limit', 50)
            if page_limit == -1:
                self.log_message(f"⚡ Configuration: NO LIMIT mode for pages")
            else:
                self.log_message(f"⚡ Configuration: {page_limit} page limit")
            
            stats = self.backup.get_statistics()
            self.log_message(f"📊 CURRENT STATUS: {stats['total_records']} pulls, {stats['multi_count']} multis")
            
            type_ids_to_check = ['1', '3', '4', '5', '8']
            all_new_raw_records = []
            
            for type_id in type_ids_to_check:
                self.log_message(f"🎯 Getting type_id {type_id}...")
                records = get_all_pages_for_type(token, email, type_id, server_code, self.log_message)
                if records:
                    all_new_raw_records.extend(records)
                    self.log_message(f"   ✅ {len(records)} pulls obtained")
                else:
                    self.log_message(f"   ℹ️  No data")
            
            if all_new_raw_records:
                added_count = self.backup.add_new_records(all_new_raw_records)
                
                self.log_message(f"\n📊 FINAL RESULT:")
                self.log_message(f"   Server pulls: {len(all_new_raw_records)}")
                self.log_message(f"   New pulls added: {added_count}")
                self.log_message(f"   Duplicates omitted: {len(all_new_raw_records) - added_count}")
                
                self.root.after(0, self.on_import_success, added_count)
                
            else:
                self.log_message(_("messages.no_new_data"))
                self.root.after(0, self.on_import_finished)
                
        except Exception as e:
            self.log_message(f"❌ ERROR: {str(e)}")
            self.root.after(0, self.on_import_error, str(e))
            
    def on_import_success(self, added_count):
        """When import finishes successfully"""
        self.progress_bar.stop()
        self.import_btn.config(state='normal')
        self.is_importing = False
        
        self.update_status_bar()
        self.load_history()
        self.update_stats_display()
        
        self.status_label.config(text=_("messages.import_success").format(count=added_count))
        messagebox.showinfo("Import Successful", 
                          f"{added_count} new pulls were added to history.")
        
    def on_import_finished(self):
        """When import finishes without new data"""
        self.progress_bar.stop()
        self.import_btn.config(state='normal')
        self.is_importing = False
        self.update_status_bar()
        self.status_label.config(text=_("messages.import_finished"))
        
    def on_import_error(self, error_msg):
        """When an error occurs during import"""
        self.progress_bar.stop()
        self.import_btn.config(state='normal')
        self.is_importing = False
        self.status_label.config(text=_("messages.import_error"))
        messagebox.showerror("Import Error", f"An error occurred:\n{error_msg}")
        
    def update_status_bar(self):
        """Updates status bar with current information"""
        stats = self.backup.get_statistics()
        self.record_count_label.config(text=_("ui.pulls").format(count=stats['total_records']))
        self.status_label.config(text=_("ui.ready"))
        
    def load_history(self):
        """Loads history into the table"""
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
                self.status_label.config(text=_("messages.showing_all").format(count=total_count))
            
        except Exception as e:
            print(f"Error loading history: {e}")
            
    def update_stats_display(self):
        """Updates the statistics tab"""
        stats = self.backup.get_statistics()
        self.current_stats = stats
        
        banner_groups = {}
        for banner_id, count in stats['banners'].items():
            banner_name = get_banner_name(banner_id)
            if banner_name in banner_groups:
                banner_groups[banner_name] += count
            else:
                banner_groups[banner_name] = count
        
        stats_text = f"""📊 HISTORY STATISTICS

• Total pulls: {stats['total_records']}
• Multis detected: {stats['multi_count']}
• Last update: {stats.get('last_update', 'N/A')}

"""
        
        if stats['total_records'] > 0:
            stats_text += f"• Time range: {stats.get('oldest', 'N/A')} - {stats.get('newest', 'N/A')}\n\n"
        
        stats_text += "🎯 BANNER DISTRIBUTION:\n"
        
        if banner_groups:
            total_pulls = stats['total_records']
            for banner_name, count in banner_groups.items():
                percentage = (count / total_pulls) * 100 if total_pulls > 0 else 0
                stats_text += f"   • {banner_name}: {count} pulls ({percentage:.1f}%)\n"
        else:
            stats_text += "   No banner data\n"
            
        self.stats_text.config(state='normal')
        self.stats_text.delete('1.0', 'end')
        self.stats_text.insert('1.0', stats_text)
        self.stats_text.config(state='disabled')
        
        self.root.after(100, lambda: self.create_pie_chart(stats))
        
    def show_stats(self):
        """Shows quick statistics in a messagebox"""
        stats = self.backup.get_statistics()
        
        banner_groups = {}
        for banner_id, count in stats['banners'].items():
            banner_name = get_banner_name(banner_id)
            if banner_name in banner_groups:
                banner_groups[banner_name] += count
            else:
                banner_groups[banner_name] = count
        
        stats_text = f"📊 QUICK STATISTICS\n\n"
        stats_text += f"Total pulls: {stats['total_records']}\n"
        stats_text += f"Multis detected: {stats['multi_count']}\n"
        
        if banner_groups:
            stats_text += f"\nDistribution:\n"
            for banner_name, count in list(banner_groups.items())[:5]:
                stats_text += f"• {banner_name}: {count}\n"
            
        messagebox.showinfo("Statistics", stats_text)

def main():
    root = tk.Tk()
    app = GachaTrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()