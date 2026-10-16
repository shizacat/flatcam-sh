# Geometry Editor

The Geometry Editor (`AppGeoEditor` in `source/appEditors/appGeoEditor.py`) is a temporary workspace between a `Geometry` object and the canvas. Opening it copies the object's geometry into editor storage. Closing it writes that storage back. The original object stays hidden while the editor is active.

## Opening

`edit_geometry()` deactivates any previous editor session, activates this one, and hides the source object. A background job then loads the geometry:

1. Read `solid_geometry`, or one tool's geometry when the object is multi-geo.
2. Flatten it into individual Shapely elements. A polygon becomes its exterior ring plus one element per hole. Points are dropped.
3. Wrap each element in a `DrawToolShape` and insert it into `self.storage` through `add_shape(..., build_ui=False)`.
4. Draw the canvas with `plot_all()`.
5. Build the geometry table once, through `build_ui_sig`.

## Storage

`self.storage` is an `AppRTreeStorage` (`source/camlib.py`). It keeps the shapes and a spatial index of their vertices.

| Store | What it holds |
|---|---|
| `objects` | The `DrawToolShape` values. A removed slot becomes `None`; `get_objects()` skips those slots |
| `self.rti` | One rtree entry per vertex, stored as the box `(x, y, x, y)` |
| `obj2points` | For each shape, the rtree indexes of its vertices |
| `points2obj` | For each rtree entry, the index of the shape that owns it |

The coordinates stay on `DrawToolShape.geo`. The index does not keep a second copy of the polyline. `nearest()` reads the matched vertex back from the rtree box and always returns it as a plain `(x, y)` tuple, together with the owning shape. Passing a `PointXY` as the query does not change that.

`self.selected` is the list of `DrawToolShape` values the editor treats as selected. It is separate from the table selection.

## Geometry table

The table is an `FCTree` with three columns: ID, Type, and Name. `build_ui()` clears the rows and adds one row per shape still in storage. The ID cell is `str(id(shape))`. That string is the only link between a row and a shape.

The table is built when the editor opens. Deletion does not rebuild it. Adding a shape, and operations that replace shapes (union, intersection, subtract, cut, orientation change), still emit `build_ui_sig` and rebuild the whole table.

## Selection

A row click and a canvas click both end with highlighted rows and a canvas redraw, but they fill `self.selected` differently.

**Table.** `itemSelectionChanged` runs `on_tree_selection`, which resolves each selected row's ID against storage, stores those shapes in `self.selected`, and calls `plot_all()`. `currentItemChanged` then runs `update_ui()`. That method clears `self.selected` and refreshes the parameter panel (length, coordinates, validity). The rows stay selected. After a row click, the table selection is the record of what is selected; `self.selected` is empty.

**Canvas click.** `FCSelect.click_release` asks `storage.nearest()` for the nearest vertex, stores that shape in `self.selected`, selects the matching row with tree signals blocked, then calls `update_ui()`. The row stays selected and `self.selected` is cleared, same as a table click.

**Drag selection.** `draw_selection_area_handler` tests each shape with `contains` (left to right) or `intersects` (right to left), replaces or toggles `self.selected`, and selects the matching rows while `currentItemChanged` is disconnected. `update_ui()` does not run, so `self.selected` stays filled.

## Drawing

Three VisPy collections are created with the editor and enabled in `activate()`:

| Collection | What it draws |
|---|---|
| `shapes` | Shapes that are not selected |
| `sel_shapes` | Selected shapes, thicker and in the selection color |
| `tool_shape` | The active tool's temporary geometry (a rubber band, a cursor preview) |

`plot_all()` walks `storage`, splits shapes into those two groups, clears both collections, and draws what remains. An empty group still clears its collection, so deleting the last shape removes it from the canvas. `plot_shape()` turns a polygon into a filled mesh plus an outline, and a line or ring into an outline. `ShapeCollection.add()` tessellates that geometry into mesh and line buffers. `redraw()` merges the buffers and sends them to the GPU.

## Deletion

The toolbar button, the editor menu, and the table context menu call `delete_selected()`.

1. Collect shapes from `self.selected` and from the selected table rows, matched by ID. Duplicates are skipped. This covers a drag selection (shapes are in `self.selected`) and a click selection (only the rows remain selected).
2. `delete_shape()` removes them from storage, from `self.selected`, and from the utility list.
3. `_remove_geometry_rows()` removes the matching table rows with `removeChild`. Tree signals are blocked for that change. `build_ui()` is not called.
4. `plot_all()` redraws whatever is left, and `on_tree_selection()` resets the parameter panel.

## Editing operations

A drawing tool builds Shapely geometry, wraps it in `DrawToolShape`, and `on_shape_complete()` passes it to `add_shape()`. That inserts it into storage and, unless told otherwise, emits `build_ui_sig`. Utility geometry used while drawing is then discarded and the canvas is replotted.

Union, intersection, subtract, and the other boolean tools read `get_selected()`, delete the inputs with `delete_shape()` (rows are not removed one by one), insert the result, replot, and rebuild the table.

Move and the other shape tools that call `delete_selected()` remove the old rows directly. The new geometry is inserted afterwards and the table is rebuilt for those new rows.

## Closing

`update_editor_geometry()` reads every remaining `shape.geo`, writes the list back to `solid_geometry` (and to the edited tool when the object is multi-geo), updates the bounds, then deactivates the editor. Deactivation clears the canvas collections and builds a fresh empty storage. The source object is shown again by the caller.
