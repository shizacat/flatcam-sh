"""Define validated, typed application settings defaults."""

import gettext
import json
import os
from collections.abc import Callable
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, ValidationError

from exceptions import SettingsError

_ = gettext.gettext


def _default_worker_number() -> int:
    """Return the worker count derived from the available CPUs."""
    return min(4, max(2, int(os.cpu_count() / 2))) if os.cpu_count() else 2


def _default_process_number() -> int:
    """Return the process count derived from the available CPUs."""
    return int(os.cpu_count() / 4) if os.cpu_count() > 4 else 1


class Settings(BaseModel):
    """
    Store the complete validated set of application settings.

    Field defaults are the values assigned when no settings file exists.
    Every setting must declare a default value.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    _change_callbacks: list[Callable[[str], None]] = PrivateAttr(default_factory=list)

    version: float = Field(default=8.992, description="Settings data-format version.")
    first_run: bool = Field(
        default=True,
        description="Whether the application is running for the first time.",
    )
    root_folder_path: str = Field(
        default="", description="Root folder used to resolve application resources."
    )
    global_serial: int = Field(
        default=0, description="Serial number of the saved settings revision."
    )
    global_stats: dict[str, int] = Field(
        default_factory=dict,
        description="Application usage counters keyed by statistic name.",
    )
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
    global_background_timeout: int = Field(
        default=300000,
        description="Default application background timeout in milliseconds.",
    )
    global_verbose_error_level: int = Field(
        default=0, description="Default application verbose error level."
    )
    global_grid_context_menu: dict[str, list[float]] = Field(
        default_factory=lambda: {
            "in": [0.01, 0.02, 0.025, 0.05, 0.1],
            "mm": [0.1, 0.2, 0.5, 1, 2.54],
        },
        description="Preset grid spacings grouped by inch and millimeter units.",
    )
    global_last_folder: str | None = Field(
        default=None, description="Path used for application last folder."
    )
    global_last_save_folder: str | None = Field(
        default=None, description="Path used for application last save folder."
    )
    global_defaults_save_period_ms: int = Field(
        default=20000,
        description="Interval between automatic settings saves in milliseconds.",
    )
    global_shell_shape: list[int] = Field(
        default_factory=lambda: [500, 300],
        description="Shell window width and height in pixels.",
    )
    global_recent_limit: int = Field(
        default=10, description="Default application recent limit."
    )
    fit_key: str = Field(
        default="V",
        description="Keyboard shortcut used to fit the drawing to the view.",
    )
    zoom_out_key: str = Field(
        default="-", description="Keyboard shortcut used to zoom out."
    )
    zoom_in_key: str = Field(
        default="=", description="Keyboard shortcut used to zoom in."
    )
    grid_toggle_key: str = Field(
        default="G", description="Keyboard shortcut used to toggle grid snapping."
    )
    global_zoom_ratio: float = Field(
        default=1.5, description="Default application zoom ratio."
    )
    global_point_clipboard_format: str = Field(
        default="(%.*f, %.*f)",
        description="Printf-style format used for copied point coordinates.",
    )
    global_tcl_path: str = Field(
        default="", description="Path to the Tcl library used by the application."
    )
    units: str = Field(default="MM", description="Default project measurement units.")
    units_precision: int = Field(default=4, description="Default units precision.")
    global_graphic_engine: str = Field(
        default="3D", description="Default application graphic engine."
    )
    global_graphic_engine_3d_no_mp: bool = Field(
        default=False,
        description="Whether the 3D graphics engine runs without multiprocessing.",
    )
    global_backface_culling: bool = Field(
        default=True, description="Whether application backface culling is enabled."
    )
    global_app_level: str = Field(
        default="b", description="Application experience level code."
    )
    global_log_verbose: int = Field(
        default=2, description="Default application log verbose."
    )
    global_portable: bool = Field(
        default=False, description="Whether application portable is enabled."
    )
    global_languages: list[str] = Field(
        default_factory=lambda: ["English"],
        description="Available application languages values.",
    )
    global_language_current: str = Field(
        default="English", description="Default application language current."
    )
    global_systray_icon: bool = Field(
        default=True, description="Whether the application displays a system-tray icon."
    )
    global_shell_at_startup: bool = Field(
        default=False, description="Whether application shell at startup is enabled."
    )
    global_project_at_startup: bool = Field(
        default=False, description="Whether application project at startup is enabled."
    )
    global_version_check: bool = Field(
        default=True, description="Whether application version check is enabled."
    )
    global_send_stats: bool = Field(
        default=True, description="Whether application send stats is enabled."
    )
    global_worker_number: int = Field(
        default_factory=_default_worker_number,
        description="Number of background worker threads.",
    )
    global_process_number: int = Field(
        default_factory=_default_process_number,
        description="Number of worker processes.",
    )
    global_tolerance: float = Field(
        default=0.005, description="Default application tolerance."
    )
    global_save_compressed: bool = Field(
        default=True, description="Whether application save compressed is enabled."
    )
    global_compression_level: int = Field(
        default=3, description="Default application compression level."
    )
    global_autosave: bool = Field(
        default=False, description="Whether application autosave is enabled."
    )
    global_autosave_timeout: int = Field(
        default=300000,
        description="Default application autosave timeout in milliseconds.",
    )
    global_tpdf_tmargin: float = Field(
        default=15.0, description="Default application PDF top margin."
    )
    global_tpdf_bmargin: float = Field(
        default=10.0, description="Default application PDF bottom margin."
    )
    global_tpdf_lmargin: float = Field(
        default=20.0, description="Default application PDF left margin."
    )
    global_tpdf_rmargin: float = Field(
        default=20.0, description="Default application PDF right margin."
    )
    pdf_python_parser: bool = Field(
        default=True, description="Whether to parse PDF files with the Python parser."
    )
    global_appearance: str = Field(
        default="default", description="Default application appearance."
    )
    global_dark_canvas: bool = Field(
        default=False, description="Whether application dark canvas is enabled."
    )
    global_theme: str = Field(
        default="default", description="Default application theme."
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
    global_bookmarks: dict[str, int] = Field(
        default_factory=dict, description="Default application bookmarks."
    )
    global_bookmarks_limit: int = Field(
        default=10, description="Default application bookmarks limit."
    )
    global_activity_icon: str = Field(
        default="Ball green", description="Default application activity icon."
    )
    gerber_plot: bool = Field(
        default=True, description="Whether Gerber plot is enabled."
    )
    gerber_solid: bool = Field(
        default=True, description="Whether Gerber solid is enabled."
    )
    gerber_multicolored: bool = Field(
        default=False, description="Whether Gerber multiple colors is enabled."
    )
    gerber_color_list: list[str] = Field(
        default_factory=list, description="Available Gerber color palette values."
    )
    gerber_store_color_list: bool = Field(
        default=True, description="Whether Gerber store color palette is enabled."
    )
    gerber_circle_steps: int = Field(
        default=16, description="Default Gerber circle steps."
    )
    gerber_use_buffer_for_union: bool = Field(
        default=True, description="Whether Gerber use buffer for union is enabled."
    )
    gerber_clean_apertures: bool = Field(
        default=True, description="Whether Gerber clean apertures is enabled."
    )
    gerber_extra_buffering: bool = Field(
        default=False, description="Whether Gerber extra buffering is enabled."
    )
    gerber_plot_on_select: bool = Field(
        default=True, description="Whether Gerber plot on select is enabled."
    )
    gerber_plot_fill: str = Field(
        default="#BBF268BF",
        description="Default Gerber plot fill as a hexadecimal color.",
    )
    gerber_plot_line_enable: bool = Field(
        default=True, description="Whether Gerber plot line enable is enabled."
    )
    gerber_plot_line: str = Field(
        default="#006E20BF",
        description="Default Gerber plot line as a hexadecimal color.",
    )
    gerber_def_units: str = Field(
        default="IN", description="Default Gerber default units."
    )
    gerber_def_zeros: str = Field(
        default="L", description="Default Gerber leading- or trailing-zero notation."
    )
    gerber_save_filters: str = Field(
        default="Gerber File .gbr (.gbr);;Gerber File .bot (.bot);;Gerber File .bsm (.bsm);;"
        "Gerber File .cmp (.cmp);;Gerber File .crc (.crc);;Gerber File .crs (.crs);;"
        "Gerber File .gb0 (.gb0);;Gerber File .gb1 (.gb1);;Gerber File .gb2 (.gb2);;"
        "Gerber File .gb3 (.gb3);;Gerber File .gb4 (.gb4);;Gerber File .gb5 (.gb5);;"
        "Gerber File .gb6 (.gb6);;Gerber File .gb7 (.gb7);;Gerber File .gb8 (.gb8);;"
        "Gerber File .gb9 (.gb9);;Gerber File .gbd (.gbd);;Gerber File .gbl (.gbl);;"
        "Gerber File .gbo (.gbo);;Gerber File .gbp (.gbp);;Gerber File .gbs (.gbs);;"
        "Gerber File .gdl (.gdl);;Gerber File .gdo (.gdo);;Gerber File .ger (.ger);;"
        "Gerber File .gko (.gko);;Gerber File .gm1 (.gm1);;Gerber File .gm2 (.gm2);;"
        "Gerber File .gm3 (.gm3);;Gerber File .gme (.gme);;Gerber File .grb (.grb);;"
        "Gerber File .gtl (.gtl);;Gerber File .gto (.gto);;Gerber File .gtp (.gtp);;"
        "Gerber File .gts (.gts);;Gerber File .ly15 (.ly15);;Gerber File .ly2 (.ly2);;"
        "Gerber File .mil (.mil);;"
        "Gerber File .outline (.outline);;Gerber File .pho (.pho);;"
        "Gerber File .plc (.plc);;Gerber File .pls (.pls);;Gerber File .smb (.smb);;"
        "Gerber File .smt (.smt);;Gerber File .sol (.sol);;Gerber File .spb (.spb);;"
        "Gerber File .spt (.spt);;Gerber File .ssb (.ssb);;Gerber File .sst (.sst);;"
        "Gerber File .stc (.stc);;Gerber File .sts (.sts);;Gerber File .top (.top);;"
        "Gerber File .tsm (.tsm);;Gerber File .art (.art)"
        "All Files (.*)",
        description="File-dialog filter string used when saving Gerber files.",
    )
    gerber_noncoppermargin: float = Field(
        default=0.1, description="Default Gerber non-copper margin."
    )
    gerber_noncopperrounded: bool = Field(
        default=False, description="Whether Gerber noncopperrounded is enabled."
    )
    gerber_bboxmargin: float = Field(
        default=0.1, description="Default Gerber bboxmargin."
    )
    gerber_bboxrounded: bool = Field(
        default=False, description="Whether Gerber bboxrounded is enabled."
    )
    gerber_aperture_display: bool = Field(
        default=False, description="Whether Gerber aperture display is enabled."
    )
    gerber_aperture_scale_factor: float = Field(
        default=1.0, description="Default Gerber aperture scale factor."
    )
    gerber_aperture_buffer_factor: float = Field(
        default=0.0, description="Default Gerber aperture buffer factor."
    )
    gerber_follow: bool = Field(
        default=False, description="Whether Gerber follow is enabled."
    )
    gerber_buffering: str = Field(
        default="full", description="Default Gerber buffering."
    )
    gerber_delayed_buffering: bool = Field(
        default=True, description="Whether Gerber delayed buffering is enabled."
    )
    gerber_simplification: bool = Field(
        default=False, description="Whether Gerber simplification is enabled."
    )
    gerber_simp_tolerance: float = Field(
        default=0.0005, description="Default Gerber simplification tolerance."
    )
    gerber_exp_units: str = Field(
        default="IN", description="Default Gerber export units."
    )
    gerber_exp_integer: int = Field(
        default=2, description="Default Gerber export integer."
    )
    gerber_exp_decimals: int = Field(
        default=4, description="Default Gerber export decimals."
    )
    gerber_exp_zeros: str = Field(
        default="L", description="Gerber export leading- or trailing-zero notation."
    )
    gerber_editor_sel_limit: int = Field(
        default=30, description="Default Gerber editor selection limit."
    )
    gerber_editor_newcode: int = Field(
        default=10, description="Default Gerber editor new aperture code."
    )
    gerber_editor_newsize: float = Field(
        default=0.8, description="Default Gerber editor new aperture size."
    )
    gerber_editor_newtype: str = Field(
        default="C", description="Default Gerber editor new aperture type."
    )
    gerber_editor_newdim: str = Field(
        default="0.5, 0.5", description="Default Gerber editor new aperture dimensions."
    )
    gerber_editor_array_size: int = Field(
        default=5, description="Default Gerber editor array size."
    )
    gerber_editor_lin_dir: str = Field(
        default="X", description="Default Gerber editor linear array dir."
    )
    gerber_editor_lin_pitch: float = Field(
        default=0.1, description="Default Gerber editor linear array pitch."
    )
    gerber_editor_lin_angle: float = Field(
        default=0.0, description="Default Gerber editor linear array angle in degrees."
    )
    gerber_editor_circ_dir: str = Field(
        default="CW", description="Default Gerber editor circular array dir."
    )
    gerber_editor_circ_angle: float = Field(
        default=0.0,
        description="Default Gerber editor circular array angle in degrees.",
    )
    gerber_editor_scale_f: float = Field(
        default=1.0, description="Default Gerber editor scale factor."
    )
    gerber_editor_buff_f: float = Field(
        default=0.1, description="Default Gerber editor buffer factor."
    )
    gerber_editor_ma_low: float = Field(
        default=0.0, description="Default Gerber editor mark-area threshold low."
    )
    gerber_editor_ma_high: float = Field(
        default=1.0, description="Default Gerber editor mark-area threshold high."
    )
    excellon_plot: bool = Field(
        default=True, description="Whether Excellon plot is enabled."
    )
    excellon_circle_steps: int = Field(
        default=16, description="Default Excellon circle steps."
    )
    excellon_solid: bool = Field(
        default=True, description="Whether Excellon solid is enabled."
    )
    excellon_multicolored: bool = Field(
        default=False, description="Whether Excellon multiple colors is enabled."
    )
    excellon_color: str | None = Field(
        default=None, description="Default Excellon color as a hexadecimal color."
    )
    excellon_merge_fuse_tools: bool = Field(
        default=True, description="Whether Excellon merge fuse tools is enabled."
    )
    excellon_format_upper_in: int = Field(
        default=2, description="Default Excellon format upper in."
    )
    excellon_format_lower_in: int = Field(
        default=4, description="Default Excellon format lower in."
    )
    excellon_format_upper_mm: int = Field(
        default=3, description="Default Excellon format upper mm."
    )
    excellon_format_lower_mm: int = Field(
        default=3, description="Default Excellon format lower mm."
    )
    excellon_zeros: str = Field(
        default="T", description="Default Excellon zero-suppression notation."
    )
    excellon_units: str = Field(default="INCH", description="Default Excellon units.")
    excellon_update: bool = Field(
        default=True, description="Whether Excellon update is enabled."
    )
    excellon_optimization_type: str = Field(
        default="B", description="Default Excellon optimization type."
    )
    excellon_search_time: int = Field(
        default=3, description="Default Excellon search time."
    )
    excellon_save_filters: str = Field(
        default="Excellon File .txt (*.txt);;Excellon File .drd (*.drd);;"
        "Excellon File .drill (*.drill);;"
        "Excellon File .drl (*.drl);;Excellon File .exc (*.exc);;"
        "Excellon File .ncd (*.ncd);;Excellon File .tap (*.tap);;"
        "Excellon File .xln (*.xln);;All Files (*.*)",
        description="File-dialog filter string used when saving Excellon files.",
    )
    excellon_plot_fill: str = Field(
        default="#C40000BF",
        description="Default Excellon plot fill as a hexadecimal color.",
    )
    excellon_plot_line: str = Field(
        default="#750000BF",
        description="Default Excellon plot line as a hexadecimal color.",
    )
    excellon_drill_tooldia: float = Field(
        default=0.8, description="Default Excellon drill tool diameter."
    )
    excellon_slot_tooldia: float = Field(
        default=1.8, description="Default Excellon slot tool diameter."
    )
    excellon_tools_table_display: bool = Field(
        default=True, description="Whether Excellon tools table display is enabled."
    )
    excellon_autoload_db: bool = Field(
        default=False, description="Whether Excellon autoload db is enabled."
    )
    excellon_exp_units: str = Field(
        default="INCH", description="Default Excellon export units."
    )
    excellon_exp_format: str = Field(
        default="dec", description="Default Excellon export format."
    )
    excellon_exp_integer: int = Field(
        default=2, description="Default Excellon export integer."
    )
    excellon_exp_decimals: int = Field(
        default=4, description="Default Excellon export decimals."
    )
    excellon_exp_zeros: str = Field(
        default="LZ", description="Excellon export zero-suppression notation."
    )
    excellon_exp_slot_type: str = Field(
        default="routing", description="Default Excellon export slot type."
    )
    excellon_editor_sel_limit: int = Field(
        default=30, description="Default Excellon editor selection limit."
    )
    excellon_editor_newdia: float = Field(
        default=1.0, description="Default Excellon editor new tool diameter."
    )
    excellon_editor_array_size: int = Field(
        default=5, description="Default Excellon editor array size."
    )
    excellon_editor_lin_dir: str = Field(
        default="X", description="Default Excellon editor linear array dir."
    )
    excellon_editor_lin_pitch: float = Field(
        default=2.54, description="Default Excellon editor linear array pitch."
    )
    excellon_editor_lin_angle: float = Field(
        default=0.0,
        description="Default Excellon editor linear array angle in degrees.",
    )
    excellon_editor_circ_dir: str = Field(
        default="CW", description="Default Excellon editor circular array dir."
    )
    excellon_editor_circ_angle: int = Field(
        default=12,
        description="Default Excellon editor circular array angle in degrees.",
    )
    excellon_editor_slot_direction: str = Field(
        default="X", description="Default Excellon editor slot direction."
    )
    excellon_editor_slot_angle: float = Field(
        default=0.0, description="Default Excellon editor slot angle in degrees."
    )
    excellon_editor_slot_length: float = Field(
        default=5.0, description="Default Excellon editor slot length."
    )
    excellon_editor_slot_array_size: int = Field(
        default=5, description="Default Excellon editor slot array size."
    )
    excellon_editor_slot_lin_dir: str = Field(
        default="X", description="Default Excellon editor slot linear array dir."
    )
    excellon_editor_slot_lin_pitch: float = Field(
        default=2.54, description="Default Excellon editor slot linear array pitch."
    )
    excellon_editor_slot_lin_angle: float = Field(
        default=0.0,
        description="Default Excellon editor slot linear array angle in degrees.",
    )
    excellon_editor_slot_circ_dir: str = Field(
        default="CW", description="Default Excellon editor slot circular array dir."
    )
    excellon_editor_slot_circ_angle: int = Field(
        default=12,
        description="Default Excellon editor slot circular array angle in degrees.",
    )
    geometry_plot: bool = Field(
        default=True, description="Whether geometry plot is enabled."
    )
    geometry_multicolored: bool = Field(
        default=False, description="Whether geometry multiple colors is enabled."
    )
    geometry_circle_steps: int = Field(
        default=32, description="Default geometry circle steps."
    )
    geometry_merge_fuse_tools: bool = Field(
        default=True, description="Whether geometry merge fuse tools is enabled."
    )
    geometry_plot_line: str = Field(
        default="#FF0000",
        description="Default geometry plot line as a hexadecimal color.",
    )
    geometry_seg_x: float = Field(default=0.0, description="Default geometry seg X.")
    geometry_seg_y: float = Field(default=0.0, description="Default geometry seg Y.")
    geometry_dxf_format: str = Field(
        default="R2010", description="Default geometry dxf format."
    )
    geometry_paths_only: bool = Field(
        default=True, description="Whether geometry paths use only is enabled."
    )
    geometry_editor_sel_limit: int = Field(
        default=30, description="Default geometry editor selection limit."
    )
    geometry_editor_milling_type: str = Field(
        default="cl", description="Default geometry editor milling type."
    )
    geometry_editor_parameters: bool = Field(
        default=False, description="Whether geometry editor parameters is enabled."
    )
    cncjob_plot: bool = Field(
        default=True, description="Whether CNC job plot is enabled."
    )
    cncjob_tooldia: float = Field(
        default=0.125, description="Default CNC job tool diameter."
    )
    cncjob_coords_type: str = Field(
        default="G90",
        description="G-code coordinate mode, such as absolute or incremental.",
    )
    cncjob_coords_decimals: int = Field(
        default=4, description="Default CNC job coordinate decimals."
    )
    cncjob_fr_decimals: int = Field(
        default=2, description="Default CNC job feed-rate decimals."
    )
    cncjob_bed_max_x: int = Field(default=300, description="Default CNC job bed max X.")
    cncjob_bed_max_y: int = Field(default=400, description="Default CNC job bed max Y.")
    cncjob_bed_offset_x: int = Field(
        default=0, description="Default CNC job bed offset X."
    )
    cncjob_bed_offset_y: int = Field(
        default=0, description="Default CNC job bed offset Y."
    )
    cncjob_bed_skew_x: int = Field(default=0, description="Default CNC job bed skew X.")
    cncjob_bed_skew_y: int = Field(default=0, description="Default CNC job bed skew Y.")
    cncjob_steps_per_circle: int = Field(
        default=16, description="Default CNC job steps per circle."
    )
    cncjob_footer: bool = Field(
        default=False, description="Whether CNC job footer is enabled."
    )
    cncjob_line_ending: bool = Field(
        default=False, description="Whether CNC job line ending is enabled."
    )
    cncjob_save_filters: str = Field(
        default="G-Code Files .nc (*.nc);;G-Code Files .din (*.din);;G-Code Files .dnc (*.dnc);;"
        "G-Code Files .ecs (*.ecs);;G-Code Files .eia (*.eia);;G-Code Files .fan (*.fan);;"
        "G-Code Files .fgc (*.fgc);;G-Code Files .fnc (*.fnc);;G-Code Files . gc (*.gc);;"
        "G-Code Files .gcd (*.gcd);;G-Code Files .gcode (*.gcode);;G-Code Files .h (*.h);;"
        "G-Code Files .hnc (*.hnc);;G-Code Files .i (*.i);;G-Code Files .min (*.min);;"
        "G-Code Files .mpf (*.mpf);;G-Code Files .mpr (*.mpr);;G-Code Files .cnc (*.cnc);;"
        "G-Code Files .ncc (*.ncc);;G-Code Files .ncg (*.ncg);;G-Code Files .ncp (*.ncp);;"
        "G-Code Files .ngc (*.ngc);;G-Code Files .out (*.out);;G-Code Files .ply (*.ply);;"
        "G-Code Files .sbp (*.sbp);;G-Code Files .tap (*.tap);;G-Code Files .xpi (*.xpi);;"
        "All Files (*.*)",
        description="File-dialog filter string used when saving CNC job files.",
    )
    cncjob_plot_line: str = Field(
        default="#4650BDFF",
        description="Default CNC job plot line as a hexadecimal color.",
    )
    cncjob_plot_fill: str = Field(
        default="#5E6CFFFF",
        description="Default CNC job plot fill as a hexadecimal color.",
    )
    cncjob_travel_line: str = Field(
        default="#B5AB3A4C",
        description="Default CNC job travel line as a hexadecimal color.",
    )
    cncjob_travel_fill: str = Field(
        default="#F0E24D4C",
        description="Default CNC job travel fill as a hexadecimal color.",
    )
    cncjob_plot_kind: str = Field(
        default="all", description="Default CNC job plot kind."
    )
    cncjob_annotation: bool = Field(
        default=True, description="Whether CNC job annotation is enabled."
    )
    cncjob_annotation_fontsize: int = Field(
        default=9, description="Default CNC job annotation font size."
    )
    cncjob_annotation_fontcolor: str = Field(
        default="#990000", description="Default CNC job annotation font color."
    )
    cncjob_prepend: str = Field(default="", description="Default CNC job prepend.")
    cncjob_append: str = Field(default="", description="Default CNC job append.")
    tools_follow_simplification: bool = Field(
        default=False, description="Whether Follow tool simplification is enabled."
    )
    tools_follow_tolerance: float = Field(
        default=0.01, description="Default Follow tool tolerance."
    )
    tools_follow_union: bool = Field(
        default=False, description="Whether Follow tool union is enabled."
    )
    tools_iso_tooldia: str = Field(
        default="0.1", description="Default isolation routing tool diameter."
    )
    tools_iso_order: int = Field(
        default=2, description="Default isolation routing order."
    )
    tools_iso_tool_cutz: float = Field(
        default=-0.05, description="Default isolation routing tool cutting Z depth."
    )
    tools_iso_newdia: float = Field(
        default=0.1, description="Default isolation routing new tool diameter."
    )
    tools_iso_tool_shape: int = Field(
        default=0, description="Default isolation routing tool shape."
    )
    tools_iso_cutz: float = Field(
        default=-0.07, description="Default isolation routing cutting Z depth."
    )
    tools_iso_vtipdia: float = Field(
        default=0.1, description="Default isolation routing V-tip diameter."
    )
    tools_iso_vtipangle: int = Field(
        default=30, description="Default isolation routing V-tip angle."
    )
    tools_iso_passes: int = Field(
        default=1, description="Default isolation routing passes."
    )
    tools_iso_pad_passes: int = Field(
        default=0, description="Default isolation routing pad passes."
    )
    tools_iso_overlap: int = Field(
        default=10, description="Default isolation routing overlap as a percentage."
    )
    tools_iso_milling_type: str = Field(
        default="cl", description="Default isolation routing milling type."
    )
    tools_iso_isotype: str = Field(
        default="full", description="Default isolation routing isolation type."
    )
    tools_iso_rest: bool = Field(
        default=False, description="Whether isolation routing rest is enabled."
    )
    tools_iso_combine_passes: bool = Field(
        default=True, description="Whether isolation routing combine passes is enabled."
    )
    tools_iso_check_valid: bool = Field(
        default=False, description="Whether isolation routing check valid is enabled."
    )
    tools_iso_isoexcept: bool = Field(
        default=False,
        description="Whether isolation routing isolation exclusion is enabled.",
    )
    tools_iso_selection: int = Field(
        default=0, description="Default isolation routing selection."
    )
    tools_iso_poly_ints: bool = Field(
        default=False,
        description="Whether isolation routing polygon interiors is enabled.",
    )
    tools_iso_force: bool = Field(
        default=True, description="Whether isolation routing force is enabled."
    )
    tools_iso_area_shape: str = Field(
        default="square", description="Default isolation routing area shape."
    )
    tools_iso_simplification: bool = Field(
        default=False,
        description="Whether isolation routing simplification is enabled.",
    )
    tools_iso_simplification_tol: float = Field(
        default=0.01,
        description="Geometry simplification tolerance for isolation routing.",
    )
    tools_iso_plotting: str = Field(
        default="normal", description="Default isolation routing plotting."
    )
    tools_drill_tool_order: str = Field(
        default="no", description="Default drilling tool order."
    )
    tools_drill_cutz: float = Field(
        default=-1.7, description="Default drilling cutting Z depth."
    )
    tools_drill_multidepth: bool = Field(
        default=False, description="Whether drilling multiple-depth cutting is enabled."
    )
    tools_drill_depthperpass: float = Field(
        default=0.7, description="Default drilling depth per pass."
    )
    tools_drill_travelz: int = Field(
        default=2, description="Default drilling travel Z height."
    )
    tools_drill_endz: int = Field(
        default=15, description="Default drilling ending Z height."
    )
    tools_drill_endxy: str | tuple[float, float] | list[float] | None = Field(
        default=None, description="Drilling job ending XY coordinates."
    )
    tools_drill_feedrate_z: int = Field(
        default=300, description="Default drilling feed rate Z."
    )
    tools_drill_spindlespeed: int = Field(
        default=0, description="Default drilling spindle speed."
    )
    tools_drill_dwell: bool = Field(
        default=False, description="Whether drilling spindle dwell is enabled."
    )
    tools_drill_dwelltime: int = Field(
        default=1, description="Default drilling dwell time."
    )
    tools_drill_min_power: float = Field(
        default=0.0, description="Default drilling min power."
    )
    tools_drill_laser_on: str = Field(
        default="M3", description="Default drilling laser on."
    )
    tools_drill_toolchange: bool = Field(
        default=False, description="Whether drilling jobs include tool-change commands."
    )
    tools_drill_toolchangez: int = Field(
        default=15, description="Default drilling tool-change Z height."
    )
    tools_drill_preprocessor_list: list[str] = Field(
        default_factory=lambda: ["default"],
        description="Available drilling preprocessor list values.",
    )
    tools_drill_ppname_e: str = Field(
        default="default", description="Default drilling preprocessor name e."
    )
    tools_drill_drill_slots: bool = Field(
        default=False, description="Whether drilling drill slots is enabled."
    )
    tools_drill_drill_overlap: float = Field(
        default=0.0, description="Default drilling drill overlap as a percentage."
    )
    tools_drill_last_drill: bool = Field(
        default=True, description="Whether drilling last drill is enabled."
    )
    tools_drill_offset: float = Field(
        default=0.0, description="Default drilling offset."
    )
    tools_drill_toolchangexy: str = Field(
        default="0.0, 0.0",
        description="Drilling tool-change XY coordinates as an X, Y pair.",
    )
    tools_drill_startz: float | None = Field(
        default=None, description="Default drilling starting Z height."
    )
    tools_drill_feedrate_rapid: int = Field(
        default=1500, description="Default drilling feed rate rapid."
    )
    tools_drill_z_p_depth: float = Field(
        default=-0.02, description="Default drilling Z p depth."
    )
    tools_drill_feedrate_probe: int = Field(
        default=75, description="Default drilling feed rate probe."
    )
    tools_drill_spindledir: str = Field(
        default="CW", description="Default drilling spindle direction."
    )
    tools_drill_f_plunge: bool = Field(
        default=False,
        description="Whether drilling uses the configured plunge feed rate.",
    )
    tools_drill_f_retract: bool = Field(
        default=False,
        description="Whether drilling uses the configured retract feed rate.",
    )
    tools_drill_area_exclusion: bool = Field(
        default=False, description="Whether drilling area exclusion is enabled."
    )
    tools_drill_area_shape: str = Field(
        default="polygon", description="Default drilling area shape."
    )
    tools_drill_area_strategy: str = Field(
        default="over", description="Default drilling area strategy."
    )
    tools_drill_area_overz: float = Field(
        default=1.0, description="Travel Z height used over excluded drilling areas."
    )
    tools_mill_tooldia: str = Field(
        default="2.4", description="Default milling tool diameter."
    )
    tools_mill_offset_type: int = Field(
        default=0, description="Default milling offset type."
    )
    tools_mill_offset_value: float = Field(
        default=0.0, description="Default milling offset value."
    )
    tools_mill_job_type: int = Field(default=0, description="Default milling job type.")
    tools_mill_tool_shape: int = Field(
        default=0, description="Default milling tool shape."
    )
    tools_mill_cutz: float = Field(
        default=-2.4, description="Default milling cutting Z depth."
    )
    tools_mill_vtipdia: float = Field(
        default=0.1, description="Default milling V-tip diameter."
    )
    tools_mill_vtipangle: int = Field(
        default=30, description="Default milling V-tip angle."
    )
    tools_mill_multidepth: bool = Field(
        default=False, description="Whether milling multiple-depth cutting is enabled."
    )
    tools_mill_depthperpass: float = Field(
        default=0.8, description="Default milling depth per pass."
    )
    tools_mill_travelz: int = Field(
        default=2, description="Default milling travel Z height."
    )
    tools_mill_toolchange: bool = Field(
        default=False, description="Whether milling jobs include tool-change commands."
    )
    tools_mill_toolchangez: float = Field(
        default=15.0, description="Default milling tool-change Z height."
    )
    tools_mill_endz: float = Field(
        default=15.0, description="Default milling ending Z height."
    )
    tools_mill_endxy: str | tuple[float, float] | list[float] | None = Field(
        default=None, description="Milling job ending XY coordinates."
    )
    tools_mill_feedrate: int = Field(
        default=120, description="Default milling feed rate."
    )
    tools_mill_feedrate_z: int = Field(
        default=60, description="Default milling feed rate Z."
    )
    tools_mill_min_power: float = Field(
        default=0.0, description="Default milling min power."
    )
    tools_mill_laser_on: str = Field(
        default="M3", description="Default milling laser on."
    )
    tools_mill_spindlespeed: int = Field(
        default=0, description="Default milling spindle speed."
    )
    tools_mill_dwell: bool = Field(
        default=False, description="Whether milling spindle dwell is enabled."
    )
    tools_mill_dwelltime: int = Field(
        default=1, description="Default milling dwell time."
    )
    tools_mill_preprocessor_list: list[str] = Field(
        default_factory=lambda: ["default"],
        description="Available milling preprocessor list values.",
    )
    tools_mill_ppname_g: str = Field(
        default="default", description="Default milling preprocessor name g."
    )
    tools_mill_toolchangexy: str = Field(
        default="0.0, 0.0",
        description="Milling tool-change XY coordinates as an X, Y pair.",
    )
    tools_mill_startz: float | None = Field(
        default=None, description="Default milling starting Z height."
    )
    tools_mill_feedrate_rapid: int = Field(
        default=1500, description="Default milling feed rate rapid."
    )
    tools_mill_extracut: bool = Field(
        default=False,
        description="Whether milling paths extend past their closing point.",
    )
    tools_mill_extracut_length: float = Field(
        default=0.1, description="Length added past a milling path closing point."
    )
    tools_mill_z_p_depth: float = Field(
        default=-0.02, description="Default milling Z p depth."
    )
    tools_mill_feedrate_probe: int = Field(
        default=75, description="Default milling feed rate probe."
    )
    tools_mill_f_plunge: bool = Field(
        default=False,
        description="Whether milling uses the configured plunge feed rate.",
    )
    tools_mill_spindledir: str = Field(
        default="CW", description="Default milling spindle direction."
    )
    tools_mill_area_exclusion: bool = Field(
        default=False, description="Whether milling area exclusion is enabled."
    )
    tools_mill_area_shape: str = Field(
        default="polygon", description="Default milling area shape."
    )
    tools_mill_area_strategy: str = Field(
        default="over", description="Default milling area strategy."
    )
    tools_mill_area_overz: float = Field(
        default=1.0, description="Travel Z height used over excluded milling areas."
    )
    tools_mill_polish: bool = Field(
        default=False, description="Whether milling polish is enabled."
    )
    tools_mill_polish_margin: float = Field(
        default=0.0, description="Default milling polish margin."
    )
    tools_mill_polish_overlap: int = Field(
        default=5, description="Default milling polish overlap as a percentage."
    )
    tools_mill_polish_method: int = Field(
        default=0, description="Default milling polish method."
    )
    tools_mill_milling_type: str = Field(
        default="both", description="Default milling direction type."
    )
    tools_mill_milling_dia: float = Field(
        default=0.1, description="Tool diameter used for milling drilled holes."
    )
    tools_mill_milling_overlap: int = Field(
        default=10, description="Overlap between hole-milling passes as a percentage."
    )
    tools_mill_milling_connect: bool = Field(
        default=True, description="Whether adjacent hole-milling paths are connected."
    )
    tools_mill_optimization_type: str = Field(
        default="R", description="Default milling optimization type."
    )
    tools_mill_search_time: int = Field(
        default=3, description="Default milling search time."
    )
    tools_al_plot_points: bool = Field(
        default=False, description="Whether auto-leveling plot points is enabled."
    )
    tools_al_avoid_exc_holes: bool = Field(
        default=False,
        description="Whether auto-leveling avoid Excellon holes is enabled.",
    )
    tools_al_avoid_exc_holes_size: float = Field(
        default=0.5, description="Default auto-leveling avoid Excellon holes size."
    )
    tools_al_status: bool = Field(
        default=False, description="Whether auto-leveling status is enabled."
    )
    tools_al_mode: str = Field(
        default="grid", description="Default auto-leveling mode."
    )
    tools_al_method: str = Field(
        default="v", description="Default auto-leveling method."
    )
    tools_al_rows: int = Field(default=4, description="Default auto-leveling rows.")
    tools_al_columns: int = Field(
        default=4, description="Default auto-leveling columns."
    )
    tools_al_travel_z: float = Field(
        default=2.0, description="Default auto-leveling travel Z."
    )
    tools_al_probe_depth: float = Field(
        default=-1.0, description="Default auto-leveling probe depth."
    )
    tools_al_probe_fr: int = Field(
        default=120, description="Default auto-leveling probe feed-rate."
    )
    tools_al_probe_tip_dia: float = Field(
        default=0.3, description="Default auto-leveling probe tip diameter."
    )
    tools_al_controller: str = Field(
        default="MACH3", description="Default auto-leveling controller."
    )
    tools_al_grbl_jog_step: int = Field(
        default=5, description="Default auto-leveling GRBL jog step."
    )
    tools_al_grbl_jog_fr: int = Field(
        default=1500, description="Default auto-leveling GRBL jog feed-rate."
    )
    tools_al_grbl_travelz: float = Field(
        default=15.0, description="Default auto-leveling GRBL travel Z height."
    )
    tools_ncc_tools: str = Field(
        default="0.5", description="Default non-copper clearing tools."
    )
    tools_ncc_order: int = Field(
        default=2, description="Default non-copper clearing order."
    )
    tools_ncc_operation: str = Field(
        default="clear", description="Default non-copper clearing operation."
    )
    tools_ncc_overlap: int = Field(
        default=40, description="Default non-copper clearing overlap as a percentage."
    )
    tools_ncc_margin: float = Field(
        default=1.0, description="Default non-copper clearing margin."
    )
    tools_ncc_method: int = Field(
        default=1, description="Default non-copper clearing method."
    )
    tools_ncc_connect: bool = Field(
        default=True, description="Whether non-copper clearing connect is enabled."
    )
    tools_ncc_contour: bool = Field(
        default=True, description="Whether non-copper clearing contour is enabled."
    )
    tools_ncc_rest: bool = Field(
        default=False, description="Whether non-copper clearing rest is enabled."
    )
    tools_ncc_offset_choice: bool = Field(
        default=False,
        description="Whether non-copper clearing offset choice is enabled.",
    )
    tools_ncc_offset_value: float = Field(
        default=0.0000, description="Default non-copper clearing offset value."
    )
    tools_ncc_ref: int = Field(
        default=0, description="Default non-copper clearing reference."
    )
    tools_ncc_area_shape: str = Field(
        default="square", description="Default non-copper clearing area shape."
    )
    tools_ncc_milling_type: str = Field(
        default="cl", description="Default non-copper clearing milling type."
    )
    tools_ncc_cutz: float = Field(
        default=-0.05, description="Default non-copper clearing cutting Z depth."
    )
    tools_ncc_tipdia: float = Field(
        default=0.1, description="Default non-copper clearing tip diameter."
    )
    tools_ncc_tipangle: int = Field(
        default=30, description="Default non-copper clearing tip angle in degrees."
    )
    tools_ncc_newdia: float = Field(
        default=0.1, description="Default non-copper clearing new tool diameter."
    )
    tools_ncc_plotting: str = Field(
        default="normal", description="Default non-copper clearing plotting."
    )
    tools_ncc_check_valid: bool = Field(
        default=True, description="Whether non-copper clearing check valid is enabled."
    )
    tools_cutout_tooldia: float = Field(
        default=2.4, description="Default board cutout tool diameter."
    )
    tools_cutout_kind: str = Field(
        default="single", description="Default board cutout kind."
    )
    tools_cutout_margin: float = Field(
        default=0.1, description="Default board cutout margin."
    )
    tools_cutout_z: float = Field(default=-1.8, description="Default board cutout Z.")
    tools_cutout_depthperpass: float = Field(
        default=0.6, description="Default board cutout depth per pass."
    )
    tools_cutout_mdepth: bool = Field(
        default=True,
        description="Whether board cutout multiple-depth cutting is enabled.",
    )
    tools_cutout_gapsize: int = Field(
        default=4, description="Default board cutout gapsize."
    )
    tools_cutout_gaps_ff: str = Field(
        default="4", description="Default board cutout gaps ff."
    )
    tools_cutout_convexshape: bool = Field(
        default=False, description="Whether board cutout convexshape is enabled."
    )
    tools_cutout_big_cursor: bool = Field(
        default=True, description="Whether board cutout big cursor is enabled."
    )
    tools_cutout_gap_type: int = Field(
        default=0, description="Default board cutout gap type."
    )
    tools_cutout_gap_depth: float = Field(
        default=-1.0, description="Default board cutout gap depth."
    )
    tools_cutout_mb_dia: float = Field(
        default=0.6, description="Default board cutout mouse-bite diameter."
    )
    tools_cutout_mb_spacing: float = Field(
        default=0.3, description="Default board cutout mouse-bite spacing."
    )
    tools_cutout_drill_dia: float = Field(
        default=1.0, description="Default board cutout drill diameter."
    )
    tools_cutout_drill_pitch: float = Field(
        default=1.0, description="Default board cutout drill pitch."
    )
    tools_cutout_drill_margin: float = Field(
        default=0.0, description="Default board cutout drill margin."
    )
    tools_paint_tooldia: float = Field(
        default=0.3, description="Default paint tool diameter."
    )
    tools_paint_order: int = Field(default=2, description="Default paint order.")
    tools_paint_overlap: int = Field(
        default=20, description="Default paint overlap as a percentage."
    )
    tools_paint_offset: float = Field(default=0.0, description="Default paint offset.")
    tools_paint_method: int = Field(default=0, description="Default paint method.")
    tools_paint_selectmethod: int = Field(
        default=0, description="Default paint selectmethod."
    )
    tools_paint_area_shape: str = Field(
        default="square", description="Default paint area shape."
    )
    tools_paint_connect: bool = Field(
        default=True, description="Whether paint connect is enabled."
    )
    tools_paint_contour: bool = Field(
        default=True, description="Whether paint contour is enabled."
    )
    tools_paint_plotting: str = Field(
        default="normal", description="Default paint plotting."
    )
    tools_paint_rest: bool = Field(
        default=False, description="Whether paint rest is enabled."
    )
    tools_paint_cutz: float = Field(
        default=-0.05, description="Default paint cutting Z depth."
    )
    tools_paint_tipdia: float = Field(
        default=0.1, description="Default paint tip diameter."
    )
    tools_paint_tipangle: int = Field(
        default=30, description="Default paint tip angle in degrees."
    )
    tools_paint_newdia: float = Field(
        default=0.1, description="Default paint new tool diameter."
    )
    tools_2sided_mirror_axis: str = Field(
        default="X", description="Default double-sided PCB mirror axis."
    )
    tools_2sided_axis_loc: str = Field(
        default="point", description="Default double-sided PCB axis loc."
    )
    tools_2sided_drilldia: float = Field(
        default=3.125, description="Default double-sided PCB drill diameter."
    )
    tools_2sided_align_type: str = Field(
        default="X", description="Default double-sided PCB alignment type."
    )
    tools_film_shape: bool = Field(
        default=False, description="Whether film export shape is enabled."
    )
    tools_film_rounded: bool = Field(
        default=False, description="Whether film export rounded is enabled."
    )
    tools_film_polarity: str = Field(
        default="neg", description="Default film export polarity."
    )
    tools_film_boundary: float = Field(
        default=1.0, description="Default film export boundary."
    )
    tools_film_scale_stroke: int = Field(
        default=0, description="Default film export scale stroke."
    )
    tools_film_color: str = Field(
        default="#000000",
        description="Default film export color as a hexadecimal color.",
    )
    tools_film_scale_cb: bool = Field(
        default=False,
        description="Whether film export scale operation enabled is enabled.",
    )
    tools_film_scale_type: int = Field(
        default=0, description="Default film export scale type."
    )
    tools_film_scale_x_entry: float = Field(
        default=0.0, description="Default film export scale X entry."
    )
    tools_film_scale_y_entry: float = Field(
        default=0.0, description="Default film export scale Y entry."
    )
    tools_film_scale_ref: int = Field(
        default=1, description="Default film export scale reference."
    )
    tools_film_skew_cb: bool = Field(
        default=False,
        description="Whether film export skew operation enabled is enabled.",
    )
    tools_film_skew_type: int = Field(
        default=0, description="Default film export skew type."
    )
    tools_film_skew_x_entry: float = Field(
        default=0.0, description="Default film export skew X entry."
    )
    tools_film_skew_y_entry: float = Field(
        default=0.0, description="Default film export skew Y entry."
    )
    tools_film_skew_ref: int = Field(
        default=1, description="Default film export skew reference."
    )
    tools_film_mirror_cb: bool = Field(
        default=False,
        description="Whether film export mirror operation enabled is enabled.",
    )
    tools_film_mirror_axis_radio: str = Field(
        default="x", description="Default film export mirror axis radio."
    )
    tools_film_file_type_radio: str = Field(
        default="svg", description="Default film export file type radio."
    )
    tools_film_orientation: str = Field(
        default="p", description="Default film export orientation."
    )
    tools_film_pagesize: str = Field(
        default="A4", description="Default film export pagesize."
    )
    tools_film_png_dpi: int = Field(
        default=96, description="Default film export png resolution in dots per inch."
    )
    tools_panelize_spacing_columns: float = Field(
        default=0.0, description="Default panelization spacing columns."
    )
    tools_panelize_spacing_rows: float = Field(
        default=0.0, description="Default panelization spacing rows."
    )
    tools_panelize_columns: int = Field(
        default=1, description="Default panelization columns."
    )
    tools_panelize_rows: int = Field(
        default=1, description="Default panelization rows."
    )
    tools_panelize_optimization: bool = Field(
        default=True, description="Whether panelization optimization is enabled."
    )
    tools_panelize_constrain: bool = Field(
        default=False, description="Whether panelization constrain is enabled."
    )
    tools_panelize_constrainx: float = Field(
        default=200.0, description="Default panelization constrainx."
    )
    tools_panelize_constrainy: float = Field(
        default=290.0, description="Default panelization constrainy."
    )
    tools_panelize_panel_type: str = Field(
        default="gerber", description="Default panelization panel type."
    )
    tools_calc_vshape_tip_dia: float = Field(
        default=0.2, description="Default calculator vshape tip diameter."
    )
    tools_calc_vshape_tip_angle: int = Field(
        default=30, description="Default calculator vshape tip angle in degrees."
    )
    tools_calc_vshape_cut_z: float = Field(
        default=-0.05, description="Default calculator vshape cut Z."
    )
    tools_calc_electro_length: float = Field(
        default=10.0, description="Default calculator electroplating length."
    )
    tools_calc_electro_width: float = Field(
        default=10.0, description="Default calculator electroplating width."
    )
    tools_calc_electro_area: float = Field(
        default=100.0, description="Default calculator electroplating area."
    )
    tools_calc_electro_cdensity: float = Field(
        default=13.0, description="Default calculator electroplating current density."
    )
    tools_calc_electro_growth: float = Field(
        default=10.0, description="Default calculator electroplating growth."
    )
    tools_transform_reference: str = Field(
        default=_("Selection"), description="Default object transformation reference."
    )
    tools_transform_ref_object: str = Field(
        default=_("Gerber"),
        description="Default object transformation reference object.",
    )
    tools_transform_ref_point: str = Field(
        default="0, 0", description="Transformation reference point as an X, Y pair."
    )
    tools_transform_rotate: int = Field(
        default=90, description="Default object transformation rotate."
    )
    tools_transform_skew_x: float = Field(
        default=0.0, description="Default object transformation skew X."
    )
    tools_transform_skew_y: float = Field(
        default=0.0, description="Default object transformation skew Y."
    )
    tools_transform_skew_link: bool = Field(
        default=True, description="Whether object transformation skew link is enabled."
    )
    tools_transform_scale_x: float = Field(
        default=1.0, description="Default object transformation scale X."
    )
    tools_transform_scale_y: float = Field(
        default=1.0, description="Default object transformation scale Y."
    )
    tools_transform_scale_link: bool = Field(
        default=True, description="Whether object transformation scale link is enabled."
    )
    tools_transform_offset_x: float = Field(
        default=0.0, description="Default object transformation offset X."
    )
    tools_transform_offset_y: float = Field(
        default=0.0, description="Default object transformation offset Y."
    )
    tools_transform_buffer_dis: float = Field(
        default=0.0, description="Default object transformation buffer distance."
    )
    tools_transform_buffer_factor: float = Field(
        default=100.0, description="Default object transformation buffer factor."
    )
    tools_transform_buffer_corner: bool = Field(
        default=True,
        description="Whether object transformation buffer corner is enabled.",
    )
    tools_solderpaste_tools: str = Field(
        default="1.0, 0.3", description="Default solder-paste dispensing tools."
    )
    tools_solderpaste_new: float = Field(
        default=0.3, description="Default solder-paste dispensing new."
    )
    tools_solderpaste_margin: float = Field(
        default=0.0, description="Default solder-paste dispensing margin."
    )
    tools_solderpaste_z_start: float = Field(
        default=0.05, description="Default solder-paste dispensing Z start."
    )
    tools_solderpaste_z_dispense: float = Field(
        default=0.1, description="Default solder-paste dispensing Z dispense."
    )
    tools_solderpaste_z_stop: float = Field(
        default=0.05, description="Default solder-paste dispensing Z stop."
    )
    tools_solderpaste_z_travel: float = Field(
        default=0.1, description="Default solder-paste dispensing Z travel."
    )
    tools_solderpaste_z_toolchange: float = Field(
        default=1.0, description="Tool-change Z height for solder-paste dispensing."
    )
    tools_solderpaste_xy_toolchange: str = Field(
        default="0.0, 0.0",
        description="Solder-paste tool-change XY coordinates as an X, Y pair.",
    )
    tools_solderpaste_frxy: int = Field(
        default=150, description="Default solder-paste dispensing XY feed rate."
    )
    tools_solderpaste_fr_rapids: int = Field(
        default=1500,
        description="Default solder-paste dispensing feed-rate rapid-move feed rate.",
    )
    tools_solderpaste_frz: int = Field(
        default=150, description="Default solder-paste dispensing Z feed rate."
    )
    tools_solderpaste_frz_dispense: float = Field(
        default=1.0, description="Default solder-paste dispensing Z feed rate dispense."
    )
    tools_solderpaste_speedfwd: int = Field(
        default=300,
        description="Default solder-paste dispensing forward dispensing speed.",
    )
    tools_solderpaste_dwellfwd: int = Field(
        default=1,
        description="Default solder-paste dispensing forward dispensing dwell time.",
    )
    tools_solderpaste_speedrev: int = Field(
        default=200,
        description="Default solder-paste dispensing reverse dispensing speed.",
    )
    tools_solderpaste_dwellrev: int = Field(
        default=1,
        description="Default solder-paste dispensing reverse dispensing dwell time.",
    )
    tools_solderpaste_preprocessor_list: list[str] = Field(
        default_factory=lambda: ["default"],
        description="Available solder-paste dispensing preprocessor list values.",
    )
    tools_solderpaste_pp: str = Field(
        default="Paste_1", description="Default solder-paste dispensing preprocessor."
    )
    tools_sub_close_paths: bool = Field(
        default=True, description="Whether subtraction close paths is enabled."
    )
    tools_sub_delete_sources: bool = Field(
        default=False, description="Whether subtraction delete sources is enabled."
    )
    tools_dist_snap_center: bool = Field(
        default=False,
        description="Whether distance measurement snap center is enabled.",
    )
    tools_dist_big_cursor: bool = Field(
        default=True, description="Whether distance measurement big cursor is enabled."
    )
    tools_markers_thickness: float = Field(
        default=0.1, description="Default marker thickness."
    )
    tools_markers_length: float = Field(
        default=3.0, description="Default marker length."
    )
    tools_markers_reference: str = Field(
        default="e", description="Default marker reference."
    )
    tools_markers_offset_x: float = Field(
        default=0.0, description="Default marker offset X."
    )
    tools_markers_offset_y: float = Field(
        default=0.0, description="Default marker offset Y."
    )
    tools_markers_type: str = Field(default="s", description="Default marker type.")
    tools_markers_drill_dia: float = Field(
        default=0.5, description="Default marker drill diameter."
    )
    tools_markers_mode: int = Field(default=0, description="Default marker mode.")
    tools_markers_big_cursor: bool = Field(
        default=True, description="Whether marker big cursor is enabled."
    )
    tools_opt_precision: int = Field(
        default=4, description="Default path optimization precision."
    )
    tools_cr_trace_size: bool = Field(
        default=True, description="Whether design-rule check trace size is enabled."
    )
    tools_cr_trace_size_val: float = Field(
        default=0.25, description="Minimum trace width checked by the design-rule tool."
    )
    tools_cr_c2c: bool = Field(
        default=True,
        description="Whether design-rule check copper-to-copper clearance is enabled.",
    )
    tools_cr_c2c_val: float = Field(
        default=0.25,
        description="Minimum copper-to-copper clearance checked by the design-rule tool.",
    )
    tools_cr_c2o: bool = Field(
        default=True,
        description="Whether design-rule check copper-to-outline clearance is enabled.",
    )
    tools_cr_c2o_val: float = Field(
        default=1.0,
        description="Minimum copper-to-outline clearance checked by the design-rule tool.",
    )
    tools_cr_s2s: bool = Field(
        default=True,
        description="Whether design-rule check silkscreen-to-silkscreen clearance is enabled.",
    )
    tools_cr_s2s_val: float = Field(
        default=0.25,
        description="Minimum silkscreen-to-silkscreen clearance checked by the design-rule tool.",
    )
    tools_cr_s2sm: bool = Field(
        default=True,
        description="Whether design-rule check silkscreen-to-solder-mask clearance is enabled.",
    )
    tools_cr_s2sm_val: float = Field(
        default=0.25,
        description="Minimum silkscreen-to-solder-mask clearance checked by the design-rule tool.",
    )
    tools_cr_s2o: bool = Field(
        default=True,
        description="Whether design-rule check silkscreen-to-outline clearance is enabled.",
    )
    tools_cr_s2o_val: float = Field(
        default=1.0,
        description="Minimum silkscreen-to-outline clearance checked by the design-rule tool.",
    )
    tools_cr_sm2sm: bool = Field(
        default=True,
        description="Whether design-rule check solder-mask-to-solder-mask clearance is enabled.",
    )
    tools_cr_sm2sm_val: float = Field(
        default=0.25,
        description="Minimum solder-mask-to-solder-mask clearance checked by the design-rule tool.",
    )
    tools_cr_ri: bool = Field(
        default=True, description="Whether design-rule check ring integrity is enabled."
    )
    tools_cr_ri_val: float = Field(
        default=0.3,
        description="Minimum annular-ring width checked by the design-rule tool.",
    )
    tools_cr_h2h: bool = Field(
        default=True,
        description="Whether design-rule check hole-to-hole clearance is enabled.",
    )
    tools_cr_h2h_val: float = Field(
        default=0.3,
        description="Minimum hole-to-hole clearance checked by the design-rule tool.",
    )
    tools_cr_dh: bool = Field(
        default=True,
        description="Whether design-rule check drill-hole clearance is enabled.",
    )
    tools_cr_dh_val: float = Field(
        default=0.3,
        description="Minimum drill-hole clearance checked by the design-rule tool.",
    )
    tools_qrcode_version: int = Field(default=1, description="QR code version number.")
    tools_qrcode_error: str = Field(
        default="L", description="QR code error-correction level."
    )
    tools_qrcode_box_size: int = Field(
        default=3, description="Default QR code box size."
    )
    tools_qrcode_border_size: int = Field(
        default=4, description="Default QR code border size."
    )
    tools_qrcode_qrdata: str = Field(
        default="", description="Default QR code encoded data."
    )
    tools_qrcode_polarity: str = Field(
        default="pos", description="Default QR code polarity."
    )
    tools_qrcode_rounded: str = Field(
        default="s", description="Default QR code rounded."
    )
    tools_qrcode_fill_color: str = Field(
        default="#000000",
        description="Default QR code fill color as a hexadecimal color.",
    )
    tools_qrcode_back_color: str = Field(
        default="#FFFFFF",
        description="Default QR code back color as a hexadecimal color.",
    )
    tools_qrcode_sel_limit: int = Field(
        default=330, description="Default QR code selection limit."
    )
    tools_copper_thieving_clearance: float = Field(
        default=0.25, description="Default copper-thieving clearance."
    )
    tools_copper_thieving_margin: float = Field(
        default=1.0, description="Default copper-thieving margin."
    )
    tools_copper_thieving_area: float = Field(
        default=0.1, description="Default copper-thieving area."
    )
    tools_copper_thieving_reference: str = Field(
        default="itself", description="Default copper-thieving reference."
    )
    tools_copper_thieving_box_type: str = Field(
        default="rect", description="Default copper-thieving box type."
    )
    tools_copper_thieving_circle_steps: int = Field(
        default=16, description="Default copper-thieving circle steps."
    )
    tools_copper_thieving_fill_type: str = Field(
        default="solid", description="Copper-thieving fill pattern."
    )
    tools_copper_thieving_dots_dia: float = Field(
        default=1.0, description="Default copper-thieving dots diameter."
    )
    tools_copper_thieving_dots_spacing: float = Field(
        default=2.0, description="Default copper-thieving dots spacing."
    )
    tools_copper_thieving_squares_size: float = Field(
        default=1.0, description="Default copper-thieving squares size."
    )
    tools_copper_thieving_squares_spacing: float = Field(
        default=2.0, description="Default copper-thieving squares spacing."
    )
    tools_copper_thieving_lines_size: float = Field(
        default=0.25, description="Default copper-thieving lines size."
    )
    tools_copper_thieving_lines_spacing: float = Field(
        default=2.0, description="Default copper-thieving lines spacing."
    )
    tools_copper_thieving_rb_margin: float = Field(
        default=1.0, description="Default copper-thieving robber-bar margin."
    )
    tools_copper_thieving_rb_thickness: float = Field(
        default=1.0, description="Default copper-thieving robber-bar thickness."
    )
    tools_copper_thieving_only_apds: bool = Field(
        default=True,
        description="Whether copper-thieving use only apertures is enabled.",
    )
    tools_copper_thieving_mask_clearance: float = Field(
        default=0.0, description="Default copper-thieving mask clearance."
    )
    tools_copper_thieving_geo_choice: str = Field(
        default="b", description="Default copper-thieving geometry choice."
    )
    tools_fiducials_dia: float = Field(
        default=1.0, description="Default fiducial diameter."
    )
    tools_fiducials_margin: float = Field(
        default=1.0, description="Default fiducial margin."
    )
    tools_fiducials_mode: str = Field(
        default="auto", description="Default fiducial mode."
    )
    tools_fiducials_second_pos: str = Field(
        default="up", description="Position of the second fiducial marker."
    )
    tools_fiducials_type: str = Field(
        default="circular", description="Default fiducial type."
    )
    tools_fiducials_line_thickness: float = Field(
        default=0.25, description="Default fiducial line thickness."
    )
    tools_fiducials_big_cursor: bool = Field(
        default=True, description="Whether fiducial big cursor is enabled."
    )
    tools_extract_hole_type: str = Field(
        default="fixed", description="Default drill extraction hole type."
    )
    tools_extract_hole_fixed_dia: float = Field(
        default=0.5, description="Default drill extraction hole fixed diameter."
    )
    tools_extract_hole_prop_factor: float = Field(
        default=80.0,
        description="Default drill extraction hole proportional factor as a percentage.",
    )
    tools_extract_circular_ring: float = Field(
        default=0.2, description="Default drill extraction circular ring."
    )
    tools_extract_oblong_ring: float = Field(
        default=0.2, description="Default drill extraction oblong ring."
    )
    tools_extract_square_ring: float = Field(
        default=0.2, description="Default drill extraction square ring."
    )
    tools_extract_rectangular_ring: float = Field(
        default=0.2, description="Default drill extraction rectangular ring."
    )
    tools_extract_others_ring: float = Field(
        default=0.2, description="Default drill extraction others ring."
    )
    tools_extract_circular: bool = Field(
        default=True, description="Whether drill extraction circular is enabled."
    )
    tools_extract_oblong: bool = Field(
        default=False, description="Whether drill extraction oblong is enabled."
    )
    tools_extract_square: bool = Field(
        default=False, description="Whether drill extraction square is enabled."
    )
    tools_extract_rectangular: bool = Field(
        default=False, description="Whether drill extraction rectangular is enabled."
    )
    tools_extract_others: bool = Field(
        default=False, description="Whether drill extraction others is enabled."
    )
    tools_extract_sm_clearance: float = Field(
        default=0.1, description="Default drill extraction solder-mask clearance."
    )
    tools_extract_cut_margin: float = Field(
        default=0.1, description="Default drill extraction cut margin."
    )
    tools_extract_cut_thickness: float = Field(
        default=0.1, description="Default drill extraction cut thickness."
    )
    tools_punch_hole_type: str = Field(
        default="exc", description="Default Gerber hole punching hole type."
    )
    tools_punch_hole_fixed_dia: float = Field(
        default=0.5, description="Default Gerber hole punching hole fixed diameter."
    )
    tools_punch_hole_prop_factor: float = Field(
        default=80.0,
        description="Default Gerber hole punching hole proportional factor as a percentage.",
    )
    tools_punch_circular_ring: float = Field(
        default=0.2, description="Default Gerber hole punching circular ring."
    )
    tools_punch_oblong_ring: float = Field(
        default=0.2, description="Default Gerber hole punching oblong ring."
    )
    tools_punch_square_ring: float = Field(
        default=0.2, description="Default Gerber hole punching square ring."
    )
    tools_punch_rectangular_ring: float = Field(
        default=0.2, description="Default Gerber hole punching rectangular ring."
    )
    tools_punch_others_ring: float = Field(
        default=0.2, description="Default Gerber hole punching others ring."
    )
    tools_punch_circular: bool = Field(
        default=True, description="Whether Gerber hole punching circular is enabled."
    )
    tools_punch_oblong: bool = Field(
        default=False, description="Whether Gerber hole punching oblong is enabled."
    )
    tools_punch_square: bool = Field(
        default=True, description="Whether Gerber hole punching square is enabled."
    )
    tools_punch_rectangular: bool = Field(
        default=False,
        description="Whether Gerber hole punching rectangular is enabled.",
    )
    tools_punch_others: bool = Field(
        default=False, description="Whether Gerber hole punching others is enabled."
    )
    tools_align_objects_align_type: str = Field(
        default="sp", description="Default object alignment method."
    )
    tools_invert_margin: float = Field(
        default=0.1, description="Default Gerber inversion margin."
    )
    tools_invert_join_style: str = Field(
        default="s", description="Default Gerber inversion join style."
    )
    fa_excellon: str = Field(
        default="drd, drill, drl, exc, ncd, tap, xln",
        description="Comma-separated filename extensions recognized as Excellon files.",
    )
    fa_gcode: str = Field(
        default="cnc, din, dnc, ecs, eia, fan, fgc, fnc, gc, gcd, gcode, h, hnc, i, min, mpf, mpr, nc, ncc, "
        "ncg, ncp, ngc, out, ply, rol, sbp, tap, xpi",
        description="Comma-separated filename extensions recognized as G-code files.",
    )
    fa_gerber: str = Field(
        default="art, bot, bsm, cmp, crc, crs, dim, gb0, gb1, gb2, gb3, gb4, gb5, gb6, gb7, gb8, gb9, gbd, "
        "gbl, gbo, gbp, gbr, gbs, gdo, ger, gko, gm1, gm2, gm3, grb, gtl, gto, gtp, gts, ly15, ly2, "
        "mil, outline, pho, plc, pls, smb, smt, sol, spb, spt, ssb, sst, stc, sts, top, tsm",
        description="Comma-separated filename extensions recognized as Gerber files.",
    )
    util_autocomplete_keywords: str = Field(
        default="Berta_CNC, Default_no_M6, Desktop, Documents, FlatConfig, FlatPrj, False, "
        "GRBL_11, GRL_11_no_M6, GRBL_laser, grbl_laser_eleks_drd, GRBL_laser_z, "
        "ISEL_CNC, ISEL_ICP_CNC, "
        "Line_xyz, Marlin, Marlin_laser_FAN_pin, "
        "Marlin_laser_Spindle_pin, NCCAD9, "
        "Marius, My Documents, Paste_1, "
        "Repetier, Roland_MDX_20, Roland_MDX_540,"
        "Toolchange_Manual, Toolchange_Probe_MACH3, True, "
        "Users, all, auto, axis, axisoffset, "
        "box, center_x, center_y, center, columns, combine, connect, contour, default, "
        "depthperpass, dia, diatol, dist, drilled_dias, drillz, dpp, dwelltime, "
        "endxy, endz, extracut_length, f, factor, feedrate, "
        "feedrate_z, gridoffsety, gridx, gridy, has_offset, "
        "holes, hpgl, iso_type, join, "
        "las_min_pwr, las_power, keep_scripts, margin, marlin, method, milled_dias, "
        "minoffset, min_bounds, name, offset, opt_type, order, "
        "outname, overlap, obj_name, "
        "p_coords, passes, postamble, pp, ppname_e, ppname_g, preamble, radius, ref, "
        "rest, "
        "rows, shellvar_, scale_factor, spacing_columns, spacing_rows, spindlespeed, "
        "startz, startxy, toolchange_xy, toolchangez, "
        "tooldia, travelz, use_threads, value, "
        "x, x0, x1, x_dist, y, y0, y1, y_dist, z_cut, "
        "z_move",
        description="Comma-separated keywords offered by command-line autocomplete.",
    )
    script_autocompleter: bool = Field(
        default=True, description="Whether script editor autocomplete is enabled."
    )
    script_text: str = Field(default="", description="Default script editor text.")
    script_plot: bool = Field(
        default=True, description="Whether script editor plot is enabled."
    )
    script_source_file: str = Field(
        default="", description="Path used for script editor source file."
    )
    document_autocompleter: bool = Field(
        default=False, description="Whether document editor autocomplete is enabled."
    )
    document_text: str = Field(default="", description="Default document editor text.")
    document_plot: bool = Field(
        default=True, description="Whether document editor plot is enabled."
    )
    document_source_file: str = Field(
        default="", description="Path used for document editor source file."
    )
    document_font_color: str = Field(
        default="#000000FF",
        description="Default document editor font color as a hexadecimal color.",
    )
    document_sel_color: str = Field(
        default="#0055ffFF",
        description="Default document editor selection color as a hexadecimal color.",
    )
    document_font_size: int = Field(
        default=6, description="Default document editor font size."
    )
    document_tab_size: int = Field(
        default=80, description="Default document editor tab size."
    )
    document_font_sizes: list[str] = Field(
        default_factory=lambda: [
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "18",
            "20",
            "22",
            "24",
            "26",
            "28",
            "32",
            "36",
            "40",
            "44",
            "48",
            "54",
            "60",
            "66",
            "72",
            "80",
            "88",
            "96",
        ],
        description="Available document editor font sizes values.",
    )

    @classmethod
    def load(cls, filename: str | os.PathLike[str]) -> Self:
        """
        Loads settings from a JSON file.

        Keys absent from the file keep their default values.

        :param filename:        path to the JSON settings file

        :return:                validated settings

        :raises SettingsError:  the file could not be read or does not contain valid settings
        """
        try:
            with open(filename, encoding="utf-8") as settings_file:
                return cls.model_validate_json(settings_file.read())
        except (OSError, ValidationError, ValueError) as error:
            raise SettingsError(f"Could not load settings from {filename}.") from error

    def write(self, filename: str | os.PathLike[str]) -> None:
        """
        Writes the settings to a JSON file.

        :param filename:        path to the JSON settings file

        :raises SettingsError:  the file could not be written
        """
        try:
            with open(filename, "w", encoding="utf-8") as settings_file:
                json.dump(self.model_dump(), settings_file, indent=2, sort_keys=True)
        except (OSError, TypeError, ValueError) as error:
            raise SettingsError(f"Could not write settings to {filename}.") from error

    def bind(self, callback: Callable[[str], None]) -> None:
        """
        Binds a callback invoked when a setting value changes.

        The callback receives the name of the changed setting. Assigning the current value does not call it.

        :param callback: function called with the changed setting name
        """
        self._change_callbacks.append(callback)

    def unbind(self, callback: Callable[[str], None]) -> None:
        """
        Removes a callback previously bound with bind.

        :param callback:        function previously passed to bind

        :raises SettingsError:  the callback is not bound
        """
        try:
            self._change_callbacks.remove(callback)
        except ValueError as error:
            raise SettingsError("Callback is not bound.") from error

    def __setattr__(self, name: str, value: object) -> None:
        """
        Sets an attribute and notifies bound callbacks when a setting changes.

        :param name:  attribute name
        :param value: attribute value
        """
        if name in self.model_fields and name in self.__dict__:
            previous = self.__dict__[name]
            super().__setattr__(name, value)
            if previous != self.__dict__[name]:
                for callback in tuple(self._change_callbacks):
                    callback(name)
            return

        super().__setattr__(name, value)
