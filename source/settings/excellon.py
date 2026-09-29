"""Excellon settings shared by saved settings and session options."""

from pydantic import BaseModel, Field


class ExcellonPreferences(BaseModel):
    """Store Excellon settings shared by saved settings and session options."""

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
