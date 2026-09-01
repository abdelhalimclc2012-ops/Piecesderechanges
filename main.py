# -*- coding: utf-8 -*-
"""
Pièces & Consommables — application Kivy en un seul fichier (Pydroid 3)
========================================================================
Ce fichier regroupe :
  SECTION 1 - BASE DE DONNÉES (ex database.py) : toutes les fonctions
              SQLite (DAO), isolées dans leurs propres fonctions.
  SECTION 2 - INTERFACE (ex main.py) : les écrans Kivy, qui appellent
              uniquement les fonctions de la SECTION 1 (aucun SQL ici).

Lancer simplement ce fichier dans Pydroid 3.

CORRECTIONS / AJOUTS (v3) :
  - Fix : titre "Pièces & Consommables" qui chevauchait le sous-titre
    (text_size non lié sur lbl_titre / lbl_sous_titre -> corrigé).
  - Fix : émojis affichés en carrés vides (tofu) -> remplacés par du texte.
  - AJOUT : fenêtre de Configuration (bouton "Config" dans l'en-tête)
    permettant de définir le nom de l'entreprise et un logo (choisi
    depuis le stockage du téléphone). Le logo + le nom sont ensuite
    utilisés automatiquement en en-tête de l'export PDF.
"""

# ============================================================================
# SECTION 1 — BASE DE DONNÉES (DAO)
# ============================================================================

import os
import sqlite3
from datetime import datetime
from contextlib import contextmanager


# ----------------------------------------------------------------------------
# Emplacement de la base de données
# ----------------------------------------------------------------------------
def get_export_dir():
    for dossier in ("/storage/emulated/0/Download", "/storage/emulated/0",
                     os.path.expanduser("~"), os.getcwd()):
        try:
            if os.path.isdir(dossier) and os.access(dossier, os.W_OK):
                return dossier
        except Exception:
            continue
    return os.getcwd()


def get_pictures_dir():
    """Dossier de départ pour choisir un logo (là où sont en général les photos)."""
    for dossier in ("/storage/emulated/0/Pictures", "/storage/emulated/0/DCIM",
                     "/storage/emulated/0/Download", "/storage/emulated/0",
                     os.path.expanduser("~"), os.getcwd()):
        try:
            if os.path.isdir(dossier):
                return dossier
        except Exception:
            continue
    return os.getcwd()


def get_db_dir():
    """Dossier PRIVE de l'app pour stocker la base de donnees.

    Sur Android 10+ (API 29+), le "scoped storage" empeche desormais une
    app d'ecrire librement dans /storage/emulated/0/Download meme avec les
    permissions declarees dans le manifest -> sqlite3.connect() y echouait
    au tout premier lancement, provoquant un crash immediat de l'app.

    python-for-android expose la variable d'environnement ANDROID_PRIVATE
    qui pointe vers le dossier prive de l'app (toujours accessible en
    lecture/ecriture, sans aucune permission requise). On l'utilise en
    priorite quand on tourne sur Android ; sinon (Pydroid, PC...) on garde
    l'ancien comportement.
    """
    android_private = os.environ.get("ANDROID_PRIVATE")
    if android_private:
        try:
            os.makedirs(android_private, exist_ok=True)
            if os.access(android_private, os.W_OK):
                return android_private
        except Exception:
            pass
    return get_export_dir()


DB_PATH = os.path.join(get_db_dir(), "pieces_equipements.db")


@contextmanager
def conexion_db():
    """Context manager SQLite : commit automatique, fermeture garantie."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ----------------------------------------------------------------------------
# Initialisation / migration du schéma
# ----------------------------------------------------------------------------
def init_db():
    with conexion_db() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS equipements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                categorie TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS pieces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipement_id INTEGER NOT NULL,
                designation TEXT NOT NULL,
                type_piece TEXT DEFAULT 'CONSOMMABLE',
                reference_piece TEXT,
                code_magasin TEXT,
                date_maj TEXT,
                FOREIGN KEY(equipement_id) REFERENCES equipements(id)
            )
        """)
        cols = {r["name"] for r in c.execute("PRAGMA table_info(pieces)")}
        if "code_magasin" not in cols:
            c.execute("ALTER TABLE pieces ADD COLUMN code_magasin TEXT")
            if "code_article" in cols:
                c.execute("UPDATE pieces SET code_magasin = code_article WHERE code_magasin IS NULL")
        if "reference_piece" not in cols:
            c.execute("ALTER TABLE pieces ADD COLUMN reference_piece TEXT")
        c.execute("CREATE INDEX IF NOT EXISTS idx_pieces_equipement ON pieces(equipement_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_pieces_designation ON pieces(designation)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_pieces_code_magasin ON pieces(code_magasin)")

        # Table de configuration (mono-ligne, id fixe = 1)
        c.execute("""
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                nom_entreprise TEXT,
                logo_path TEXT
            )
        """)
        c.execute("INSERT OR IGNORE INTO config (id, nom_entreprise, logo_path) VALUES (1, '', '')")


# ----------------------------------------------------------------------------
# Configuration (nom entreprise + logo)
# ----------------------------------------------------------------------------
def get_config():
    with conexion_db() as conn:
        return conn.execute("SELECT * FROM config WHERE id=1").fetchone()


