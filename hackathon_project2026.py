"""
משחק ניחוש אותיות - עברית או אנגלית?
Letter Guessing Game - Hebrew or English?

דרישות: pip install arcade
"""

import arcade
import random

# ─── קבועים ───────────────────────────────────────────────
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE  = "עברית או אנגלית? | Hebrew or English?"

FONT_SIZE_HUGE   = 120
FONT_SIZE_LARGE  = 48
FONT_SIZE_MEDIUM = 32
FONT_SIZE_SMALL  = 22

TOTAL_ROUNDS = 10

# פלטות צבעים לכל מסך
PALETTES: list = [
    {"bg": (255, 230, 100), "accent": (220,  60,  60), "btn": (255, 120,  50)},
    {"bg": ( 80, 200, 180), "accent": (255, 255, 255), "btn": (255, 100, 150)},
    {"bg": (160,  80, 220), "accent": (255, 230,  80), "btn": ( 80, 200, 120)},
    {"bg": (255, 120, 100), "accent": (255, 255, 255), "btn": ( 80, 140, 255)},
    {"bg": ( 60, 180, 100), "accent": (255, 230,  80), "btn": (255, 100,  80)},
    {"bg": ( 40, 120, 200), "accent": (255, 240, 100), "btn": (255, 140,  60)},
]

# אותיות עבריות ואנגליות
HEBREW_LETTERS: tuple = (
    "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י",
    "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ", "ק", "ר",
    "ש", "ת", "ך", "ם", "ן", "ף", "ץ"
)
ENGLISH_LETTERS: tuple = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# מצבי משחק
STATE_INTRO   = "intro"
STATE_PLAYING = "playing"
STATE_FEEDBACK = "feedback"
STATE_RESULTS = "results"


# ─── מחלקת כפתור ──────────────────────────────────────────
class Button:
    """כפתור לחיצה פשוט."""

    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, color: tuple, text_color: tuple = (255, 255, 255)):
        self.x          = x
        self.y          = y
        self.width      = width
        self.height     = height
        self.text       = text
        self.color      = color
        self.text_color = text_color
        self.hovered    = False

    def draw(self) -> None:
        c = tuple(min(255, v + 30) for v in self.color) if self.hovered else self.color
        arcade.draw_lrbt_rectangle_filled(
            self.x - self.width // 2, self.x + self.width // 2,
            self.y - self.height // 2, self.y + self.height // 2,
            c
        )
        arcade.draw_lrbt_rectangle_outline(
            self.x - self.width // 2, self.x + self.width // 2,
            self.y - self.height // 2, self.y + self.height // 2,
            (255, 255, 255), 3
        )
        arcade.draw_text(
            self.text, self.x, self.y,
            self.text_color, FONT_SIZE_SMALL,
            anchor_x="center", anchor_y="center",
            bold=True
        )

    def is_clicked(self, mx: float, my: float) -> bool:
        return (abs(mx - self.x) <= self.width  // 2 and
                abs(my - self.y) <= self.height // 2)

    def update_hover(self, mx: float, my: float) -> None:
        self.hovered = self.is_clicked(mx, my)


# ─── מחלקת משחק בסיסית ────────────────────────────────────
class BaseGame(arcade.Window):
    """מחלקת בסיס – מגדירה מבנה משותף לכל מסכי המשחק."""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.bg_color: tuple = (255, 230, 100)

    def draw_background(self) -> None:
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, self.bg_color
        )

    def draw_centered_text(self, text: str, y: int,
                           color: tuple, size: int, bold: bool = False) -> None:
        arcade.draw_text(
            text, SCREEN_WIDTH // 2, y,
            color, size,
            anchor_x="center", anchor_y="center",
            bold=bold
        )


