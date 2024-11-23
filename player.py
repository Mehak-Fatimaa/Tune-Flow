import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import os
from datetime import datetime
from PIL import Image, ImageTk  # Import for handling images

# Initialize the pygame mixer
pygame.mixer.init()

# Initialize the main app window
root = tk.Tk()
root.title('Music Player')
root.geometry('600x530')
root.config(bg='#2e2e2e')  # Dark background

# Set the font for the entire application
font_style = ("Arial", 12)

# File to save song list
song_list_file = 'song_list.txt'

# Song listbox with a dark background and light text for contrast
song_list = tk.Listbox(root, width=80, bg='#1e1e1e', fg='white', selectmode=tk.SINGLE, font=font_style)
song_list.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

# Function to save the song list to the file
def save_song_list():
    with open(song_list_file, 'w') as file:
        for i in range(song_list.size()):
            file.write(song_list.get(i) + '\n') 
            
# Function to load the saved song list from the file
def load_song_list():
    if os.path.exists(song_list_file):
        with open(song_list_file, 'r') as file:
            songs = file.readlines()
            for song in songs:
                song_list.insert(tk.END, song.strip())  # Insert into the same Listbox

# Load the song list from the file when the app starts
load_song_list()

# Current song label
current_song_label = tk.Label(root, text="Now Playing: None", bg='#2e2e2e', fg='white', font=font_style)
current_song_label.pack(pady=5)

# Function to update date and time label
def update_date_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

# Function to add songs to the list
def add_song():
    songs = filedialog.askopenfilenames(
        initialdir='E:/JUW/Sec sem/Data Structures/Project/Tune Flow/songs',
        title='Add Music',
        filetypes=(('MP3 Files', '*.mp3'),)
    )
    if songs:  # Check if any songs were selected
        for song in songs:
            song_name = os.path.basename(song)  # Get only the file name
            song_add_time = update_date_time()  # Get the current date and time
            # Insert song name with date and time
            song_list.insert(tk.END, f"{song_name}  |  Added on: {song_add_time}")  
        messagebox.showinfo("Success", "Songs added successfully!")
    save_song_list()  # save updated list

# Function to remove the selected song from the list
def remove_song():
    selected_song_index = song_list.curselection()
    if selected_song_index:
        # Get the selected song name
        song_name = song_list.get(selected_song_index)  
        confirm = messagebox.askyesno("Confirm Deletion", f"Do you really want to delete '{song_name}'?")
        if confirm:  # If the user confirms, remove the song
            song_list.delete(selected_song_index)
            # Reset label if the song is removed
            current_song_label.config(text="Now Playing: None")  
            messagebox.showinfo("Removed", "Song removed from the list.")
            save_song_list()
    else:
        messagebox.showwarning("Warning", "Select a song to remove.")

