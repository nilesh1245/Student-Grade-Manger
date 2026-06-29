import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QScrollArea, QMessageBox,
    QStackedWidget, QGridLayout, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon


DATABASE = "student.json"

# ─── Load / Save ──────────────────────────────────────────────────────────────
def load_students():
    if os.path.exists(DATABASE):
        with open(DATABASE, "r") as f:
            return json.load(f)
    return []

def save_students(students):
    with open(DATABASE, "w") as f:
        json.dump(students, f, indent=4)


# ─── Colours ──────────────────────────────────────────────────────────────────
C = {
    "bg":        "#0f1117",
    "surface":   "#1a1d27",
    "surface2":  "#21253a",
    "border":    "#2e3250",
    "accent":    "#4f8ef7",
    "accent2":   "#1e3a6e",
    "success":   "#22c55e",
    "success2":  "#14532d",
    "warning":   "#f59e0b",
    "warning2":  "#451a03",
    "danger":    "#ef4444",
    "danger2":   "#450a0a",
    "text":      "#e2e8f0",
    "muted":     "#64748b",
    "white":     "#ffffff",
}

def grade_color(avg):
    if avg >= 75: return C["success"], C["success2"]
    if avg >= 60: return C["accent"],  C["accent2"]
    if avg >= 40: return C["warning"], C["warning2"]
    return C["danger"], C["danger2"]


# ─── Reusable widgets ─────────────────────────────────────────────────────────
class Card(QFrame):
    def __init__(self, parent=None, bg=None):
        super().__init__(parent)
        bg = bg or C["surface"]
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 1px solid {C['border']};
                border-radius: 12px;
            }}
        """)


class StyledInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {C['surface2']};
                border: 1px solid {C['border']};
                border-radius: 8px;
                padding: 10px 14px;
                color: {C['text']};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {C['accent']};
            }}
        """)
        self.setFont(QFont("Segoe UI", 10))


class PrimaryButton(QPushButton):
    def __init__(self, text, color=None, parent=None):
        super().__init__(text, parent)
        bg = color or C["accent"]
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                border: none;
                border-radius: 8px;
                padding: 10px 22px;
                color: {C['white']};
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: #3a7ef5; }}
            QPushButton:pressed {{ background: #2563eb; }}
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))


class GhostButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {C['border']};
                border-radius: 8px;
                padding: 10px 22px;
                color: {C['muted']};
                font-size: 13px;
            }}
            QPushButton:hover {{
                border-color: {C['accent']};
                color: {C['text']};
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 10))


class TabButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self._update_style()

    def setChecked(self, val):
        super().setChecked(val)
        self._update_style()

    def _update_style(self):
        if self.isChecked():
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {C['accent']};
                    border: none;
                    border-radius: 8px;
                    padding: 9px 20px;
                    color: white;
                    font-size: 13px;
                    font-weight: 700;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                    padding: 9px 20px;
                    color: {C['muted']};
                    font-size: 13px;
                }}
                QPushButton:hover {{ color: {C['text']}; background: {C['surface2']}; }}
            """)


class StatCard(Card):
    def __init__(self, label, value_id, color, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {C['muted']}; font-size: 12px; background: transparent; border: none;")
        lbl.setFont(QFont("Segoe UI", 9))

        self.val = QLabel("—")
        self.val.setObjectName(value_id)
        self.val.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: 700; background: transparent; border: none;")
        self.val.setFont(QFont("Segoe UI", 18, QFont.Bold))

        layout.addWidget(lbl)
        layout.addWidget(self.val)


class GradeBadge(QLabel):
    def __init__(self, avg_val, parent=None):
        super().__init__(parent)
        g = "A" if avg_val >= 75 else "B" if avg_val >= 60 else "C" if avg_val >= 40 else "F"
        fg, bg = grade_color(avg_val)
        self.setText(f"  {g} · {avg_val}%  ")
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border: 1px solid {fg};
                border-radius: 12px;
                padding: 3px 6px;
                font-size: 12px;
                font-weight: 700;
            }}
        """)
        self.setFont(QFont("Segoe UI", 9, QFont.Bold))


