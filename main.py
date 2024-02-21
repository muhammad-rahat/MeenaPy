import os
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import speech_recognition as sr
import pyttsx3
import datetime
import pywhatkit
import pyjokes
import openai
import requests
from PIL import Image, ImageTk
from io import BytesIO
from openai import OpenAI




listener = sr.Recognizer()
meena = pyttsx3.init()
voices = meena.getProperty('voices')
meena.setProperty('voice', voices[1].id)
meena.setProperty('rate', 115)

class MeenaGUI:
    def __init__(self, master):
        self.master = master
        master.title("Meena Assistant")
        master.configure(bg='maroon')

        style = ttk.Style()
        style.configure('Maroon.TButton', background='maroon', foreground='Gray', padding=(20, 10))
        style.map('Maroon.TButton',
                  background=[('active', 'white'), ('pressed', 'white')],
                  foreground=[('active', 'maroon'), ('pressed', 'maroon')])

        self.label = tk.Label(master, text="HI! THIS IS MEENA.", font=("Helvetica", 16, "bold"), bg='maroon', fg='white')
        self.label.pack(pady=10)

        self.text_display = tk.Text(master, height=10, width=50, wrap=tk.WORD, bg='maroon', fg='white')
        self.text_display.pack(pady=10)

        self.activate_button = ttk.Button(master, text="PRESS HERE to Talk to MEENA", command=self.toggle_meena, style='Maroon.TButton')
        self.activate_button.pack(pady=10)

        self.help_button = ttk.Button(master, text="Help", command=self.show_help, style='Blue.TButton')
        self.help_button.pack(side=tk.LEFT, padx=10)

        self.exit_button = ttk.Button(master, text="Exit", command=self.stop_meena, style='Red.TButton')
        self.exit_button.pack(side=tk.RIGHT, padx=10)

        self.listening_flag = False

    def talk(self, text):
        meena.say(text)
        meena.runAndWait()

    def take_command(self):
        command = ""
        try:
            with sr.Microphone() as source:
                print('listening...')
                voice = listener.listen(source)
                command = listener.recognize_google(voice)
                command = command.lower()
                print("Raw Recognized Command:", command)
                if 'Meena' in command:
                    command = command.replace('Meena', '')
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except Exception as e:
            print("Error in speech recognition: {0}".format(e))
        return command

    def confirm_action(self, message):
        self.talk(message)  #Meena saying the confirmation message
        confirm_dialog = messagebox.askyesno("Confirmation", message)
        return confirm_dialog

    def generate_image(self, description):
        try:
            #API key
            openai.api_key = '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'
            client = OpenAI()

            #using DALL-E
            response = client.images.generate(
                model="dall-e-3",
                prompt="a white siamese cat",
                size="1024x1024",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            # Display image
            image_response = requests.get(generated_image_url)
            img = Image.open(BytesIO(image_response.content))
            img.show()  # Replace with code to display or save the image

            self.talk('Here is the generated image based on your command.')

        except Exception as e:
            self.talk('Sorry, I could not generate the image at the moment. Error: {}'.format(e))

            # Extract URL
            generated_image_url = response.choices[0].file["url"]

            # Display
            image_response = requests.get(generated_image_url)
            img = Image.open(BytesIO(image_response.content))
            img.show()

            self.talk('Here is the generated image based on your command.')

        except Exception as e:
            self.talk('Sorry, I could not generate the image at the moment. Error: {}'.format(e))

    def run_meena(self):
        while self.listening_flag:
            command = self.take_command()
            print("Recognized Command:", command)
            if command:
                if 'time' in command:
                    time = datetime.datetime.now().strftime('%I:%M %p')
                    print(time)
                    self.talk('Current time is ' + time)
                elif 'play' in command:
                    song = command.replace('play', '')
                    self.talk('playing ' + song)
                    pywhatkit.playonyt(song)
                elif 'joke' in command:
                    joke = pyjokes.get_joke()
                    self.text_display.insert(tk.END, f"Meena: {joke}\n")
                    self.text_display.see(tk.END)
                    self.talk(joke)
                elif 'date' in command:
                    self.talk('Sorry bhaaiya, I am in another relation')
                elif 'shut down' in command:
                    confirm_shutdown = self.confirm_action('Are you sure you want to shut down your PC?')
                    if confirm_shutdown:
                        self.talk('Shutting down your PC. Goodbye!')
                        os.system('shutdown /s /t 1')  #shutdown after 1 second
                elif 'sleep' in command:
                    confirm_sleep = self.confirm_action('Are you sure you want to put your PC to sleep?')
                    if confirm_sleep:
                        self.talk('Putting your PC to sleep. Good night!')
                        os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')  #sleep
                elif 'generate image' in command:
                    description = command.split('generate image')[1].strip() if len(command.split('generate image')) > 1 else 'random image'
                    print("Image Description:", description)  # Print for troubleshooting
                    self.generate_image(description)
                else:
                    self.talk('I did not get it but I am going to search it for you')
                    pywhatkit.search(command)

    def confirm_action(self, message):
        confirm_dialog = tk.messagebox.askyesno("Confirmation", message)
        return confirm_dialog

    def toggle_meena(self):
        if not self.listening_flag:
            self.listening_flag = True
            self.label.config(text="Meena is actively listening. Speak now.")
            # Run the Meena loop in a separate thread to keep the GUI responsive
            Thread(target=self.run_meena).start()
        else:
            self.listening_flag = False
            self.label.config(text="Meena is not listening. Click to activate.")

    def show_help(self):
        help_text = "Meena Assistant Help:\n" \
                    "- Speak commands like 'time', 'play music', 'tell me a joke', etc.\n" \
                    "- Click 'PRESS HERE to Talk to MEENA' to activate voice recognition.\n" \
                    "- Click 'Help' to see this help message.\n" \
                    "- Click 'Exit' to close the application."
        self.text_display.insert(tk.END, help_text + "\n")
        self.text_display.see(tk.END)
        self.talk("Here is some help. You can ask me about the time, play music, or tell you a joke.")

    def stop_meena(self):
            self.listening_flag = False
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MeenaGUI(root)
    root.mainloop()
