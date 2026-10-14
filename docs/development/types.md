# Types

Shared value types live in `source/settings/st_types.py`. Combo indexes for a tool live in `source/tools_database.py`.

## Point

A point is X then Y, in the project units (inch or millimeter).

### `PointXY`

`PointXY` is a named tuple of two floats. `point.x` and `point.y` are the coordinates. `point[0]` and `point[1]` are those same numbers, so existing index access still works. Adding or subtracting two points returns a point. Multiplying or dividing by a number scales both coordinates. `abs(point)` is the distance from the origin.

A canvas click becomes this pair after `translate_coords` turns pixel coordinates into project coordinates. When grid snap is on, the pair is the snapped grid point. Polygon selection stores the pairs in click order. Three or more pairs build a Shapely polygon.

`PointXY` does not read the text `"x, y"`. A saved file still stores the point as two numbers, not under the names `x` and `y`.

Use it for a point that is already two numbers:

- vertices of an exclusion polygon, and the cursor while that polygon is drawn
- the geometry and Excellon editor cursors, and geometry editor clicks: `DrawTool.click`, `DrawTool.click_release`, and `DrawTool.points`

### `XYPair`

`XYPair` is the same point when Preferences or the tools database store it. Pydantic accepts a `PointXY`, a list of two numbers, or the text `"x, y"`, and keeps a `PointXY`.

`PointXY` and `XYPair` both name a point. They stay separate while a stored field can still arrive as text. They may be merged later.

Use `XYPair` for a saved position, such as a tool change or an end point (`tools_mill_toolchangexy`, `tools_mill_endxy`, and the matching drill and transform fields).

## Tool database indexes

These values are the combo index written in the tools database. On disk they stay that number.

| Type | Values |
|---|---|
| `ToolTarget` | `GENERAL` 0, `MILLING` 1, `DRILLING` 2, `ISOLATION` 3, `PAINT` 4, `NCC` 5, `CUTOUT` 6 |
| `MillJobType` | `ROUGHING` 0, `FINISHING` 1, `ISOLATION` 2, `POLISHING` 3 |

The tools database form stores the milling job label on `data.job`. That label is not `MillJobType`. Solder paste writes `'SP'` into a geometry tool. That string is not one of the four job types.
