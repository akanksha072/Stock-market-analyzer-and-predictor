import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import tempfile
import os
import asyncio
import pygame
import edge_tts

pygame.mixer.init()

# Voice options
VOICES = {
    "English - Jenny": "en-US-JennyNeural",
    "Telugu - Mohan": "te-IN-MohanNeural",
    "Hindi - Swara": "hi-IN-SwaraNeural"
}

current_voice = VOICES["English - Jenny"]
speech_rate = "+0%"  # Default rate

async def save_tts_to_file(text, filename):
    communicate = edge_tts.Communicate(text, current_voice, rate=speech_rate)
    await communicate.save(filename)

def play_audio(file_path):
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.stop()
    except Exception as e:
        log_phrase(f"Error playing audio: {e}")

def speak(text):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            temp_name = tmpfile.name
        asyncio.run(save_tts_to_file(text, temp_name))
        play_audio(temp_name)
        os.remove(temp_name)
    except Exception as e:
        log_phrase(f"Error in speak: {e}")

def log_phrase(text):
    history_box.config(state='normal')
    history_box.insert(tk.END, text + '\n')
    history_box.see(tk.END)
    history_box.config(state='disabled')

def process_command(command):
    response = " You said: " + command
    log_phrase(f"User typed: {command}")
    speak(response)
    log_phrase(f"Assistant: {response}")

def on_send():
    user_input = entry.get()
    if user_input.strip():
        threading.Thread(target=process_command, args=(user_input,), daemon=True).start()
        entry.delete(0, tk.END)

def on_phrase_click(phrase):
    def task():
        log_phrase(f"Button pressed: {phrase}")
        speak(phrase)
        log_phrase(f"Assistant: {phrase}")
    threading.Thread(target=task, daemon=True).start()

def on_voice_change(event):
    global current_voice
    selected = voice_menu.get()
    current_voice = VOICES[selected]

def on_rate_change(val):
    global speech_rate
    rate_percent = (float(val) - 1.0) * 100
    if rate_percent >= 0:
        speech_rate = f"+{int(rate_percent)}%"
    else:
        speech_rate = f"{int(rate_percent)}%"

root = tk.Tk()
root.title("Multilingual AI Assistant for Communication")
root.geometry("600x700")

canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

scroll_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Voice selector
tk.Label(scroll_frame, text="Select Language/Voice:").pack(pady=(10, 0))
voice_menu = ttk.Combobox(scroll_frame, values=list(VOICES.keys()), state="readonly")
voice_menu.current(0)
voice_menu.pack(pady=5)
voice_menu.bind("<<ComboboxSelected>>", on_voice_change)

# Rate control
tk.Label(scroll_frame, text="Adjust Speech Rate:").pack(pady=(10, 0))
rate_slider = tk.Scale(scroll_frame, from_=0.5, to=2.0, resolution=0.1, orient="horizontal", command=on_rate_change)
rate_slider.set(1.0)
rate_slider.pack(pady=5, fill="x", padx=10)

# Input frame
input_frame = tk.Frame(scroll_frame)
input_frame.pack(padx=10, pady=10, fill=tk.X)

entry = tk.Entry(input_frame, width=50)
entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

send_btn = tk.Button(input_frame, text="Send", command=on_send)
send_btn.pack(side=tk.LEFT)

# Phrase board
tk.Label(scroll_frame, text="Phrase Board (Click to Speak):", font=("Arial", 12, "bold")).pack(pady=(15, 5))
phrase_frame = tk.Frame(scroll_frame)
phrase_frame.pack(padx=10, pady=5)

