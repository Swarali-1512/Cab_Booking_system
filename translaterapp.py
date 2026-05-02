import tkinter as tk
from tkinter import ttk, messagebox
from deep_translator import GoogleTranslator 
from gtts import gTTS 
import os
import speech_recognition as sr 
import threading
from indic_transliteration.sanscript import transliterate, ITRANS, DEVANAGARI 
import datetime
import nltk

nltk.download('punkt')

language_map = {
    'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar',
    'armenian': 'hy', 'azerbaijani': 'az', 'basque': 'eu', 'bengali': 'bn',
    'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb',
    'chichewa': 'ny', 'chinese (simplified)': 'zh-CN', 'chinese (traditional)': 'zh-TW',
    'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da',
    'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et',
    'filipino': 'tl', 'finnish': 'fi', 'french': 'fr', 'frisian': 'fy',
    'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el',
    'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw',
    'hebrew': 'iw', 'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu',
    'icelandic': 'is', 'igbo': 'ig', 'indonesian': 'id', 'irish': 'ga',
    'italian': 'it', 'japanese': 'ja', 'javanese': 'jw', 'kannada': 'kn',
    'kazakh': 'kk', 'khmer': 'km', 'korean': 'ko', 'kurdish': 'ku',
    'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv',
    'lithuanian': 'lt', 'luxembourgish': 'lb', 'macedonian': 'mk', 'malagasy': 'mg',
    'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi',
    'marathi': 'mr', 'mongolian': 'mn', 'myanmar': 'my', 'nepali': 'ne',
    'norwegian': 'no', 'odia': 'or', 'pashto': 'ps', 'persian': 'fa',
    'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'romanian': 'ro',
    'russian': 'ru', 'samoan': 'sm', 'scots gaelic': 'gd', 'serbian': 'sr',
    'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si',
    'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es',
    'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tamil': 'ta',
    'telugu': 'te', 'thai': 'th', 'turkish': 'tr', 'ukrainian': 'uk',
    'urdu': 'ur', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy',
    'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'
}

recognizer = sr.Recognizer()

# === Autocomplete Combobox class ===
class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        """Use our completion list as drop down menu."""
        self._completion_list = sorted(completion_list, key=str.lower)
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self['values'] = self._completion_list
        self.bind('<KeyRelease>', self.handle_keyrelease)

    def autocomplete(self, delta=0):
        """Autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits."""
        if delta:  # need to delete selection otherwise we would fix the current position
            self.delete(self.position, tk.END)
        else:  # set position to end so selection starts where text entry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):
                _hits.append(element)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # no hits
        if not _hits:
            return
        # cycling through hits
        self._hit_index = (self._hit_index + delta) % len(self._hits)
        # update entry with new hit
        self.delete(0, tk.END)
        self.insert(0, self._hits[self._hit_index])
        self.select_range(self.position, tk.END)

    def handle_keyrelease(self, event):
        if event.keysym == "BackSpace":
            self.delete(self.index(tk.INSERT), tk.END)
            self.position = self.index(tk.END)
        elif event.keysym == "Left":
            if self.position < self.index(tk.END):
                self.delete(self.position, tk.END)
            else:
                self.position -= 1
        elif event.keysym == "Right":
            self.position = self.index(tk.END)
        elif len(event.keysym) == 1:
            self.autocomplete()

# === GUI setup ===
root = tk.Tk()
root.title("NLP Translator (Voice, History, Dropdown, NLP)")
root.geometry("900x500")
root.configure(bg="#f0f0f0")

main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(padx=20, pady=20)

tk.Label(main_frame, text="NLP Translator (Voice, History, Dropdown, NLP)", font=("Arial", 16, 'bold'),
         fg="white", bg="#1e3d78", pady=10).grid(row=0, column=0, columnspan=4, sticky="ew")

# Input
tk.Label(main_frame, text="Enter text to translate:", bg="#f0f0f0", anchor='w', font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=(15, 0))
input_text = tk.Text(main_frame, height=4, width=60, font=("Arial", 12))
input_text.grid(row=2, column=0, columnspan=4, pady=(0, 5))

# Searchable dropdowns with autocomplete
tk.Label(main_frame, text="Select Input Language:", bg="#f0f0f0", font=("Arial", 12)).grid(row=3, column=0, sticky="w")

input_lang = AutocompleteCombobox(main_frame, width=20, font=("Arial", 12))
input_lang.set_completion_list(list(language_map.keys()))
input_lang.set("english")
input_lang.grid(row=3, column=1, pady=5)

tk.Label(main_frame, text="Select Target Language:", bg="#f0f0f0", font=("Arial", 12)).grid(row=3, column=2, sticky="w")

