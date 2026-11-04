from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.image import AsyncImage
import requests

API = "http://127.0.0.1:8000"
COLORS = {"bg": (0.96, 0.97, 1.0, 1), "primary": (0.35, 0.45, 0.98, 1), "dark": (0.13, 0.15, 0.25, 1)}

class NiceButton(Button):
    def __init__(self, bg_color=COLORS["primary"], **kwargs):
        self.bg_c = bg_color
        super().__init__(background_normal='', background_color=(0,0,0,0), **kwargs)
        with self.canvas.before:
            Color(rgba=self.bg_c)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=lambda *a: setattr(self.rect, 'pos', self.pos), size=lambda *a: setattr(self.rect, 'size', self.size))

class Card(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(rgba=(1,1,1,1))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
        self.bind(pos=lambda *a: setattr(self.rect, 'pos', self.pos), size=lambda *a: setattr(self.rect, 'size', self.size))

class QGApp(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation='vertical', **kw)
        self.nom = ""
        self.continent_actuel = "africa"
        self.mission = None
        self.index = 0
        self.score = 0
        self.points_totaux = 0
        self.conquis = [] # continents conquis
        with self.canvas.before:
            Color(rgba=COLORS["bg"])
            self.bg = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda *a: setattr(self.bg, 'pos', self.pos), size=lambda *a: setattr(self.bg, 'size', self.size))
        self.ecran_accueil()

    def ecran_accueil(self):
        self.clear_widgets()
        self.add_widget(Label(text="[b]QG WORLD[/b]\n[size=14sp]Conquiers le monde en Anglais[/size]", markup=True, font_size='28sp', color=COLORS["dark"], size_hint_y=0.4))
        body = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15), size_hint_y=0.6)
        card = Card(orientation='vertical', padding=dp(20), spacing=dp(15))
        card.add_widget(Label(text="Salama, future conquerante! Ton nom?", bold=True, color=(0.2,0.2,0.2,1)))
        self.input_nom = TextInput(hint_text="Ando", multiline=False, size_hint_y=None, height=dp(50))
        card.add_widget(self.input_nom)
        card.add_widget(NiceButton(text="VOIR LA CARTE DU MONDE ->", height=dp(55), size_hint_y=None, on_press=self.ecran_carte))
        body.add_widget(card)
        self.add_widget(body)

    def ecran_carte(self, *a):
        if hasattr(self, 'input_nom') and self.input_nom.text:
            self.nom = self.input_nom.text
        self.clear_widgets()
        self.add_widget(Label(text=f"Carte de {self.nom} - Conquis: {len(self.conquis)}/5", bold=True, color=COLORS["dark"], size_hint_y=0.15))
        try:
            conts = requests.get(f"{API}/continents", timeout=3).json()
        except:
            conts = {}
        body = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))
        ordre = ["africa", "europe", "asia", "america", "oceania"]
        for cid in ordre:
            c = conts.get(cid)
            if not c: continue
            is_conquis = cid in self.conquis
            # Couleur grise si pas encore debloque (on doit faire Afrique d'abord)
            can_play = (cid == "africa" or ordre[ordre.index(cid)-1] in self.conquis)
            bg = c["couleur"] if can_play else (0.7,0.7,0.7,1)
            txt = f"{'✅' if is_conquis else '🌍'} {c['nom']} - {c['pays_actuel']} ({c['points']}pts/q) - {c['nb_q']}Q"
            if not can_play: txt = f"🔒 {c['nom']} - Termine {ordre[ordre.index(cid)-1]} avant"
            b = NiceButton(text=txt, bg_color=bg, height=dp(60), size_hint_y=None)
            if can_play:
                b.bind(on_press=lambda x, k=cid: self.charger_mission(k))
            body.add_widget(b)
        self.add_widget(body)

    def charger_mission(self, cid):
        self.continent_actuel = cid
        self.clear_widgets()
        self.add_widget(Label(text=f"Chargement {cid}..."))
        try:
            data = requests.get(f"{API}/mission/v2/{cid}", timeout=3).json()
            self.mission = data
            self.index = 0
            self.score = 0
            self.points_totaux = 0
            self.afficher_question()
        except Exception as e:
            self.add_widget(Label(text=f"Erreur {e}"))

    def afficher_question(self):
        self.clear_widgets()
        if self.index >= len(self.mission["questions"]):
            return self.ecran_fin()
        q = self.mission["questions"][self.index]
        cont = self.mission["continent"]
        # Header avec drapeau + points
        header = BoxLayout(orientation='horizontal', size_hint_y=0.15, padding=dp(10), spacing=dp(10))
        header.add_widget(AsyncImage(source=cont["drapeau"], size_hint_x=0.3))
        header.add_widget(Label(text=f"{cont['nom']} - {cont['pays_actuel']}\nQ {self.index+1}/{len(self.mission['questions'])} - {q['points']}pts", color=COLORS["dark"], bold=True))
        self.add_widget(header)
        card = Card(padding=dp(15), size_hint_y=0.25)
        card.add_widget(Label(text=q["question"], bold=True, color=COLORS["dark"], font_size='16sp'))
        self.add_widget(card)
        body = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=0.6)
        for i, choix in enumerate(q["choix"]):
            b = NiceButton(text=choix, bg_color=(1,1,1,1), height=dp(50), size_hint_y=None)
            b.color = (0.2,0.2,0.2,1)
            b.bind(on_press=lambda x, c=i: self.verifier(c))
            body.add_widget(b)
        self.add_widget(body)

    def verifier(self, choix):
        qid = self.mission["questions"][self.index]["id"]
        try:
            r = requests.post(f"{API}/verifier/v2/{self.continent_actuel}/{qid}/{choix}", timeout=3).json()
            if r["correct"]:
                self.score += 1
                self.points_totaux += self.mission["continent"]["points"]
            self.ecran_correction(r)
        except:
            self.index += 1
            self.afficher_question()

    def ecran_correction(self, res):
        self.clear_widgets()
        col = (0.18, 0.8, 0.44, 1) if res["correct"] else (0.95, 0.32, 0.32, 1)
        txt = "CORRECT! +" + str(self.mission["continent"]["points"]) + "pts" if res["correct"] else "FAUX"
        card = Card(orientation='vertical', padding=dp(20), spacing=dp(10), size_hint_y=0.6)
        card.add_widget(Label(text=txt, bold=True, font_size='22sp', color=col))
        q = self.mission["questions"][self.index]
        card.add_widget(Label(text=f"Bonne reponse: {q['bonne_reponse_texte']}\nErreur: {q['erreur']}", color=COLORS["dark"]))
        self.add_widget(card)
        self.add_widget(NiceButton(text="SUIVANT ->", height=dp(55), size_hint_y=None, bg_color=col, on_press=lambda x: self.next_q()))

    def next_q(self, *a):
        self.index += 1
        self.afficher_question()

    def ecran_fin(self):
        self.clear_widgets()
        total = len(self.mission["questions"])
        pct = int(self.score/total*100) if total else 0
        max_pts = self.mission["total_points_possibles"]
        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        root.add_widget(Label(text=f"{self.score}/{total} - {pct}%\n{self.points_totaux}/{max_pts} pts", bold=True, font_size='28sp', color=COLORS["primary"], size_hint_y=0.3))
        cont = self.mission["continent"]
        if pct >= 80:
            if self.continent_actuel not in self.conquis:
                self.conquis.append(self.continent_actuel)
            root.add_widget(Label(text=f"🎉 CONTINENT CONQUIS! {cont['nom']}", bold=True, color=(0.18, 0.8, 0.44, 1)))
            root.add_widget(AsyncImage(source=cont["drapeau"], size_hint_y=0.4))
            root.add_widget(Label(text=f"Tu as conquis {cont['pays_actuel']}! +{self.points_totaux} pts\nProchain continent debloque!", font_size='13sp', color=COLORS["dark"]))
        else:
            root.add_widget(Label(text=f"Il te faut 80% pour conquerir {cont['nom']}\nTu as {pct}%, retente!", color=(0.95, 0.32, 0.32, 1)))
        root.add_widget(NiceButton(text="CARTE DU MONDE", height=dp(55), size_hint_y=None, bg_color=COLORS["dark"], on_press=lambda x: self.ecran_carte()))
        root.add_widget(NiceButton(text=f"REJOUER {cont['nom']} (nouvelles questions)", height=dp(50), size_hint_y=None, bg_color=cont["couleur"], on_press=lambda x: self.charger_mission(self.continent_actuel)))
        self.add_widget(root)

class MainApp(App):
    def build(self): return QGApp()
MainApp().run()
