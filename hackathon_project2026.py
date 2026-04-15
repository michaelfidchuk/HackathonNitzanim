import arcade
import arcade.gui
import random

class Game(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "AI Game")

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.current_screen = "start"
        self.score = 0

        # שאלות לפי סוג
        self.questions = [
            {"type": "text", "content": "The sun exploded yesterday", "answer": "ai"},
            {"type": "text", "content": "I went to school today", "answer": "human"},
            {"type": "text", "content": "Cats can control humans secretly", "answer": "ai"},
            {"type": "text", "content": "I played basketball with my friends", "answer": "human"}
        ]

        # עותק למשחק (כדי למחוק ממנו)
        self.available_questions = []

        self.current_question = {}

        # טעויות לפי סוג
        self.wrong_text = 0

        self.setup_ui()

    # =========================
    def setup_ui(self):
        self.manager.clear()
        layout = arcade.gui.UIAnchorLayout()

        if self.current_screen == "start":
            btn = arcade.gui.UIFlatButton(text="Start", width=200)

            def start(event):
                self.current_screen = "game"
                self.score = 0
                self.wrong_text = 0

                # העתקת שאלות
                self.available_questions = []
                for q in self.questions:
                    self.available_questions.append(q)

                self.next_question()
                self.setup_ui()

            btn.on_click = start
            layout.add(btn, anchor_x="center_x", anchor_y="center_y")

        elif self.current_screen == "game":
            box = arcade.gui.UIBoxLayout(space_between=40)

            ai_btn = arcade.gui.UIFlatButton(text="AI", width=120)
            human_btn = arcade.gui.UIFlatButton(text="Human", width=120)

            def ai_click(event):
                self.check("ai")

            def human_click(event):
                self.check("human")

            ai_btn.on_click = ai_click
            human_btn.on_click = human_click

            box.add(ai_btn)
            box.add(human_btn)

            layout.add(box, anchor_x="center_x", anchor_y="bottom", align_y=50)

        elif self.current_screen == "end":
            btn = arcade.gui.UIFlatButton(text="Exit", width=200)

            def exit_game(event):
                arcade.close_window()

            btn.on_click = exit_game
            layout.add(btn, anchor_x="center_x", anchor_y="center_y")

        self.manager.add(layout)

    # =========================
    def next_question(self):
        self.current_question = random.choice(self.available_questions)

    # =========================
    def check(self, answer):

        # בדיקה
        if answer == self.current_question["answer"]:
            self.score += 1
        else:
            if self.current_question["type"] == "text":
                self.wrong_text += 1

        # מחיקת שאלה כדי שלא תחזור
        self.available_questions.remove(self.current_question)

        # סיום או המשך
        if len(self.available_questions) == 0:
            self.current_screen = "end"
            self.setup_ui()
        else:
            self.next_question()

    # =========================
    def get_tip(self):
        tip = ""

        if self.wrong_text > 1:
            tip = "Tip: AI texts are often unusual or unrealistic"

        if tip == "":
            tip = "Great job! You can identify AI well"

        return tip

    # =========================
    def on_draw(self):
        self.clear()

        if self.current_screen == "start":
            arcade.set_background_color(arcade.color.BEIGE)

        elif self.current_screen == "game":
            arcade.set_background_color(arcade.color.LIGHT_YELLOW)

        elif self.current_screen == "end":
            arcade.set_background_color(arcade.color.LIGHT_BLUE)

        if self.current_screen == "start":
            arcade.draw_text("AI or Human?", 260, 400, arcade.color.BLACK, 30)
            arcade.draw_text("Press Start to play", 280, 340, arcade.color.DARK_GRAY, 18)

        elif self.current_screen == "game":
            arcade.draw_text(
                self.current_question["content"],
                100, 300,
                arcade.color.BLACK,
                20,
                width=600,
                align="center"
            )

            arcade.draw_text(
                "Score: " + str(self.score),
                10, 560,
                arcade.color.BLACK,
                14
            )

        elif self.current_screen == "end":
            arcade.draw_text(
                "Final Score: " + str(self.score),
                260, 350,
                arcade.color.BLACK,
                30
            )

            arcade.draw_text(
                self.get_tip(),
                120, 250,
                arcade.color.DARK_BLUE,
                18,
                width=560,
                align="center"
            )

        self.manager.draw()


# =========================
game = Game()
arcade.run()