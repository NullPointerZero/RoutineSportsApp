# main.py
# Korrigierte, lauffähige Ein-Datei-Kivy-App
# Änderungen gegenüber der ersten Version:
# - Eigene Widget-Klasse TodoRow mit Properties (text, done, index)
# - Ersetzung von Builder.template -> Factory.TodoRow (robuster)
# - Kleinere Anpassungen im KV (Regel <TodoRow> statt <TodoRow@BoxLayout>)

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.factory import Factory

KV = """
#:import dp kivy.metrics.dp
#:import NoTransition kivy.uix.screenmanager.NoTransition

<NavBar@BoxLayout>:
    size_hint_y: None
    height: dp(48)
    padding: dp(8)
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: app.bg_accent
        Rectangle:
            pos: self.pos
            size: self.size
    Button:
        text: 'Home'
        on_release: app.go('home')
    Button:
        text: 'Todos'
        on_release: app.go('todos')
    Button:
        text: 'Einstellungen'
        on_release: app.go('settings')

<TodoRow>:
    # Python-Klasse stellt Properties bereit
    size_hint_y: None
    height: dp(44)
    spacing: dp(8)
    padding: dp(8)
    canvas.before:
        Color:
            rgba: app.card_bg
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10),]
    CheckBox:
        active: root.done
        on_active: app.toggle_todo_done(root.index, self.active)
        size_hint_x: None
        width: dp(32)
    Label:
        text: root.text
        color: app.fg
        text_size: self.size
        halign: 'left'
        valign: 'middle'
        shorten: True
    Button:
        text: 'Löschen'
        size_hint_x: None
        width: dp(90)
        on_release: app.delete_todo(root.index)

<HomeScreen>:
    name: 'home'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: app.bg
            Rectangle:
                pos: self.pos
                size: self.size
        NavBar:
        BoxLayout:
            orientation: 'vertical'
            padding: dp(16)
            spacing: dp(16)
            Label:
                text: 'Willkommen'
                font_size: '22sp'
                size_hint_y: None
                height: dp(40)
                color: app.fg
            Label:
                id: counter_label
                text: f"Zähler: {app.counter}"
                font_size: '18sp'
                size_hint_y: None
                height: dp(30)
                color: app.fg
            BoxLayout:
                size_hint_y: None
                height: dp(48)
                spacing: dp(8)
                Button:
                    text: '+1'
                    on_release: app.inc()
                Button:
                    text: 'Reset'
                    on_release: app.reset()
            Widget:

<TodosScreen>:
    name: 'todos'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: app.bg
            Rectangle:
                pos: self.pos
                size: self.size
        NavBar:
        BoxLayout:
            orientation: 'vertical'
            padding: dp(16)
            spacing: dp(12)
            Label:
                text: 'ToDo-Liste'
                font_size: '22sp'
                size_hint_y: None
                height: dp(40)
                color: app.fg
            BoxLayout:
                size_hint_y: None
                height: dp(44)
                spacing: dp(8)
                TextInput:
                    id: todo_input
                    hint_text: 'Neue Aufgabe eingeben'
                    multiline: False
                    on_text_validate: app.add_todo(self.text); self.text = ''
                    foreground_color: app.fg
                    background_color: app.input_bg
                Button:
                    text: 'Hinzufügen'
                    size_hint_x: None
                    width: dp(120)
                    on_release:
                        app.add_todo(todo_input.text)
                        todo_input.text = ''
            ScrollView:
                bar_width: dp(6)
                scroll_type: ['bars', 'content']
                do_scroll_x: False
                GridLayout:
                    id: todos_box
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(8)

<SettingsScreen>:
    name: 'settings'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: app.bg
            Rectangle:
                pos: self.pos
                size: self.size
        NavBar:
        BoxLayout:
            orientation: 'vertical'
            padding: dp(16)
            spacing: dp(16)
            Label:
                text: 'Einstellungen'
                font_size: '22sp'
                size_hint_y: None
                height: dp(40)
                color: app.fg
            BoxLayout:
                size_hint_y: None
                height: dp(48)
                spacing: dp(8)
                Label:
                    text: 'Dunkler Modus'
                    color: app.fg
                ToggleButton:
                    id: theme_toggle
                    text: 'An' if app.dark_mode else 'Aus'
                    state: 'down' if app.dark_mode else 'normal'
                    on_state:
                        app.set_dark_mode(self.state == 'down')
                        self.text = 'An' if app.dark_mode else 'Aus'
            Button:
                text: 'Alle Todos löschen'
                size_hint_y: None
                height: dp(44)
                on_release: app.clear_all_todos()
            Widget:

<RootSM@ScreenManager>:
    transition: NoTransition()

RootSM:
    HomeScreen:
    TodosScreen:
    SettingsScreen:
"""

