import pyxel
import pygame
import json
import os

# Constants
WINDOW_WIDTH = 256
WINDOW_HEIGHT = 256
SEQUENCE_SIZE = 16
JUDGE_LINE_X = 128
PERFECT_THRESHOLD = 1
GOOD_THRESHOLD = 5
FPS = 60
RESULT_DELAY = 2.0
FADEOUT_DURATION = 2000  # Fadeout duration in milliseconds

# Game class
def load_sequences(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as file:
        return json.load(file)

class RhythmGame:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT, title="Rhythm Game")
        pygame.mixer.init()

        # Load music and sequences
        self.sequences = load_sequences("sequences.json")
        self.music_file = "starlightyellow.mp3"
        if os.path.exists(self.music_file):
            pygame.mixer.music.load(self.music_file)
        
        self.current_time = 0
        self.sequence_index = 0
        self.score = 0
        self.combo = 0
        self.judgement = ""
        self.result_time = None
        self.is_game_over = False
        pyxel.mouse(True)

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.is_game_over:
            if self.result_time and self.current_time - self.result_time >= RESULT_DELAY:
                self.show_result()
            return

        # Start music
        if self.current_time == 0 and os.path.exists(self.music_file):
            pygame.mixer.music.play()

        if self.sequence_index < len(self.sequences):
            sequence = self.sequences[self.sequence_index]

            # Check for END condition
            if sequence["time"] == "END":
                if self.result_time is None:
                    self.result_time = self.current_time
                    self.is_game_over = True
                    pygame.mixer.music.fadeout(FADEOUT_DURATION)
                return

            time_diff = self.current_time - sequence["time"]

            # Check input
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                seq_x = JUDGE_LINE_X - time_diff * sequence["speed"]
                distance = abs(seq_x - JUDGE_LINE_X)

                if distance <= PERFECT_THRESHOLD:
                    self.judgement = "PERFECT"
                    self.score += 100
                    self.combo += 1
                    self.sequence_index += 1
                elif distance <= GOOD_THRESHOLD:
                    self.judgement = "GOOD"
                    self.score += 50
                    self.combo += 1
                    self.sequence_index += 1
                else:
                    self.judgement = "MISS"
                    self.combo = 0

            # Move to next sequence if passed
            if time_diff > GOOD_THRESHOLD / sequence["speed"]:
                self.judgement = "MISS"
                self.combo = 0
                self.sequence_index += 1

        self.current_time += 1 / FPS

    def show_result(self):
        pyxel.cls(0)
        pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 - 10, "Game Over!", 7)
        pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 10, f"Score: {self.score}", 7)
        pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 20, f"Combo: {self.combo}", 7)

    def draw(self):
        if self.is_game_over:
            self.show_result()
            return

        pyxel.cls(0)

        # Draw judge line
        pyxel.rect(JUDGE_LINE_X - 2, 0, 4, WINDOW_HEIGHT, 7)

        # Draw sequences
        for i in range(self.sequence_index, len(self.sequences)):
            sequence = self.sequences[i]
            if sequence["time"] == "END":
                continue

            time_diff = self.current_time - sequence["time"]
            seq_x = JUDGE_LINE_X - time_diff * sequence["speed"]
            if 0 <= seq_x <= WINDOW_WIDTH:
                pyxel.rect(seq_x - SEQUENCE_SIZE // 2, WINDOW_HEIGHT // 2 - SEQUENCE_SIZE // 2, SEQUENCE_SIZE, SEQUENCE_SIZE, 9)

        # Draw score and judgement
        pyxel.text(5, 5, f"Score: {self.score}", 7)
        pyxel.text(5, 15, f"Combo: {self.combo}", 7)
        pyxel.text(5, 25, f"Judgement: {self.judgement}", 7)

# Example sequences.json format:
# [
#     {"time": 2.0, "speed": 50},
#     {"time": 3.0, "speed": 50},
#     {"time": "END"}
# ]

if __name__ == "__main__":
    RhythmGame()