target_lang = AutocompleteCombobox(main_frame, width=20, font=("Arial", 12))
target_lang.set_completion_list(list(language_map.keys()))
target_lang.set("marathi")
target_lang.grid(row=3, column=3, pady=5)

# Output
tk.Label(main_frame, text="Translated Text:", bg="#f0f0f0", anchor='w', font=("Arial", 12)).grid(row=5, column=0, sticky="w", pady=(10, 0))
output_text = tk.Text(main_frame, height=4, width=60, font=("Arial", 12))
output_text.grid(row=6, column=0, columnspan=4)

# Transliterate function
def transliterate_names(original, translated, lang_code):
    if lang_code != 'mr':
        return translated
    words = original.split()
    for word in words:
        if word.istitle() and word.lower() not in ["my", "name", "is"]:
            try:
                devanagari = transliterate(word, ITRANS, DEVANAGARI)
                translated = translated.replace(word, devanagari)
            except:
                pass
    return translated

# Speak input
def speak_input():
    def run():
        with sr.Microphone() as source:
            try:
                input_text.delete("1.0", tk.END)
                input_text.insert(tk.END, "Listening...")
                audio = recognizer.listen(source)
                lang_code = language_map.get(input_lang.get().lower(), 'en')
                query = recognizer.recognize_google(audio, language=lang_code)
                input_text.delete("1.0", tk.END)
                input_text.insert(tk.END, query)
            except Exception as e:
                messagebox.showerror("Speech Error", str(e))
    threading.Thread(target=run).start()

# Translate
def translate_text():
    src = input_lang.get().lower()
    tgt = target_lang.get().lower()
    if src not in language_map or tgt not in language_map:
        messagebox.showerror("Translation Error", "Unsupported language selected.")
        return

    raw_text = input_text.get("1.0", tk.END).strip()
    if not raw_text:
        messagebox.showwarning("Missing Input", "Please enter text to translate.")
        return

    try:
        translated = GoogleTranslator(source=language_map[src], target=language_map[tgt]).translate(raw_text)
        translated = transliterate_names(raw_text, translated, language_map[tgt])
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, translated)

        translation_count = 0
        try:
            with open("translation_history.txt", "r", encoding="utf-8") as f:
                translation_count = f.read().count("==================================================")
        except FileNotFoundError:
            translation_count = 0

        translation_count += 1
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("translation_history.txt", "a", encoding="utf-8") as f:
            f.write("==================================================\n")
            f.write(f"Translation #{translation_count}\n")
            f.write(f"Time: {now}\n")
            f.write(f"Original: {raw_text}\n")
            f.write(f"Target ({language_map[tgt]}): {translated}\n\n")

    except Exception as e:
        messagebox.showerror("Translation Error", str(e))

# Speak output
def speak_output():
    text = output_text.get("1.0", tk.END).strip()
    if not text:
        return
    tts = gTTS(text=text, lang=language_map.get(target_lang.get().lower(), 'en'))
    tts.save("speak.mp3")
    os.system("start speak.mp3" if os.name == 'nt' else "xdg-open speak.mp3")

# Clear all
def clear_all():
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)

# Copy input
def copy_input():
    root.clipboard_clear()
    root.clipboard_append(input_text.get("1.0", tk.END).strip())

# Copy output
def copy_output():
    root.clipboard_clear()
    root.clipboard_append(output_text.get("1.0", tk.END).strip())

# Buttons
tk.Button(main_frame, text="🎤 Speak Input", command=speak_input, bg="#4da6ff", width=15, font=("Arial", 12)).grid(row=4, column=0, pady=10)
tk.Button(main_frame, text="📋 Copy Input", command=copy_input, bg="gold", width=15, font=("Arial", 12)).grid(row=4, column=1)
tk.Button(main_frame, text="🔄 Translate", command=translate_text, bg="#204dff", fg="white", width=15, font=("Arial", 12)).grid(row=4, column=2)
tk.Button(main_frame, text="🧹 Clear All", command=clear_all, bg="salmon", width=15, font=("Arial", 12)).grid(row=4, column=3)

tk.Button(main_frame, text="🔊 Speak Output", command=speak_output, bg="lightgreen", width=15, font=("Arial", 12)).grid(row=7, column=0, pady=10)
tk.Button(main_frame, text="📋 Copy Output", command=copy_output, bg="gold", width=15, font=("Arial", 12)).grid(row=7, column=1)

# Footer
tk.Label(root, text="💾 Translations saved in translation_history.txt", bg="#f0f0f0", font=("Arial", 10), fg="gray").pack(side=tk.BOTTOM)

root.mainloop()

