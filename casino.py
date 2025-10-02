# pisklyavoe_kazino.py
import tkinter as tk
import random
import time
import os
import math

# === ЗВУКИ ===
USE_SOUND = True
pygame = None
spin_tick_sound = None
spin_stop_sound = None

try:
    import pygame
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=64)
    pygame.mixer.init()
    
    # Генерация звука "тик" (короткий щелчок)
    def generate_tick_sound(duration=0.05, freq=800):
        sample_rate = 22050
        n_samples = int(round(duration * sample_rate))
        buf = bytearray(n_samples * 2)
        for i in range(n_samples):
            t = i / sample_rate
            val = int(32767 * 0.3 * math.sin(2 * math.pi * freq * t + 50 * t**2))  # chirp
            buf[2*i] = val & 0xff
            buf[2*i + 1] = (val >> 8) & 0xff
        return pygame.mixer.Sound(buffer=bytes(buf))
    
    # Генерация звука "стоп" (звон)
    def generate_stop_sound():
        sample_rate = 22050
        duration = 0.2
        n_samples = int(round(duration * sample_rate))
        buf = bytearray(n_samples * 2)
        for i in range(n_samples):
            t = i / sample_rate
            # Затухающий синус
            envelope = math.exp(-t * 10)
            val = int(32767 * envelope * math.sin(2 * math.pi * 1200 * t))
            buf[2*i] = val & 0xff
            buf[2*i + 1] = (val >> 8) & 0xff
        return pygame.mixer.Sound(buffer=bytes(buf))
    
    spin_tick_sound = generate_tick_sound()
    spin_stop_sound = generate_stop_sound()
    
except Exception:
    USE_SOUND = False


# === ИГРА ===
class PisklyavoeKazino:
    def __init__(self, root):
        self.root = root
        self.root.title("🐭 Писклявое Казино")
        self.root.geometry("620x550")
        self.root.resizable(False, False)
        
        self.balance = 1000
        self.bet = 50
        self.symbols = ["🐭", "🍒", "🍋", "🍇", "🍉", "🔔", "7️⃣"]
        self.multipliers = {
            "🐭": 3, "🍒": 2, "🍋": 3, "🍇": 4, "🍉": 5, "🔔": 6, "7️⃣": 10
        }
        self.reels = [tk.StringVar(value="🐭") for _ in range(3)]
        self.setup_ui()
        self.update_balance_display()
        self.try_play_music()
    
    def try_play_music(self):
        if not USE_SOUND:
            return
        music_path = os.path.join(os.path.dirname(__file__), "music.mp3")
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1)
            except:
                pass
    
    def play_sound(self, sound_type):
        if not USE_SOUND or not pygame:
            return
        try:
            if sound_type == "tick" and spin_tick_sound:
                spin_tick_sound.play()
            elif sound_type == "stop" and spin_stop_sound:
                spin_stop_sound.play()
        except:
            pass
    
    def setup_ui(self):
        title = tk.Label(self.root, text="🐭 ПИСКЛЯВОЕ КАЗИНО 🐭", font=("Comic Sans MS", 24, "bold"), fg="#FF6B6B")
        title.pack(pady=10)
        
        self.balance_label = tk.Label(self.root, text="", font=("Arial", 16))
        self.balance_label.pack()
        
        bet_frame = tk.Frame(self.root)
        bet_frame.pack(pady=10)
        tk.Label(bet_frame, text="Ставка:", font=("Arial", 14)).pack(side=tk.LEFT)
        self.bet_label = tk.Label(bet_frame, text=f"{self.bet} ₽", font=("Arial", 14, "bold"), fg="blue")
        self.bet_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(bet_frame, text="–", command=lambda: self.change_bet(-10), width=3).pack(side=tk.LEFT)
        tk.Button(bet_frame, text="+", command=lambda: self.change_bet(10), width=3).pack(side=tk.LEFT, padx=(5,0))
        
        reels_frame = tk.Frame(self.root)
        reels_frame.pack(pady=20)
        self.labels = []
        for i in range(3):
            label = tk.Label(
                reels_frame,
                textvariable=self.reels[i],
                font=("Arial", 48),
                width=3,
                relief="raised",
                bg="pink"
            )
            label.pack(side=tk.LEFT, padx=10)
            self.labels.append(label)
        
        self.spin_button = tk.Button(
            self.root,
            text="КРУТИТЬ 🎰",
            font=("Arial", 16, "bold"),
            bg="#FF5722",
            fg="white",
            command=self.spin,
            height=2,
            width=15
        )
        self.spin_button.pack(pady=15)
        
        self.result_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.result_label.pack(pady=5)
        self.check_spin_button()
    
    def update_balance_display(self):
        self.balance_label.config(text=f"Баланс: {self.balance} ₽")
    
    def change_bet(self, delta):
        new_bet = self.bet + delta
        if 10 <= new_bet <= 500 and new_bet <= self.balance:
            self.bet = new_bet
            self.bet_label.config(text=f"{self.bet} ₽")
            self.check_spin_button()
    
    def check_spin_button(self):
        self.spin_button.config(state="normal" if self.balance >= self.bet else "disabled")
    
    def spin(self):
        if self.balance < self.bet:
            return
        
        self.balance -= self.bet
        self.update_balance_display()
        self.check_spin_button()
        
        self.spin_button.config(state="disabled", text="Крутим...")
        self.result_label.config(text="")
        self.root.update()
        
        # Анимация с звуками
        for step in range(15):
            for j in range(3):
                self.reels[j].set(random.choice(self.symbols))
            self.root.update()
            self.play_sound("tick")  # 💡 Звук прокрутки
            time.sleep(0.08)
        
        self.play_sound("stop")  # 💡 Финальный звук
        
        final_result = [random.choice(self.symbols) for _ in range(3)]
        for i in range(3):
            self.reels[i].set(final_result[i])
        
        if final_result[0] == final_result[1] == final_result[2]:
            symbol = final_result[0]
            multiplier = self.multipliers.get(symbol, 5)
            win_amount = self.bet * multiplier
            self.balance += win_amount
            self.result_label.config(
                text=f"🎉 ПИСК! ВЫ ВЫИГРАЛИ!\n+{win_amount} ₽ (x{multiplier})",
                fg="green"
            )
        else:
            self.result_label.config(text="Писк... не повезло 😿", fg="red")
        
        self.update_balance_display()
        self.check_spin_button()
        self.spin_button.config(state="normal", text="КРУТИТЬ 🎰")


if __name__ == "__main__":
    root = tk.Tk()
    app = PisklyavoeKazino(root)
    root.mainloop()