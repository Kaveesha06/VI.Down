from tkinter import *
from tkinter import ttk, messagebox, filedialog
from yt_dlp import YoutubeDL
import threading
import os
from datetime import datetime

# ---------------------------- Download Function ---------------------------- #
def download_video():
    video_url = url_entry.get()
    save_path = save_entry.get()
    quality = quality_choice.get()
    download_type = download_type_choice.get()

    if not video_url:
        messagebox.showwarning("Input Missing", "Please enter a video URL!")
        return
        
    if not save_path:
        messagebox.showwarning("Input Missing", "Please select a save path!")
        return

    # Update UI
    download_button.config(state="disabled", text="⏳ Downloading...")
    status_label.config(text="Preparing download...", foreground="blue")
    progress_bar['value'] = 0
    progress_text.set("0%")
    window.update()

    def run_download():
        try:
            # Base options
            ydl_opts = {
                "outtmpl": f"{save_path}/%(title)s.%(ext)s",
                "progress_hooks": [progress_hook],
                "noplaylist": True,
                "quiet": True,
                "ignoreerrors": True,
            }
            
            # Format selection based on type and quality
            if download_type == "Video":
                if quality == "Best Quality":
                    ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
                else:
                    ydl_opts["format"] = f"bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best[ext=mp4]"
                ydl_opts["merge_output_format"] = "mp4"
            else:  # Audio only
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]

            with YoutubeDL(ydl_opts) as ydl:
                # Get video info first for better progress tracking
                info = ydl.extract_info(video_url, download=False)
                video_title = info.get('title', 'Unknown')
                
                # Update UI with video title
                window.after(0, lambda: status_label.config(
                    text=f"Downloading: {video_title[:50]}..." if len(video_title) > 50 else f"Downloading: {video_title}"
                ))
                
                # Start download
                ydl.download([video_url])

            window.after(0, lambda: status_label.config(
                text="✅ Download Completed!", 
                foreground="green"
            ))
            
        except Exception as e:
            error_msg = str(e)
            window.after(0, lambda: status_label.config(
                text=f"❌ Error: {error_msg}", 
                foreground="red"
            ))
        finally:
            window.after(0, lambda: download_button.config(
                state="normal", 
                text="⬇️ Download"
            ))

    # Run download in thread
    threading.Thread(target=run_download, daemon=True).start()

# ---------------------------- Improved Progress Bar Hook ---------------------------- #
def progress_hook(d):
    if d['status'] == 'downloading':
        # Calculate percentage
        if d.get('total_bytes'):
            percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
        elif d.get('total_bytes_estimate'):
            percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
        else:
            # Fallback to string parsing
            percent_str = d.get('_percent_str', '0%').strip()
            try:
                percent = float(percent_str.replace('%', ''))
            except:
                percent = 0

        # Update progress bar and text
        window.after(0, lambda: update_progress(percent, d))
        
    elif d['status'] == 'finished':
        window.after(0, lambda: progress_text.set("Processing..."))

def update_progress(percent, d):
    progress_bar['value'] = percent
    progress_text.set(f"{percent:.1f}%")
    
    # Show download speed and ETA if available
    speed = d.get('_speed_str', 'N/A')
    eta = d.get('_eta_str', 'N/A')
    
    if speed != 'N/A' and eta != 'N/A':
        status_label.config(text=f"Downloading... {speed} | ETA: {eta}")
    
    window.update_idletasks()

# ---------------------------- Browse Folder ---------------------------- #
def browse_folder():
    path = filedialog.askdirectory()
    if path:
        save_entry.delete(0, END)
        save_entry.insert(0, path)

# ---------------------------- Modern UI Setup ---------------------------- #
window = Tk()
window.title("🎬 Advanced Video Downloader")
window.geometry("580x500")
window.config(bg="#2C2C2C")
window.resizable(True, True)

# Style configuration
style = ttk.Style()
style.theme_use('clam')
style.configure("TFrame", background="#2C2C2C")
style.configure("TLabel", background="#2C2C2C", foreground="white")
style.configure("TButton", background="#00A86B", foreground="white")
style.configure("TEntry", fieldbackground="#404040", foreground="white")
style.configure("TCombobox", fieldbackground="#404040", foreground="white")
style.configure("Horizontal.TProgressbar", 
                background="#00A86B", 
                troughcolor="#404040",
                bordercolor="#2C2C2C",
                lightcolor="#00A86B",
                darkcolor="#00A86B")

