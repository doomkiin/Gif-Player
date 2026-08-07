import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
from pathlib import Path


"""
While loops are illegal: While loops inside root.mainloop() will cause the window to pause for the length of the while loop.
"""

class AnimatedGIF(tk.Label):
    def __init__(self, master, gif_paths: list[str], resize=None, *args, **kwargs):
        #Passing additional tk.Label class argumets up to parent and declaring parameters into variables
        super().__init__(master, *args, **kwargs)

        self.frames = []
        self.durations = []
        self.playlist = gif_paths
        self.resize = resize

        #animation playback state tracking and timer variables
        self.path_gen = None
        self.current_frame = 0
        self.is_running = False
        self.timer_id = None

    def _load_gif(self, path):
        """Extract frames and frame durations using Pillow."""
        self.frames.clear()
        self.durations.clear()
        try:
            with Image.open(path) as img:
                for frame in ImageSequence.Iterator(img):
                    # Convert to RGBA to preserve color accuracy and transparency
                    converted_frame = frame.convert("RGBA")

                    #Checks to see if resize is anything other than None
                    #if self.resize:
                    converted_frame = converted_frame.resize(self.resize, Image.Resampling.LANCZOS)#<- high-quality downsampling/upsampling algorithm
                    
                    # Convert Pillow frame to Tkinter-compatible PhotoImage and append to frames list
                    photo = ImageTk.PhotoImage(converted_frame)
                    self.frames.append(photo)
                    
                    # Get duration metadata (defaults to 100ms if not specified in GIF)
                    duration = frame.info.get("duration", 100)
                    # Fallback for broken metadata (0ms duration)
                    self.durations.append(duration if duration > 0 else 100)

        except Exception as e:
            print(f"Error loading GIF or frame corrupted: {e}")
            #If corruption caused partial loading, clear out broken frame data
            #!!!Implement some logic to display the gif name that is at fault.
        
        self.next_frame()

    def _path_generator(self):
        for path in self.playlist:
            yield str(path)

    def _load_next_gif(self):
        """Pull the next path from the persistent generator."""
        # Create generator if it doesn't exist yet
        if self.path_gen is None:
            self.path_gen = self._path_generator()

        try:
            next_path = next(self.path_gen)
        except StopIteration:
            # Playlist finished: recreate generator to loop back to the first GIF
            self.path_gen = self._path_generator()
            next_path = next(self.path_gen)

        self.current_frame = 0
        self._load_gif(next_path)

    #animation "engine" | tkinter event schedular loop
    def next_frame(self):

        #Start and stop switch check, the loop will stop if ever self.is_running is ever False
        if not self.is_running or not self.frames:
            return
    
        # Advance frame counter
        self.current_frame += 1

        # LATCH CONDITION: Reached end of current GIF -> load next GIF
        if self.current_frame >= len(self.frames):
            self._load_next_gif()
        else:
            # Render current frame
            self.config(image=self.frames[self.current_frame])
            delay = self.durations[self.current_frame]

            # Schedule next frame timer
            self.timer_id = self.after(delay, self.next_frame)

    def start(self):
        """Start playing the animation."""
        if not self.is_running:
            self.is_running = True
        
        #ensure there are no latent background timers caused by after()
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

        self._load_next_gif()

    def stop(self):
        """Pause the animation."""
        self.is_running = False
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

#Controle loop: _list_loop > _plath_generator > change_gif > _load_gif > start > next_frame

#initialize tkinter window
root = tk.Tk()
root.title("PIL + Tkinter GIF Player")
root.geometry("400x400")

#gif label
playlist = [str(file.resolve()) for file in Path('/home/redacted/Documents/Python/Projects/Gif-Player/Gifs').rglob('*') if file.is_file()]
print(*playlist, sep="\n")
gif_label = AnimatedGIF(root, gif_paths=playlist, resize=(300, 300))
gif_label.pack(expand=True, fill="both", padx=20, pady=20)
gif_label.start()

root.mainloop()