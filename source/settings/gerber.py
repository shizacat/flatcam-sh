"""Gerber settings shared by saved settings and session options."""

from pydantic import BaseModel, Field


class GerberPreferences(BaseModel):
    """Store Gerber settings shared by saved settings and session options."""

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
