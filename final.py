import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import os
from datetime import datetime
from PIL import Image, ImageTk
import numpy as np
import threading
from pydub import AudioSegment

# Initialize the pygame mixer
pygame.mixer.init()

# App settings
ALBUM_ART_PATH = r"E:\JUW\Sec sem\Data Structures\Project\Tune Flow\img.jpg"  

# Initialize the main app window
root = tk.Tk()
root.title('Music Player')
root.geometry('600x600') # widh X height 
root.config(bg='#2b2b2b')

# Set the font for the entire application
font_style = ("Arial", 12)

# File to save song list
song_list_file = 'song_list.txt'

# Song listbox with a dark background and light text for contrast
song_list = tk.Listbox(root, width=80, height=15, bg='#1e1e1e', fg='white', selectmode=tk.SINGLE, font=font_style)
song_list.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

# Function to save the song list to the file
def save_song_list():
    with open(song_list_file, 'w') as file:
        for i in range(song_list.size()):
            # hr element ko file m likhngy then line break 
            file.write(song_list.get(i) + '\n') 
            
# Function to load the saved song list from the file
def load_song_list():
    if os.path.exists(song_list_file):
        with open(song_list_file, 'r') as file:
            songs = file.readlines()
            # print(songs) 
            for song in songs:
                song_list.insert(tk.END, song.strip())  # Insert into the same Listbox

# Load the song list from the file when the app starts
load_song_list()

# Current song label
current_song_label = tk.Label(root, text="Now Playing: None", bg='#2b2b2b', fg='white', font=("Arial", 14))
current_song_label.pack(pady=10)

# Function to update date and time label
def update_date_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

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

# Function to add songs to the list
def add_song():
    songs = filedialog.askopenfilenames(
        initialdir='E:/JUW/Sec sem/Data Structures/Project/Tune Flow/songs/',
        title='Add Music',
        filetypes=(('MP3 Files', '*.mp3'),)
    )
   # Check karna agar user ne koi song select kiya hai
    if songs:
        # Har selected song ke liye loop
        for song in songs:
            song_name = os.path.basename(song)  # Sirf file ka naam lena, path nahi
            song_add_time = update_date_time()  # Current date aur time 
            # Song ke saath date aur time add karna aur Listbox me dikhana
            song_list.insert(tk.END, f"{song_name}  |  Added on: {song_add_time}")
        # Success message dikhana
        messagebox.showinfo("Success", "Songs added successfully!")
    # Updated list ko save karna file me
    save_song_list()

# remove song
def remove_song():
    # Selected song ka index Listbox se
    selected_song_index = song_list.curselection()
    # Check karna agar koi song select kiya hai
    if selected_song_index:
        # Selected song ka naam
        song_name = song_list.get(selected_song_index)
        # Confirmation popup
        confirm = messagebox.askyesno("Confirm Deletion", f"Do you really want to delete '{song_name}'?")
        if confirm:  
            # Song ko Listbox se delete
            song_list.delete(selected_song_index)
            # Current song label ko reset
            current_song_label.config(text="Now Playing: None")
            # Success message
            messagebox.showinfo("Removed", "Song removed from the list.")
            # Updated list ko file me save
            save_song_list()
    else:
        # Warning agar koi song select nahi kiya
        messagebox.showwarning("Warning", "Select a song to remove.")

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
        num_bars = canvas.winfo_width() // 20  # Canvas ki width ke mutabiq number of bars
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

# Open play window for the selected song
def play_selected_song():
    # Listbox me se selected song ka index lena
    selected_index = song_list.curselection()
    if selected_index:  # Check karna ke kya koi song select kiya gaya hai
        # Selected song ka information lena
        song_info = song_list.get(selected_index[0])  # Listbox se song info lena
        # Song ka naam lena, time info ko alag karna
        song_name = song_info.split("  |")[0]  
        # Song ka full path generate karna
        song_path = os.path.join('E:/JUW/Sec sem/Data Structures/Project/Tune Flow/songs/', song_name)
        try:
            # Pygame mixer se song load aur then play
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
        except pygame.error as e:
            print(f"Error loading song: {e}")
    else:
        messagebox.showwarning("Warning", "Please select a song to play!")

