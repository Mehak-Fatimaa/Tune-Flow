import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pygame
import os

# Initialize the mixer
pygame.mixer.init()

# Set up the main window
root = tk.Tk()
root.title('Music Player')
root.geometry('500x500')
root.config(bg='white')

# Configure the style for buttons
style = ttk.Style()
style.configure("Custom.TButton",
                font=("Helvetica", 10, "bold"),
                foreground="black",
                padding=(10, 5),
                width=12)
style.map("Custom.TButton",
          background=[('active', 'blue')])

# Create the song listbox
song_list = tk.Listbox(root, width=60, bg='black', fg='white')
song_list.pack(pady=20)

# Function to add songs
def add_song():
    songs = filedialog.askopenfilenames(initialdir='E:/JUW/Sec sem/Data Structures/Project/iqra/Semester2/',
                                        title='Add Music',
                                        filetypes=(('mp3 Files', '*.mp3'),))
    for song in songs:
        song_name = os.path.basename(song)  # Get only the file name
        song_list.insert(tk.END, song_name)

# Function to play the selected song
def play_song():
    song = song_list.get(tk.ACTIVE)
    song_path = f'E:/JUW/Sec sem/Data Structures/Project/iqra/Semester2/{song}'
    try:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(1.0)  # Set volume to maximum (0.0 to 1.0)
        pygame.mixer.music.play(loops=0)
    except Exception as e:
        print(f"Error playing song: {e}")

# Function to stop the song
def stop_song():
    pygame.mixer.music.stop()
    song_list.selection_clear(tk.ACTIVE)

# Pause functionality
paused = False
def pause_song():
    global paused
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        pygame.mixer.music.pause()
        paused = True

# Play next song
def play_next_song():
    next_song = song_list.curselection()
    if next_song:
        next_index = next_song[0] + 1
        if next_index < song_list.size():  # Ensure within bounds
            song = song_list.get(next_index)
            song_path = f'E:/JUW/Sec sem/Data Structures/Project/iqra/Semester2/{song}'
            try:
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play(loops=0)
                song_list.selection_clear(0, tk.END)
                song_list.selection_set(next_index)
            except Exception as e:
                print(f"Error playing next song: {e}")

# Play previous song
def play_previous_song():
    previous_song = song_list.curselection()
    if previous_song:
        previous_index = previous_song[0] - 1
        if previous_index >= 0:  # Ensure within bounds
            song = song_list.get(previous_index)
            song_path = f'E:/JUW/Sec sem/Data Structures/Project/iqra/Semester2/{song}'
            try:
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play(loops=0)
                song_list.selection_clear(0, tk.END)
                song_list.selection_set(previous_index)
            except Exception as e:
                print(f"Error playing previous song: {e}")

# Create button frame
button_frame = tk.Frame(root, bg="#a0a0a0", padx=15, pady=10)
button_frame.pack(pady=20)

# Create buttons
play_button = ttk.Button(button_frame, text='Play', style="Custom.TButton", command=play_song)
pause_button = ttk.Button(button_frame, text='Pause', style="Custom.TButton", command=pause_song)
stop_button = ttk.Button(button_frame, text='Stop', style="Custom.TButton", command=stop_song)
next_button = ttk.Button(button_frame, text='Next', style="Custom.TButton", command=play_next_song)
previous_button = ttk.Button(button_frame, text='Previous', style="Custom.TButton", command=play_previous_song)

# Arrange buttons
play_button.grid(row=0, column=0, padx=10, pady=5)
pause_button.grid(row=0, column=1, padx=10, pady=5)
stop_button.grid(row=0, column=2, padx=10, pady=5)
next_button.grid(row=0, column=3, padx=10, pady=5)
previous_button.grid(row=0, column=4, padx=10, pady=5)

# Add song button
add_song_btn = ttk.Button(root, text='Add Songs', style="Custom.TButton", command=add_song)
add_song_btn.pack(pady=20)

# Run the application
root.mainloop()
