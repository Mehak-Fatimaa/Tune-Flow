import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import os
from datetime import datetime
from PIL import Image, ImageTk
import numpy as np
import threading
from pydub import AudioSegment
from tkinter import ttk
import winsound
from PIL import Image, ImageTk, ImageEnhance, ImageDraw
from welcome import show_welcome_page

# Initialize the pygame mixer
pygame.mixer.init()

# Default Paths
ALBUM_ART_PATH = r"E:\JUW\Sec sem\Data Structures\Project\Tune Flow\images\img.jpg"  
SONG_LOGO = r"E:\JUW\Sec sem\Data Structures\Project\Tune Flow\images\logo.jpg"
default_song_path = "E:/JUW/Sec sem/Data Structures/Project/Tune Flow/songs/"

# Initialize the main app window
root = tk.Tk()
root.title('Tune flow')
root.geometry('800x600') # widh X height 
# root.config(bg='#2b2b2b')
root.config(bg='#2b2b2b')

# Set the font for the entire application
font_style = ("Arial", 12)

# File to save song list
song_list_file = 'song_list.txt'

# Create frames for the screens
welcome_frame = tk.Frame(root, bg='black')
main_screen_frame = tk.Frame(root, bg='#2b2b2b')

# Function to switch frames
def show_frame(frame_to_show):
    """Hide all frames and show the selected frame."""
    for frame in (welcome_frame, main_screen_frame):
        frame.pack_forget()  # Hide all frames
    frame_to_show.pack(fill=tk.BOTH, expand=True)  # Show the desired frame

# ** Add welcome page content to welcome_frame **
show_welcome_page(welcome_frame, lambda: show_frame(main_screen_frame)) 

# Frame to hold the song list and canvas for scrolling
song_list_frame = tk.Frame(main_screen_frame, bg='#1e1e1e')
song_list_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

# Canvas for song list
song_list_canvas = tk.Canvas(song_list_frame, bg="#1e1e1e", bd=0, highlightthickness=0)
song_list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar for the canvas
scrollbar = ttk.Scrollbar(song_list_frame, orient=tk.VERTICAL, command=song_list_canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
song_list_canvas.configure(yscrollcommand=scrollbar.set)
song_list_canvas.bind('<Configure>', lambda e: song_list_canvas.configure(scrollregion=song_list_canvas.bbox("all")))

# Frame to hold song frames inside the canvas
song_frames_container = tk.Frame(song_list_canvas, bg="#1e1e1e")
song_list_canvas.create_window((0, 0), window=song_frames_container, anchor="nw")

# Function to save the song list to the file
def save_song_list():
        song_names = []
        for song_frame in song_frames_container.winfo_children():
            song_label = song_frame.winfo_children()[1]  # Get the song label
            song_names.append(song_label.cget("text"))

        # Save updated list to the file
        with open(song_list_file, 'w') as file:
            for song_name in song_names:
                file.write(song_name + '\n')

# Function to load the saved song list from the file

def load_song_list():
    if os.path.exists(song_list_file):
        with open(song_list_file, 'r') as file:
            songs = file.readlines()
        for song in songs:
            song_name = song.strip()
            add_song_to_canvas(song_name)

show_frame(welcome_frame)

# designing buttons
def style_button(button, color="#4CAF50", hover_color="#45a049"):
    button.config(
        bg=color,                     # Button background color
        fg="white",                   # Button text color
        font=("Arial", 12, "bold"),   # Font style
        relief="flat",                # Flat button look
        activebackground=hover_color, # Hover background color
        activeforeground="white",     # Hover text color
        padx=10,                      # Horizontal padding
        pady=5                        # Vertical padding
    )

def add_song_to_canvas(song_name):
    # Create a frame for each song
    song_frame = tk.Frame(song_frames_container, bg='#1e1e1e')
    song_frame.pack(fill=tk.X, pady=5)

    # Add album art (replace with actual path)
    song_logo = Image.open(SONG_LOGO)
    song_logo = song_logo.resize((50, 50), Image.Resampling.LANCZOS)
    song_logo = ImageTk.PhotoImage(song_logo)

    # Album art on the left
    logo_label = tk.Label(song_frame, image=song_logo, bg="#1e1e1e")
    logo_label.image = song_logo
    logo_label.pack(side=tk.LEFT, padx=10)  # Align logo to the left

    # Song name label next to the logo
    song_label = tk.Label(song_frame, text=song_name, font=("Helvetica", 12), bg="#1e1e1e", fg="white", anchor="w")
    song_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)  # Expand label to fill the middle space

    # Buttons container aligned to the right
    button_container = tk.Frame(song_frame, bg="#1e1e1e")
    button_container.pack(side=tk.RIGHT, padx=10, anchor="e")  # Align buttons to the far-right corner

    # Add play button
    play_button = tk.Button(
        button_container, 
        text="Play", 
        command=lambda song=song_name: on_play_button_click(song)
    )
    style_button(play_button, color="#ff4d4d", hover_color="#cc0000")
    play_button.pack(side=tk.LEFT, padx=45)  # Pack to the right

    # Add delete button
    delete_button = tk.Button(
        button_container, 
        text="Delete", 
        command=lambda song=song_name: remove_song(song)
    )
    style_button(delete_button, color="#ff4d4d", hover_color="#cc0000")
    delete_button.pack(side=tk.LEFT, padx=5)  # Pack to the right


