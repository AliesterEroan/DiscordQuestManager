# Dummy Window Implementation Notes

## Current Issues
- Timer not updating
- Percentage not updating
- Cat animation not showing correctly (showing controller placeholder)

## How Dummy Window Works

### Initialization Flow
1. `__init__()` is called with game_exe_name, game_name, duration_minutes, theme_colors, cat_selection
2. Sets up:
   - `self.duration_seconds = duration_minutes * 60`
   - `self.elapsed_seconds = 0`
   - `self.is_complete = False`
3. Calls:
   - `_register_dummy()` - registers fake exe with DummyRegistry
   - `_setup_window()` - creates Tkinter window
   - `_setup_icon()` - sets window icon
   - `_setup_content()` - creates UI elements
4. **CRITICAL**: Timer thread start is deferred with `self.root.after(100, self._start_timer_thread)`
5. Shows window with `self.root.mainloop()`

### Timer System

#### Original Implementation (BROKEN)
```python
# In __init__:
threading.Thread(target=self._run_timer, daemon=True).start()

# Problem: Thread starts before mainloop, so UI updates don't work
```

#### Fixed Implementation
```python
# In __init__:
self.root.after(100, self._start_timer_thread)  # Start after window shown

# New method:
def _start_timer_thread(self):
    threading.Thread(target=self._run_timer, daemon=True).start()

def _run_timer(self):
    while self.elapsed_seconds < self.duration_seconds:
        time.sleep(1)
        self.elapsed_seconds += 1
        self.root.after(0, self._update_progress)  # Schedule UI update
    self.root.after(0, self._on_complete)
```

### Progress Update System

#### `_update_progress()` Method
```python
def _update_progress(self):
    if self.is_complete:
        return
    
    # Calculate percentage
    percentage = (self.elapsed_seconds / self.duration_seconds) * 100
    
    # Update progress bar canvas
    canvas_width = self.progress_bar.winfo_width()
    if canvas_width <= 1:
        canvas_width = 300
    progress_width = (percentage / 100) * canvas_width
    self.progress_bar.coords(self.progress_fill, 0, 0, progress_width, 16)
    
    # Update colors (REMOVED - was causing issues)
    # self.root.config(bg=self.colors["base"])
    # ... other color updates
    
    # Update telemetry label
    elapsed_min = int(self.elapsed_seconds // 60)
    elapsed_sec = int(self.elapsed_seconds % 60)
    total_min = int(self.duration_seconds // 60)
    total_sec = int(self.duration_seconds % 60)
    self.telemetry_label.config(
        text=f"{elapsed_min:02d}:{elapsed_sec:02d} / {total_min:02d}:{total_sec:02d} • {int(percentage)}%"
    )
```

### Cat Animation System

#### Original Implementation (BROKEN)
```python
def _get_cat_animation(self, state: str):
    # Listed files in directory and returned first GIF found
    # Problem: Always returned same animation regardless of cat selection
```

#### Fixed Implementation
```python
def _get_cat_animation(self, state: str):
    animations = ["run", "itch", "walk", "stretch", "sleep"]
    random.shuffle(animations)
    
    for animation in animations:
        animation_dir = os.path.join(base_dir, "assets", "animations", "cat", animation, "big")
        
        # Special case for sleep (different structure)
        if animation == "sleep":
            animation_dir = os.path.join(base_dir, "assets", "animations", "cat", "sleep", "1")
        
        if os.path.exists(animation_dir):
            # Special case for stretch: file is "Stretching" not "Stretch"
            if animation == "stretch":
                cat_file = f"{self.cat_selection}-Stretching_b.gif"
            elif animation == "sleep":
                cat_file = f"{self.cat_selection}-Sleeping1.png"
            else:
                cat_file = f"{self.cat_selection}-{animation.capitalize()}_b.gif"
            
            animation_path = os.path.join(animation_dir, cat_file)
            if os.path.exists(animation_path):
                return animation_path
    
    return None
```

### Theme Color System

#### Original Implementation (BROKEN)
```python
def update_colors(self, colors):
    self.colors = colors
    # Only updated specific widgets with hardcoded color names
```