# ─── המשחק הראשי ──────────────────────────────────────────
class LetterGame(BaseGame):
    """המשחק המלא – ירושה מ-BaseGame."""

    def __init__(self):
        super().__init__()
        self.arcade = arcade          # שמירת מחלקת arcade.ARCADE
        self.state: str = STATE_INTRO

        # נתוני המשחק
        self.score:         int  = 0
        self.round_num:     int  = 0
        self.current_letter: str = ""
        self.is_hebrew:     bool = False
        self.feedback_msg:  str  = ""
        self.feedback_color: tuple = (255, 255, 255)
        self.correct:       bool = False

        # היסטוריה – list of dict
        self.history: list = []

        # פלטה נוכחית
        self.palette_index: int = 0
        self._apply_palette()

        # כפתורים – list of Button
        self.buttons: list = []
        self._build_buttons()

    # ── פלטות ──────────────────────────────────────────────
    def _apply_palette(self) -> None:
        p = PALETTES[self.palette_index % len(PALETTES)]
        self.bg_color    = p["bg"]
        self.accent_color = p["accent"]
        self.btn_color   = p["btn"]

    def _next_palette(self) -> None:
        self.palette_index += 1
        self._apply_palette()
        for btn in self.buttons:
            btn.color = self.btn_color

    # ── בניית כפתורים ──────────────────────────────────────
    def _build_buttons(self) -> None:
        self.buttons = [
            Button(250, 120, 200, 60, "עברית 🔡", self.btn_color),
            Button(550, 120, 200, 60, "English 🔤", self.btn_color),
        ]

    # ── בחירת אות חדשה ─────────────────────────────────────
    def _new_round(self) -> None:
        self.is_hebrew = random.choice([True, False])
        if self.is_hebrew:
            self.current_letter = random.choice(HEBREW_LETTERS)
        else:
            self.current_letter = random.choice(ENGLISH_LETTERS)
        self._next_palette()
        self.state = STATE_PLAYING

    # ─── ציור ──────────────────────────────────────────────
    def on_draw(self) -> None:
        self.clear()
        self.draw_background()

        if   self.state == STATE_INTRO:    self._draw_intro()
        elif self.state == STATE_PLAYING:  self._draw_playing()
        elif self.state == STATE_FEEDBACK: self._draw_feedback()
        elif self.state == STATE_RESULTS:  self._draw_results()

    def _draw_intro(self) -> None:
        self.draw_centered_text("🎮 ברוכים הבאים! 🎮", 480,
                                self.accent_color, FONT_SIZE_LARGE, bold=True)
        self.draw_centered_text("משחק ניחוש אותיות", 410,
                                self.accent_color, FONT_SIZE_MEDIUM, bold=True)

        lines: list = [
            "תופיע אות על המסך – עברית או אנגלית?",
            "לחץ על הכפתור המתאים וצבור נקודות!",
            "10 סיבובים בכל משחק.",
        ]
        for i, line in enumerate(lines):
            self.draw_centered_text(line, 310 - i * 50,
                                    (60, 40, 20), FONT_SIZE_SMALL)

        self.draw_centered_text("לחץ על המסך להתחלה! 👇",
                                170, self.accent_color, FONT_SIZE_MEDIUM, bold=True)

    def _draw_playing(self) -> None:
        # כותרת סיבוב וניקוד
        self.draw_centered_text(
            f"סיבוב {self.round_num + 1} / {TOTAL_ROUNDS}   |   ניקוד: {self.score}",
            560, self.accent_color, FONT_SIZE_SMALL, bold=True
        )
        # האות הגדולה
        self.draw_centered_text(self.current_letter, 340,
                                self.accent_color, FONT_SIZE_HUGE, bold=True)
        # שאלה
        self.draw_centered_text("האות היא באיזו שפה?",
                                210, self.accent_color, FONT_SIZE_MEDIUM)
        # כפתורים
        for btn in self.buttons:
            btn.draw()

    def _draw_feedback(self) -> None:
        emoji = "✅" if self.correct else "❌"
        self.draw_centered_text(f"{emoji} {self.feedback_msg} {emoji}",
                                340, self.feedback_color, FONT_SIZE_LARGE, bold=True)

        lang = "עברית" if self.is_hebrew else "אנגלית"
        self.draw_centered_text(f"האות '{self.current_letter}' היא {lang}",
                                260, self.accent_color, FONT_SIZE_SMALL)
        self.draw_centered_text("לחץ להמשך...",
                                160, self.accent_color, FONT_SIZE_SMALL)

    def _draw_results(self) -> None:
        self.draw_centered_text("🏆 סיום המשחק! 🏆",
                                500, self.accent_color, FONT_SIZE_LARGE, bold=True)
        self.draw_centered_text(
            f"ניחשת נכון {self.score} מתוך {TOTAL_ROUNDS}",
            400, self.accent_color, FONT_SIZE_MEDIUM, bold=True
        )

        # תוצאה לפי ביצוע
        if   self.score == TOTAL_ROUNDS: msg = "מושלם! גאון! 🌟"
        elif self.score >= 8:            msg = "מעולה! כמעט מושלם! 🎉"
        elif self.score >= 6:            msg = "טוב מאוד! 👍"
        elif self.score >= 4:            msg = "סביר, תנסה שוב! 💪"
        else:                            msg = "אולי בפעם הבאה... 🙈"

        self.draw_centered_text(msg, 320, self.accent_color, FONT_SIZE_SMALL)

        # היסטוריה – for על list of dict
        self.draw_centered_text("היסטוריה:", 255,
                                self.accent_color, FONT_SIZE_SMALL - 4)
        x_start = 60
        for i, entry in enumerate(self.history):
            icon = "✅" if entry["correct"] else "❌"
            col = (60, 200, 100) if entry["correct"] else (220, 60, 60)
            arcade.draw_text(
                f"{icon} {entry['letter']}",
                x_start + i * 70, 215,
                col, 20, bold=True
            )

        self.draw_centered_text("לחץ לסיום המשחק",
                                140, self.accent_color, FONT_SIZE_SMALL)

    # ─── אירועי עכבר ───────────────────────────────────────
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        if self.state == STATE_PLAYING:
            for btn in self.buttons:
                btn.update_hover(x, y)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if self.state == STATE_INTRO:
            self._next_palette()
            self._new_round()

        elif self.state == STATE_PLAYING:
            # כפתור עברית
            if self.buttons[0].is_clicked(x, y):
                self._check_answer(guessed_hebrew=True)
            # כפתור אנגלית
            elif self.buttons[1].is_clicked(x, y):
                self._check_answer(guessed_hebrew=False)

        elif self.state == STATE_FEEDBACK:
            self.round_num += 1
            if self.round_num >= TOTAL_ROUNDS:
                self._next_palette()
                self.state = STATE_RESULTS
            else:
                self._new_round()

        elif self.state == STATE_RESULTS:
            arcade.exit()

    # ─── בדיקת תשובה ───────────────────────────────────────
    def _check_answer(self, guessed_hebrew: bool) -> None:
        self.correct = (guessed_hebrew == self.is_hebrew)

        if self.correct:
            self.score += 1
            self.feedback_msg   = "כל הכבוד! ניחשת נכון!"
            self.feedback_color = (60, 220, 100)
        else:
            self.feedback_msg   = "לא נכון, נסה שוב בפעם הבאה!"
            self.feedback_color = (220, 60, 60)

        # שמירה להיסטוריה – dict בתוך list
        self.history.append({
            "round":   self.round_num + 1,
            "letter":  self.current_letter,
            "hebrew":  self.is_hebrew,
            "guessed": guessed_hebrew,
            "correct": self.correct,
        })

        self._next_palette()
        self.state = STATE_FEEDBACK


# ─── נקודת כניסה ──────────────────────────────────────────
def main() -> None:
    game = LetterGame()
    arcade.run()


if __name__ == "__main__":
    main()