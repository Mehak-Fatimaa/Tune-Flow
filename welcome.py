import tkinter as tk
import winsound
from PIL import Image, ImageTk, ImageEnhance, ImageDraw

def show_welcome_page(root, switch_to_main_screen):
    LOGO_IMG = "images/main_logo.jpg"
    BG_IMG = "images/main_img.jpg"

    # Create a Canvas widget for the background and elements
    canvas = tk.Canvas(root, width=800, height=600, bg="black")
    canvas.pack(fill="both", expand=True)

    # Load and adjust the background image
    bg_image_path = BG_IMG
    bg_image = Image.open(bg_image_path).resize((800, 600), Image.Resampling.LANCZOS)

    # Convert image to RGB mode if necessary and adjust brightness
    if bg_image.mode != 'RGB':
        bg_image = bg_image.convert('RGB')

    enhancer = ImageEnhance.Brightness(bg_image)
    bg_image = enhancer.enhance(0.7)  # Darker background for better contrast

    # Convert the image to a format Tkinter can use
    bg_image = ImageTk.PhotoImage(bg_image)

    # Keep a reference to the image to prevent garbage collection
    canvas.bg_image = bg_image
    canvas.create_image(400, 300, image=bg_image, anchor="center")

    # Load and create a circular logo
    logo_image_path = LOGO_IMG
    logo_image = Image.open(logo_image_path).resize((150, 150), Image.Resampling.LANCZOS)

    # Convert logo to RGB mode if necessary
    if logo_image.mode != 'RGB':
        logo_image = logo_image.convert('RGB')

    # Create a circular mask for the logo
    mask = Image.new("L", logo_image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, logo_image.size[0], logo_image.size[1]), fill=255)

    # Apply the mask to the logo image to create a circular shape
    logo_image.putalpha(mask)

    # Add a subtle shadow effect to the logo
    shadow_offset = 5
    shadow = Image.new("RGBA", (logo_image.size[0] + shadow_offset * 2, logo_image.size[1] + shadow_offset * 2), (0, 0, 0, 0))
    shadow.paste(logo_image, (shadow_offset, shadow_offset))
    shadow = ImageEnhance.Brightness(shadow).enhance(0.3)  # Darker shadow
    shadow = ImageTk.PhotoImage(shadow)

    # Convert the logo image to a format Tkinter can use
    logo_image = ImageTk.PhotoImage(logo_image)

    # Keep references to the images
    canvas.shadow_image = shadow
    canvas.logo_image = logo_image

    # Add the shadow first, then the logo with animation
    canvas.create_image(400, 200, image=shadow, anchor="center", tags="logo")
    canvas.create_image(400, 200, image=logo_image, anchor="center", tags="logo")

    # Create a progress bar for loading
    progress_bar_bg = canvas.create_rectangle(200, 400, 600, 420, outline="white", fill="gray", tags="progress_bar_bg")
    progress_bar = canvas.create_rectangle(200, 400, 200, 420, outline="", fill="green", tags="progress_bar")

    # Create a loading animation that blinks dots smoothly and updates the progress bar
    loading_text = canvas.create_text(400, 300, text="Loading...", font=("Freestyle Script", 30, "bold"), fill="gray")

    # Local variable for dots count
    loading_dots = 0

    def update_loading(dots_count=0):
        nonlocal loading_dots  # Declare to modify outer variable
        loading_dots = dots_count  # Update dots count

        # Update the loading message with blinking dots
        dots = "." * (loading_dots % 4)
        canvas.itemconfig(loading_text, text=f"Loading{dots}")
        loading_dots += 1

        if loading_dots <= 40:  # Run for approximately 10 seconds
            canvas.after(250, lambda: update_loading(loading_dots))  # Pass updated count
        else:
            canvas.delete(loading_text)
            canvas.delete("progress_bar_bg")
            canvas.delete("progress_bar")
            show_welcome_message()

        # Updated Smooth Progress Bar Fill
        percentage = min((loading_dots * 100) // 40, 100)  # Clamp percentage to 100
        canvas.coords(progress_bar, 200, 400, 200 + (percentage * 4), 420)

    # Display "Welcome to Tuneflow" word by word
    def show_welcome_message():
        welcome_message = "Welcome to Tuneflow"
        message_index = 0

        def display_message():
            nonlocal message_index
            if message_index < len(welcome_message):
                current_message = welcome_message[:message_index + 1]
                canvas.delete("welcome_text")
                canvas.create_text(400, 320, text=current_message, font=("Freestyle Script", 30, "bold"), fill="Sky Blue", tags="welcome_text")
                message_index += 1
                canvas.after(100, display_message)  # Delay between each character
            else:
                show_button_after_message()

        display_message()

    # Function to show the button after the message is displayed
    def show_button_after_message():
        global button_text
        button_text = canvas.create_text(400, 350, text="Get Started", font=("Freestyle Script", 24, "bold"), fill="Purple", tags="button")
        canvas.tag_bind("button", "<Button-1>", on_click)

    # Interactive button with hover and click effects
    def on_click(event):
        print("Button Clicked")
        play_click_sound()  # Play sound on button click
        canvas.itemconfig(button_text, fill="green")  # Change color to green after click
        canvas.destroy()  # Clear the canvas
        switch_to_main_screen()  # Call the function to switch frames

    # Sound effect for button click
    def play_click_sound():
        winsound.PlaySound('click_sound.wav', winsound.SND_ASYNC)

    # Start the smoother loading animation
    canvas.after(500, lambda: update_loading(loading_dots))
