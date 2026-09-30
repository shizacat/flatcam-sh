"""Geometry settings shared by saved settings and session options."""

from pydantic import BaseModel, Field


class GeometryPreferences(BaseModel):
    """Store geometry settings shared by saved settings and session options."""

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