# Function to handle the play button click
def on_play_button_click(song_name):
    # Find the index of the song from the song frames container
    for index, song_frame in enumerate(song_frames_container.winfo_children()):
        song_label = song_frame.winfo_children()[1]  # Get the song label
        if song_label.cget("text") == song_name:  # Check if the song name matches
            global current_song_index  # Declare as global to modify the variable
            current_song_index = index  # Set the current song index
            break  # Stop once the song is found

    # Now open the playing window for the selected song
    open_playing_window(current_song_index)  # Pass the current song index

# Load the song list from the file when the app starts
load_song_list()

# Current song label
current_song_label = tk.Label(main_screen_frame, text="Now Playing: None", bg='#1e1e1e', fg='white', font=("Helvetica", 14))
current_song_label.pack(pady=10)

# Open play window for the selected song
def play_selected_song(song_info):
    try:
        # Split to extract only the song name before the " | "
        song_name = song_info.split("  |")[0].strip()
        
        # Song ka full path generate karna
        song_path = os.path.join(default_song_path, song_name)
        
        # Pygame mixer initialize karna agar pehle initialize nahi hua
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Load aur play the song
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        
        # Update the "Now Playing" label
        current_song_label.config(text=f"Now Playing: {song_name}")
    except pygame.error as e:
        print(f"Error loading song: {e}")
        messagebox.showerror("Error", f"Could not play the song: {song_name}\nError: {e}")

# Function to add songs to the list
def add_song():
    songs = filedialog.askopenfilenames(
        initialdir=default_song_path,
        title='Add Music',
        filetypes=(('MP3 Files', '*.mp3'),)
    )

    # Check if the user selected any songs
    if songs:
        for song in songs:
            song_name = os.path.basename(song)  # Get the file name, not the path

            # Add song to canvas
            add_song_to_canvas(song_name)

        # Save updated song list
        save_song_list()

        # Success message
        messagebox.showinfo("Success", "Songs added successfully!")

# remove song
def remove_song(song_name):
    # Find the song frame that matches the song name and destroy it
    for song_frame in song_frames_container.winfo_children():
        song_label = song_frame.winfo_children()[1]  # Get the song label
        if song_label.cget("text") == song_name:
            song_frame.destroy()  # Remove the song frame from the canvas
            break

    # Reset "Now Playing" label if the song being removed is currently playing
    if current_song_label.cget("text").endswith(song_name):
        current_song_label.config(text="Now Playing: None")

    # Show success message
    messagebox.showinfo("Removed", f"'{song_name}' removed from the list.")

    # Remove song from the file
    save_song_list()

# Global variable to track playback state
is_paused = False