playing_window = None 
# Function to open the song playing window
def open_playing_window(song_index):
    # Agar ek window pehle se open hai, toh use destroy kar do
    global playing_window
    if playing_window:
        playing_window.destroy()

    # Agar song_index invalid ho, toh function se exit
    if song_index < 0 or song_index >= song_list.size():
        return

    playing_window = tk.Toplevel(root)
    playing_window.title("Playing")
    playing_window.geometry("710x450")
    playing_window.config(bg='#2e2e2e')  # Dark theme background

    # Current song ka info aur path
    song_info = song_list.get(song_index)
    current_song = song_info.split('  |  ')[0]  # Sirf song name lena
    song_path = os.path.join('E:/JUW/Sec sem/Data Structures/Project/Tune Flow/songs/', current_song)

    # Current song ka label update karna
    current_song_label.config(text=f"Now Playing: {current_song}")

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
        pygame.mixer.music.stop()  # Stop the music
        playing_window.destroy()  # Close the window

    # Bind the on_close function to the window close event
    playing_window.protocol("WM_DELETE_WINDOW", on_close)

    # Initialize the current song index for next/previous functionality
    current_song_index = song_index

    # Label for song name
    song_name_label = tk.Label(playing_window, text=current_song, bg='#2e2e2e', fg='white', font=font_style)
    song_name_label.pack(pady=10)

    # Function to play the song
    def play_song(song_path):
        try:
            pygame.mixer.music.load(song_path)  # Load the song
            pygame.mixer.music.play(loops=0)  # Play the song
            print(f"Now playing: {song_path}")
        except Exception as e:
            print(f"Error playing song: {e}")

    def stop_song():
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

    def play_next_song():
        # agr song list empty hai tu return krdi ese hi
        if song_list.size() == 0:
            return

        nonlocal current_song_index  # Local variable ko access karne ke liye
        current_song_index += 1  # Current song index ko increment karna
        if current_song_index >= song_list.size():  # Agar list ke last song ke baad chala jaye
            current_song_index = 0  # Index ko first song pe reset kar do

        # Agle song ka naam listbox se lena
        next_song = song_list.get(current_song_index).split('  |  ')[0]
        # UI labels update karna
        current_song_label.config(text=f"Now Playing: {next_song}")  # "Now Playing" ka label
        song_name_label.config(text=next_song)  # Song name label
        
        # Previous selection ko clear karna aur new selection set karna
        song_list.selection_clear(0, tk.END)
        song_list.selection_set(current_song_index)

        # Pygame mixer se next song ko load aur play karna
        pygame.mixer.music.load(os.path.join('E:/JUW/Sec sem/Data Structures/Project/Tune Flow/songs', next_song))
        pygame.mixer.music.play(loops=0)  # Agle song ko play karna bina kisi loop ke

    def play_previous_song():
        nonlocal current_song_index  # Outer function ka current_song_index variable use karna
        current_song_index -= 1  # Current song index ko decrement karna (ek step peeche)
        
        # Agar current song first song pe ho, toh last song pe chala jao
        if current_song_index < 0:
            current_song_index = song_list.size()-1  # Last song ka index set karna
        
        # Previous song ka naam fetch karna aur usay play karna
        previous_song = song_list.get(current_song_index).split('  |  ')[0]
        
        # UI labels update karna
        current_song_label.config(text=f"Now Playing: {previous_song}")  # "Now Playing" ka label update karna
        song_name_label.config(text=previous_song)  # Song name label ko update karna
        
        # Previous selection ko clear karna aur nayi selection set karna
        song_list.selection_clear(0, tk.END)
        song_list.selection_set(current_song_index)

        # Pygame mixer se previous song ko load aur play karna
        pygame.mixer.music.load(os.path.join('E:/JUW/Sec sem/Data Structures/Project/Tune Flow/songs', previous_song))
        pygame.mixer.music.play(loops=0)  # Song ko play karna, aur koi loop nahi hoga

    # Frame for playback buttons (pack after the image to avoid overlap)
    button_frame = tk.Frame(playing_window, bg='#2b2b2b')
    button_frame.pack(pady=10, fill=tk.X, padx=20)  # Ensure the frame fills horizontally

    pause_button = tk.Button(button_frame, text="Pause", command=pause_song)
    style_button(pause_button, color="#ff4d4d", hover_color="#cc0000")  # Red theme
    pause_button.pack(side=tk.LEFT, padx=25)

    stop_button = tk.Button(button_frame, text="Close", command=stop_song)
    style_button(stop_button, color="#ff4d4d", hover_color="#cc0000")  # Red theme
    stop_button.pack(side=tk.LEFT, padx=20)

    resume_button = tk.Button(button_frame, text="Resume", command=resume_song)
    style_button(resume_button, color="#ff4d4d", hover_color="#cc0000")  # Red theme
    resume_button.pack(side=tk.LEFT, padx=20)

    # Next Button
    next_button = tk.Button(button_frame, text="Next", command=play_next_song)
    style_button(next_button, color="#ff4d4d", hover_color="#cc0000")  # Green theme
    next_button.pack(side=tk.LEFT, padx=20)

    # Previous Button
    previous_button = tk.Button(button_frame, text="Previous", command=play_previous_song)
    style_button(previous_button, color="#ff4d4d", hover_color="#cc0000")  # Green theme
    previous_button.pack(side=tk.LEFT, padx=20)

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

# Bind the double-click event to the song list
song_list.bind('<Double-1>', lambda event: open_playing_window(song_list.curselection()[0]))

# Control buttons for main window
control_frame = tk.Frame(root, bg='#2b2b2b')
control_frame.pack(pady=10)

tk.Button(control_frame, text="Add Song", command=add_song, bg='#4CAF50', fg='white', font=font_style).pack(side=tk.LEFT, padx=10)
tk.Button(control_frame, text="Remove Song", command=remove_song, bg='#f44336', fg='white', font=font_style).pack(side=tk.LEFT, padx=10)

# Run the app
root.mainloop()