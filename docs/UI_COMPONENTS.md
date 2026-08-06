# UI Components Reference List

**Location:** `c:\Users\user\OneDrive\Desktop\DiscordQuestManager\version 1.1.0`

## Main Window

### Window Dimensions
- **Main Window:** 1000 x 650 pixels
- **Sidebar Width:** 250 pixels
- **Main Panel:** Remaining width (750px)

---

## Sidebar Components

### Header Card
- **Container:** Frame with padx=12, pady=15
- **Background:** surface color
- **Padding:** 10px (outer), 12px/15px (inner)

#### App Icon
- **Size:** Default app icon size
- **Location:** Left side of header
- **Padding:** Right 10px

#### Title Label
- **Text:** "Discord Quest\nManager"
- **Font:** Press Start 2P, size 7
- **Color:** pink
- **Padding:** Left 6px

#### Status Label
- **Text:** "● DATABASE READY"
- **Font:** status (Press Start 2P, size 6, italic)
- **Color:** green
- **Alignment:** anchor="w"

#### Game Count Label
- **Text:** "Connecting..." / "X,XXX registered"
- **Font:** Segoe UI, size 8
- **Color:** subtext0
- **Padding:** Bottom 15px

---

### Queue Card
- **Container:** Frame with padx=15, pady=15
- **Background:** surface color
- **Padding:** 10px (outer), 15px (inner)

#### Queue Label
- **Text:** "SELECTED: 0 Games Queued"
- **Font:** badge (Press Start 2P, size 6)
- **Color:** text
- **Padding:** Left 6px, right 5px

---

### Favorites Card
- **Container:** Frame with padx=15, pady=15
- **Background:** surface color
- **Padding:** 10px (outer), 15px (inner)

#### Favorites Header
- **Icon:** bookmark.png (16x16)
- **Text:** " Favorites"
- **Font:** label (Press Start 2P, size 7, bold)
- **Color:** text
- **Icon Padding:** Right 5px

#### Favorites Listbox
- **Height:** 5 items
- **Font:** listbox (Press Start 2P, size 6)
- **Background:** surface0
- **Text Color:** text
- **Selection:** mauve background, base foreground
- **Border:** flat, bd=0, highlightthickness=0

---

### Recent Card
- **Container:** Frame with padx=15, pady=15
- **Background:** surface color
- **Padding:** 10px (outer), 15px (inner)

#### Recent Header
- **Text:** "⏱ Recent"
- **Font:** label (Press Start 2P, size 7, bold)
- **Color:** text
- **Padding:** Bottom 10px

#### Recent Listbox
- **Height:** 5 items
- **Font:** listbox (Press Start 2P, size 6)
- **Background:** surface0
- **Text Color:** text
- **Selection:** mauve background, base foreground
- **Border:** flat, bd=0, highlightthickness=0

---

### Button Container
- **Container:** Frame with background=mantle
- **Location:** Bottom of sidebar
- **Padding:** 10px (sides), 20px (bottom), 10px (top)

#### Clean Dummies Button (PixelButton)
- **Width:** 200 pixels
- **Height:** 45 pixels
- **Icon:** trash.png (18x18)
- **Text:** "Clean Dummies"
- **Font:** Courier, size 10, bold
- **Background:** surface0
- **Text Color:** red
- **Padding:** Bottom 5px

#### Settings Button (PixelButton)
- **Width:** 200 pixels
- **Height:** 45 pixels
- **Icon:** cog.png (18x18)
- **Text:** "Settings"
- **Font:** Courier, size 10, bold
- **Background:** surface0
- **Text Color:** text

---

## Main Panel Components

### Toolbar
- **Container:** Frame with background=mantle, padx=15, pady=10
- **Layout:** fill="x"

#### Search Frame
- **Background:** surface0
- **Layout:** fill="x", expand=True
- **Padding:** Right 10px

#### Search Icon
- **Size:** search.png (16x16)
- **Padding:** Left 8px

