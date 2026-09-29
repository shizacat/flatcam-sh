"""Application behavior shared by saved settings and session options."""

from pydantic import BaseModel, Field

from .support import _default_process_number, _default_worker_number


class Application(BaseModel):
    """Store application behavior shared by saved settings and session options."""

    first_run: bool = Field(
        default=True,
        description="Whether the application is running for the first time.",
    )
    root_folder_path: str = Field(
        default="", description="Root folder used to resolve application resources."
    )
    global_serial: str = Field(
        default="0", description="Installation identifier stored with the settings."
    )
    global_background_timeout: int = Field(
        default=300000,
        description="Default application background timeout in milliseconds.",
    )
    global_verbose_error_level: int = Field(
        default=0, description="Default application verbose error level."
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
    global_bookmarks: dict[str, int] = Field(
        default_factory=dict, description="Default application bookmarks."
    )
    global_bookmarks_limit: int = Field(
        default=10, description="Default application bookmarks limit."
    )
