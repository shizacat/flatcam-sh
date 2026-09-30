"""Preference groups shared by saved settings and session options."""

from .application import Application
from .cncjob import CncJobPreferences
from .excellon import ExcellonPreferences
from .geometry import GeometryPreferences
from .gerber import GerberPreferences
from .interface import Interface
from .tools import (
    TwoSidedTool,
    CopperThievingTool,
    SolderPasteTool,
    AlignObjectsTool,
    AutoLevelTool,
    CalculatorTool,
    DesignRulesTool,
    CutoutTool,
    DistanceTool,
    DrillTool,
    ExtractTool,
    FiducialsTool,
    FilmTool,
    FollowTool,
    InvertTool,
    IsolationTool,
    MarkersTool,
    MillingTool,
    NonCopperClearTool,
    PathOptimizationTool,
    PaintTool,
    PanelizeTool,
    PunchTool,
    QrCodeTool,
    SubtractTool,
    TransformTool,
)
from .utilities import UtilitiesPreferences

SHARED = (
    Application,
    Interface,
    GerberPreferences,
    ExcellonPreferences,
    GeometryPreferences,
    CncJobPreferences,
    TwoSidedTool,
    CopperThievingTool,
    SolderPasteTool,
    AlignObjectsTool,
    AutoLevelTool,
    CalculatorTool,
    DesignRulesTool,
    CutoutTool,
    DistanceTool,
    DrillTool,
    ExtractTool,
    FiducialsTool,
    FilmTool,
    FollowTool,
    InvertTool,
    IsolationTool,
    MarkersTool,
    MillingTool,
    NonCopperClearTool,
    PathOptimizationTool,
    PaintTool,
    PanelizeTool,
    PunchTool,
    QrCodeTool,
    SubtractTool,
    TransformTool,
    UtilitiesPreferences,
)