# Function to open the song playing window
def open_playing_window(song_index):
    if song_index < 0 or song_index >= song_list.size():
        return  # Exit if the index is out of bounds
    
    playing_window = tk.Toplevel(root)
    playing_window.title("Playing")
    playing_window.geometry("660x550")
    playing_window.config(bg='#2e2e2e')  # Dark background

    current_song = song_list.get(song_index).split('  |  ')[0]  # Get the currently selected song name
    current_song_label.config(text=f"Now Playing: {current_song}")

    # Function to handle window close
    def on_close():
        pygame.mixer.music.stop()  # Stop the music
        playing_window.destroy()  # Close the window

    # Bind the on_close function to the window close event
    playing_window.protocol("WM_DELETE_WINDOW", on_close)


    # Initialize the current song index for next/previous functionality
    current_song_index = song_index

    # Function to play the song in the new window
    def play_song():
        pygame.mixer.music.load(os.path.join('E:/JUW/Sec sem/Data Structures/Project/Tune Flow/songs', current_song))
        pygame.mixer.music.play(loops=0)

    # Function to stop the current song
    def stop_song():
        pygame.mixer.music.stop()

    # Pause and unpause functionality
    paused = False
    def pause_song():
        nonlocal paused
        if paused:
            pygame.mixer.music.unpause()
            paused = False
        else:
            pygame.mixer.music.pause()
            paused = True

    # Function to play the next song
    def play_next_song():
        nonlocal current_song_index
        current_song_index += 1
        if current_song_index < song_list.size():
            next_song = song_list.get(current_song_index).split('  |  ')[0]
            current_song_label.config(text=f"Now Playing: {next_song}")
            song_name_label.config(text=next_song)
            song_list.selection_clear(0, tk.END)  # Clear previous selection
            song_list.selection_set(current_song_index)  # Set new selection
            pygame.mixer.music.load(os.path.join('E:/JUW/Sec sem/Data Structures/Project/Tune Flow/songs', next_song))
            pygame.mixer.music.play(loops=0)
        else:
            current_song_index -= 1  # Stay on the last song

    # Function to play the previous song
    def play_previous_song():
        nonlocal current_song_index
        current_song_index -= 1
        if current_song_index >= 0:
            previous_song = song_list.get(current_song_index).split('  |  ')[0]
            current_song_label.config(text=f"Now Playing: {previous_song}")
            song_name_label.config(text=previous_song)
            song_list.selection_clear(0, tk.END)  # Clear previous selection
            song_list.selection_set(current_song_index)  # Set new selection
            pygame.mixer.music.load(os.path.join('E:/JUW/Sec sem/Data Structures/Project/Tune Flow/songs', previous_song))
            pygame.mixer.music.play(loops=0)
        else:
            current_song_index += 1  # Stay on the first song

    # Album art container
    album_art_frame = tk.Frame(playing_window, bg='black', width=400, height=200)
    album_art_frame.pack(pady=10, padx=20, fill=tk.X)

    # Set your fixed album art path
    fixed_album_art_path = 'E:/JUW/Sec sem/Data Structures/Project/Tune Flow/images.png'  # Update path as needed

    # Check if the file exists before loading
    if os.path.exists(fixed_album_art_path):
        try:
            # Load and resize image using Image.LANCZOS
            img = Image.open(fixed_album_art_path)
            img = img.resize((250, 250), Image.LANCZOS)  # Increased image size
            album_art_image = ImageTk.PhotoImage(img)
            
            # Display the image in the container
            album_art_label = tk.Label(album_art_frame, image=album_art_image, bg='black')  # Dark background for image
            album_art_label.image = album_art_image  # Keep a reference to avoid garbage collection
            album_art_label.pack(expand=True, fill=tk.BOTH)
        
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not load image: {e}")
    else:
        messagebox.showerror("File Not Found", f"The file '{fixed_album_art_path}' was not found.")

    # Label for song name
    song_name_label = tk.Label(playing_window, text=current_song, bg='#2e2e2e', fg='white', font=font_style)
    song_name_label.pack(pady=10)

    # Frame for playback buttons
    button_frame = tk.Frame(playing_window, bg='#2e2e2e', padx=20, pady=20)
    button_frame.pack(pady=20, fill=tk.X)

    # Create buttons for play, pause, and stop functions
    button_color = '#007bff'  # Blue button color
    button_width = 20  # Increased button width
    button_height = 2  # Increased button height

    play_button = tk.Button(button_frame, text='Play', command=play_song, bg=button_color, fg='white', width=button_width, height=button_height, font=font_style)
    pause_button = tk.Button(button_frame, text='Pause', command=pause_song, bg=button_color, fg='white', width=button_width, height=button_height, font=font_style)
    stop_button = tk.Button(button_frame, text='Stop', command=stop_song, bg=button_color, fg='white', width=button_width, height=button_height, font=font_style)

    # Arrange the first three buttons in the frame in one line
    play_button.grid(row=0, column=0, padx=10, pady=5)
    pause_button.grid(row=0, column=1, padx=10, pady=5)
    stop_button.grid(row=0, column=2, padx=10, pady=5)

    # Create a frame for next and previous buttons
    navigation_frame = tk.Frame(playing_window, bg='#2e2e2e')
    navigation_frame.pack(pady=10)

    # Create buttons for next and previous functions
    next_button = tk.Button(navigation_frame, text='Next', command=play_next_song, bg=button_color, fg='white', width=button_width, height=button_height, font=font_style)
    previous_button = tk.Button(navigation_frame, text='Previous', command=play_previous_song, bg=button_color, fg='white', width=button_width, height=button_height, font=font_style)

    # Arrange the next and previous buttons in the navigation frame, centered
    next_button.pack(side=tk.LEFT, padx=10)
    previous_button.pack(side=tk.LEFT, padx=10)

# Bind the double-click event to the song list
song_list.bind('<Double-1>', lambda event: open_playing_window(song_list.curselection()[0]))

# Frame for buttons to add and remove songs
button_frame = tk.Frame(root, bg='#2e2e2e')
button_frame.pack(pady=10)

# Add and remove song buttons with increased size
add_song_button = tk.Button(button_frame, text='Add Song', command=add_song, bg='#007bff', fg='white', width=15, height=2, font=font_style)
remove_song_button = tk.Button(button_frame, text='Remove Song', command=remove_song, bg='#007bff', fg='white', width=15, height=2, font=font_style)

# Arrange the add and remove buttons in the frame
add_song_button.pack(side=tk.LEFT, padx=5)
remove_song_button.pack(side=tk.LEFT, padx=5)

# Run the application
root.mainloop()