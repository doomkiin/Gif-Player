import tkinter as tk
from PIL import Image, ImageTk, ImageSequence

class AnimatedGIF(tk.Label):
    def __init__(self, master, gif_path, resize=None, *args, **kwargs):
        #Passing additional tk.Label class argumets up to parent and declaring parameters into variables
        super().__init__(master, *args, **kwargs)
        self.gif_path = gif_path
        self.resize = resize

        #Lists to store gif data to reduce constant processing on gif loops, and call private method
        self.frames = []
        self.durations = []
        self._load_gif()

        #animation playback state tracking and timer variables
        self.current_frame = 0
        self.is_running = False
        self.timer_id = None
        
        # Display the first frame immediately and call start method
        if self.frames: #insures list isn't empty, corruption check, this can probably be removed since error handlings happens in _load_gif
            self.config(image=self.frames[0])
            self.start()

    def _load_gif(self):
        """Extract frames and frame durations using Pillow."""
        try:
            with Image.open(self.gif_path) as img:
                for frame in ImageSequence.Iterator(img):
                    # Convert to RGBA to preserve color accuracy and transparency
                    converted_frame = frame.convert("RGBA")

                    #Checks to see if resize is anything other than None
                    if self.resize:#Image.Resampling.LANCZOS is a high-quality downsampling/upsampling algorithm
                        converted_frame = converted_frame.resize(self.resize, Image.Resampling.LANCZOS)
                    
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
            self.frames.clear()
            self.durations.clear()

    #animation "engine" | tkinter event schedular loop
    def next_frame(self):
        #Start and stop switch check, the loop will stop if ever self.is_running is ever False
        if not self.is_running:
            return
    
        '''
        If (self.current_frame + 1) > len(self.frames) then self.current_frame = (self.current_frame + 1)
        If (self.current_frame + 1) = len(self.frames) then self.current_frame will equal 0
        '''#Core loop logic
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.config(image=self.frames[self.current_frame])
        
        # Schedule next frame update based on individual frame delay
        delay = self.durations[self.current_frame]
        self.timer_id = self.after(delay, self.next_frame)

    def change_gif(self, new_path):
        #load up new path
        #self.stop()
        self.gif_path = new_path

        #clear out frames and durations so they aren't just appended on
        self.frames.clear()
        self.durations.clear()

        #load the frames and durations into their appropirate lists and start
        self._load_gif()
        #self.start()

    def start(self):
        """Start playing the animation."""
        if not self.is_running:
            #ensure there are no latent background timers caused by after()
            if self.timer_id:
                self.after_cancel(self.timer_id)
                self.timer_id = None

            self.is_running = True
            self.next_frame()

    def stop(self):
        """Pause the animation."""
        self.is_running = False

#initialize tkinter window
root = tk.Tk()
root.title("PIL + Tkinter GIF Player")
root.geometry("400x400")

gif_label = AnimatedGIF(root, gif_path="Gifs/hug.gif", resize=(300, 300))
gif_label.pack(expand=True, fill="both", padx=20, pady=20)



if input() == "change":
    gif_label.change_gif("Gifs/ZeroTwo.gif")

root.mainloop()