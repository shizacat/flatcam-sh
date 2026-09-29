# Settings

`Settings` and `Options` answer different questions.

## `Settings`

Saved application settings. They are loaded from `current_defaults_<version>.FlatConfig` and written back when the user saves preferences. A missing file is created from the built-in defaults. A file that cannot be read is deleted and replaced with those defaults; the replacement is written to the log. The file-format `version` and the usage counters in `global_stats` belong here.

## `Options`

Session values used by tools, editors, and the open project. `Options.from_settings()` builds them from the saved settings. After that they may diverge: a theme choice or a loaded project changes options and does not write the settings file.

Options do not repeat the settings schema. Shared preference groups are defined once and inherited by both objects:

- application behavior: units, language, workers, autosave
- interface: theme, canvas, grid, cursor, layout
- Gerber, Excellon, geometry, and CNC job
- each tool
- file associations, scripts, and documents

`version` and `global_stats` stay on `Settings` only.

## Current application stores

`App` stores saved settings on `self.settings` and the session copy on `self.options`. Modules outside `appMain.py` still read `app.defaults` and dictionary keys on `app.options` until those call sites are switched. Each store answers a different question.

| Question | Read and write |
|---|---|
| What should a tool or object use in this session? | `app.options` |
| What did the user save in Preferences, and what comes back on the next launch? | `app.defaults`, file `current_defaults_<version>.FlatConfig` |
| Window layout, theme, language, font sizes? | `QSettings("Open Source", "FlatCAM_EVO")` |

`app.options` is the working copy. `app.defaults` is the saved Preferences. They start as a copy of each other and then diverge. Writing one does not write the other.

## `app.defaults`

`App` creates this in `App.__init__` (`source/appMain.py`).

`AppDefaults` (`source/defaults.py`) wraps a `LoudDict`. `app.defaults["key"]` is that dictionary. The class attribute `factory_defaults` is the built-in starting set. On construction the dictionary is filled from `factory_defaults`. Then `defaults.load()` overlays `current_defaults_<version>.FlatConfig` from the data folder.

Data folder:

- Windows, normal install: `%APPDATA%/FlatCAM`
- Windows, portable: `<app>/config`
- macOS and Linux: `~/.FlatCAM`

The settings file name uses the application version, `App.version`, as in `current_defaults_Unstable.FlatConfig`. The `version` field inside the file is the data-format version and is not part of the file name.

`PreferencesUIManager.current_defaults` is an in-memory `Settings` snapshot used to undo an unsaved Preferences edit. It is not the file.

Startup no longer writes `factory_defaults_<version>.FlatConfig`. Built-in defaults live on `Settings`. Restore through the old preferences code still uses the in-memory `factory_defaults`.

## `app.options`

`AppOptions` is a second `LoudDict`, created empty immediately after `defaults` is loaded. Startup then copies every key:

```python
for def_key, def_val in self.defaults.items():
    self.options[def_key] = deepcopy(def_val)
```

Tools, editors, and objects read and write `app.options["key"]`. That value lives for this process. It is not the Preferences file.

A new object copies the keys it needs into its own `obj_options`. That dictionary belongs to the object. Changing it does not change `app.options` or the file.

`AppOptions.load()` exists for New Project and Import Preferences. The normal startup path does not call it.

## When the two dictionaries are copied

They are copied only at these points.

**Startup.** `factory_defaults`, then the FlatConfig file, then a full `deepcopy` into `app.options`.

**Apply in Preferences** (`PreferencesUIManager.on_save_button`):

1. The form writes into `app.defaults`. Only keys listed in `settings_from_fields` are read.
2. `app.options.update(app.defaults)` copies the whole defaults dictionary over the session.
3. `save_defaults()` writes `app.defaults` to `current_defaults_<version>.FlatConfig`.

**File → Save Defaults** (`AppIO.on_file_save_defaults`) copies `app.options` onto `app.settings`, then writes the settings file.

**Close Preferences without saving** restores the form and `app.settings` from `PreferencesUIManager.current_defaults`. `app.options` is left as it was.

**New Project** does not read the settings file again. `on_settings2options()` reads the form into `app.settings` and copies `app.settings` over `app.options`.

After Apply, `options.update(defaults)` stores the same value objects in both dictionaries. A later in-place edit of a nested list or dict is visible from both sides. The startup copy is a `deepcopy`, so the two dictionaries are independent until the next Apply or Save Defaults.

## Preferences form

`PreferencesUIManager.settings_from_fields` maps an option key to a widget. Apply reads that map into `app.defaults`. Keys absent from the map are never taken from the form, so they stay at the factory or file value and are still written out with the rest of `app.defaults`.

Opening Preferences fills the form from `app.defaults` (`defaults_write_form`). A change callback on `app.options` can push a single key back into the matching widget (`App.on_defaults_dict_change`). The widget is not a store.

Some color controls write `app.options` as the color changes, before Apply. That updates the session immediately. The file still changes only when Apply or Save Defaults runs.

`AppDefaults.propagate_defaults()` copies a few keys (`excellon_*`, `gerber_use_buffer_for_union`, `geometry_multidepth`) onto the class-level defaults of the Gerber, Excellon, and Geometry parsers. That path is separate from `app.options`.

## `QSettings`

`QSettings("Open Source", "FlatCAM_EVO")` has no shared object with the two dictionaries. Call sites open it, read or write a key, and drop it.

Stored there, and not in the FlatConfig file:

- window geometry, splitter, saved GUI state, layout, toolbar lock, menu text
- theme and appearance (`theme`, `appearance`, `dark_canvas`, `style`)
- language
- `font_size`, `notebook_font_size`, `axis_font_size`, `textbox_font_size`, `hud_font_size`
- splash screen

`font_size` is read once in `flatcam.py` before `App` is constructed, and written only by the **Apply and Restart** button. The other font sizes are written on Preferences Apply and read by the widgets and canvases that draw them.

On the first run, `app.options["first_run"]` clears every key in this `QSettings` store.

## Where to put a new setting

Use `app.options` when the running tool or object needs the value now.

Also add it to `factory_defaults` and to `settings_from_fields` when it must survive a restart through Preferences. Apply is what copies the widget into `app.defaults`, into `app.options`, and into the FlatConfig file.

Use `QSettings("Open Source", "FlatCAM_EVO")` for window chrome, theme, language, and font sizes. Those keys are not part of `app.defaults`.
