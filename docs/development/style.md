# Style

Style and color are separate settings. Style chooses which Qt style draws the controls. Color chooses the palette, the icon set, and the plot background.

Preferences → General → GUI shows both: the **Color** radio (System, Light, Dark) and the **Style** combo.

## Style

A style is a `QStyle` from `QStyleFactory.keys()`. The combo lists whatever this process reports. Typical names:

| Name | What it draws |
|---|---|
| `macOS` | Native macOS controls. Present on macOS builds. |
| `Windows` | Windows-style controls, including on macOS. |
| `Fusion` | Qt's own style. The same drawing on every platform. |

The style does not pick light or dark. It only draws buttons, combo boxes, sliders, and the rest of the chrome. The color scheme below supplies the palette those controls use. On macOS, the native style follows that palette: Dark uses the system dark drawing, Light uses the system light drawing.

The choice is stored by name in `QSettings("Open Source", "FlatCAM_EVO")` under the key `style`. It is not a field of `Settings` and it is not written to the FlatConfig file. A stored value that is not one of the available style names is ignored, and Qt keeps its default style.

`App.__init__` calls `GuiSettings.apply_style()` after the color scheme and before the splash screen, the first widget, so the window is created with the saved style. Changing the combo calls the same function immediately and writes the name. No restart.

A stylesheet on the application replaces the style object. Setting a new style while a sheet is active leaves the previous style in place. `GuiSettings.set_widget_style()` clears the sheet, calls `QApplication.setStyle()`, then puts the same sheet back.

## Color

Color is the **Color** radio on the same page.

| Choice | Stored value | Qt color scheme | Session theme |
|---|---|---|---|
| System | `system` | `Qt.ColorScheme.Unknown` (follow the OS) | `darkdetect` decides light or dark |
| Light | `light` | `Qt.ColorScheme.Light` | light |
| Dark | `dark` | `Qt.ColorScheme.Dark` | dark |

The saved field is `global_appearance` on `Settings` (`source/settings/models/interface.py`). Older files used `default` and `auto` for the same idea; both load as `system`.

Startup resolves that field once:

1. `Options.theme_from_appearance()` writes `options.global_theme` as `light` or `dark`. System follows the operating system through `darkdetect`.
2. `apply_color_scheme()` sets `QApplication.styleHints().setColorScheme()`. System uses `Qt.ColorScheme.Unknown`, so Qt keeps following the OS.
3. The icon folder is chosen from `global_theme`: `assets/resources` for light, `assets/resources/dark_resources` for dark.

The window, the icon set, and the canvas are built from that result and are not rebuilt later. Changing Color or **Dark Canvas** asks for a restart. Apply copies the form into the settings file first, then the process starts again. A loaded project must not replace these fields; they are listed in `STARTUP_THEME_FIELDS` (`source/settings/utils.py`).

`App` also copies `appearance`, `theme`, and `dark_canvas` into the same `QSettings` store. The plot canvases read `theme` and `dark_canvas` from there. `theme` is the resolved session value, `light` or `dark`. A leftover `default` in that key is treated as light.

`MainGUI.theme_safe_colors` swaps a few named text colors (blue, green, red, and others) for values that stay readable on a dark background. Light keeps the original name.

## Dark Canvas

**Dark Canvas** forces a dark plot background while the rest of the application stays on the selected color. It is `global_dark_canvas` on `Settings`, and the same value is copied to the `QSettings` key `dark_canvas`.

The canvas is white when the resolved theme is light and Dark Canvas is off. Otherwise the canvas is black. With a light color and Dark Canvas on, the 3D cursor is gray instead of black. The icon set still follows the color, not this checkbox.

Changing it requires a restart, the same path as Color.

## Icons

| Folder | Used when |
|---|---|
| `source/assets/resources` | Light session theme |
| `source/assets/resources/dark_resources` | Dark session theme. Toolbar icons are light gray (`#F3F3F3`) so they stay visible on a dark bar. |
| `source/assets/resources/dark_red_resources` | Not loaded. The previous red dark-theme icons, kept so they can be copied back. |

Icons that mean a color or a warning stay red in both sets (`red32`, `apply_red32`, `youtube32`, and the same kind). The `dark_resources/Makefile` is the ImageMagick recipe that built the gray set from the light PNGs: drop the white background, invert, then flatten the remaining grays to `#F3F3F3`.
