"""File-association, script, and document settings shared by saved settings and session options."""

from pydantic import BaseModel, Field


class UtilitiesPreferences(BaseModel):
    """Store file-association, script, and document settings shared by saved settings and session options."""

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