# Main container
main_frame = ttk.Frame(window, padding="20")
main_frame.pack(fill=BOTH, expand=True)

# Header
header_frame = ttk.Frame(main_frame)
header_frame.pack(fill=X, pady=(0, 20))

Label(header_frame, text="🎬 Advanced Video Downloader", 
      fg="white", bg="#2C2C2C", font=("Segoe UI", 18, "bold")).pack()

Label(header_frame, text="Download videos and audio from various platforms", 
      fg="#CCCCCC", bg="#2C2C2C", font=("Segoe UI", 10)).pack(pady=(5, 0))

# Input frame
input_frame = ttk.Frame(main_frame)
input_frame.pack(fill=X, pady=10)

# URL input
Label(input_frame, text="Video URL:", fg="white", bg="#2C2C2C", 
      font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=W, pady=(0, 5))
url_entry = Entry(input_frame, width=60, bg="#404040", fg="white", 
                 insertbackground="white", font=("Segoe UI", 10))
url_entry.grid(row=1, column=0, columnspan=2, sticky=EW, pady=(0, 10))

# Save path with browse button
path_frame = ttk.Frame(input_frame)
path_frame.grid(row=2, column=0, columnspan=2, sticky=EW, pady=(0, 10))
Label(path_frame, text="Save Location:", fg="white", bg="#2C2C2C", 
      font=("Segoe UI", 10, "bold")).pack(anchor=W)
path_input_frame = ttk.Frame(path_frame)
path_input_frame.pack(fill=X, pady=(5, 0))

save_entry = Entry(path_input_frame, width=50, bg="#404040", fg="white", 
                  insertbackground="white", font=("Segoe UI", 10))
save_entry.pack(side=LEFT, fill=X, expand=True)
save_entry.insert(0, os.path.expanduser("~/Downloads"))

browse_btn = Button(path_input_frame, text="📁 Browse", command=browse_folder,
                   bg="#555555", fg="white", font=("Segoe UI", 9), relief="flat")
browse_btn.pack(side=RIGHT, padx=(5, 0))

# Options frame
options_frame = ttk.Frame(input_frame)
options_frame.grid(row=3, column=0, columnspan=2, sticky=EW, pady=10)

# Download type
Label(options_frame, text="Download Type:", fg="white", bg="#2C2C2C", 
      font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=W)
download_type_choice = ttk.Combobox(options_frame, 
                                   values=["Video", "Audio"], 
                                   width=15, state="readonly")
download_type_choice.set("Video")
download_type_choice.grid(row=1, column=0, sticky=W, pady=(5, 0))

# Quality selection
Label(options_frame, text="Quality:", fg="white", bg="#2C2C2C", 
      font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky=W, padx=(20, 0))
quality_choice = ttk.Combobox(options_frame, 
                             values=["Best Quality", "1080", "720", "480", "360"], 
                             width=15, state="readonly")
quality_choice.set("720")
quality_choice.grid(row=1, column=1, sticky=W, padx=(20, 0), pady=(5, 0))

# Download button
download_button = Button(main_frame, text="⬇️ Download", command=download_video,
                        bg="#00A86B", fg="white", font=("Segoe UI", 12, "bold"),
                        relief="flat", padx=20, pady=10, cursor="hand2")
download_button.pack(pady=20)

# Progress frame
progress_frame = ttk.Frame(main_frame)
progress_frame.pack(fill=X, pady=10)

# Progress bar with text
progress_text = StringVar(value="0%")
progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate')
progress_bar.pack(fill=X, pady=(0, 5))

progress_label = Label(progress_frame, textvariable=progress_text, 
                      fg="white", bg="#2C2C2C", font=("Segoe UI", 10))
progress_label.pack()

# Status label
status_label = Label(main_frame, text="Ready to download", 
                    fg="#CCCCCC", bg="#2C2C2C", font=("Segoe UI", 10))
status_label.pack(pady=10)

# Configure grid weights
input_frame.columnconfigure(0, weight=1)
window.columnconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)

window.mainloop()