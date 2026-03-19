#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐄 CATTLE MANAGER PRO - VERSION DEFINITIVA
SIN TextInput - Todo con Spinners y Popups
"""

import os
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.utils import get_color_from_hex, platform
import sqlite3
import re

# Colores
BG = get_color_from_hex('#0f1419')
CARD = get_color_from_hex('#1c2128')
PRIMARY = get_color_from_hex('#58a6ff')
SUCCESS = get_color_from_hex('#3fb950')
WARNING = get_color_from_hex('#d29922')
DANGER = get_color_from_hex('#f85149')
TEXT = get_color_from_hex('#e6edf3')
TEXT_DIM = get_color_from_hex('#7d8590')

Window.clearcolor = BG


class ModernButton(Button):
    def __init__(self, bg_color=PRIMARY, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = TEXT
        self.bold = True
        self.bg_color = bg_color
        with self.canvas.before:
            self.rect_color = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ModernCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*CARD)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Database:
    def __init__(self):
        try:
            if platform == 'android':
                from android.storage import app_storage_path
                storage_path = app_storage_path()
                self.db_path = os.path.join(storage_path, 'cattle_manager.db')
            else:
                self.db_path = os.path.expanduser('~/cattle_manager.db')
        except:
            self.db_path = os.path.expanduser('~/cattle_manager.db')
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cattle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_number TEXT UNIQUE NOT NULL,
                name TEXT,
                birth_date TEXT,
                weight REAL,
                category TEXT,
                is_pregnant INTEGER DEFAULT 0,
                pregnancy_date TEXT,
                expected_birth_date TEXT,
                last_birth_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vaccination_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cattle_id INTEGER,
                vaccine_name TEXT,
                vaccination_date TEXT,
                next_vaccination_date TEXT,
                notes TEXT,
                FOREIGN KEY (cattle_id) REFERENCES cattle (id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cattle_id INTEGER,
                event_type TEXT,
                event_date TEXT,
                notes TEXT,
                FOREIGN KEY (cattle_id) REFERENCES cattle (id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cattle_id INTEGER,
                activity_type TEXT,
                description TEXT,
                activity_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cattle_id) REFERENCES cattle (id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_cattle(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO cattle (tag_number, name, birth_date, weight, category,
                                    is_pregnant, pregnancy_date, expected_birth_date,
                                    last_birth_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data.get('tag_number'), data.get('name'), data.get('birth_date'),
                  data.get('weight'), data.get('category'), data.get('is_pregnant', 0),
                  data.get('pregnancy_date'), data.get('expected_birth_date'),
                  data.get('last_birth_date'), data.get('notes')))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def update_cattle(self, cattle_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        fields = []
        values = []
        for key, value in data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                values.append(value)
        values.append(cattle_id)
        query = f"UPDATE cattle SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    
    def get_all_cattle(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cattle ORDER BY tag_number')
        columns = [desc[0] for desc in cursor.description]
        cattle_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return cattle_list
    
    def get_cattle_by_id(self, cattle_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cattle WHERE id = ?', (cattle_id,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        conn.close()
        return dict(zip(columns, row)) if row else None
    
    def search_cattle(self, query):
        conn = self.get_connection()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE tag_number LIKE ? OR name LIKE ?
            ORDER BY tag_number
        ''', (search_term, search_term))
        columns = [desc[0] for desc in cursor.description]
        cattle_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return cattle_list
    
    def delete_cattle(self, cattle_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cattle WHERE id = ?', (cattle_id,))
        conn.commit()
        conn.close()
    
    def add_vaccination(self, cattle_id, vaccine_name, vaccination_date, next_date, notes=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vaccination_history (cattle_id, vaccine_name, vaccination_date,
                                             next_vaccination_date, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (cattle_id, vaccine_name, vaccination_date, next_date, notes))
        conn.commit()
        conn.close()
    
    def get_vaccinations(self, cattle_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM vaccination_history 
            WHERE cattle_id = ?
            ORDER BY vaccination_date DESC
        ''', (cattle_id,))
        columns = [desc[0] for desc in cursor.description]
        vaccinations = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return vaccinations
    
    def add_event(self, cattle_id, event_type, event_date, notes=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (cattle_id, event_type, event_date, notes)
            VALUES (?, ?, ?, ?)
        ''', (cattle_id, event_type, event_date, notes))
        conn.commit()
        conn.close()
    
    def get_events(self, cattle_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM events 
            WHERE cattle_id = ?
            ORDER BY event_date DESC
        ''', (cattle_id,))
        columns = [desc[0] for desc in cursor.description]
        events = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return events
    
    def add_activity_log(self, cattle_id, activity_type, description):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activity_log (cattle_id, activity_type, description)
            VALUES (?, ?, ?)
        ''', (cattle_id, activity_type, description))
        conn.commit()
        conn.close()
    
    def get_activity_log(self, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT al.*, c.tag_number, c.name
            FROM activity_log al
            JOIN cattle c ON al.cattle_id = c.id
            ORDER BY al.activity_date DESC
            LIMIT ?
        ''', (limit,))
        columns = [desc[0] for desc in cursor.description]
        activities = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return activities
    
    def get_statistics(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM cattle')
        stats['total_cattle'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM cattle WHERE is_pregnant = 1')
        stats['pregnant'] = cursor.fetchone()[0]
        
        today = datetime.now().strftime('%Y-%m-%d')
        future_60 = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date BETWEEN ? AND ?
        ''', (today, future_60))
        stats['near_birth_60'] = cursor.fetchone()[0]
        
        future_90 = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date BETWEEN ? AND ?
        ''', (future_60, future_90))
        stats['to_dry'] = cursor.fetchone()[0]
        
        past_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM cattle 
            WHERE last_birth_date >= ?
        ''', (past_30,))
        stats['recent_births'] = cursor.fetchone()[0]
        
        year_start = f"{datetime.now().year}-01-01"
        cursor.execute('''
            SELECT COUNT(*) FROM events 
            WHERE event_type = 'birth' 
            AND event_date >= ?
        ''', (year_start,))
        stats['births_this_year'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(weight) FROM cattle WHERE weight IS NOT NULL')
        avg_weight = cursor.fetchone()[0]
        stats['avg_weight'] = round(avg_weight, 1) if avg_weight else 0
        
        # % PARTOS/AÑO
        two_years_ago = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM cattle')
        total_cows = cursor.fetchone()[0]
        cursor.execute('''
            SELECT COUNT(*) FROM events 
            WHERE event_type = 'birth' 
            AND event_date >= ?
        ''', (two_years_ago,))
        births_2y = cursor.fetchone()[0]
        
        if total_cows > 0:
            births_per_cow = births_2y / total_cows
            stats['birth_rate_annual'] = round((births_per_cow / 2) * 100, 1)
        else:
            stats['birth_rate_annual'] = 0
        
        conn.close()
        return stats
    
    def get_agenda_items(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        agenda = {
            'to_dry': [],
            'near_birth': [],
            'need_vaccine': [],
            'recent_births': [],
            'overdue': []
        }
        
        future_60 = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        future_90 = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date BETWEEN ? AND ?
            ORDER BY expected_birth_date
        ''', (future_60, future_90))
        columns = [desc[0] for desc in cursor.description]
        agenda['to_dry'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date BETWEEN ? AND ?
            ORDER BY expected_birth_date
        ''', (today, future_60))
        agenda['near_birth'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date < ?
            ORDER BY expected_birth_date
        ''', (today,))
        agenda['overdue'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        past_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE last_birth_date >= ?
            ORDER BY last_birth_date DESC
        ''', (past_30,))
        agenda['recent_births'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        future_30 = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT c.*, vh.vaccine_name, vh.next_vaccination_date
            FROM cattle c
            JOIN vaccination_history vh ON c.id = vh.cattle_id
            WHERE vh.next_vaccination_date BETWEEN ? AND ?
            ORDER BY vh.next_vaccination_date
        ''', (today, future_30))
        columns_vacc = [desc[0] for desc in cursor.description]
        agenda['need_vaccine'] = [dict(zip(columns_vacc, row)) for row in cursor.fetchall()]
        
        conn.close()
        return agenda


def calculate_age(birth_date):
    if not birth_date:
        return "N/A"
    try:
        birth = datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.now()
        years = today.year - birth.year
        months = today.month - birth.month
        if months < 0:
            years -= 1
            months += 12
        return f"{years}a {months}m"
    except:
        return "N/A"


def calculate_days_to_birth(expected_date):
    if not expected_date:
        return None
    try:
        expected = datetime.strptime(expected_date, '%Y-%m-%d')
        today = datetime.now()
        delta = (expected - today).days
        return delta
    except:
        return None


def calculate_days_since(date_str):
    if not date_str:
        return None
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now()
        delta = (today - date).days
        return delta
    except:
        return None


# PANTALLA PRINCIPAL - LISTA SIMPLE SIN CAJAS
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = Label(
            text='[b]🐄 Gestión Ganadera PRO[/b]',
            markup=True,
            font_size='30sp',
            color=PRIMARY,
            size_hint_y=None,
            height=70
        )
        self.layout.add_widget(header)
        
        # Stats como LISTA DE LABELS (no cajas)
        scroll = ScrollView()
        self.stats_layout = BoxLayout(
            orientation='vertical',
            spacing=8,
            size_hint_y=None,
            padding=[15, 10]
        )
        self.stats_layout.bind(minimum_height=self.stats_layout.setter('height'))
        scroll.add_widget(self.stats_layout)
        self.layout.add_widget(scroll)
        
        # Botones
        buttons = GridLayout(cols=2, spacing=12, size_hint_y=None, height=200)
        
        btn_list = ModernButton(text='📋\nVer Ganado', font_size='20sp', bg_color=PRIMARY)
        btn_list.bind(on_press=lambda x: setattr(self.manager, 'current', 'cattle_list'))
        
        btn_add = ModernButton(text='➕\nAgregar', font_size='20sp', bg_color=SUCCESS)
        btn_add.bind(on_press=lambda x: setattr(self.manager, 'current', 'add_cattle'))
        
        btn_agenda = ModernButton(text='📅\nAgenda', font_size='20sp', bg_color=WARNING)
        btn_agenda.bind(on_press=lambda x: setattr(self.manager, 'current', 'agenda'))
        
        btn_quick = ModernButton(text='⚡\nRápido', font_size='20sp', bg_color=PRIMARY)
        btn_quick.bind(on_press=lambda x: setattr(self.manager, 'current', 'quick_log'))
        
        buttons.add_widget(btn_list)
        buttons.add_widget(btn_add)
        buttons.add_widget(btn_agenda)
        buttons.add_widget(btn_quick)
        
        self.layout.add_widget(buttons)
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.update_stats()
    
    def update_stats(self):
        self.stats_layout.clear_widgets()
        
        try:
            db = App.get_running_app().db
            stats = db.get_statistics()
            
            # FORMATO LISTA SIMPLE - TODO VISIBLE
            data = [
                ('🐮 Total Vacas:', stats.get('total_cattle', 0)),
                ('🤰 Preñadas:', stats.get('pregnant', 0)),
                ('⚠️ Próximas 60d:', stats.get('near_birth_60', 0)),
                ('🚫 Para Secar:', stats.get('to_dry', 0)),
                ('👶 Partos 30d:', stats.get('recent_births', 0)),
                (f'📊 Año {datetime.now().year}:', stats.get('births_this_year', 0)),
                ('📈 % Partos/Año:', f"{stats.get('birth_rate_annual', 0)}%"),
                ('⚖️ Peso Promedio:', f"{stats.get('avg_weight', 0)} kg"),
            ]
            
            for label, value in data:
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=[10, 5])
                
                label_widget = Label(
                    text=f'[b]{label}[/b]',
                    markup=True,
                    font_size='22sp',
                    color=TEXT,
                    halign='left',
                    size_hint_x=0.6
                )
                label_widget.bind(size=label_widget.setter('text_size'))
                
                value_widget = Label(
                    text=str(value),
                    font_size='26sp',
                    color=PRIMARY,
                    halign='right',
                    size_hint_x=0.4
                )
                value_widget.bind(size=value_widget.setter('text_size'))
                
                row.add_widget(label_widget)
                row.add_widget(value_widget)
                self.stats_layout.add_widget(row)
        
        except Exception as e:
            print(f"[ERROR] update_stats: {e}")


# LISTA DE GANADO - SIN CAJAS DE BÚSQUEDA
class CattleListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        
        # Header simple
        top_bar = BoxLayout(size_hint_y=None, height=80, spacing=10)
        
        btn_back = ModernButton(text='← Inicio', bg_color=CARD, font_size='20sp')
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        
        title = Label(
            text='[b]📋 Lista de Ganado[/b]',
            markup=True,
            font_size='26sp',
            color=TEXT
        )
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(title)
        self.layout.add_widget(top_bar)
        
        # Lista
        self.scroll = ScrollView()
        self.cattle_container = BoxLayout(
            orientation='vertical',
            spacing=15,
            size_hint_y=None,
            padding=[10, 10]
        )
        self.cattle_container.bind(minimum_height=self.cattle_container.setter('height'))
        self.scroll.add_widget(self.cattle_container)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.load_cattle_list()
    
    def load_cattle_list(self):
        self.cattle_container.clear_widgets()
        
        try:
            db = App.get_running_app().db
            cattle_list = db.get_all_cattle()
            
            if not cattle_list:
                no_data = Label(
                    text='No hay vacas',
                    size_hint_y=None,
                    height=100,
                    font_size='22sp',
                    color=TEXT_DIM
                )
                self.cattle_container.add_widget(no_data)
                return
            
            for cattle in cattle_list:
                # CARD SIMPLE CON BOTÓN
                card = ModernCard(
                    orientation='vertical',
                    size_hint_y=None,
                    height=140,
                    padding=25,
                    spacing=12
                )
                
                tag = Label(
                    text=f"[b]{cattle['tag_number']}[/b]",
                    markup=True,
                    font_size='38sp',
                    color=PRIMARY,
                    size_hint_y=None,
                    height=50
                )
                
                name = Label(
                    text=cattle.get('name', 'Sin nombre'),
                    font_size='24sp',
                    color=TEXT,
                    size_hint_y=None,
                    height=35
                )
                
                btn = ModernButton(
                    text='Ver Detalles',
                    size_hint_y=None,
                    height=55,
                    font_size='18sp'
                )
                btn.bind(on_press=lambda x, cid=cattle['id']: self.view_detail(cid))
                
                card.add_widget(tag)
                card.add_widget(name)
                card.add_widget(btn)
                
                self.cattle_container.add_widget(card)
        except Exception as e:
            print(f"[ERROR] load_cattle_list: {e}")
    
    def view_detail(self, cattle_id):
        detail_screen = self.manager.get_screen('cattle_detail')
        detail_screen.load_cattle(cattle_id)
        self.manager.current = 'cattle_detail'


# AGREGAR VACA - CON SPINNERS EN LUGAR DE TEXTINPUT
class AddCattleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        
        # Header
        top_bar = BoxLayout(size_hint_y=None, height=80, spacing=10)
        
        btn_back = ModernButton(text='← Atrás', bg_color=CARD, font_size='20sp')
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'cattle_list'))
        
        title = Label(
            text='[b]➕ Agregar Vaca[/b]',
            markup=True,
            font_size='26sp',
            color=TEXT
        )
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(title)
        self.layout.add_widget(top_bar)
        
        # Formulario con BOTONES para ingresar datos
        scroll = ScrollView()
        form = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint_y=None,
            padding=[15, 15]
        )
        form.bind(minimum_height=form.setter('height'))
        
        # Arete - con botón para ingresar
        form.add_widget(Label(
            text='🏷️ Número de Arete *',
            size_hint_y=None,
            height=50,
            font_size='22sp',
            color=TEXT,
            halign='left'
        ))
        
        self.tag_label = Label(
            text='Click para ingresar',
            font_size='24sp',
            color=TEXT_DIM,
            size_hint_y=None,
            height=60
        )
        
        btn_tag = ModernButton(
            text='Ingresar Arete',
            size_hint_y=None,
            height=70,
            font_size='20sp'
        )
        btn_tag.bind(on_press=self.show_tag_input)
        
        form.add_widget(self.tag_label)
        form.add_widget(btn_tag)
        
        # Categoría
        form.add_widget(Label(
            text='📂 Categoría',
            size_hint_y=None,
            height=50,
            font_size='22sp',
            color=TEXT,
            halign='left'
        ))
        
        self.category_spinner = Spinner(
            text='Seleccionar',
            values=('Vaca', 'Vaquilla', 'Becerra', 'Otro'),
            size_hint_y=None,
            height=80,
            background_color=CARD,
            color=TEXT,
            font_size='24sp'
        )
        form.add_widget(self.category_spinner)
        
        # Preñada
        form.add_widget(Label(
            text='🤰 ¿Está preñada?',
            size_hint_y=None,
            height=50,
            font_size='22sp',
            color=TEXT,
            halign='left'
        ))
        
        preg_box = BoxLayout(size_hint_y=None, height=75, spacing=12)
        self.pregnant_yes = ModernButton(text='SÍ', bg_color=CARD, font_size='22sp')
        self.pregnant_no = ModernButton(text='NO', bg_color=PRIMARY, font_size='22sp')
        self.pregnant_yes.bind(on_press=self.toggle_pregnant_yes)
        self.pregnant_no.bind(on_press=self.toggle_pregnant_no)
        preg_box.add_widget(self.pregnant_yes)
        preg_box.add_widget(self.pregnant_no)
        form.add_widget(preg_box)
        
        self.is_pregnant = False
        
        scroll.add_widget(form)
        self.layout.add_widget(scroll)
        
        # Botón guardar
        btn_save = ModernButton(
            text='💾 Guardar Vaca',
            size_hint_y=None,
            height=80,
            bg_color=SUCCESS,
            font_size='24sp'
        )
        btn_save.bind(on_press=self.save_cattle)
        self.layout.add_widget(btn_save)
        
        self.add_widget(self.layout)
        
        self.tag_value = ''
    
    def show_tag_input(self, instance):
        # Popup con teclado numérico
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        content.add_widget(Label(
            text='Ingresa el número de arete:',
            font_size='20sp',
            size_hint_y=None,
            height=40
        ))
        
        display = Label(
            text='',
            font_size='32sp',
            size_hint_y=None,
            height=60,
            color=PRIMARY
        )
        content.add_widget(display)
        
        # Teclado numérico
        keyboard = GridLayout(cols=3, spacing=10, size_hint_y=None, height=320)
        
        for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '←', 'OK']:
            btn = ModernButton(text=num, font_size='28sp')
            if num == 'OK':
                btn.bg_color = SUCCESS
            elif num == '←':
                btn.bg_color = DANGER
            
            def on_press(x, n=num):
                if n == 'OK':
                    self.tag_value = display.text
                    self.tag_label.text = self.tag_value
                    popup.dismiss()
                elif n == '←':
                    display.text = display.text[:-1]
                else:
                    display.text += n
            
            btn.bind(on_press=on_press)
            keyboard.add_widget(btn)
        
        content.add_widget(keyboard)
        
        popup = Popup(
            title='Número de Arete',
            content=content,
            size_hint=(0.9, 0.8)
        )
        popup.open()
    
    def toggle_pregnant_yes(self, instance):
        self.is_pregnant = True
        self.pregnant_yes.bg_color = PRIMARY
        self.pregnant_no.bg_color = CARD
    
    def toggle_pregnant_no(self, instance):
        self.is_pregnant = False
        self.pregnant_yes.bg_color = CARD
        self.pregnant_no.bg_color = PRIMARY
    
    def save_cattle(self, instance):
        if not self.tag_value:
            return
        
        data = {
            'tag_number': self.tag_value,
            'name': '',
            'category': self.category_spinner.text if self.category_spinner.text != 'Seleccionar' else None,
            'is_pregnant': 1 if self.is_pregnant else 0
        }
        
        try:
            db = App.get_running_app().db
            cattle_id = db.add_cattle(data)
            
            if cattle_id:
                self.tag_value = ''
                self.tag_label.text = 'Click para ingresar'
                self.category_spinner.text = 'Seleccionar'
                self.toggle_pregnant_no(None)
                self.manager.current = 'cattle_list'
        except Exception as e:
            print(f"[ERROR] save_cattle: {e}")


# Resto de pantallas simplificadas...
class CattleDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cattle_id = None
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        
        top_bar = BoxLayout(size_hint_y=None, height=80, spacing=10)
        btn_back = ModernButton(text='← Lista', bg_color=CARD, font_size='20sp')
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'cattle_list'))
        self.title_label = Label(text='Detalle', font_size='26sp', color=TEXT)
        btn_delete = ModernButton(text='🗑️', size_hint_x=0.3, bg_color=DANGER, font_size='20sp')
        btn_delete.bind(on_press=self.confirm_delete)
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(self.title_label)
        top_bar.add_widget(btn_delete)
        self.layout.add_widget(top_bar)
        
        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=[15, 15])
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)
    
    def load_cattle(self, cattle_id):
        self.cattle_id = cattle_id
        self.content.clear_widgets()
        
        try:
            db = App.get_running_app().db
            c = db.get_cattle_by_id(cattle_id)
            
            if not c:
                return
            
            # Info como LISTA DE LABELS
            info_lines = [
                ('Arete:', c['tag_number']),
                ('Nombre:', c.get('name', 'Sin nombre')),
                ('Categoría:', c.get('category', 'N/A')),
                ('Edad:', calculate_age(c.get('birth_date'))),
                ('Peso:', f"{c.get('weight') or 0} kg"),
                ('Estado:', '🤰 PREÑADA' if c['is_pregnant'] else 'Sin cargar'),
            ]
            
            for label, value in info_lines:
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=[10, 5])
                
                label_widget = Label(
                    text=f'[b]{label}[/b]',
                    markup=True,
                    font_size='20sp',
                    color=TEXT_DIM,
                    halign='left',
                    size_hint_x=0.5
                )
                label_widget.bind(size=label_widget.setter('text_size'))
                
                value_widget = Label(
                    text=str(value),
                    font_size='22sp',
                    color=TEXT,
                    halign='right',
                    size_hint_x=0.5
                )
                value_widget.bind(size=value_widget.setter('text_size'))
                
                row.add_widget(label_widget)
                row.add_widget(value_widget)
                self.content.add_widget(row)
            
            # Botones
            actions = GridLayout(cols=2, spacing=12, size_hint_y=None, height=160, padding=[0, 20])
            
            btn_birth = ModernButton(text='🐄 Parto', bg_color=SUCCESS, font_size='20sp')
            btn_birth.bind(on_press=self.register_birth)
            
            btn_dry = ModernButton(text='🚫 Secar', bg_color=WARNING, font_size='20sp')
            btn_dry.bind(on_press=self.dry_cow)
            
            btn_preg = ModernButton(text='🤰 Cargar', bg_color=PRIMARY, font_size='20sp')
            btn_preg.bind(on_press=self.mark_pregnant)
            
            btn_vacc = ModernButton(text='💉 Vacunar', bg_color=PRIMARY, font_size='20sp')
            btn_vacc.bind(on_press=self.add_vaccination)
            
            actions.add_widget(btn_birth)
            actions.add_widget(btn_dry)
            actions.add_widget(btn_preg)
            actions.add_widget(btn_vacc)
            
            self.content.add_widget(actions)
            
        except Exception as e:
            print(f"[ERROR] load_cattle: {e}")
    
    def add_vaccination(self, instance):
        try:
            db = App.get_running_app().db
            today = datetime.now().strftime('%Y-%m-%d')
            db.add_vaccination(self.cattle_id, 'Vacuna general', today, today, '')
            db.add_activity_log(self.cattle_id, 'vaccination', 'Vacunación')
            self.load_cattle(self.cattle_id)
        except Exception as e:
            print(f"[ERROR] add_vaccination: {e}")
    
    def register_birth(self, instance):
        try:
            db = App.get_running_app().db
            today = datetime.now().strftime('%Y-%m-%d')
            db.update_cattle(self.cattle_id, {
                'is_pregnant': 0,
                'last_birth_date': today,
                'pregnancy_date': None,
                'expected_birth_date': None
            })
            db.add_event(self.cattle_id, 'birth', today, 'Parto')
            db.add_activity_log(self.cattle_id, 'birth', 'Parto registrado')
            self.load_cattle(self.cattle_id)
        except Exception as e:
            print(f"[ERROR] register_birth: {e}")
    
    def dry_cow(self, instance):
        try:
            db = App.get_running_app().db
            today = datetime.now().strftime('%Y-%m-%d')
            db.add_event(self.cattle_id, 'drying', today, 'Secado')
            db.add_activity_log(self.cattle_id, 'drying', 'Vaca secada')
            self.load_cattle(self.cattle_id)
        except Exception as e:
            print(f"[ERROR] dry_cow: {e}")
    
    def mark_pregnant(self, instance):
        try:
            db = App.get_running_app().db
            today = datetime.now().strftime('%Y-%m-%d')
            expected = (datetime.now() + timedelta(days=283)).strftime('%Y-%m-%d')
            db.update_cattle(self.cattle_id, {
                'is_pregnant': 1,
                'pregnancy_date': today,
                'expected_birth_date': expected
            })
            db.add_activity_log(self.cattle_id, 'pregnancy', f'Preñada - Parto: {expected}')
            self.load_cattle(self.cattle_id)
        except Exception as e:
            print(f"[ERROR] mark_pregnant: {e}")
    
    def confirm_delete(self, instance):
        try:
            db = App.get_running_app().db
            db.delete_cattle(self.cattle_id)
            self.manager.current = 'cattle_list'
        except Exception as e:
            print(f"[ERROR] confirm_delete: {e}")


class AgendaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        
        top_bar = BoxLayout(size_hint_y=None, height=80, spacing=10)
        btn_back = ModernButton(text='← Inicio', bg_color=CARD, font_size='20sp')
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text='[b]📅 Agenda[/b]', markup=True, font_size='26sp', color=TEXT)
        top_bar.add_widget(btn_back)
        top_bar.add_widget(title)
        self.layout.add_widget(top_bar)
        
        self.scroll = ScrollView()
        self.events_container = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=[15, 15])
        self.events_container.bind(minimum_height=self.events_container.setter('height'))
        self.scroll.add_widget(self.events_container)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.load_events()
    
    def load_events(self):
        self.events_container.clear_widgets()
        
        try:
            db = App.get_running_app().db
            agenda = db.get_agenda_items()
            
            if agenda['near_birth']:
                self.events_container.add_widget(Label(
                    text='[b]⚠️ PRÓXIMAS A PARIR[/b]',
                    markup=True,
                    size_hint_y=None,
                    height=50,
                    font_size='24sp',
                    color=WARNING
                ))
                
                for c in agenda['near_birth']:
                    days = calculate_days_to_birth(c['expected_birth_date'])
                    
                    row = BoxLayout(orientation='horizontal', size_hint_y=None, height=70, padding=[15, 5])
                    
                    info = Label(
                        text=f"{c['tag_number']} - Faltan {days}d",
                        font_size='22sp',
                        color=TEXT,
                        halign='left'
                    )
                    info.bind(size=info.setter('text_size'))
                    
                    row.add_widget(info)
                    self.events_container.add_widget(row)
            
            if not any(agenda.values()):
                self.events_container.add_widget(Label(
                    text='Sin eventos',
                    size_hint_y=None,
                    height=100,
                    font_size='22sp',
                    color=TEXT_DIM
                ))
        except Exception as e:
            print(f"[ERROR] load_events: {e}")


class QuickLogScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        
        top_bar = BoxLayout(size_hint_y=None, height=80, spacing=10)
        btn_back = ModernButton(text='← Inicio', bg_color=CARD, font_size='20sp')
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text='[b]⚡ Rápido[/b]', markup=True, font_size='26sp', color=TEXT)
        top_bar.add_widget(btn_back)
        top_bar.add_widget(title)
        self.layout.add_widget(top_bar)
        
        inst = Label(
            text='Comandos: "vacuné 123", "secé 456", "parió 789", "cargué 101"',
            font_size='16sp',
            size_hint_y=None,
            height=50,
            color=TEXT_DIM
        )
        self.layout.add_widget(inst)
        
        self.scroll = ScrollView()
        self.log_container = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, padding=[15, 15])
        self.log_container.bind(minimum_height=self.log_container.setter('height'))
        self.scroll.add_widget(self.log_container)
        self.layout.add_widget(self.scroll)
        
        # Botón para ingresar comando
        btn_cmd = ModernButton(
            text='Ingresar Comando',
            size_hint_y=None,
            height=80,
            bg_color=SUCCESS,
            font_size='22sp'
        )
        btn_cmd.bind(on_press=self.show_command_input)
        self.layout.add_widget(btn_cmd)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.load_activity_log()
    
    def load_activity_log(self):
        self.log_container.clear_widgets()
        
        try:
            db = App.get_running_app().db
            activities = db.get_activity_log(10)
            
            if not activities:
                self.log_container.add_widget(Label(
                    text='Sin actividades',
                    size_hint_y=None,
                    height=100,
                    font_size='22sp',
                    color=TEXT_DIM
                ))
                return
            
            for act in activities:
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=[10, 5])
                
                info = Label(
                    text=f"{act['tag_number']} - {act['description']}",
                    font_size='20sp',
                    color=TEXT,
                    halign='left'
                )
                info.bind(size=info.setter('text_size'))
                
                row.add_widget(info)
                self.log_container.add_widget(row)
        except Exception as e:
            print(f"[ERROR] load_activity_log: {e}")
    
    def show_command_input(self, instance):
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        content.add_widget(Label(
            text='Ingresa comando:',
            font_size='20sp',
            size_hint_y=None,
            height=40
        ))
        
        display = Label(
            text='',
            font_size='28sp',
            size_hint_y=None,
            height=60,
            color=PRIMARY
        )
        content.add_widget(display)
        
        # Teclado
        keyboard = GridLayout(cols=3, spacing=10, size_hint_y=None, height=320)
        
        for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '←', 'OK']:
            btn = ModernButton(text=num, font_size='28sp')
            if num == 'OK':
                btn.bg_color = SUCCESS
            elif num == '←':
                btn.bg_color = DANGER
            
            def on_press(x, n=num):
                if n == 'OK':
                    self.process_command(display.text)
                    popup.dismiss()
                elif n == '←':
                    display.text = display.text[:-1]
                else:
                    display.text += n
            
            btn.bind(on_press=on_press)
            keyboard.add_widget(btn)
        
        content.add_widget(keyboard)
        
        # Botones de comando
        cmd_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=150)
        
        cmds = [
            ('💉 Vacuné', 'vacuné '),
            ('🐄 Parió', 'parió '),
            ('🚫 Secé', 'secé '),
            ('🤰 Cargué', 'cargué ')
        ]
        
        for label, cmd in cmds:
            btn = ModernButton(text=label, font_size='18sp')
            btn.bind(on_press=lambda x, c=cmd: setattr(display, 'text', c))
            cmd_grid.add_widget(btn)
        
        content.add_widget(cmd_grid)
        
        popup = Popup(
            title='Comando Rápido',
            content=content,
            size_hint=(0.95, 0.85)
        )
        popup.open()
    
    def process_command(self, command):
        command = command.strip().lower()
        
        if not command:
            return
        
        try:
            db = App.get_running_app().db
            
            arete_match = re.search(r'(\d+)', command)
            if not arete_match:
                return
            
            arete = arete_match.group(1)
            cattle_list = db.search_cattle(arete)
            if not cattle_list:
                return
            
            cattle = cattle_list[0]
            cattle_id = cattle['id']
            today = datetime.now().strftime('%Y-%m-%d')
            
            if 'vacun' in command:
                db.add_vaccination(cattle_id, 'Vacuna general', today, today, '')
                db.add_activity_log(cattle_id, 'vaccination', 'Vacunación')
            
            elif 'sec' in command:
                db.add_event(cattle_id, 'drying', today, 'Secado')
                db.add_activity_log(cattle_id, 'drying', 'Secado')
            
            elif 'pari' in command:
                db.update_cattle(cattle_id, {
                    'is_pregnant': 0,
                    'last_birth_date': today,
                    'pregnancy_date': None,
                    'expected_birth_date': None
                })
                db.add_event(cattle_id, 'birth', today, 'Parto')
                db.add_activity_log(cattle_id, 'birth', 'Parto')
            
            elif 'carg' in command:
                expected_date = (datetime.now() + timedelta(days=283)).strftime('%Y-%m-%d')
                db.update_cattle(cattle_id, {
                    'is_pregnant': 1,
                    'pregnancy_date': today,
                    'expected_birth_date': expected_date
                })
                db.add_activity_log(cattle_id, 'pregnancy', f'Preñada ({expected_date})')
            
            self.load_activity_log()
        except Exception as e:
            print(f"[ERROR] process_command: {e}")


class CattleManagerApp(App):
    def build(self):
        try:
            self.db = Database()
            sm = ScreenManager()
            sm.add_widget(HomeScreen(name='home'))
            sm.add_widget(CattleListScreen(name='cattle_list'))
            sm.add_widget(AddCattleScreen(name='add_cattle'))
            sm.add_widget(CattleDetailScreen(name='cattle_detail'))
            sm.add_widget(AgendaScreen(name='agenda'))
            sm.add_widget(QuickLogScreen(name='quick_log'))
            return sm
        except Exception as e:
            print(f"[ERROR] build: {e}")
            error = BoxLayout(orientation='vertical', padding=20)
            error.add_widget(Label(text=f'Error: {str(e)}', color=DANGER))
            return error


if __name__ == '__main__':
    CattleManagerApp().run()