def save_config(nom_entreprise, logo_path):
    with conexion_db() as conn:
        conn.execute("UPDATE config SET nom_entreprise=?, logo_path=? WHERE id=1",
                     (nom_entreprise.strip(), logo_path.strip()))


# ----------------------------------------------------------------------------
# Équipements
# ----------------------------------------------------------------------------
def list_equipements():
    with conexion_db() as conn:
        return conn.execute("SELECT * FROM equipements ORDER BY nom").fetchall()


def get_equipement(eq_id):
    with conexion_db() as conn:
        return conn.execute("SELECT * FROM equipements WHERE id=?", (eq_id,)).fetchone()


def save_equipement(nom, categorie, eq_id=None):
    with conexion_db() as conn:
        if eq_id:
            conn.execute("UPDATE equipements SET nom=?, categorie=? WHERE id=?",
                        (nom, categorie, eq_id))
            return eq_id
        cur = conn.execute("INSERT INTO equipements (nom, categorie) VALUES (?,?)",
                           (nom, categorie))
        return cur.lastrowid


def delete_equipement(eq_id):
    with conexion_db() as conn:
        conn.execute("DELETE FROM pieces WHERE equipement_id=?", (eq_id,))
        conn.execute("DELETE FROM equipements WHERE id=?", (eq_id,))


# ----------------------------------------------------------------------------
# Pièces
# ----------------------------------------------------------------------------
def count_pieces():
    with conexion_db() as conn:
        return conn.execute("SELECT COUNT(*) c FROM pieces").fetchone()["c"]


def list_pieces(equipement_id, terme=""):
    with conexion_db() as conn:
        if terme:
            like = f"%{terme}%"
            return conn.execute("""
                SELECT * FROM pieces WHERE equipement_id=? AND
                (designation LIKE ? OR code_magasin LIKE ? OR reference_piece LIKE ?)
                ORDER BY designation
            """, (equipement_id, like, like, like)).fetchall()
        return conn.execute(
            "SELECT * FROM pieces WHERE equipement_id=? ORDER BY designation",
            (equipement_id,)).fetchall()


def equipement_ids_matching(terme):
    """IDs des équipements possédant au moins une pièce correspondant au terme recherché."""
    like = f"%{terme}%"
    with conexion_db() as conn:
        rows = conn.execute("""
            SELECT DISTINCT equipement_id FROM pieces
            WHERE designation LIKE ? OR code_magasin LIKE ? OR reference_piece LIKE ?
        """, (like, like, like)).fetchall()
    return {r["equipement_id"] for r in rows}


def get_piece(piece_id):
    with conexion_db() as conn:
        return conn.execute("SELECT * FROM pieces WHERE id=?", (piece_id,)).fetchone()


def save_piece(equipement_id, designation, reference_piece, code_magasin, piece_id=None):
    with conexion_db() as conn:
        if piece_id:
            conn.execute("""
                UPDATE pieces SET designation=?, reference_piece=?, code_magasin=?,
                date_maj=? WHERE id=?
            """, (designation, reference_piece, code_magasin, now_str(), piece_id))
            return piece_id
        cur = conn.execute("""
            INSERT INTO pieces (equipement_id, designation, reference_piece, code_magasin, date_maj)
            VALUES (?,?,?,?,?)
        """, (equipement_id, designation, reference_piece, code_magasin, now_str()))
        return cur.lastrowid


def delete_piece(piece_id):
    with conexion_db() as conn:
        conn.execute("DELETE FROM pieces WHERE id=?", (piece_id,))


def list_all_pieces_with_equipement():
    """Utilisé pour les exports CSV / PDF."""
    with conexion_db() as conn:
        return conn.execute("""
            SELECT e.nom AS equipement, e.categorie, p.designation, p.reference_piece,
                   p.code_magasin, p.date_maj
            FROM pieces p JOIN equipements e ON e.id = p.equipement_id
            ORDER BY e.nom, p.designation
        """).fetchall()


# ============================================================================
# SECTION 2 — INTERFACE KIVY
# ============================================================================

import csv

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.filechooser import FileChooserIconView
from kivy.metrics import dp
from kivy.graphics import (Color, Rectangle, RoundedRectangle,
                           StencilPush, StencilUse, StencilUnUse, StencilPop)
from kivy.clock import Clock
from kivy.utils import platform

# ----------------------------------------------------------------------------
# Palette (thème sombre)
# ----------------------------------------------------------------------------
COL_BG = (0.043, 0.047, 0.058, 1)
COL_CARD = (0.09, 0.10, 0.13, 1)
COL_CARD_2 = (0.13, 0.14, 0.18, 1)
COL_INPUT_ERROR = (0.32, 0.11, 0.11, 1)
COL_TEXT = (0.95, 0.95, 0.96, 1)
COL_TEXT_DIM = (0.65, 0.66, 0.70, 1)
COL_ACCENT = (0.29, 0.56, 0.60, 1)
COL_ACCENT_TEXT = (0.05, 0.09, 0.10, 1)
COL_RED = (0.90, 0.35, 0.32, 1)
COL_BADGE_COUNT_BG = (0.20, 0.21, 0.26, 1)
COL_BLUE_TITRE = (0.35, 0.55, 0.95, 1)