class AvatarLabel(QLabel):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        initials = "".join(w[0] for w in name.strip().split() if w)[:2].upper()
        self.setText(initials)
        self.setFixedSize(40, 40)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background: {C['accent2']};
                color: {C['accent']};
                border-radius: 20px;
                font-size: 14px;
                font-weight: 700;
                border: none;
            }}
        """)
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))


# ─── Student row widget ───────────────────────────────────────────────────────
class StudentRow(QFrame):
    deleted = pyqtSignal(str)
    edit_requested = pyqtSignal(str)

    def __init__(self, student, rank=None, parent=None):
        super().__init__(parent)
        self.student = student
        self.setStyleSheet(f"""
            QFrame {{
                background: {C['surface']};
                border: 1px solid {C['border']};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border-color: {C['accent']};
            }}
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(12)

        if rank is not None:
            rank_lbl = QLabel(f"#{rank}")
            rank_lbl.setStyleSheet(f"color: {C['muted']}; font-size: 13px; font-weight: 700; background: transparent; border: none;")
            rank_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
            rank_lbl.setFixedWidth(30)
            row.addWidget(rank_lbl)

        row.addWidget(AvatarLabel(student["name"]))

        info = QVBoxLayout()
        info.setSpacing(3)
        name_lbl = QLabel(student["name"])
        name_lbl.setStyleSheet(f"color: {C['text']}; font-size: 14px; font-weight: 700; background: transparent; border: none;")
        name_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))

        marks_lbl = QLabel(
            f"Maths: {student['Maths']}  ·  Physics: {student['Physics']}  ·  Chemistry: {student['chemistry']}"
        )
        marks_lbl.setStyleSheet(f"color: {C['muted']}; font-size: 12px; background: transparent; border: none;")
        marks_lbl.setFont(QFont("Segoe UI", 9))
        info.addWidget(name_lbl)
        info.addWidget(marks_lbl)
        row.addLayout(info, 1)

        avg_val = (student["Maths"] + student["Physics"] + student["chemistry"]) // 3
        row.addWidget(GradeBadge(avg_val))

        if rank is None:
            edit_btn = QPushButton("✏")
            edit_btn.setFixedSize(32, 32)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C['surface2']};
                    border: 1px solid {C['border']};
                    border-radius: 8px;
                    color: {C['muted']};
                    font-size: 14px;
                }}
                QPushButton:hover {{ border-color: {C['accent']}; color: {C['accent']}; }}
            """)
            edit_btn.clicked.connect(lambda: self.edit_requested.emit(student["name"]))

            del_btn = QPushButton("🗑")
            del_btn.setFixedSize(32, 32)
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C['surface2']};
                    border: 1px solid {C['border']};
                    border-radius: 8px;
                    color: {C['muted']};
                    font-size: 14px;
                }}
                QPushButton:hover {{ border-color: {C['danger']}; color: {C['danger']}; background: {C['danger2']}; }}
            """)
            del_btn.clicked.connect(lambda: self.deleted.emit(student["name"]))
            row.addWidget(edit_btn)
            row.addWidget(del_btn)


# ─── Panels ───────────────────────────────────────────────────────────────────
class StudentsPanel(QWidget):
    def __init__(self, app_ref, parent=None):
        super().__init__(parent)
        self.app = app_ref
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.search = StyledInput("🔍  Search students…")
        self.search.textChanged.connect(self.refresh)
        layout.addWidget(self.search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 6px; background: transparent; } QScrollBar::handle:vertical { background: #2e3250; border-radius: 3px; }")
        self.inner = QWidget()
        self.inner.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.inner)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()
        scroll.setWidget(self.inner)
        layout.addWidget(scroll)

    def refresh(self):
        q = self.search.text().lower()
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtered = [s for s in self.app.students if q in s["name"].lower()]

        if not filtered:
            empty = QLabel("No students found." if self.app.students else "No students yet — add one!")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"color: {C['muted']}; font-size: 14px; padding: 40px;")
            self.list_layout.insertWidget(0, empty)
            return

        for s in filtered:
            row = StudentRow(s)
            row.deleted.connect(self.app.delete_student)
            row.edit_requested.connect(self.app.open_edit)
            self.list_layout.insertWidget(self.list_layout.count() - 1, row)


