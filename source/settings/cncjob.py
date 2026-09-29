"""CNC job settings shared by saved settings and session options."""

from pydantic import BaseModel, Field


class CncJobPreferences(BaseModel):
    """Store CNC job settings shared by saved settings and session options."""

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
