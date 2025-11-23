import requests
import json
import os
import sys
from datetime import datetime
from urllib.parse import urlencode
import urllib3

# Desactivar warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Obtener el directorio donde está este script
if getattr(sys, 'frozen', False):
    # Si está empaquetado como exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si se ejecuta como script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')
LOCALIZATIONS_DIR = os.path.join(BASE_DIR, 'localizations')

# Crear carpetas si no existen
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOCALIZATIONS_DIR, exist_ok=True)

# CONFIGURACIÓN DE SERVIDORES - ACTUALIZADA
SERVERS = {
    "darkwinter": {
        "name": "Darkwinter (US/EU)",
        "code": "darkwinter",
        "endpoint": "https://gf2-gacha-record-us.sunborngame.com/list",
        "zone_endpoint": "https://gf2-zoneinfo-us.sunborngame.com"
    },
    "haoplay": {
        "name": "Haoplay Asia",
        "code": "haoplay", 
        "endpoint": "https://gf2-gacha-record-asia.haoplay.com/list",
        "zone_endpoint": "https://gf2-zoneinfo-asia.haoplay.com"
    },
    "haoplay-jp": {
        "name": "Haoplay Japan", 
        "code": "haoplay-jp",
        "endpoint": "https://gf2-gacha-record-jp.haoplay.com/list",
        "zone_endpoint": "https://gf2-zoneinfo-jp.haoplay.com"
    },
    "haoplay-kr": {
        "name": "Haoplay Korea",
        "code": "haoplay-kr", 
        "endpoint": "https://gf2-gacha-record-kr.haoplay.com/list",
        "zone_endpoint": "https://gf2-zoneinfo-kr.haoplay.com"
    },
    "haoplay-intl": {
        "name": "Haoplay International",
        "code": "haoplay-intl",
        "endpoint": "https://gf2-gacha-record-intl.haoplay.com/list", 
        "zone_endpoint": "https://gf2-zoneinfo-intl.haoplay.com"
    },
    "cn": {
        "name": "CN Server",
        "code": "cn",
        "endpoint": "https://gf2-gacha-record.sunborngame.com/list",
        "zone_endpoint": "https://gf2-zoneinfo.sunborngame.com"
    }
}

