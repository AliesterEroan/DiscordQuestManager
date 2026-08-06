# Cat Selection and Animation System Documentation

## Current Implementation

### How Cat Selection Should Work

1. **User Selection in Settings Dialog**
   - User opens Settings dialog
   - Navigates to "Dummy Window" tab
   - Selects a cat from the 2x3 grid (Cat-1 through Cat-6)
   - Selection is saved to settings as `dummy_cat_selection`

2. **Settings Storage**
   - Setting key: `dummy_cat_selection`
   - Default value: "Cat-1"
   - Stored in: `data/settings.json`
   - Example value: "Cat-3"

3. **Main Window Loading**
   - Main window loads settings on startup: `self.dummy_cat_selection = self.settings_manager.get("dummy_cat_selection", "Cat-1")`
   - When settings are saved, main window reloads: `self.dummy_cat_selection = self.settings_manager.get("dummy_cat_selection", "Cat-1")`

4. **Dummy Window Launch**
   - When quest starts, main window spawns dummy process:
   ```python
   self.process_manager.spawn_dummy_process(
       quest_id, fake_exe_path, exe_name, game_name, 
       script_path, self.colors, self.custom_duration, self.dummy_cat_selection
   )
   ```
   - Cat selection is passed as command-line argument to dummy process

5. **Dummy Window Reception**
   - Dummy window receives cat selection from command line:
   ```python
   cat_selection = "Cat-1"  # Default
   if dummy_index + 4 < len(sys.argv):
       try:
           cat_selection = sys.argv[dummy_index + 4]
       except (ValueError, IndexError):
           cat_selection = "Cat-1"
   ```

6. **Animation Display**
   - Dummy window should load and display the selected cat animation
   - Animation files should be in: `assets/animations/`
   - Each cat should have corresponding animation files

### Current Issues

1. **CRITICAL: Cat Selection vs Animation Structure Mismatch**
   - Settings system expects cat selection like "Cat-1", "Cat-2", etc.
   - Animation files are organized by ACTION (run, itch, stretch, walk) not by cat number
   - This is a fundamental design mismatch
   - Current system: User selects Cat-1 through Cat-6 in settings
   - Actual file structure: animations organized by actions (run/itch/stretch/walk)
   - The cat selection system needs to be redesigned to match the animation structure

2. **Animation Placeholders**
   - Some animations show controller placeholder instead of actual cat
   - This is likely because the system is trying to load cat-specific animations that don't exist
   - The animation loading logic needs to be fixed to match the actual file structure

### Animation File Structure

Actual structure:
```
assets/
  animations/
    cat/
      Run/
        big/
          [animation frames]
      itch/
        big/
          [animation frames - cat 3 missing]
      stretch/
        [animation frames]
      walk/
        big/
          [animation frames]
```

The animations are organized by action (run, itch, stretch, walk) rather than by cat number (Cat-1, Cat-2, etc.).

### Required Fixes

1. **REDESIGN NEEDED: Cat Selection System**
   - Current system: User selects "Cat-1" through "Cat-6"
   - Animation structure: Organized by actions (run, itch, stretch, walk)
   - **Solution Options:**
     - Option A: Change settings to select animation actions instead of cat numbers
     - Option B: Reorganize animation files by cat number (Cat-1/Run, Cat-1/itch, etc.)
     - Option C: Create mapping system (Cat-1 = run animation, Cat-2 = itch animation, etc.)
   - **Recommendation:** Option C - Create a mapping system since animations are already organized by action

2. **Fix Animation Loading Logic**
   - Update dummy window to load animations based on action rather than cat number
   - Add proper error handling for missing animations
   - Ensure animation paths match the actual file structure

3. **Update Settings Dialog**
   - Change cat selection UI to reflect animation actions
   - Or keep cat selection but map internally to animation actions

3. **Animation System Design**
   - Define clear animation file naming convention
   - Create animation loader that handles missing files gracefully
   - Add placeholder animation if specific cat animation is missing

### Testing Checklist

- [ ] Select different cats in settings
- [ ] Verify setting is saved to settings.json
- [ ] Verify main window reloads setting after save
- [ ] Start quest and verify cat selection is passed to dummy window
- [ ] Verify dummy window receives correct cat selection
- [ ] Verify correct animation is displayed
- [ ] Test all 6 cat options
- [ ] Test with missing animation files (should show placeholder or default)