# Function to visualize beats
def visualize_beats(canvas, song_path, background_image):
    global is_paused
    try:
        # Song ko pydub se load karna
        song = AudioSegment.from_file(song_path)  # File path se audio load
        frame_rate = song.frame_rate  # Audio ka frame rate lena
        samples = np.array(song.get_array_of_samples())  # Samples ko numpy array me convert karna
        chunk_size = 1024  # Ek chunk ka size (samples ka)

        # Bar visualization ke parameters
        num_bars = canvas.winfo_width() // 10 # Canvas ki width ke mutabiq number of bars
        bar_height = canvas.winfo_height()  # Canvas ki height
        max_amplitude = np.max(np.abs(samples))  # Max amplitude calculate karna
        max_bar_height = 800  # Ek bar ki max height (pixels me)

        # Bars ko update karne ka function
        def update_bars():
            # Visualization tabhi chalega jab music playing ho
            if pygame.mixer.music.get_busy():
                # Agar paused nahi hai tabhi bars move karengi
                if not is_paused:
                    pos = pygame.mixer.music.get_pos()  # Current position (milliseconds me)
                    current_sample = int((pos / 1000) * frame_rate)  # Milliseconds ko sample index me convert karna

                    # Current chunk lena aur uska amplitude calculate karna
                    chunk = samples[current_sample:current_sample + chunk_size]
                    amplitude = np.abs(chunk).mean() / max_amplitude  # Normalize amplitude

                    # Canvas clear karna hr frame pr aur bars ko redraw karna
                    canvas.delete("all")
                    if background_image:
                        canvas.create_image(0, 0, anchor=tk.NW, image=background_image)  # Background image draw karna

                    bar_width = canvas.winfo_width() // num_bars  # Har bar ki width
                    for i in range(num_bars):
                        # Dynamic amplitude scaling
                        amplitude_factor = amplitude * (i + 1) / num_bars
                        bar_length = int(amplitude_factor * max_bar_height)
                        bar_length = min(bar_length, max_bar_height)  # Bar ki height ko cap karna

                        # Gradient color lena
                        color = get_gradient_color(amplitude, i)

                        # Bar ki position aur drawing
                        x_position = i * (bar_width + 3)
                        canvas.create_rectangle(
                            x_position, bar_height - bar_length, x_position + bar_width, bar_height,
                            fill=color, outline=""  # Outline remove karna
                        )

            # Function ko 50ms ke baad dobara call karna
            canvas.after(50, update_bars)

        # Visualization start karna
        update_bars()

    except Exception as e:
        print(f"Visualization error: {e}")  # Agar error aaye toh print karna

# rainbow effect
def get_gradient_color(amplitude, index):
    amplitude_scaled = min(1, amplitude)  # Clamp amplitude to a maximum of 1
    num_colors = 256  # Define number of colors in the rainbow spectrum

    # Generate RGB values for the rainbow gradient using HSV color wheel
    hue = (index / 30) % 1.0  # Distribute hues across the bars (0-30)
    saturation = 1.0  # Full saturation for vibrancy
    value = max(0.5, amplitude_scaled)  # Value proportional to amplitude (min brightness 50%)

    r, g, b = hsv_to_rgb(hue, saturation, value)  # Convert HSV to RGB
    return f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'

def hsv_to_rgb(h, s, v):
    i = int(h * 6)  # Determine sector of the HSV color space
    f = (h * 6) - i  # Fractional part
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i %= 6
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    elif i == 5:
        r, g, b = v, p, q
    return r, g, b

