"""Tool settings shared by saved settings and session options."""

from pydantic import BaseModel, Field

from .st_types import ToolDiameters, XYPair
from .support import _


class TwoSidedTool(BaseModel):
    """Store double-sided board settings shared by saved settings and session options."""

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


class CopperThievingTool(BaseModel):
    """Store copper thieving settings shared by saved settings and session options."""

    tools_copper_thieving_clearance: float = Field(
        default=0.25, description="Default copper-thieving clearance."
    )
    tools_copper_thieving_margin: float = Field(
        default=1.0, description="Default copper-thieving margin."
    )
    tools_copper_thieving_area: float = Field(
        default=0.1, description="Default copper-thieving area."
    )
    tools_copper_thieving_reference: int = Field(
        default=0,
        description="Copper-thieving reference. 0 is the object itself, 1 is an area selection, 2 is another object.",
    )
    tools_copper_thieving_box_type: str = Field(
        default="rect", description="Default copper-thieving box type."
    )
    tools_copper_thieving_circle_steps: int = Field(
        default=16, description="Default copper-thieving circle steps."
    )
    tools_copper_thieving_fill_type: int = Field(
        default=0,
        description="Copper-thieving fill pattern. 0 is solid, 1 is a dots grid, 2 is a squares grid, 3 is a lines grid.",
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
    tools_copper_thieving_geo_choice: int = Field(
        default=0,
        description="Geometry added to the pattern plating mask. 0 is both, 1 is thieving, 2 is the robber bar, 3 is none.",
    )


class SolderPasteTool(BaseModel):
    """Store solder paste settings shared by saved settings and session options."""

    tools_solderpaste_tools: ToolDiameters = Field(
        default=(1.0, 0.3),
        description="Solder-paste nozzle diameters. One number, or several when more than one nozzle is listed.",
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
    tools_solderpaste_xy_toolchange: XYPair = Field(
        default=(0.0, 0.0),
        description="Solder-paste tool-change position as X and Y.",
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


class AlignObjectsTool(BaseModel):
    """Store object alignment settings shared by saved settings and session options."""

    tools_align_objects_align_type: str = Field(
        default="sp", description="Default object alignment method."
    )


class AutoLevelTool(BaseModel):
    """Store auto-leveling settings shared by saved settings and session options."""

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


class CalculatorTool(BaseModel):
    """Store calculator settings shared by saved settings and session options."""

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


class DesignRulesTool(BaseModel):
    """Store design-rule check settings shared by saved settings and session options."""

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


class CutoutTool(BaseModel):
    """Store board cutout settings shared by saved settings and session options."""

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


class DistanceTool(BaseModel):
    """Store distance-tool settings shared by saved settings and session options."""

    tools_dist_snap_center: bool = Field(
        default=False,
        description="Whether distance measurement snap center is enabled.",
    )
    tools_dist_big_cursor: bool = Field(
        default=True, description="Whether distance measurement big cursor is enabled."
    )


class DrillTool(BaseModel):
    """Store drill-tool settings shared by saved settings and session options."""

    tools_drill_tool_order: int = Field(
        default=0,
        description="Drilling tool order. 0 keeps the file order, 1 sorts from small to big, 2 sorts from big to small.",
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
    tools_drill_endxy: XYPair | None = Field(
        default=None,
        description="Drilling job ending position as X and Y. Empty when the job has no ending position.",
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
    tools_drill_toolchangexy: XYPair = Field(
        default=(0.0, 0.0),
        description="Drilling tool-change position as X and Y.",
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


class ExtractTool(BaseModel):
    """Store drill-extract settings shared by saved settings and session options."""

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


class FiducialsTool(BaseModel):
    """Store fiducial settings shared by saved settings and session options."""

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
    tools_fiducials_type: int = Field(
        default=0,
        description="Fiducial marker shape. 0 is circular, 1 is a cross, 2 is a chess pattern.",
    )
    tools_fiducials_line_thickness: float = Field(
        default=0.25, description="Default fiducial line thickness."
    )
    tools_fiducials_big_cursor: bool = Field(
        default=True, description="Whether fiducial big cursor is enabled."
    )


class FilmTool(BaseModel):
    """Store film-tool settings shared by saved settings and session options."""

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


class FollowTool(BaseModel):
    """Store follow-tool settings shared by saved settings and session options."""

    tools_follow_simplification: bool = Field(
        default=False, description="Whether Follow tool simplification is enabled."
    )
    tools_follow_tolerance: float = Field(
        default=0.01, description="Default Follow tool tolerance."
    )
    tools_follow_union: bool = Field(
        default=False, description="Whether Follow tool union is enabled."
    )


class InvertTool(BaseModel):
    """Store invert-geometry settings shared by saved settings and session options."""

    tools_invert_margin: float = Field(
        default=0.1, description="Default Gerber inversion margin."
    )
    tools_invert_join_style: str = Field(
        default="s", description="Default Gerber inversion join style."
    )


class IsolationTool(BaseModel):
    """Store isolation-routing settings shared by saved settings and session options."""

    tools_iso_tooldia: ToolDiameters = Field(
        default=0.1,
        description="Isolation tool diameters. One number, or several when more than one tool is listed.",
    )
    tools_iso_order: int = Field(
        default=2,
        description="Isolation tool order. 0 keeps the file order, 1 sorts from small to big, 2 sorts from big to small.",
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


class MarkersTool(BaseModel):
    """Store marker settings shared by saved settings and session options."""

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


class MillingTool(BaseModel):
    """Store milling-tool settings shared by saved settings and session options."""

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
    tools_mill_endxy: XYPair | None = Field(
        default=None,
        description="Milling job ending position as X and Y. Empty when the job has no ending position.",
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
    tools_mill_toolchangexy: XYPair = Field(
        default=(0.0, 0.0),
        description="Milling tool-change position as X and Y.",
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


class NonCopperClearTool(BaseModel):
    """Store non-copper-clear settings shared by saved settings and session options."""

    tools_ncc_tools: ToolDiameters = Field(
        default=0.5,
        description="Non-copper clearing tool diameters. One number, or several when more than one tool is listed.",
    )
    tools_ncc_order: int = Field(
        default=2,
        description="Non-copper clearing tool order. 0 keeps the file order, 1 sorts from small to big, 2 sorts from big to small.",
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


class PathOptimizationTool(BaseModel):
    """Store path-optimization settings shared by saved settings and session options."""

    tools_opt_precision: int = Field(
        default=4, description="Default path optimization precision."
    )


class PaintTool(BaseModel):
    """Store paint-tool settings shared by saved settings and session options."""

    tools_paint_tooldia: float = Field(
        default=0.3, description="Default paint tool diameter."
    )
    tools_paint_order: int = Field(
        default=2,
        description="Paint tool order. 0 keeps the file order, 1 sorts from small to big, 2 sorts from big to small.",
    )
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


class PanelizeTool(BaseModel):
    """Store panelize settings shared by saved settings and session options."""

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


class PunchTool(BaseModel):
    """Store punch-tool settings shared by saved settings and session options."""

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


class QrCodeTool(BaseModel):
    """Store QR-code settings shared by saved settings and session options."""

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


class SubtractTool(BaseModel):
    """Store subtract-tool settings shared by saved settings and session options."""

    tools_sub_close_paths: bool = Field(
        default=True, description="Whether subtraction close paths is enabled."
    )
    tools_sub_delete_sources: bool = Field(
        default=False, description="Whether subtraction delete sources is enabled."
    )


class TransformTool(BaseModel):
    """Store object-transformation settings shared by saved settings and session options."""

    tools_transform_reference: str = Field(
        default=_("Selection"), description="Default object transformation reference."
    )
    tools_transform_ref_object: str = Field(
        default=_("Gerber"),
        description="Default object transformation reference object.",
    )
    tools_transform_ref_point: XYPair = Field(
        default=(0.0, 0.0),
        description="Transformation reference point as X and Y.",
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