class AddEditPanel(QWidget):
    def __init__(self, app_ref, parent=None):
        super().__init__(parent)
        self.app = app_ref
        self.edit_name = None  # None = add mode, str = edit mode
        self.setStyleSheet("background: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.title_lbl = QLabel("Add a new student")
        self.title_lbl.setStyleSheet(f"color: {C['text']}; font-size: 18px; font-weight: 700; background: transparent; border: none;")
        self.title_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout.addWidget(self.title_lbl)

        self.name_input = StyledInput("Full name  e.g. Priya Sharma")
        layout.addWidget(QLabel("Name", styleSheet=f"color:{C['muted']};font-size:12px;font-weight:600;background:transparent;border:none;"))
        layout.addWidget(self.name_input)

        grid = QGridLayout()
        grid.setSpacing(12)
        self.maths_input   = StyledInput("0 – 100")
        self.physics_input = StyledInput("0 – 100")
        self.chem_input    = StyledInput("0 – 100")
        for col, (lbl, inp) in enumerate([("Maths", self.maths_input), ("Physics", self.physics_input), ("Chemistry", self.chem_input)]):
            l = QLabel(lbl)
            l.setStyleSheet(f"color:{C['muted']};font-size:12px;font-weight:600;background:transparent;border:none;")
            l.setFont(QFont("Segoe UI", 9, QFont.Bold))
            grid.addWidget(l, 0, col)
            grid.addWidget(inp, 1, col)
        layout.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.clear_btn = GhostButton("Clear")
        self.clear_btn.clicked.connect(self.clear)
        self.submit_btn = PrimaryButton("Add student")
        self.submit_btn.clicked.connect(self.submit)
        btn_row.addWidget(self.clear_btn)
        btn_row.addWidget(self.submit_btn)
        layout.addLayout(btn_row)

        outer.addWidget(card)
        outer.addStretch()

    def set_edit_mode(self, student):
        self.edit_name = student["name"]
        self.title_lbl.setText(f"Edit marks — {student['name']}")
        self.name_input.setText(student["name"])
        self.name_input.setReadOnly(True)
        self.name_input.setStyleSheet(self.name_input.styleSheet() + f"color:{C['muted']};")
        self.maths_input.setText(str(student["Maths"]))
        self.physics_input.setText(str(student["Physics"]))
        self.chem_input.setText(str(student["chemistry"]))
        self.submit_btn.setText("Save changes")

    def set_add_mode(self):
        self.edit_name = None
        self.title_lbl.setText("Add a new student")
        self.name_input.setReadOnly(False)
        self.name_input.setStyleSheet(StyledInput().styleSheet())
        self.submit_btn.setText("Add student")
        self.clear()

    def clear(self):
        for inp in [self.name_input, self.maths_input, self.physics_input, self.chem_input]:
            inp.clear()

    def submit(self):
        name   = self.name_input.text().strip()
        maths_t  = self.maths_input.text().strip()
        phys_t   = self.physics_input.text().strip()
        chem_t   = self.chem_input.text().strip()

        if not name:
            self.app.alert("Enter a student name.", "error"); return
        try:
            m, p, c = int(maths_t), int(phys_t), int(chem_t)
        except ValueError:
            self.app.alert("Enter valid numeric marks.", "error"); return
        if not all(0 <= v <= 100 for v in [m, p, c]):
            self.app.alert("Marks must be between 0 and 100.", "error"); return

        if self.edit_name:
            self.app.update_student(self.edit_name, m, p, c)
        else:
            self.app.add_student(name, m, p, c)


class LeaderboardPanel(QWidget):
    def __init__(self, app_ref, parent=None):
        super().__init__(parent)
        self.app = app_ref
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.top_card = Card(bg=C["success2"])
        self.top_card.setStyleSheet(f"QFrame {{ background: {C['success2']}; border: 1px solid {C['success']}; border-radius: 12px; }}")
        top_row = QHBoxLayout(self.top_card)
        top_row.setContentsMargins(16, 14, 16, 14)
        self.trophy = QLabel("🏆")
        self.trophy.setFont(QFont("Segoe UI", 22))
        self.trophy.setStyleSheet("background: transparent; border: none;")
        self.top_name = QLabel("—")
        self.top_name.setStyleSheet(f"color: {C['success']}; font-size: 16px; font-weight: 700; background: transparent; border: none;")
        self.top_name.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.top_avg = QLabel("")
        self.top_avg.setStyleSheet(f"color: #86efac; font-size: 13px; background: transparent; border: none;")
        info = QVBoxLayout(); info.addWidget(self.top_name); info.addWidget(self.top_avg)
        top_row.addWidget(self.trophy); top_row.addLayout(info, 1)
        layout.addWidget(self.top_card)

        sec = QLabel("FULL RANKINGS")
        sec.setStyleSheet(f"color: {C['muted']}; font-size: 11px; font-weight: 700; letter-spacing: 1px; background: transparent;")
        sec.setFont(QFont("Segoe UI", 8, QFont.Bold))
        layout.addWidget(sec)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 6px; } QScrollBar::handle:vertical { background: #2e3250; border-radius: 3px; }")
        self.inner = QWidget(); self.inner.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.inner)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()
        scroll.setWidget(self.inner)
        layout.addWidget(scroll)

    def refresh(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not self.app.students:
            self.top_name.setText("No students yet")
            self.top_avg.setText("")
            return

        sorted_s = sorted(self.app.students, key=lambda s: -(s["Maths"] + s["Physics"] + s["chemistry"]))
        top = sorted_s[0]
        top_avg = (top["Maths"] + top["Physics"] + top["chemistry"]) // 3
        self.top_name.setText(f"🥇  {top['name']}")
        self.top_avg.setText(f"Average: {top_avg}%  ·  Grade {'A' if top_avg>=75 else 'B' if top_avg>=60 else 'C' if top_avg>=40 else 'F'}")

        for i, s in enumerate(sorted_s):
            row = StudentRow(s, rank=i + 1)
            self.list_layout.insertWidget(self.list_layout.count() - 1, row)


# ─── Toast notification ───────────────────────────────────────────────────────
class Toast(QLabel):
    def __init__(self, msg, kind, parent):
        super().__init__(f"  {'✓' if kind=='success' else '✕' if kind=='error' else 'ℹ'}  {msg}  ", parent)
        colors = {"success": (C["success"], C["success2"]), "error": (C["danger"], C["danger2"])}
        fg, bg = colors.get(kind, (C["text"], C["surface2"]))
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border: 1px solid {fg};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }}
        """)
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.adjustSize()
        self.setParent(parent)
        self._place()
        self.show()
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(2500, self.deleteLater)

    def _place(self):
        p = self.parent()
        self.move(p.width() // 2 - self.width() // 2, 20)


# ─── Main window ──────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.students = load_students()
        self.setWindowTitle("Student Grade Manager")
        self.setMinimumSize(780, 620)
        self.resize(860, 680)
        self._build_ui()
        self._apply_palette()
        self.refresh_all()

    def _apply_palette(self):
        self.setStyleSheet(f"QMainWindow {{ background: {C['bg']}; }} QWidget {{ background: {C['bg']}; color: {C['text']}; }}")

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(16)

        # Header
        header = QHBoxLayout()
        icon_lbl = QLabel("🎓")
        icon_lbl.setFont(QFont("Segoe UI", 22))
        icon_lbl.setFixedSize(48, 48)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"background: {C['accent2']}; border-radius: 12px; border: none;")
        h_texts = QVBoxLayout(); h_texts.setSpacing(2)
        h1 = QLabel("Student Grade Manager")
        h1.setFont(QFont("Segoe UI", 15, QFont.Bold))
        h1.setStyleSheet(f"color: {C['text']}; background: transparent;")
        h2 = QLabel("Track maths, physics & chemistry marks")
        h2.setFont(QFont("Segoe UI", 10))
        h2.setStyleSheet(f"color: {C['muted']}; background: transparent;")
        h_texts.addWidget(h1); h_texts.addWidget(h2)
        header.addWidget(icon_lbl); header.addLayout(h_texts, 1)
        main.addLayout(header)

        # Stats
        stats_row = QHBoxLayout(); stats_row.setSpacing(10)
        self.stat_total = StatCard("Total students",  "s1", C["accent"])
        self.stat_avg   = StatCard("Class average",   "s2", C["success"])
        self.stat_high  = StatCard("Highest mark",    "s3", C["text"])
        self.stat_pass  = StatCard("Passing (≥40)",   "s4", C["warning"])
        for c in [self.stat_total, self.stat_avg, self.stat_high, self.stat_pass]:
            stats_row.addWidget(c)
        main.addLayout(stats_row)

        # Tab bar
        tab_bar = QHBoxLayout(); tab_bar.setSpacing(4)
        self.tab_students  = TabButton("👥  Students")
        self.tab_add       = TabButton("➕  Add / Edit")
        self.tab_leaders   = TabButton("🏆  Leaderboard")
        for btn in [self.tab_students, self.tab_add, self.tab_leaders]:
            tab_bar.addWidget(btn)
        tab_bar.addStretch()
        self.tab_students.clicked.connect(lambda: self._switch_tab(0))
        self.tab_add.clicked.connect(lambda: self._switch_tab(1))
        self.tab_leaders.clicked.connect(lambda: self._switch_tab(2))
        main.addLayout(tab_bar)

        # Panels
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        self.panel_students  = StudentsPanel(self)
        self.panel_add       = AddEditPanel(self)
        self.panel_leaders   = LeaderboardPanel(self)
        for p in [self.panel_students, self.panel_add, self.panel_leaders]:
            self.stack.addWidget(p)
        main.addWidget(self.stack, 1)

        self._switch_tab(0)

    def _switch_tab(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate([self.tab_students, self.tab_add, self.tab_leaders]):
            btn.setChecked(i == idx)
        if idx == 2:
            self.panel_leaders.refresh()

    # ── Actions ───────────────────────────────────────────────────────────────
    def add_student(self, name, maths, physics, chem):
        if any(s["name"].lower() == name.lower() for s in self.students):
            self.alert("Student already exists.", "error"); return
        self.students.append({"name": name, "Maths": maths, "Physics": physics, "chemistry": chem})
        save_students(self.students)
        self.refresh_all()
        self.panel_add.clear()
        self._switch_tab(0)
        self.alert(f"{name} added.", "success")

    def update_student(self, name, maths, physics, chem):
        for s in self.students:
            if s["name"] == name:
                s["Maths"] = maths; s["Physics"] = physics; s["chemistry"] = chem
                break
        save_students(self.students)
        self.refresh_all()
        self.panel_add.set_add_mode()
        self._switch_tab(0)
        self.alert("Marks updated.", "success")

    def delete_student(self, name):
        reply = QMessageBox.question(self, "Delete student", f"Remove {name}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.students = [s for s in self.students if s["name"] != name]
            save_students(self.students)
            self.refresh_all()
            self.alert(f"{name} removed.", "")

    def open_edit(self, name):
        s = next((x for x in self.students if x["name"] == name), None)
        if s:
            self.panel_add.set_edit_mode(s)
            self._switch_tab(1)

    def refresh_all(self):
        self.panel_students.refresh()
        # Stats
        n = len(self.students)
        self.stat_total.val.setText(str(n))
        if not n:
            self.stat_avg.val.setText("—")
            self.stat_high.val.setText("—")
            self.stat_pass.val.setText("—")
        else:
            avgs = [(s["Maths"] + s["Physics"] + s["chemistry"]) // 3 for s in self.students]
            self.stat_avg.val.setText(f"{sum(avgs)//n}%")
            highest = max(s["Maths"] for s in self.students + [{"Maths":0}])
            highest = max(max(s["Maths"], s["Physics"], s["chemistry"]) for s in self.students)
            self.stat_high.val.setText(str(highest))
            passing = sum(1 for a in avgs if a >= 40)
            self.stat_pass.val.setText(f"{passing}/{n}")

    def alert(self, msg, kind):
        Toast(msg, kind, self.centralWidget())


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())