#### Search Entry
- **Font:** entry (Press Start 2P, size 7)
- **Background:** surface0
- **Text Color:** text
- **Cursor:** green
- **Padding:** Left/Right 8px, ipady=5
- **Border:** flat, bd=0, highlightthickness=0

---

### Target Frame
- **Container:** Frame with background=base, padx=15, pady=10
- **Layout:** fill="both", expand=True

#### Target Header
- **Background:** base
- **Layout:** fill="x", bottom padding 10px

##### Title Label
- **Text:** "TARGET EXECUTABLES"
- **Font:** card_title (Press Start 2P, size 7, bold)
- **Color:** pink

##### Selected Count Label
- **Text:** "0 Selected"
- **Font:** status (Press Start 2P, size 6, italic)
- **Color:** subtext0

---

### Executables Container
- **Background:** mantle
- **Border:** bd=2, highlightbackground=mauve, highlightthickness=2
- **Layout:** fill="both", expand=True

#### Empty State
- **Background:** mantle
- **Layout:** fill="both", expand=True

##### Folder Icon
- **Size:** folder.png (48x48)
- **Padding:** Top 20px

##### Empty State Title
- **Text:** "NO GAMES ADDED"
- **Font:** empty_state (Press Start 2P, size 7, bold)
- **Color:** text
- **Padding:** Bottom 5px

##### Empty State Subtitle
- **Text:** "Type in the search bar above to select and queue game executables."
- **Font:** body_small (Press Start 2P, size 6)
- **Color:** subtext0
- **Wrap Length:** 380px

---

### Queue Items
- **Container:** Frame with background=surface0
- **Padding:** 5px (sides), 2px (top/bottom)
- **Layout:** fill="x"

#### Checkbox
- **Background:** surface0
- **Selection Color:** surface0
- **Padding:** Left 5px

#### Game Info Label
- **Text:** "Game Name → exe_name"
- **Font:** entry (Press Start 2P, size 7)
- **Color:** text
- **Padding:** Left 5px, fill="x", expand=True

#### Favorite Button
- **Icon:** bookmark.png (16x16)
- **Background:** surface0
- **Padding:** Right 2px

#### Remove Button
- **Icon:** close.png (16x16)
- **Background:** surface0
- **Padding:** Right 2px

---

### Footer
- **Container:** Frame with background=mantle, padx=15, pady=15
- **Layout:** fill="x", side="bottom"

#### Timer Label
- **Text:** "15:00"
- **Font:** pixel_timer (Press Start 2P, size 13)
- **Color:** green
- **Padding:** Bottom 10px

#### Quest Count Label
- **Text:** "0 QUESTS READY"
- **Font:** status (Press Start 2P, size 6, italic)
- **Color:** subtext0
- **Padding:** Bottom 10px

#### Start/Stop Button (PixelButton)
- **Width:** 220 pixels
- **Height:** 45 pixels
- **Icon:** play.png / stop.png (18x18)
- **Text:** "Start Quests (0)" / "Stop All Quests"
- **Font:** Courier, size 10, bold
- **Background:** green (start) / red (stop)
- **Text Color:** base
- **Padding:** Bottom 10px

---

### Progress Bar
- **Container:** Frame with background=mantle
- **Layout:** fill="x", top padding 10px

#### Progress Canvas
- **Height:** 16 pixels
- **Background:** mantle
- **Border:** flat, highlightthickness=0

#### Progress Fill
- **Height:** 16 pixels
- **Color:** green
- **Initial Width:** 0px

---

## Settings Dialog

### Window Dimensions
- **Settings Window:** 400 x 450 pixels
- **Resizable:** False

### Notebook (Tabs)
- **Padding:** 10px (sides), 10px (top/bottom)
- **Layout:** fill="both", expand=True

---

### Theme Tab

#### Theme Label
- **Text:** "Theme:"
- **Font:** label (Press Start 2P, size 7, bold)
- **Color:** text
- **Padding:** Left 10px, top 10px, bottom 5px

#### Theme Frame
- **Background:** base
- **Padding:** Left 10px, top/bottom 5px

