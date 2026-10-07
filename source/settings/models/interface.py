"""Canvas, theme, and layout settings shared by saved settings and session options."""

from pydantic import BaseModel, Field

from settings.st_types import Appearance, ColorAppearance


class Interface(BaseModel):
    """Store canvas, theme, and layout settings shared by saved settings and session options."""

    global_tabs_detachable: bool = Field(
        default=False, description="Whether application tabs can be detached."
    )
    global_coords_bar_show: bool = Field(
        default=True, description="Whether the absolute-coordinate bar is shown."
    )
    global_delta_coords_bar_show: bool = Field(
        default=False, description="Whether the delta-coordinate bar is shown."
    )
    global_statusbar_show: bool = Field(
        default=True, description="Whether the application status bar is shown."
    )
    global_jump_ref: str = Field(
        default="abs",
        description="Coordinate reference mode used by the jump-to dialog.",
    )
    global_locate_pt: str = Field(
        default="bl", description="Anchor-point code used when locating objects."
    )
    global_move_ref: str = Field(
        default="abs", description="Coordinate reference mode used when moving objects."
    )
    global_gui_layout: int = Field(
        default=0, description="Application interface layout mode."
    )
    global_grid_context_menu: dict[str, list[float]] = Field(
        default_factory=lambda: {
            "in": [0.01, 0.02, 0.025, 0.05, 0.1],
            "mm": [0.1, 0.2, 0.5, 1, 2.54],
        },
        description="Preset grid spacings grouped by inch and millimeter units.",
    )
    global_shell_shape: list[int] = Field(
        default_factory=lambda: [500, 300],
        description="Shell window width and height in pixels.",
    )
    global_appearance: ColorAppearance = Field(
        default=Appearance.SYSTEM,
        description="Application color scheme: system, light, or dark.",
    )
    global_dark_canvas: bool = Field(
        default=False, description="Whether application dark canvas is enabled."
    )
    global_layout: str = Field(
        default="compact", description="Default application layout."
    )
    global_hover_shape: bool = Field(
        default=False, description="Whether application hover shape is enabled."
    )
    global_selection_shape: bool = Field(
        default=True, description="Whether application selection shape is enabled."
    )
    global_selection_shape_as_line: bool = Field(
        default=False,
        description="Whether application selection shape as line is enabled.",
    )
    global_sel_fill: str = Field(
        default="#a5a5ffbf",
        description="Default application selection fill as a hexadecimal color.",
    )
    global_sel_line: str = Field(
        default="#0000ffbf",
        description="Default application selection line as a hexadecimal color.",
    )
    global_alt_sel_fill: str = Field(
        default="#BBF268BF",
        description="Default application alt selection fill as a hexadecimal color.",
    )
    global_alt_sel_line: str = Field(
        default="#006E20BF",
        description="Default application alt selection line as a hexadecimal color.",
    )
    global_draw_color: str = Field(
        default="#00000080",
        description="Default application draw color as a hexadecimal color.",
    )
    global_sel_draw_color: str = Field(
        default="#0000FF80",
        description="Default application selection draw color as a hexadecimal color.",
    )
    global_proj_item_color_light: str = Field(
        default="#000000FF",
        description="Default application project item color light as a hexadecimal color.",
    )
    global_proj_item_dis_color_light: str = Field(
        default="#b7b7cbFF",
        description="Disabled project-item color for the light theme as a hexadecimal color.",
    )
    global_proj_item_color_dark: str = Field(
        default="#AAAAAAFF",
        description="Default application project item color dark as a hexadecimal color.",
    )
    global_proj_item_dis_color_dark: str = Field(
        default="#4a4a4aFF",
        description="Disabled project-item color for the dark theme as a hexadecimal color.",
    )
    global_project_autohide: bool = Field(
        default=True,
        description="Whether application project automatic hiding is enabled.",
    )
    global_grid_bar_show: bool = Field(
        default=True, description="Whether application grid bar show is enabled."
    )
    global_gridx: float = Field(
        default=1.0, description="Default application horizontal grid spacing."
    )
    global_gridy: float = Field(
        default=1.0, description="Default application vertical grid spacing."
    )
    global_snap_max: float = Field(
        default=0.05, description="Default application snap max."
    )
    global_workspace: bool = Field(
        default=False, description="Whether application workspace is enabled."
    )
    global_workspaceT: str = Field(
        default="A4", description="Default application workspace page size."
    )
    global_workspace_orientation: str = Field(
        default="p", description="Default application workspace orientation."
    )
    global_axis: bool = Field(
        default=True, description="Whether application axis is enabled."
    )
    global_axis_color: str = Field(
        default="#B34D4D",
        description="Default application axis color as a hexadecimal color.",
    )
    global_hud: bool = Field(
        default=False, description="Whether the canvas heads-up display is shown."
    )
    global_grid_lines: bool = Field(
        default=True, description="Whether application grid lines is enabled."
    )
    global_grid_snap: bool = Field(
        default=True, description="Whether application grid snap is enabled."
    )
    global_cursor_type: str = Field(
        default="small", description="Default application cursor type."
    )
    global_cursor_size: int = Field(
        default=20, description="Default application cursor size."
    )
    global_cursor_width: int = Field(
        default=2, description="Default application cursor width."
    )
    global_cursor_color: str = Field(
        default="#FF0000",
        description="Default application cursor color as a hexadecimal color.",
    )
    global_cursor_color_enabled: bool = Field(
        default=True, description="Whether application cursor color enabled is enabled."
    )
    global_pan_button: str = Field(
        default="2", description="Default application pan button."
    )
    global_mselect_key: str = Field(
        default="Control", description="Default application multiple-selection key."
    )
    global_delete_confirmation: bool = Field(
        default=True, description="Whether application delete confirmation is enabled."
    )
    global_allow_edit_in_project_tab: bool = Field(
        default=False,
        description="Whether application allow edit in project tab is enabled.",
    )
    global_open_style: bool = Field(
        default=True, description="Whether application open style is enabled."
    )
    global_toggle_tooltips: bool = Field(
        default=True, description="Whether application toggle tooltips is enabled."
    )
    global_activity_icon: str = Field(
        default="Ball green", description="Default application activity icon."
    )