phrases = {
    # English
    "I'm thirsty": "I'm thirsty",
    "Help": "Help me, please",
    "Yes": "Yes",
    "No": "No",
    "Bathroom": "I need to go to the bathroom",
    "I'm hungry": "I'm hungry",
    "I'm tired": "I'm tired",
    "Thank you": "Thank you",
    "I'm happy": "I'm happy",
    "I'm sad": "I'm feeling sad",

    # Telugu
    "నాకు దాహం వేసింది": "నాకు దాహం వేసింది",
    "సహాయం చేయండి": "దయచేసి నాకు సహాయం చేయండి",
    "అవును": "అవును",
    "లేదు": "లేదు",
    "బాత్రూమ్ కి వెళ్ళాలి": "నాకు బాత్రూమ్ కి వెళ్ళాలి",
    "నాకు ఆకలి వేస్తోంది": "నాకు చాలా ఆకలి వేస్తోంది",
    "నాకు నిద్రగా ఉంది": "నాకు నిద్రగా ఉంది",
    "ధన్యవాదాలు": "ధన్యవాదాలు",
    "నాకు సంతోషంగా ఉంది": "నాకు చాలా సంతోషంగా ఉంది",
    "నాకు బాధగా ఉంది": "నాకు చాలా బాధగా ఉంది",
    "నన్ను ఆసుపత్రికి తీసుకెళ్ళండి": "దయచేసి నన్ను ఆసుపత్రికి తీసుకెళ్ళండి",
    "నన్ను ఒంటరిగా వదలండి": "దయచేసి నన్ను ఒంటరిగా వదలండి",
    "ఎవరినైనా పిలవండి": "ఎవరినైనా పిలవండి",
    "నా తల్లిని పిలవండి": "దయచేసి నా తల్లిని పిలవండి",
    "నేను ఇంటికి వెళ్ళాలి": "నేను ఇంటికి వెళ్ళాలి",
    "నాకు నీళ్లు కావాలి": "నాకు నీళ్లు కావాలి",
    "నాకు జ్వరంగా ఉంది": "నాకు జ్వరంగా ఉంది",
    "నాకు సహాయం అవసరం": "నాకు సహాయం అవసరం",
    "నాకు కొంత విశ్రాంతి కావాలి": "నాకు కొంత విశ్రాంతి కావాలి",

    # Hindi
    "मुझे प्यास लगी है": "मुझे प्यास लगी है",
    "मदद करो": "कृपया मेरी मदद करें",
    "हाँ": "हाँ",
    "नहीं": "नहीं",
    "बाथरूम जाना है": "मुझे बाथरूम जाना है",
    "मुझे भूख लगी है": "मुझे बहुत भूख लगी है",
    "मैं थक गया हूँ": "मैं थक गया हूँ",
    "धन्यवाद": "आपका धन्यवाद",
    "मैं खुश हूँ": "मैं खुश हूँ",
    "मैं दुखी हूँ": "मैं बहुत दुखी हूँ",
    "मुझे डॉक्टर के पास ले चलो": "कृपया मुझे डॉक्टर के पास ले चलो",
    "मुझे अकेला छोड़ दो": "कृपया मुझे अकेला छोड़ दो",
    "किसी को बुलाओ": "कृपया किसी को बुलाओ",
    "मुझे पानी दो": "मुझे पानी दो",
    "मुझे बुखार है": "मुझे बुखार है",
    "मुझे नींद आ रही है": "मुझे नींद आ रही है",
    "मैं घर जाना चाहता हूँ": "मैं घर जाना चाहता हूँ"
}

# Create buttons for phrases
row, col = 0, 0
for label, text in phrases.items():
    btn = tk.Button(phrase_frame, text=label, width=30, height=2, command=lambda t=text: on_phrase_click(t))
    btn.grid(row=row, column=col, padx=5, pady=5)
    col += 1
    if col > 1:
        col = 0
        row += 1

# History log
tk.Label(scroll_frame, text="Phrase History:", font=("Arial", 12, "bold")).pack(pady=(15, 5))
history_box = scrolledtext.ScrolledText(scroll_frame, width=60, height=10, state='disabled', wrap=tk.WORD)
history_box.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

root.mainloop()