class TodoRow(BoxLayout):
    text = StringProperty("")
    done = BooleanProperty(False)
    index = NumericProperty(0)

class HomeScreen(Screen):
    pass

class TodosScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class MiniKivyApp(App):
    title = "Kivy Mini-App"

    dark_mode = BooleanProperty(False)
    counter = NumericProperty(0)
    todos = ListProperty([])  # Liste von Dicts: {"text": str, "done": bool}

    @property
    def bg(self):
        return (0.08, 0.08, 0.09, 1) if self.dark_mode else (0.97, 0.97, 0.98, 1)

    @property
    def bg_accent(self):
        return (0.16, 0.16, 0.18, 1) if self.dark_mode else (0.90, 0.90, 0.92, 1)

    @property
    def card_bg(self):
        return (0.13, 0.13, 0.14, 1) if self.dark_mode else (1, 1, 1, 1)

    @property
    def fg(self):
        return (1, 1, 1, 1) if self.dark_mode else (0.12, 0.12, 0.14, 1)

    @property
    def input_bg(self):
        return (0.20, 0.20, 0.22, 1) if self.dark_mode else (1, 1, 1, 1)

    def build(self):
        self.store = JsonStore('appdata.json')
        self._load_state()
        root = Builder.load_string(KV)
        Clock.schedule_once(lambda *a: self._refresh_todos_ui())
        return root

    # Navigation
    def go(self, screen_name: str):
        self.root.current = screen_name

    # Counter-Logik
    def inc(self):
        self.counter += 1
        self._save_state()

    def reset(self):
        self.counter = 0
        self._save_state()

    # Theme
    def set_dark_mode(self, value: bool):
        self.dark_mode = bool(value)
        self._save_state()

    # Todos-Logik
    def add_todo(self, text: str):
        text = (text or '').strip()
        if not text:
            return
        self.todos.append({"text": text, "done": False})
        self._save_state()
        self._refresh_todos_ui()

    def toggle_todo_done(self, index: int, done: bool):
        if 0 <= index < len(self.todos):
            self.todos[index]["done"] = bool(done)
            self._save_state()

    def delete_todo(self, index: int):
        if 0 <= index < len(self.todos):
            self.todos.pop(index)
            self._save_state()
            self._refresh_todos_ui()

    def clear_all_todos(self):
        self.todos = []
        self._save_state()
        self._refresh_todos_ui()

    # UI-Helfer
    def _refresh_todos_ui(self):
        try:
            screen = self.root.get_screen('todos')
            box = screen.ids.todos_box
            box.clear_widgets()
            for i, item in enumerate(self.todos):
                row = Factory.TodoRow(text=item['text'], done=item['done'], index=i)
                box.add_widget(row)
        except Exception as e:
            print('Fehler beim Aktualisieren der Todos:', e)

    # Persistenz
    def _save_state(self):
        try:
            self.store.put('state',
                           counter=int(self.counter),
                           dark_mode=bool(self.dark_mode),
                           todos=self.todos)
        except Exception as e:
            print('Speichern fehlgeschlagen:', e)

    def _load_state(self):
        if self.store.exists('state'):
            data = self.store.get('state')
            self.counter = int(data.get('counter', 0))
            self.dark_mode = bool(data.get('dark_mode', False))
            self.todos = list(data.get('todos', []))
        else:
            self.counter = 0
            self.dark_mode = False
            self.todos = []

if __name__ == '__main__':
    MiniKivyApp().run()