playing_window = None 
# Function to open the song playing window
def open_playing_window(song_index):
    # Agar ek window pehle se open hai, toh use destroy kar do
    global playing_window
    if playing_window:
        playing_window.destroy()

    # If song_index is invalid, return early
    if song_index < 0 or song_index >= len(song_frames_container.winfo_children()):
        return

    # Fetch the song name using the song index
    song_frame = song_frames_container.winfo_children()[song_index]
    song_name = song_frame.winfo_children()[1].cget("text")  # Get song name from the label

    # Agar song_name empty ho, toh function se exit
    if not song_name:
        return

    playing_window = tk.Toplevel(root)
    playing_window.title("Playing")
    playing_window.geometry("710x520")
    playing_window.config(bg='#2e2e2e')  # Dark theme background

    # Current song ka info aur path
    song_path = os.path.join(default_song_path, song_name)

    # Current song ka label update karna
    current_song_label.config(text=f"Now Playing: {song_name}")

    # Visualization ke liye canvas create karna
    visualization_canvas = tk.Canvas(playing_window, width=700, height=200, bg="black", highlightthickness=0)
    visualization_canvas.pack(pady=20)

    # Background image load karna (agar available hai)
    background_image = None
    if os.path.exists(ALBUM_ART_PATH):
        try:
            # Image resize aur canvas ke liye load
            background_image = Image.open(ALBUM_ART_PATH).resize((700, 300), Image.LANCZOS)
            background_image = ImageTk.PhotoImage(background_image)
        except Exception as e:
            print(f"Error loading image: {e}")
    else:
        print(f"Image not found at {ALBUM_ART_PATH}")

    # Canvas me image set karna, ya default black background use karna
    if background_image:
        visualization_canvas.create_image(0, 0, anchor=tk.NW, image=background_image)
        visualization_canvas.image = background_image  # Garbage collection prevent karne ke liye
    else:
        visualization_canvas.create_rectangle(0, 0, 700, 200, fill="black")

    # Beat visualization thread shuru karna
    threading.Thread(target=visualize_beats, args=(visualization_canvas, song_path, background_image), daemon=True).start()

    # Function to handle window close
    def on_close():
        stop_song()

    # Bind the on_close function to the window close event
    playing_window.protocol("WM_DELETE_WINDOW", on_close)

    # Label for song name
    song_name_label = tk.Label(playing_window, text=song_name, bg='#2e2e2e', fg='white', font=font_style)
    song_name_label.pack(pady=10)  

    # Function to play the song
    def play_song(song_path):
        try:
            # Pygame mixer initialize karna agar pehle initialize nahi hua
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            # Load aur play the song
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            
            # Update the "Now Playing" label
        except pygame.error as e:
            print(f"Error loading song: {e}")
            messagebox.showerror("Error", f"Could not play the song: \nError: {e}")

    def stop_song():
        current_song_label.config(text=f"Now Playing: None")
        song_frame.config(bg='#1e1e1e')
        pygame.mixer.music.stop()
        playing_window.destroy()

    def pause_song():
        global is_paused
        pygame.mixer.music.pause()
        is_paused = True  # Set playback state to paused

    def resume_song():
        global is_paused
        pygame.mixer.music.unpause()
        is_paused = False  # Set playback state to playing

    def update_volume(val):
        pygame.mixer.music.set_volume(float(val))  # Set volume level

    # Initialize the current song index for next/previous functionality
    current_song_index = song_index

    def play_next_song():
        # Agar song list empty hai tu return kar dena
        if len(song_frames_container.winfo_children()) == 0:  # Check for available song frames
            return

        nonlocal current_song_index  # Access the current song index

        # Increment the index for the next song
        current_song_index += 1

        # Check if current index exceeds the number of songs, then reset to 0
        if current_song_index >= len(song_frames_container.winfo_children()):
            current_song_index = 0  # Reset to first song

        # Get the next song name from the song frames container (button text)
        next_song_frame = song_frames_container.winfo_children()[current_song_index]
        next_song_name = next_song_frame.winfo_children()[1].cget("text")  # Get the song name from the label

        # Update the UI labels with the new song name
        current_song_label.config(text=f"Now Playing: {next_song_name}")  # Update 'Now Playing' label
        song_name_label.config(text=next_song_name)  # Update the song name label in the playing window

        # Update song selection in the buttons (visual feedback)
        for frame in song_frames_container.winfo_children():
            frame.config(bg="#1e1e1e")  # Reset all frames to default color (no selection)
        next_song_frame.config(bg="#4CAF50")  # Highlight selected song frame in green

        # Load and play the next song using pygame mixer
        song_path = os.path.join(default_song_path, next_song_name)
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(loops=0)  # Play next song without looping

        # Update the "Now Playing" label in the main window
        current_song_label.config(text=f"Now Playing: {next_song_name}")

    def play_previous_song():
        # Ensure we are getting the correct song index
        nonlocal current_song_index  # Access the outer function's current_song_index
        current_song_index -= 1  # Decrement the index to go to the previous song

        # If we're at the first song, wrap around to the last song
        if current_song_index < 0:
            current_song_index = len(song_frames_container.winfo_children()) - 1  # Last song index

        # Fetch the previous song name
        previous_song = song_frames_container.winfo_children()[current_song_index].winfo_children()[1].cget("text")

        # Update the "Now Playing" label in the main window
        current_song_label.config(text=f"Now Playing: {previous_song}")

        # Update the song name label in the playing window (if open)
        if playing_window:
            song_name_label.config(text=previous_song)

        # Clear the previous selection and highlight the current one
        for song_frame in song_frames_container.winfo_children():
            song_frame.config(bg='#1e1e1e')  # Reset the background color of all song frames

        # Highlight the selected song
        selected_song_frame = song_frames_container.winfo_children()[current_song_index]
        selected_song_frame.config(bg='#4CAF50')  # Change color to highlight the selected song

        # Load and play the previous song using pygame
        song_path = os.path.join(default_song_path, previous_song)
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(loops=0)  # Play the previous song

        # Update song list selection to reflect the current song
        for i, song_frame in enumerate(song_frames_container.winfo_children()):
            if i == current_song_index:
                song_frame.config(bg='#4CAF50')  # Highlight the song button for the selected song
            else:
                song_frame.config(bg='#1e1e1e')  # Reset background color for others

    # Frame for playback buttons (pack after the image to avoid overlap)
    button_frame = tk.Frame(playing_window, bg='#2b2b2b')
    button_frame.pack(pady=10, fill=tk.X, padx=20, expand=True)  # Ensure the frame fills horizontally

    # Ensure the frame is divided into 5 columns (one for each button)
    for i in range(5):
        button_frame.grid_columnconfigure(i, weight=1, uniform="equal")

    # Adding buttons to the grid, each in its own column, all centered in the same row
    pause_button = tk.Button(button_frame, text="Pause", command=pause_song)
    style_button(pause_button, color="#ff4d4d", hover_color="#cc0000")  # Red theme
    pause_button.grid(row=0, column=0, padx=25)

    stop_button = tk.Button(button_frame, text="Close", command=stop_song)
    style_button(stop_button, color="#ff4d4d", hover_color="#cc0000")  # Red theme
    stop_button.grid(row=0, column=1, padx=20)

    resume_button = tk.Button(button_frame, text="Resume", command=resume_song)
    style_button(resume_button, color="#ff4d4d", hover_color="#cc0000")  # Red theme
    resume_button.grid(row=0, column=2, padx=20)

    next_button = tk.Button(button_frame, text="Next", command=play_next_song)
    style_button(next_button, color="#ff4d4d", hover_color="#cc0000")  # Green theme
    next_button.grid(row=0, column=3, padx=20)

    previous_button = tk.Button(button_frame, text="Previous", command=play_previous_song)
    style_button(previous_button, color="#ff4d4d", hover_color="#cc0000")  # Green theme
    previous_button.grid(row=0, column=4, padx=20)

    volume_slider = tk.Scale(
        playing_window,
        from_=0,
        to=1,
        orient="horizontal",
        resolution=0.01,
        bg="#2b2b2b",
        fg="white",
        label="Volume",
        highlightthickness=0,
        command= update_volume
    )
    volume_slider.set(0.5)  # Default volume at 50%
    volume_slider.pack(pady=10)

    # Initialize song for playback (Make sure the song path is loaded)
    play_song(song_path)

# Control buttons for main window
control_frame = tk.Frame(main_screen_frame, bg='#2b2b2b')
control_frame.pack(pady=10)

tk.Button(control_frame, text="Add Song", command=add_song, bg='#4CAF50', fg='white', font=font_style).pack(side=tk.LEFT, padx=10)

# Run the app
root.mainloop()