Window.clearcolor = COL_BG
APP_TITLE = "Pieces & Consommables"


# ----------------------------------------------------------------------------
# Widgets utilitaires
# ----------------------------------------------------------------------------
def rounded_bg(widget, color, radius=dp(10)):
    with widget.canvas.before:
        Color(*color)
        rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])
    widget.bind(pos=lambda *a: setattr(rect, "pos", widget.pos))
    widget.bind(size=lambda *a: setattr(rect, "size", widget.size))
    return rect


def toast(msg):
    box = BoxLayout(padding=dp(10))
    box.add_widget(Label(text=msg, color=COL_TEXT))
    p = Popup(title="", separator_height=0, content=box, size_hint=(0.85, 0.18),
              background_color=(0, 0, 0, 0))
    rounded_bg(box, COL_CARD_2)
    p.open()
    Clock.schedule_once(lambda dt: p.dismiss(), 1.6)


def confirm_popup(texte, on_yes):
    box = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(14))
    rounded_bg(box, COL_CARD)
    box.add_widget(Label(text=texte, color=COL_TEXT))
    btns = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
    popup = Popup(title="Confirmation", content=box, size_hint=(0.85, 0.35),
                  separator_color=COL_ACCENT, title_color=COL_TEXT,
                  background_color=(0, 0, 0, 0.6))

    def yes(*a):
        popup.dismiss()
        on_yes()

    btns.add_widget(Button(text="Annuler", background_color=COL_CARD_2, color=COL_TEXT,
                           on_release=popup.dismiss))
    btns.add_widget(Button(text="Supprimer", background_color=COL_RED, color=(1, 1, 1, 1),
                           on_release=yes))
    box.add_widget(btns)
    popup.open()


def field_label(txt):
    return Label(text=txt, color=COL_TEXT_DIM, size_hint_y=None, height=dp(20),
                font_size="12sp", halign="left", valign="middle")


class ValidatedField(BoxLayout):
    """Bloc [label] + [TextInput] + [message d'erreur sous le champ].
    Bordure/fond rouge + message quand set_error() est appelé ; se réinitialise
    automatiquement dès que l'utilisateur retape quelque chose."""

    def __init__(self, label_txt, hint="", text="", input_filter=None, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, height=dp(20 + 44 + 16),
                         spacing=dp(2), **kwargs)
        self.add_widget(field_label(label_txt))
        self.input = TextInput(hint_text=hint, text=text, multiline=False, size_hint_y=None,
                               height=dp(44), background_color=COL_CARD_2,
                               foreground_color=COL_TEXT, hint_text_color=COL_TEXT_DIM,
                               cursor_color=COL_ACCENT, padding=[dp(10)] * 4)
        if input_filter:
            self.input.input_filter = input_filter
        self.add_widget(self.input)
        self.error_label = Label(text="", color=COL_RED, font_size="11sp", size_hint_y=None,
                                 height=dp(16), halign="left", valign="middle")
        self.error_label.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        self.add_widget(self.error_label)
        self.input.bind(text=lambda *a: self.clear_error())

    @property
    def text(self):
        return self.input.text.strip()

    def set_error(self, message):
        self.error_label.text = message
        self.input.background_color = COL_INPUT_ERROR

    def clear_error(self):
        if self.error_label.text:
            self.error_label.text = ""
        self.input.background_color = COL_CARD_2


def popup_scroll_form(title, height_hint=0.7):
    """Crée un Popup dont le contenu est scrollable (clavier Android friendly).
    Retourne (popup, box) : ajouter les widgets du formulaire dans `box`."""
    scroll = ScrollView(size_hint=(1, 1))
    box = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(16), size_hint_y=None)
    box.bind(minimum_height=box.setter("height"))
    rounded_bg(box, COL_CARD)
    scroll.add_widget(box)
    popup = Popup(title=title, content=scroll, size_hint=(0.92, height_hint),
                  title_color=COL_TEXT, separator_color=COL_ACCENT,
                  background_color=(0, 0, 0, 0.6))
    return popup, box


def ascii_safe(v):
    """Nettoie une chaîne pour l'écriture PDF (police Helvetica = latin-1 uniquement)."""
    return str(v).encode("latin-1", "replace").decode("latin-1") if v is not None else ""