class ConfigManager:
    """Gestor de configuración de la aplicación"""
    _config = None
    _config_file = os.path.join(BASE_DIR, "config.json")
    
    @classmethod
    def load_config(cls):
        """Carga la configuración desde config.json"""
        if cls._config is None:
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
            
            try:
                if os.path.exists(cls._config_file):
                    with open(cls._config_file, 'r', encoding='utf-8') as f:
                        cls._config = json.load(f)
                    print(f"✅ Configuración cargada: {cls._config_file}")
                else:
                    cls._config = default_config
                    cls.save_config()
                    print(f"📁 Configuración por defecto creada: {cls._config_file}")
            except Exception as e:
                print(f"❌ Error cargando configuración: {e}")
                cls._config = default_config
        
        return cls._config
    
    @classmethod
    def save_config(cls):
        """Guarda la configuración actual"""
        try:
            with open(cls._config_file, 'w', encoding='utf-8') as f:
                json.dump(cls._config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
            return False
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Obtiene un valor de configuración"""
        config = cls.load_config()
        return config['settings'].get(key, default)
    
    @classmethod
    def set_setting(cls, key, value):
        """Establece un valor de configuración"""
        config = cls.load_config()
        config['settings'][key] = value
        cls._config = config
        return cls.save_config()

class DataManager:
    """Gestor de datos externos - Lee desde archivos JSON"""
    _dolls = None
    _weapons = None
    _mbox = None
    _weapon_banners = None
    _promotional_banners = None
    _localization = None
    _current_language = "EN"
    
    @classmethod
    def load_dolls(cls):
        """Carga el diccionario de personajes desde data/dolls.json"""
        if cls._dolls is None:
            try:
                dolls_path = os.path.join(DATA_DIR, 'dolls.json')
                with open(dolls_path, 'r', encoding='utf-8') as f:
                    dolls_data = json.load(f)
                    cls._dolls = {int(k): v for k, v in dolls_data.items()}
            except Exception as e:
                print(f"❌ Error cargando dolls.json: {e}")
                cls._dolls = {}
        return cls._dolls
    
    @classmethod
    def load_weapons(cls):
        """Carga el diccionario de armas desde data/weapons.json"""
        if cls._weapons is None:
            try:
                weapons_path = os.path.join(DATA_DIR, 'weapons.json')
                with open(weapons_path, 'r', encoding='utf-8') as f:
                    weapons_data = json.load(f)
                    cls._weapons = {int(k): v for k, v in weapons_data.items()}
            except Exception as e:
                print(f"❌ Error cargando weapons.json: {e}")
                cls._weapons = {}
        return cls._weapons
    
    @classmethod
    def load_mbox(cls):
        """Carga el diccionario de mbox desde data/mbox.json"""
        if cls._mbox is None:
            try:
                mbox_path = os.path.join(DATA_DIR, 'mbox.json')
                with open(mbox_path, 'r', encoding='utf-8') as f:
                    mbox_data = json.load(f)
                    cls._mbox = {int(k): v for k, v in mbox_data.items()}
                print(f"✅ mbox.json cargado: {len(cls._mbox)} items")
            except Exception as e:
                print(f"❌ Error cargando mbox.json: {e}")
                cls._mbox = {}
        return cls._mbox
    
    @classmethod
    def load_weapon_banners(cls):
        """Carga el diccionario de banners de armas desde data/weapon_banners.json"""
        if cls._weapon_banners is None:
            try:
                weapon_banners_path = os.path.join(DATA_DIR, 'weapon_banners.json')
                with open(weapon_banners_path, 'r', encoding='utf-8') as f:
                    weapon_banners_data = json.load(f)
                    cls._weapon_banners = {int(k): v for k, v in weapon_banners_data.items()}
                print(f"✅ weapon_banners.json cargado: {len(cls._weapon_banners)} banners de armas")
            except Exception as e:
                print(f"❌ Error cargando weapon_banners.json: {e}")
                cls._weapon_banners = {}
        return cls._weapon_banners
    
    @classmethod
    def load_promotional_banners(cls):
        """Carga el diccionario de banners promocionales desde data/promotional_banners.json"""
        if cls._promotional_banners is None:
            try:
                promotional_banners_path = os.path.join(DATA_DIR, 'promotional_banners.json')
                with open(promotional_banners_path, 'r', encoding='utf-8') as f:
                    promotional_banners_data = json.load(f)
                    cls._promotional_banners = {int(k): v for k, v in promotional_banners_data.items()}
                print(f"✅ promotional_banners.json cargado: {len(cls._promotional_banners)} banners promocionales")
            except Exception as e:
                print(f"❌ Error cargando promotional_banners.json: {e}")
                cls._promotional_banners = {}
        return cls._promotional_banners
    
    @classmethod
    def load_localization(cls, language=None):
        """Carga las traducciones para el idioma especificado"""
        if language:
            cls._current_language = language
        
        try:
            localization_path = os.path.join(LOCALIZATIONS_DIR, f'localization_{cls._current_language}.json')
            with open(localization_path, 'r', encoding='utf-8') as f:
                cls._localization = json.load(f)
            print(f"✅ Localización cargada: {cls._current_language}")
        except Exception as e:
            print(f"❌ Error cargando localization_{cls._current_language}.json: {e}")
            # Fallback a español
            if cls._current_language != "EN":
                print("🔄 Intentando cargar español como fallback...")
                cls._current_language = "EN"
                cls.load_localization()
            else:
                cls._localization = {}
                print("❌ No se pudo cargar ningún archivo de localización")
        return cls._localization
    
    @classmethod
    def get_text(cls, key, default=None):
        """Obtiene texto traducido usando notación de puntos: 'ui.title'"""
        if cls._localization is None:
            cls.load_localization()
        
        # Primero intentar cargar la localización si no está cargada
        if cls._localization is None:
            cls.load_localization()
        
        keys = key.split('.')
        value = cls._localization
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default if default is not None else key
    
    @classmethod
    def set_language(cls, language):
        """Cambia el idioma de la aplicación"""
        cls._current_language = language
        cls._localization = None  # Forzar recarga
        return cls.load_localization(language)

class LocalizationManager:
    """Gestor de localización para la aplicación"""
    _current_language = "EN"
    
    @classmethod
    def set_language(cls, language):
        """Cambia el idioma de la aplicación"""
        cls._current_language = language
        return DataManager.set_language(language)
    
    @classmethod
    def get_text(cls, key, default=None):
        """Obtiene texto traducido"""
        return DataManager.get_text(key, default)
    
    @classmethod
    def get_current_language(cls):
        return cls._current_language

# Alias corto para uso fácil
_ = LocalizationManager.get_text

class SimpleGachaBackup:
    def __init__(self):
        self.backup_file = os.path.join(BASE_DIR, "backup.json")
        self.data_manager = DataManager()
        self.init_backup()
    
    def init_backup(self):
        """Inicializa el backup si no existe"""
        if not os.path.exists(self.backup_file):
            base_structure = {
                "version": 3,
                "created": datetime.now().isoformat(),
                "last_updated": None,
                "records": []
            }
            self.save_backup(base_structure)
            print("📁 Backup creado: backup.json")
    
    def load_backup(self):
        """Carga el backup completo"""
        try:
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error cargando backup: {e}")
            return self.init_backup()
    
    def save_backup(self, data):
        """Guarda el backup"""
        try:
            data["last_updated"] = datetime.now().isoformat()
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error guardando backup: {e}")
            return False
    
    def add_new_records(self, new_records):
        """Agrega SOLO registros NUEVOS comparando con el backup existente"""
        backup_data = self.load_backup()
        existing_records = backup_data["records"]
        
        print(f"   🔍 Comparando {len(new_records)} registros nuevos vs {len(existing_records)} existentes...")
        
        # Para el backup existente, crear un mapa de "grupos de multi"
        existing_groups = self.group_by_multi(existing_records)
        
        # Para los nuevos registros, también agrupar por multi
        new_groups = self.group_by_multi(new_records)
        
        # Combinar: para cada grupo de multi, agregar solo lo que no existe
        combined_records = existing_records.copy()
        added_count = 0
        
        for timestamp, new_multi_group in new_groups.items():
            if timestamp not in existing_groups:
                # Multi completamente nueva - agregar todo
                combined_records.extend(new_multi_group)
                added_count += len(new_multi_group)
                print(f"      ✅ Multi nueva: {datetime.fromtimestamp(timestamp).strftime('%H:%M')} - {len(new_multi_group)} tiradas")
            else:
                # Multi existente - verificar item por item
                existing_multi_group = existing_groups[timestamp]
                existing_items = {(r['item'], r['pool_id']) for r in existing_multi_group}
                
                new_items_to_add = []
                for new_record in new_multi_group:
                    item_key = (new_record['item'], new_record['pool_id'])
                    if item_key not in existing_items:
                        new_items_to_add.append(new_record)
                
                if new_items_to_add:
                    combined_records.extend(new_items_to_add)
                    added_count += len(new_items_to_add)
                    print(f"      ➕ Multi existente: {datetime.fromtimestamp(timestamp).strftime('%H:%M')} - {len(new_items_to_add)} items nuevos")
        
        # Actualizar backup solo si hay cambios
        if added_count > 0:
            backup_data["records"] = combined_records
            self.save_backup(backup_data)
        
        return added_count
    
    def group_by_multi(self, records):
        """Agrupa registros por timestamp (cada grupo es una multi)"""
        groups = {}
        for record in records:
            timestamp = record['time']
            if timestamp not in groups:
                groups[timestamp] = []
            groups[timestamp].append(record)
        return groups
    
    def get_all_records(self):
        """Obtiene todos los registros del backup"""
        backup_data = self.load_backup()
        return backup_data["records"]
    
    def get_statistics(self):
        """Estadísticas del backup"""
        records = self.get_all_records()
        stats = {
            'total_records': len(records),
            'banners': {},
            'last_update': None,
            'multi_count': 0
        }
        
        if records:
            # Agrupar por timestamp para detectar multis
            timestamp_groups = {}
            for record in records:
                timestamp = record['time']
                if timestamp not in timestamp_groups:
                    timestamp_groups[timestamp] = []
                timestamp_groups[timestamp].append(record)
            
            # Contar multis (grupos con más de 1 registro)
            stats['multi_count'] = sum(1 for group in timestamp_groups.values() if len(group) > 1)
            
            # Ordenar por tiempo
            sorted_records = sorted(records, key=lambda x: x['time'])
            stats['oldest'] = datetime.fromtimestamp(sorted_records[0]['time']).strftime("%Y-%m-%d")
            stats['newest'] = datetime.fromtimestamp(sorted_records[-1]['time']).strftime("%Y-%m-%d")
            stats['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Contar por banner
            for record in records:
                banner_id = record['pool_id']
                stats['banners'][banner_id] = stats['banners'].get(banner_id, 0) + 1
        
        return stats

def get_all_pages_for_type(token, email, type_id, server_code="darkwinter", progress_callback=None):
    """Obtiene TODAS las páginas para un type_id específico - CON LÍMITE CONFIGURABLE"""
    all_records = []
    next_cursor = None
    page_count = 0
    
    # Obtener configuración
    page_limit = ConfigManager.get_setting('page_limit', 50)
    request_timeout = ConfigManager.get_setting('request_timeout', 20)
    max_retries = ConfigManager.get_setting('max_retries', 3)
    
    # Determinar modo de límite
    unlimited_mode = (page_limit == -1)
    
    if unlimited_mode:
        print(f"   📦 Obteniendo type_id {type_id}: MODO SIN LÍMITE")
    else:
        print(f"   📦 Obteniendo type_id {type_id}: {page_limit} páginas máx.")
    
    # Obtener endpoint del servidor seleccionado
    server_config = SERVERS.get(server_code, SERVERS["darkwinter"])
    base_url = server_config["endpoint"]
    
    print(f"   🌐 Servidor: {server_config['name']}")
    
    while True:
        page_count += 1
        retry_count = 0
        success = False
        
        # Parámetros base
        params = {
            'game_channel_id': '5',
            'type_id': type_id, 
            'u': email
        }
        
        # Agregar cursor si existe
        if next_cursor:
            params['next'] = next_cursor
        
        headers = {
            'authorization': token,
            'user-agent': 'UnityPlayer/2019.4.40f1 (UnityWebRequest/1.0, libcurl/7.80.0-DEV)',
            'accept': '*/*',
            'accept-encoding': 'deflate, gzip',
            'content-type': 'application/x-www-form-urlencoded',
            'x-unity-version': '2019.4.40f1'
        }
        
        payload = {'server': '1'}  # Este parámetro parece ser siempre '1'
        
        # Intentar con reintentos
        while retry_count <= max_retries and not success:
            try:
                url_with_params = f"{base_url}?{urlencode(params)}"
                
                response = requests.post(
                    url_with_params,
                    headers=headers,
                    data=payload,
                    timeout=request_timeout,
                    verify=False
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('code') == 0:
                        records = data['data']['list']
                        next_cursor = data['data'].get('next', '')
                        
                        print(f"      ✅ Página {page_count}: {len(records)} tiradas")
                        
                        # Callback de progreso si está disponible
                        if progress_callback:
                            progress_callback(f"Página {page_count}: {len(records)} tiradas")
                        
                        # AGREGAR TODOS LOS REGISTROS SIN PROCESAR
                        all_records.extend(records)
                        success = True
                        
                        # Si no hay más datos, salir
                        if not next_cursor:
                            print(f"      🏁 Fin de datos del servidor")
                            break
                    else:
                        error_msg = f"Error API: {data.get('message')}"
                        print(f"      ❌ {error_msg}")
                        if progress_callback:
                            progress_callback(f"❌ {error_msg}")
                        if retry_count < max_retries:
                            retry_count += 1
                            print(f"      🔄 Reintentando... ({retry_count}/{max_retries})")
                            continue
                        break
                else:
                    error_msg = f"Error HTTP: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    if progress_callback:
                        progress_callback(f"❌ {error_msg}")
                    if retry_count < max_retries:
                        retry_count += 1
                        print(f"      🔄 Reintentando... ({retry_count}/{max_retries})")
                        continue
                    break
                    
            except requests.exceptions.Timeout:
                error_msg = f"Timeout en página {page_count}"
                print(f"      ⏰ {error_msg}")
                if progress_callback:
                    progress_callback(f"⏰ {error_msg}")
                if retry_count < max_retries:
                    retry_count += 1
                    print(f"      🔄 Reintentando... ({retry_count}/{max_retries})")
                    continue
                break
                
            except Exception as e:
                error_msg = f"Error de conexión: {e}"
                print(f"      ❌ {error_msg}")
                if progress_callback:
                    progress_callback(f"❌ {error_msg}")
                if retry_count < max_retries:
                    retry_count += 1
                    print(f"      🔄 Reintentando... ({retry_count}/{max_retries})")
                    continue
                break
        
        # Si no tuvo éxito después de los reintentos, salir
        if not success:
            break
            
        # Verificar límite de páginas CONFIGURABLE (solo si no es modo sin límite)
        if not unlimited_mode and page_count >= page_limit:
            print(f"      ⚠️  Límite configurado de páginas alcanzado ({page_limit})")
            break
            
        # Si no hay más datos del servidor, salir
        if not next_cursor:
            break
    
    print(f"      📊 Total type_id {type_id}: {len(all_records)} tiradas en {page_count} páginas")
    return all_records

def get_banner_name(pool_id):
    """Nombres de banners - VERSIÓN MEJORADA CON LOCALIZACIÓN"""
    data_manager = DataManager()
    
    # 1. Banners especiales que tienen IDs específicos FIJOS - USANDO LOCALIZACIÓN
    special_banners = {
        130002: _("banners.weapons"), 
        130003: _("banners.characters"),
        130004: _("banners.special"), 
        130005: _("banners.beginner"),
        130008: _("banners.event"),
        1001: _("banners.permanent"),
        99001: _("banners.mystery_box")
    }
    
    # Si es un banner especial fijo, devolver su nombre TRADUCIDO
    if pool_id in special_banners:
        return special_banners[pool_id]
    
    # 2. Verificar en banners de armas (IDs variables)
    weapon_banners = data_manager.load_weapon_banners()
    if pool_id in weapon_banners:
        return _("banners.weapons")  # Siempre "Armas" o "Weapons"
    
    # 3. Verificar en banners promocionales de personajes (IDs variables)
    promotional_banners = data_manager.load_promotional_banners()
    if pool_id in promotional_banners:
        return _("banners.promotional")  # Siempre "Promocional" o "Promotional"
    
    # 4. Cualquier otro ID no reconocido es "Promocional" por defecto
    return _("banners.promotional")

def get_item_name(item_id):
    """Nombres de items usando los diccionarios desde archivos JSON"""
    data_manager = DataManager()
    dolls = data_manager.load_dolls()
    weapons = data_manager.load_weapons()
    mbox = data_manager.load_mbox()
    
    # Primero buscar en personajes (DOLLS)
    if item_id in dolls:
        name_key = dolls[item_id]["name_key"]
        rarity = dolls[item_id]["rarity"]
        # Usar el sistema de localización mejorado
        item_name = DataManager.get_text(name_key, f"Personaje {item_id}")
        return item_name, rarity
    
    # Luego buscar en armas (WEAPONS)
    if item_id in weapons:
        name_key = weapons[item_id]["name_key"]
        rarity = weapons[item_id]["rarity"]
        item_name = DataManager.get_text(name_key, f"Arma {item_id}")
        return item_name, rarity
    
    # Buscar en mbox
    if item_id in mbox:
        name_key = mbox[item_id]["name_key"]
        rarity = mbox[item_id]["rarity"]
        item_name = DataManager.get_text(name_key, f"Mbox {item_id}")
        return item_name, rarity
    
    # Si no se encuentra en ningún diccionario
    return f"Item {item_id}", 3

def get_item_type(item_id):
    """Determina el tipo de item (character, weapon, mbox, other)"""
    data_manager = DataManager()
    dolls = data_manager.load_dolls()
    weapons = data_manager.load_weapons()
    mbox = data_manager.load_mbox()
    
    if item_id in dolls:
        return "character"
    elif item_id in weapons:
        return "weapon"
    elif item_id in mbox:
        return "mbox"
    else:
        return "other"

def get_server_display_name(server_code):
    """Obtiene el nombre para mostrar del servidor"""
    server_config = SERVERS.get(server_code, SERVERS["darkwinter"])
    return server_config["name"]

def debug_api_response(response):
    """Debug completo de la respuesta API - PARA SOLUCIONAR ERROR NoneType"""
    print(f"🔍 DEBUG API RESPONSE:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Headers: {response.headers}")
    print(f"   Content: {response.text[:500]}...")  # Primeros 500 chars
    
    try:
        data = response.json()
        print(f"   JSON Structure: {list(data.keys()) if data else 'EMPTY'}")
        if 'data' in data:
            print(f"   Data keys: {list(data['data'].keys()) if data['data'] else 'EMPTY_DATA'}")
    except Exception as e:
        print(f"   JSON Parse Error: {e}")

def get_complete_gacha_history_simple_backup():
    print("=== 🚀 SCRAPER GACHA - SISTEMA FINAL ===")
    print("=== 💾 COMPARA CON BACKUP + PERMITE MULTIS ===\n")
    
    # Mostrar opciones de servidor
    print("🌐 SERVERS DISPONIBLES:")
    for code, config in SERVERS.items():
        print(f"   {code}: {config['name']}")
    
    # Configuración
    token = input("\nPega tu token de autorización: ").strip()
    email = input("Ingresa tu email: ").strip()
    server_code = input("Servidor (darkwinter/haoplay/haoplay-jp/etc): ").strip() or "darkwinter"
    
    # Validar servidor
    if server_code not in SERVERS:
        print(f"❌ Servidor '{server_code}' no válido. Usando darkwinter por defecto.")
        server_code = "darkwinter"
    
    print(f"✅ Servidor seleccionado: {SERVERS[server_code]['name']}")
    
    # Inicializar backup
    backup = SimpleGachaBackup()
    
    # Mostrar estado actual
    stats = backup.get_statistics()
    print(f"\n📊 ESTADO ACTUAL DEL BACKUP:")
    print(f"   Total de tiradas: {stats['total_records']}")
    print(f"   Multis detectadas: {stats['multi_count']}")
    if stats['total_records'] > 0:
        print(f"   Rango: {stats['oldest']} - {stats['newest']}")
    
    print(f"\n📦 Obteniendo datos del servidor...")
    
    # Obtener datos CRUDOS
    type_ids_to_check = ['1', '3', '4', '5', '8']
    all_new_raw_records = []
    
    for type_id in type_ids_to_check:
        print(f"\n🎯 Type_id {type_id}:")
        records = get_all_pages_for_type(token, email, type_id, server_code)
        if records:
            # Verificar duplicados en esta request (solo para info)
            unique_timestamps = len({r['time'] for r in records})
            if len(records) > unique_timestamps:
                print(f"   🎯 {len(records) - unique_timestamps} duplicados de multi detectados")
            
            all_new_raw_records.extend(records)
            print(f"   📥 {len(records)} tiradas obtenidas")
        else:
            print(f"   ℹ️  Sin datos")
    
    # 🔥 COMPARAR Y AGREGAR SOLO LO NUEVO
    if all_new_raw_records:
        added_count = backup.add_new_records(all_new_raw_records)
        
        print(f"\n{'='*50}")
        print("📊 RESULTADO DE LA ACTUALIZACIÓN:")
        print(f"   Tiradas del servidor: {len(all_new_raw_records)}")
        print(f"   Nuevas tiradas agregadas: {added_count}")
        print(f"   Duplicados omitidos: {len(all_new_raw_records) - added_count}")
        
        # Mostrar estadísticas actualizadas
        new_stats = backup.get_statistics()
        print(f"\n📈 ESTADO ACTUALIZADO:")
        print(f"   Total de tiradas: {new_stats['total_records']}")
        print(f"   Multis detectadas: {new_stats['multi_count']}")
        
        # Mostrar distribución
        if new_stats['banners']:
            print(f"\n🎯 DISTRIBUCIÓN:")
            for banner_id, count in new_stats['banners'].items():
                banner_name = get_banner_name(banner_id)
                print(f"   {banner_name}: {count} tiradas")
        
        # Mostrar últimas tiradas
        if new_stats['total_records'] > 0:
            all_records = backup.get_all_records()
            recent_records = sorted(all_records, key=lambda x: x['time'], reverse=True)[:15]
            
            print(f"\n📜 ÚLTIMAS TIRADAS:")
            current_time_group = None
            for i, pull in enumerate(recent_records, 1):
                time_str = datetime.fromtimestamp(pull['time']).strftime("%Y-%m-%d %H:%M")
                banner_name = get_banner_name(pull['pool_id'])
                item_name, rarity = get_item_name(pull['item'])
                
                # Agrupar por multi visualmente
                if current_time_group != pull['time']:
                    if current_time_group is not None:
                        print("   ──────────────────────")
                    current_time_group = pull['time']
                    multi_count = len([r for r in recent_records if r['time'] == pull['time']])
                    multi_indicator = " 🎯" if multi_count > 1 else ""
                    print(f"   {time_str}{multi_indicator}")
                
                print(f"        {banner_name} → {item_name}")
    
    else:
        print(f"\n❌ No se obtuvieron nuevos datos")
    
    print(f"\n💾 Backup: {os.path.abspath(backup.backup_file)}")
    print(f"\n{'='*60}")
    input("🎉 Presiona ENTER para cerrar...")

if __name__ == "__main__":
    get_complete_gacha_history_simple_backup()