##### Dark Theme Radio
- **Icon:** full-moon.png (16x16)
- **Padding:** Right 5px
- **Text:** "Catppuccin Mocha (Dark)"
- **Font:** about_text (Press Start 2P, size 6)
- **Color:** text
- **Background:** base
- **Selection:** surface0

##### Light Theme Radio
- **Icon:** sun.png (16x16)
- **Padding:** Right 5px
- **Text:** "Catppuccin Latte (Light)"
- **Font:** about_text (Press Start 2P, size 6)
- **Color:** text
- **Background:** base
- **Selection:** surface0

---

### Quest Tab

#### Duration Label
- **Text:** "Quest Duration (minutes):"
- **Font:** label (Press Start 2P, size 7, bold)
- **Color:** text
- **Padding:** Left 10px, top 10px, bottom 5px

#### Preset Frame
- **Background:** base
- **Padding:** Left 10px, top/bottom 5px

##### Preset Buttons
- **Text:** "5", "10", "15", "30"
- **Font:** button_small (Press Start 2P, size 6, bold)
- **Background:** surface1
- **Text Color:** text
- **Width:** 5 characters
- **Padding:** Left/right 2px

##### Duration Entry
- **Font:** entry (Press Start 2P, size 7)
- **Background:** surface0
- **Text Color:** text
- **Cursor:** white
- **Width:** 8 characters
- **Padding:** Left 5px

#### Remember Duration Checkbox
- **Text:** "Remember last used duration"
- **Font:** about_text (Press Start 2P, size 6)
- **Color:** text
- **Background:** base
- **Selection:** surface0
- **Padding:** Left 10px, top/bottom 10px

---

### System Tab
(Components vary based on settings)

---

### Updates Tab
(Components vary based on settings)

---

### Save Button
- **Text:** "Save Settings"
- **Font:** button (Press Start 2P, size 7)
- **Background:** green
- **Text Color:** mantle
- **Padding:** pady=5, padx=20
- **Top Padding:** 10px

---

## Font Reference

| Font Name | Size | Style | Usage |
|-----------|------|-------|-------|
| Press Start 2P | 7 | - | App title, section titles, buttons |
| Press Start 2P | 6 | italic | Status labels, game count |
| Press Start 2P | 6 | - | Listbox items, body text |
| Press Start 2P | 6 | bold | Badges, small buttons |
| Press Start 2P | 7 | bold | Labels, card titles |
| Press Start 2P | 13 | - | Timer display |
| Press Start 2P | 5 | - | Footer text |
| Courier | 10 | bold | PixelButton text |
| Segoe UI | 8 | - | Game count label |

## Icon Reference

| Icon Name | Size | Usage |
|-----------|------|-------|
| app_icon | Default | Window icon, header |
| bookmark.png | 16x16 | Favorites header, queue favorite button |
| trash.png | 18x18 | Clean Dummies button |
| cog.png | 18x18 | Settings button |
| search.png | 16x16 | Search bar |
| folder.png | 48x48 | Empty state |
| play.png | 18x18 | Start button |
| stop.png | 18x18 | Stop button |
| close.png | 16x16 | Queue remove button |
| sun.png | 16x16 | Light theme radio |
| full-moon.png | 16x16 | Dark theme radio |

## Color Reference

| Color Name | Dark Theme | Light Theme | Usage |
|------------|------------|-------------|-------|
| base | #11111b | #eff1f5 | Main background |
| mantle | #1e1e2e | #e6e9ef | Sidebar, toolbar, footer |
| surface | #252538 | #e6e9ef | Cards |
| surface0 | #313244 | #ccd0da | Inputs, listboxes |
| surface1 | #45475a | #bcc0cc | Borders, preset buttons |
| text | #cdd6f4 | #1e1e2e | Primary text |
| subtext0 | #a6adc8 | #6c7086 | Secondary text |
| green | #a6e3a1 | #40a02b | Status, success, start button |
| red | #f38ba8 | #d20f39 | Error, stop button, clean dummies |
| pink | #f5c2e7 | #ea76cb | Titles, accents |
| mauve | #cba6f7 | #8839ef | Selection, highlights |