# ----------------------------------------------------------------------------
# Application principale
# ----------------------------------------------------------------------------
class PiecesApp(App):
    def build(self):
        try:
            init_db()
        except Exception as e:
            # Evite un crash muet au demarrage (ex: souci d'acces disque) :
            # on affiche l'erreur a l'ecran plutot que de fermer l'app.
            root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
            with root.canvas.before:
                Color(*COL_BG)
                bg = Rectangle(pos=root.pos, size=root.size)
            root.bind(pos=lambda *a: setattr(bg, "pos", root.pos))
            root.bind(size=lambda *a: setattr(bg, "size", root.size))
            lbl = Label(
                text=("Impossible d'initialiser la base de donnees.\n\n"
                      f"Chemin : {DB_PATH}\n\nErreur : {e}"),
                color=COL_TEXT, halign="left", valign="top",
            )
            lbl.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
            root.add_widget(lbl)
            return root

        self.title = APP_TITLE
        self.expanded = set()
        self.search_text = ""

        self.root_layout = BoxLayout(orientation="vertical")
        with self.root_layout.canvas.before:
            Color(*COL_BG)
            self._bg_rect = Rectangle(pos=self.root_layout.pos, size=self.root_layout.size)
        self.root_layout.bind(pos=self._sync_bg, size=self._sync_bg)

        self._build_header()
        self._refresh_header_branding()
        self._build_search()

        self.scroll = ScrollView()
        self.liste = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=(dp(12), dp(6)))
        self.liste.bind(minimum_height=self.liste.setter("height"))
        self.scroll.add_widget(self.liste)
        self.root_layout.add_widget(self.scroll)

        self._build_footer()

        self.refresh()
        return self.root_layout

    def _sync_bg(self, *a):
        self._bg_rect.pos = self.root_layout.pos
        self._bg_rect.size = self.root_layout.size

    def _build_header(self):
        # Ligne 1 : logo + nom entreprise (plus grand, mis en avant)
        # Ligne 2 : boutons Config et + Equipement
        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(130),
                           padding=(dp(14), dp(10)), spacing=dp(8))
        rounded_bg(header, COL_CARD, radius=0)

        ligne1 = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))

        titre_box = BoxLayout(orientation="vertical")
        self.lbl_titre = Label(text=APP_TITLE, bold=True, font_size="18sp", color=COL_BLUE_TITRE,
                               halign="left", valign="middle")
        self.lbl_titre.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        titre_box.add_widget(self.lbl_titre)
        ligne1.add_widget(titre_box)

        self.icon_holder = FloatLayout(size_hint_x=None, width=dp(50))
        with self.icon_holder.canvas.before:
            self._icon_color = Color(*COL_ACCENT)
            self._icon_rect = RoundedRectangle(pos=self.icon_holder.pos,
                                               size=self.icon_holder.size, radius=[dp(12)])
            # Masque : tout ce qui est ajouté APRES StencilUse (donc les enfants comme
            # l'image du logo) est decoupe a la forme arrondie -> plus de coins qui depassent.
            StencilPush()
            self._icon_mask = RoundedRectangle(pos=self.icon_holder.pos,
                                               size=self.icon_holder.size, radius=[dp(12)])
            StencilUse()
        with self.icon_holder.canvas.after:
            StencilUnUse()
            self._icon_mask2 = RoundedRectangle(pos=self.icon_holder.pos,
                                                size=self.icon_holder.size, radius=[dp(12)])
            StencilPop()

        def _sync_icon_mask(*a):
            self._icon_rect.pos = self.icon_holder.pos
            self._icon_rect.size = self.icon_holder.size
            self._icon_mask.pos = self.icon_holder.pos
            self._icon_mask.size = self.icon_holder.size
            self._icon_mask2.pos = self.icon_holder.pos
            self._icon_mask2.size = self.icon_holder.size

        self.icon_holder.bind(pos=_sync_icon_mask, size=_sync_icon_mask)
        ligne1.add_widget(self.icon_holder)

        header.add_widget(ligne1)

        ligne2 = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        btn_config = Button(text="Config", size_hint_x=0.35,
                            background_color=COL_CARD_2, color=COL_TEXT, font_size="12sp")
        btn_config.bind(on_release=lambda *a: self.popup_configuration())

        btn_add = Button(text="+ Equipement", size_hint_x=0.65,
                         background_color=COL_ACCENT, background_normal="",
                         color=COL_ACCENT_TEXT, bold=True, font_size="13sp")
        btn_add.bind(on_release=lambda *a: self.popup_equipement())

        ligne2.add_widget(btn_config)
        ligne2.add_widget(btn_add)
        header.add_widget(ligne2)

        self.root_layout.add_widget(header)

    def _refresh_header_branding(self):
        """Met à jour le titre et le badge/logo de l'en-tête selon la configuration."""
        cfg = get_config()
        nom = (cfg["nom_entreprise"] or "").strip() if cfg else ""
        self.lbl_titre.text = nom if nom else APP_TITLE
        self._refresh_icon(cfg)

    def _refresh_icon(self, cfg=None):
        if cfg is None:
            cfg = get_config()
        logo_path = (cfg["logo_path"] or "").strip() if cfg else ""
        self.icon_holder.clear_widgets()
        if logo_path and os.path.isfile(logo_path):
            # Fond blanc pour se fondre avec le fond blanc habituel des logos
            # (évite le liseré jaune qui dépassait autour de l'image)
            self._icon_color.rgba = (1, 1, 1, 1)
            img = KivyImage(source=logo_path, size_hint=(1, 1), allow_stretch=True,
                            keep_ratio=True, pos_hint={"x": 0, "y": 0})
            self.icon_holder.add_widget(img)
        else:
            self._icon_color.rgba = COL_ACCENT
            lbl = Label(text="EQ", font_size="15sp", bold=True, color=COL_ACCENT_TEXT,
                       size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
            self.icon_holder.add_widget(lbl)

    def _build_search(self):
        wrap = BoxLayout(size_hint_y=None, height=dp(52), padding=(dp(12), dp(6)), spacing=dp(6))
        rounded_bg(wrap, COL_BG, radius=0)
        self.search_input = TextInput(hint_text="Rechercher equipement, reference, code magasin",
                                      multiline=False, size_hint_y=None, height=dp(44),
                                      background_color=COL_CARD_2, foreground_color=COL_TEXT,
                                      hint_text_color=COL_TEXT_DIM, cursor_color=COL_ACCENT,
                                      padding=[dp(10)] * 4)
        self.search_input.bind(text=self._on_search)
        self.btn_clear_search = Button(text="X", size_hint_x=None, width=dp(0), opacity=0,
                                       background_color=COL_CARD_2, color=COL_TEXT_DIM)
        self.btn_clear_search.bind(on_release=lambda *a: setattr(self.search_input, "text", ""))
        wrap.add_widget(self.search_input)
        wrap.add_widget(self.btn_clear_search)
        self.root_layout.add_widget(wrap)

    def _build_footer(self):
        footer = BoxLayout(size_hint_y=None, height=dp(50), padding=(dp(10), dp(4)), spacing=dp(8))
        b_csv = Button(text="Export CSV", background_color=COL_CARD_2, color=COL_TEXT)
        b_pdf = Button(text="Export PDF", background_color=COL_CARD_2, color=COL_TEXT)
        b_csv.bind(on_release=lambda *a: self.export_csv())
        b_pdf.bind(on_release=lambda *a: self.export_pdf())
        footer.add_widget(b_csv)
        footer.add_widget(b_pdf)
        self.root_layout.add_widget(footer)

        credit = Label(text="Realise par Hichri Abdelhalim", font_size="15sp",
                      color=COL_TEXT_DIM, size_hint_y=None, height=dp(30))
        self.root_layout.add_widget(credit)

    def _on_search(self, inst, val):
        self.search_text = val.strip()
        if self.search_text:
            self.btn_clear_search.width = dp(40)
            self.btn_clear_search.opacity = 1
        else:
            self.btn_clear_search.width = 0
            self.btn_clear_search.opacity = 0
        self.refresh()

    # ------------------------------------------------------------------
    def refresh(self):
        self.liste.clear_widgets()
        equipements = list_equipements()

        if self.search_text:
            self.expanded |= equipement_ids_matching(self.search_text)

        for eq in equipements:
            nom_ok = self.search_text.lower() in (eq["nom"] or "").lower()
            if self.search_text and not nom_ok:
                pieces = list_pieces(eq["id"], self.search_text)
                if not pieces:
                    continue
            else:
                pieces = list_pieces(eq["id"])
            self.liste.add_widget(self._equipement_card(eq, pieces))

        if not equipements:
            l = Label(text="Aucun equipement. Touchez « + Equipement » pour commencer.",
                      color=COL_TEXT_DIM, size_hint_y=None, height=dp(60))
            self.liste.add_widget(l)

    # ------------------------------------------------------------------
    def _equipement_card(self, eq, pieces):
        card = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(2), spacing=dp(2))
        rounded_bg(card, COL_CARD)

        header = BoxLayout(size_hint_y=None, height=dp(62), padding=(dp(14), dp(6)), spacing=dp(8))
        expanded = eq["id"] in self.expanded
        arrow = Label(text="v" if expanded else ">", size_hint_x=None, width=dp(20),
                     color=COL_TEXT, bold=True)
        info = BoxLayout(orientation="vertical")
        lbl_nom = Label(text=eq["nom"], bold=True, font_size="16sp", color=COL_TEXT,
                       halign="left", valign="middle")
        lbl_nom.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        info.add_widget(lbl_nom)
        if eq["categorie"]:
            lbl_cat = Label(text=eq["categorie"], font_size="12sp", color=COL_TEXT_DIM,
                           halign="left", valign="middle")
            lbl_cat.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
            info.add_widget(lbl_cat)
        badge = Label(text=str(len(pieces)), size_hint=(None, None), size=(dp(30), dp(30)),
                     color=COL_TEXT, bold=True)
        rounded_bg(badge, COL_BADGE_COUNT_BG, radius=dp(8))

        header.add_widget(arrow)
        header.add_widget(info)
        header.add_widget(badge)

        fl = FloatLayout(size_hint_y=None, height=dp(62))
        header.size_hint = (1, 1)
        header.pos_hint = {"x": 0, "y": 0}
        touch_overlay = Button(background_color=(0, 0, 0, 0), size_hint=(1, 1),
                               pos_hint={"x": 0, "y": 0})
        touch_overlay.bind(on_release=lambda *a: self.toggle(eq["id"]))
        fl.add_widget(header)
        fl.add_widget(touch_overlay)
        card.add_widget(fl)

        if expanded:
            sep = BoxLayout(size_hint_y=None, height=dp(1))
            rounded_bg(sep, COL_CARD_2, radius=0)
            card.add_widget(sep)
            for p in pieces:
                card.add_widget(self._piece_row(p))
            btn_add_piece = Button(text="+ Ajouter une piece", size_hint_y=None, height=dp(42),
                                   background_color=(0, 0, 0, 0), color=COL_ACCENT)
            btn_add_piece.bind(on_release=lambda *a, e=eq["id"]: self.popup_piece(e))
            card.add_widget(btn_add_piece)

            ligne_eq_actions = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(6),
                                         padding=(dp(10), 0))
            b_mod = Button(text="Modifier equipement", background_color=(0, 0, 0, 0),
                          color=COL_TEXT_DIM, font_size="12sp")
            b_del = Button(text="Supprimer equipement", background_color=(0, 0, 0, 0),
                          color=COL_RED, font_size="12sp")
            b_mod.bind(on_release=lambda *a, e=eq: self.popup_equipement(e))
            b_del.bind(on_release=lambda *a, e=eq["id"]: self.supprimer_equipement(e))
            ligne_eq_actions.add_widget(b_mod)
            ligne_eq_actions.add_widget(b_del)
            card.add_widget(ligne_eq_actions)

        hauteur = dp(62)
        if expanded:
            hauteur += dp(1) + len(pieces) * dp(78) + dp(42) + dp(38)
        card.height = hauteur
        return card

    def toggle(self, eq_id):
        if eq_id in self.expanded:
            self.expanded.discard(eq_id)
        else:
            self.expanded.add(eq_id)
        self.refresh()

    def _piece_row(self, p):
        row = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(78),
                        padding=(dp(14), dp(6)), spacing=dp(4))
        lbl_desig = Label(text=p["designation"], bold=True, color=COL_TEXT, font_size="14sp",
                          size_hint_y=None, height=dp(22), halign="left", valign="middle")
        lbl_desig.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        row.add_widget(lbl_desig)

        ligne_badges = BoxLayout(size_hint_y=None, height=dp(26), spacing=dp(8))
        if p["reference_piece"]:
            ligne_badges.add_widget(Label(text=f"# {p['reference_piece']}", font_size="11sp",
                                          color=COL_TEXT_DIM))
        if p["code_magasin"]:
            ligne_badges.add_widget(Label(text=f"Code: {p['code_magasin']}", font_size="11sp",
                                          color=COL_TEXT_DIM))
        ligne_badges.add_widget(BoxLayout())
        row.add_widget(ligne_badges)

        actions = BoxLayout(size_hint_y=None, height=dp(26), spacing=dp(16))
        b_mod = Button(text="Modifier", background_color=(0, 0, 0, 0), color=COL_TEXT_DIM,
                      font_size="12sp")
        b_del = Button(text="Supprimer", background_color=(0, 0, 0, 0), color=COL_RED,
                      font_size="12sp")
        b_mod.bind(on_release=lambda *a, eid=p["equipement_id"]: self.popup_piece(eid, p))
        b_del.bind(on_release=lambda *a, pid=p["id"]: self.supprimer_piece(pid))
        actions.add_widget(b_mod)
        actions.add_widget(b_del)
        row.add_widget(actions)

        wrap = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(78))
        wrap.add_widget(row)
        return wrap

    # ------------------------------------------------------------------
    # Popup Équipement (avec ScrollView + validation visuelle)
    # ------------------------------------------------------------------
    def popup_equipement(self, eq=None):
        popup, box = popup_scroll_form("Modifier l'equipement" if eq else "Nouvel equipement",
                                       height_hint=0.5)

        f_nom = ValidatedField("Nom de l'equipement *", text=eq["nom"] if eq else "")
        box.add_widget(f_nom)
        f_cat = ValidatedField("Categorie", text=eq["categorie"] if eq and eq["categorie"] else "",
                               hint="ex: Conditionnement, Process, Emballage...")
        box.add_widget(f_cat)

        def save(*a):
            nom = f_nom.text
            ok = True
            if not nom:
                f_nom.set_error("Le nom de l'equipement est obligatoire")
                ok = False
            if not ok:
                return
            save_equipement(nom, f_cat.text, eq["id"] if eq else None)
            popup.dismiss()
            toast("Equipement enregistre")
            self.refresh()

        btns = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        btns.add_widget(Button(text="Annuler", background_color=COL_CARD_2, color=COL_TEXT,
                               on_release=popup.dismiss))
        btns.add_widget(Button(text="Enregistrer", background_color=COL_ACCENT,
                               color=COL_ACCENT_TEXT, bold=True, on_release=save))
        box.add_widget(btns)
        popup.open()

    def supprimer_equipement(self, eq_id):
        def do_delete():
            delete_equipement(eq_id)
            self.expanded.discard(eq_id)
            toast("Equipement supprime")
            self.refresh()
        confirm_popup("Supprimer cet equipement et toutes ses references ?", do_delete)

    # ------------------------------------------------------------------
    # Popup Pièce (avec ScrollView + validation visuelle)
    # ------------------------------------------------------------------
    def popup_piece(self, equipement_id, p=None):
        popup, box = popup_scroll_form("Modifier la piece" if p else "Nouvelle piece",
                                       height_hint=0.65)

        f_nom = ValidatedField("Nom piece *", text=p["designation"] if p else "")
        box.add_widget(f_nom)
        f_ref = ValidatedField("Reference piece", text=p["reference_piece"] if p and p["reference_piece"] else "",
                               hint="ex: RUL-6205")
        box.add_widget(f_ref)
        f_code = ValidatedField("Code magasin *", text=p["code_magasin"] if p and p["code_magasin"] else "",
                                hint="ex: 90104-10000")
        box.add_widget(f_code)

        def save(*a):
            nom = f_nom.text
            code_mag = f_code.text
            if not nom:
                f_nom.set_error("Le nom de la piece est obligatoire")
                return
            save_piece(equipement_id, nom, f_ref.text, code_mag, p["id"] if p else None)
            popup.dismiss()
            toast("Piece enregistree")
            self.refresh()

        btns = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        btns.add_widget(Button(text="Annuler", background_color=COL_CARD_2, color=COL_TEXT,
                               on_release=popup.dismiss))
        btns.add_widget(Button(text="Enregistrer", background_color=COL_ACCENT,
                               color=COL_ACCENT_TEXT, bold=True, on_release=save))
        box.add_widget(btns)
        popup.open()

    def supprimer_piece(self, piece_id):
        def do_delete():
            delete_piece(piece_id)
            toast("Piece supprimee")
            self.refresh()
        confirm_popup("Supprimer cette piece ?", do_delete)

    # ------------------------------------------------------------------
    # Popup Configuration (nom entreprise + logo)
    # ------------------------------------------------------------------
    def popup_configuration(self):
        cfg = get_config()
        popup, box = popup_scroll_form("Configuration", height_hint=0.8)

        f_nom = ValidatedField("Nom de l'entreprise",
                               text=cfg["nom_entreprise"] if cfg and cfg["nom_entreprise"] else "",
                               hint="ex: Delice")
        box.add_widget(f_nom)

        box.add_widget(field_label("Logo (utilise dans les PDF)"))

        logo_preview_box = BoxLayout(size_hint_y=None, height=dp(110), padding=dp(6))
        rounded_bg(logo_preview_box, COL_CARD_2)
        box.add_widget(logo_preview_box)

        # État temporaire du logo pendant l'édition (validé seulement au Save)
        state = {"logo_path": cfg["logo_path"] if cfg and cfg["logo_path"] else ""}

        def refresh_preview():
            logo_preview_box.clear_widgets()
            path = state["logo_path"]
            if path and os.path.isfile(path):
                img = KivyImage(source=path, size_hint=(None, None), size=(dp(96), dp(96)))
                logo_preview_box.add_widget(img)
            else:
                logo_preview_box.add_widget(Label(text="Aucun logo selectionne",
                                                   color=COL_TEXT_DIM, font_size="12sp"))

        refresh_preview()

        def choisir_logo(*a):
            def on_selected(path):
                state["logo_path"] = path
                refresh_preview()
            self.choisir_logo_natif(on_selected)

        def supprimer_logo(*a):
            state["logo_path"] = ""
            refresh_preview()

        btns_logo = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        btns_logo.add_widget(Button(text="Choisir un logo", background_color=COL_ACCENT,
                                    color=COL_ACCENT_TEXT, bold=True, on_release=choisir_logo))
        btns_logo.add_widget(Button(text="Retirer le logo", background_color=COL_CARD_2,
                                    color=COL_RED, on_release=supprimer_logo))
        box.add_widget(btns_logo)

        def save(*a):
            save_config(f_nom.text, state["logo_path"])
            popup.dismiss()
            toast("Configuration enregistree")
            self._refresh_header_branding()

        btns = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        btns.add_widget(Button(text="Annuler", background_color=COL_CARD_2, color=COL_TEXT,
                               on_release=popup.dismiss))
        btns.add_widget(Button(text="Enregistrer", background_color=COL_ACCENT,
                               color=COL_ACCENT_TEXT, bold=True, on_release=save))
        box.add_widget(btns)
        popup.open()

    def choisir_logo_natif(self, on_selected):
        """Ouvre le selecteur d'images natif d'Android quand c'est possible.

        Le FileChooserIconView de Kivy lit le systeme de fichiers directement,
        or sur Android moderne (scoped storage) les dossiers appartenant a
        d'autres apps (Messenger, WhatsApp, Galerie...) sont invisibles de
        cette maniere meme avec la permission READ_MEDIA_IMAGES accordee.
        Le selecteur natif (via plyer) passe par le systeme Android et voit
        donc bien toutes les images, peu importe l'app qui les a creees.

        Sur Pydroid/PC (pas de selecteur natif disponible), on retombe sur
        l'ancien FileChooserIconView integre.
        """
        if platform == "android":
            try:
                from plyer import filechooser

                def _on_selection(selection):
                    if selection:
                        Clock.schedule_once(lambda dt: on_selected(selection[0]))
                    else:
                        Clock.schedule_once(lambda dt: toast("Aucune image selectionnee"))

                filechooser.open_file(
                    on_selection=_on_selection,
                    filters=[["Images", "*.png", "*.jpg", "*.jpeg"]],
                )
                return
            except Exception as e:
                toast(f"Selecteur natif indisponible ({e}), utilisation du mode alternatif")

        self._popup_file_chooser(on_selected)

    def _popup_file_chooser(self, on_selected):
        """Popup avec navigateur de fichiers pour choisir une image (logo)."""
        box = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        rounded_bg(box, COL_CARD)

        chooser = FileChooserIconView(path=get_pictures_dir(),
                                      filters=["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"])
        box.add_widget(chooser)

        popup = Popup(title="Choisir un logo", content=box, size_hint=(0.95, 0.9),
                     title_color=COL_TEXT, separator_color=COL_ACCENT,
                     background_color=(0, 0, 0, 0.6))

        def choose(*a):
            if chooser.selection:
                on_selected(chooser.selection[0])
                popup.dismiss()
            else:
                toast("Aucun fichier selectionne")

        btns = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        btns.add_widget(Button(text="Annuler", background_color=COL_CARD_2, color=COL_TEXT,
                               on_release=popup.dismiss))
        btns.add_widget(Button(text="Choisir", background_color=COL_ACCENT,
                               color=COL_ACCENT_TEXT, bold=True, on_release=choose))
        box.add_widget(btns)
        popup.open()

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def _show_export_popup(self, path, note=""):
        """Popup persistante (contrairement au toast) montrant le chemin
        complet du fichier exporte, pour qu'on puisse le retrouver."""
        box = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
        rounded_bg(box, COL_CARD)
        texte = f"Fichier enregistre :\n\n{path}"
        if note:
            texte += f"\n\n{note}"
        lbl = Label(text=texte, color=COL_TEXT, halign="left", valign="top")
        lbl.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        box.add_widget(lbl)
        popup = Popup(title="Export termine", content=box, size_hint=(0.9, 0.5),
                      title_color=COL_TEXT, separator_color=COL_ACCENT,
                      background_color=(0, 0, 0, 0.6))
        btn = Button(text="OK", size_hint_y=None, height=dp(46),
                    background_color=COL_ACCENT, color=COL_ACCENT_TEXT, bold=True,
                    on_release=popup.dismiss)
        box.add_widget(btn)
        popup.open()

    def _export_with_fallback(self, filename, writer_func):
        """Essaie d'ecrire dans le dossier public (Download...). Si ca echoue
        (ex: restriction scoped storage sur Android 10+), bascule
        automatiquement sur le dossier prive de l'app, qui est toujours
        accessible. Affiche ensuite une popup avec le chemin complet final,
        pour qu'on sache toujours exactement ou le fichier a ete enregistre."""
        primary_path = os.path.join(get_export_dir(), filename)
        try:
            writer_func(primary_path)
            self._show_export_popup(primary_path)
            return
        except Exception:
            pass

        fallback_path = os.path.join(get_db_dir(), filename)
        try:
            writer_func(fallback_path)
            self._show_export_popup(
                fallback_path,
                note="(dossier public indisponible sur cet appareil -> "
                     "enregistre dans le dossier interne de l'app)")
        except Exception as e:
            toast(f"Erreur export: {e}")

    def export_csv(self):
        rows = list_all_pieces_with_equipement()
        filename = f"pieces_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

        def write_csv(path):
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Equipement", "Categorie eq.", "Nom piece", "Reference piece",
                                 "Code magasin", "MAJ"])
                for r in rows:
                    writer.writerow([r["equipement"], r["categorie"], r["designation"],
                                     r["reference_piece"], r["code_magasin"], r["date_maj"]])

        self._export_with_fallback(filename, write_csv)

    def export_pdf(self):
        try:
            from fpdf import FPDF
        except ImportError:
            toast("Module fpdf2 manquant (pip install fpdf2)")
            return
        rows = list_all_pieces_with_equipement()
        cfg = get_config()
        nom_entreprise = (cfg["nom_entreprise"] or "").strip() if cfg else ""
        logo_path = (cfg["logo_path"] or "").strip() if cfg else ""
        has_logo = bool(logo_path) and os.path.isfile(logo_path)

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()

        # --- En-tête : logo à gauche + nom entreprise / titre à droite ---
        top_y = 10
        text_x = 10
        if has_logo:
            try:
                pdf.image(logo_path, x=10, y=top_y, w=22)
                text_x = 36
            except Exception:
                has_logo = False
                text_x = 10

        if nom_entreprise:
            pdf.set_xy(text_x, top_y)
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 7, ascii_safe(nom_entreprise), ln=1, align="L")
            pdf.set_x(text_x)
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(0, 5, "Pieces et consommables par equipement", ln=1, align="L")
        else:
            pdf.set_xy(text_x, top_y + (4 if has_logo else 0))
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 8, "Pieces et consommables par equipement", ln=1, align="L")

        pdf.set_x(text_x)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(0, 5, datetime.now().strftime("Genere le %d/%m/%Y a %H:%M"), ln=1, align="L")

        # Descend sous le logo si celui-ci est plus grand que le bloc de texte
        pdf.set_y(max(pdf.get_y(), top_y + 22) + 4)

        headers = ["Equipement", "Nom piece", "Reference piece", "Code magasin"]
        widths = [45, 65, 40, 40]

        def draw_row(cells, bold=False):
            pdf.set_font("Helvetica", "B" if bold else "", 8)
            x0, y0 = pdf.get_x(), pdf.get_y()
            max_h = 6
            x = x0
            for cell, w in zip(cells, widths):
                pdf.rect(x, y0, w, max_h)
                pdf.set_xy(x, y0)
                pdf.multi_cell(w, max_h, ascii_safe(cell), border=0, align="L")
                x += w
            pdf.set_xy(x0, y0 + max_h)

        draw_row(headers, bold=True)
        for r in rows:
            if pdf.get_y() > 270:
                pdf.add_page()
                draw_row(headers, bold=True)
            draw_row([r["equipement"], r["designation"], r["reference_piece"], r["code_magasin"]])

        filename = f"pieces_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        self._export_with_fallback(filename, pdf.output)


if __name__ == "__main__":
    PiecesApp().run()