#### Fixed Implementation
```python
def update_colors(self, colors):
    self.colors = colors
    
    # Comprehensive color mapping for ALL mocha and latte colors
    bg_map = {
        "#1e1e2e": colors["base"],      # Mocha base
        "#181825": colors["mantle"],    # Mocha mantle
        "#313244": colors["surface"],   # Mocha surface
        "#45475a": colors["surface0"],  # Mocha surface0
        "#585b70": colors["surface1"],  # Mocha surface1
        "#6c7086": colors["overlay0"],  # Mocha overlay0
        "#7f849c": colors["overlay1"],  # Mocha overlay1
        "#9399b2": colors["overlay2"],  # Mocha overlay2
        "#eff1f5": colors["base"],      # Latte base
        "#e6e9ef": colors["mantle"],    # Latte mantle
        # ... more latte colors
    }
    
    fg_map = {
        "#cdd6f4": colors["text"],      # Mocha text
        "#a6adc8": colors["subtext0"],  # Mocha subtext0
        "#bac2de": colors["subtext1"],  # Mocha subtext1
        # ... all accent colors for both themes
    }
    
    # Recursive widget update
    def update_widget(widget):
        if hasattr(widget, 'config'):
            # Update background
            current_bg = widget.cget("bg")
            if current_bg in bg_map:
                widget.config(bg=bg_map[current_bg])
            
            # Update foreground
            current_fg = widget.cget("fg")
            if current_fg and current_fg != "" and current_fg in fg_map:
                widget.config(fg=fg_map[current_fg])
        
        for child in widget.winfo_children():
            update_widget(child)
    
    # Update specific widgets directly
    self.root.config(bg=colors["base"])
    # ... all other widgets
    
    # Recursively update all children
    update_widget(self.root)
```

## What I Changed

### 1. Timer Thread Start
- **Before**: Started thread immediately in `__init__`
- **After**: Deferred with `root.after(100, self._start_timer_thread)`
- **Reason**: Thread was starting before mainloop, so UI updates didn't work

### 2. Cat Animation File Selection
- **Before**: Listed directory and returned first GIF found
- **After**: Randomly selects from specific animations for the selected cat
- **Reason**: Was showing same animation regardless of cat selection
- **Special cases**: 
  - "stretch" → "Stretching_b.gif"
  - "sleep" → "Sleeping1.png" in different directory

### 3. Theme Color Mapping
- **Before**: Only updated specific widgets with hardcoded colors
- **After**: Comprehensive mapping of ALL mocha and latte colors with recursive widget update
- **Reason**: Colors were getting stuck when changing themes

### 4. Removed Color Updates from Progress Loop
- **Before**: Updated all widget colors on every timer tick
- **After**: Removed color updates from `_update_progress()`
- **Reason**: Was redundant and potentially causing performance issues

## Current Status

### Working
- Timer thread starts after window is shown
- Cat animation file selection is correct
- Theme color mapping is comprehensive

### Potentially Still Broken
- Timer may still not be updating (need to verify if thread is actually running)
- Progress bar may not be updating (need to verify if canvas coords are working)
- Cat animation may still show placeholder (need to verify file paths exist)

## Debug Output Added
```python
print(f"[DummyWindow] Timer started: duration={self.duration_seconds}s")
print(f"[DummyWindow] Timer tick: {self.elapsed_seconds}/{self.duration_seconds}s")
print(f"[DummyWindow] _update_progress called: elapsed={self.elapsed_seconds}, duration={self.duration_seconds}")
print(f"[DummyWindow] Calculated percentage: {percentage}%")
print(f"[DummyWindow] Canvas width: {canvas_width}")
print(f"[DummyWindow] Progress width: {progress_width}")
print(f"[DummyWindow] Found animation: {animation_path}")
print(f"[DummyWindow] No animation found for cat {self.cat_selection}")
```

## What to Check

1. **Timer Thread**: Is the thread actually starting? Check debug output for "Timer started"
2. **Progress Updates**: Is `_update_progress()` being called? Check debug output
3. **Canvas Width**: Is canvas width > 1? If not, progress bar won't show
4. **Animation Files**: Do the animation files actually exist at the expected paths?
5. **Theme Colors**: Are colors actually changing when theme is changed?

## Possible Issues

1. **Timer not running**: Thread might not be starting due to threading issues
2. **Canvas not updating**: Canvas might need to be updated differently on Windows
3. **Animation files missing**: File paths might be wrong or files don't exist
4. **Color mapping incomplete**: Some widgets might have colors not in the mapping
