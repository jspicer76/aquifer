"""
BOUNDARY DEFINITIONS FOR 2-D FINITE DIFFERENCE GROUNDWATER MODEL
----------------------------------------------------------------
Supports:
    • Constant-head boundaries (Dirichlet)
    • No-flow boundaries (Neumann = 0)
    • Specified flux boundaries (Neumann = q)
    • River boundaries (Cauchy / head + conductance)
    • Recharge boundaries (areal recharge)
"""

import numpy as np


class ConstantHeadBoundary:
    """Dirichlet boundary: h = specified head."""
    def __init__(self, cells, head_ft):
        self.cells = set(cells)
        self.head_ft = head_ft
        self.type = "constant_head"


class NoFlowBoundary:
    """No-flow: ∂h/∂n = 0."""
    def __init__(self, cells):
        self.cells = set(cells)
        self.type = "no_flow"


class SpecifiedFluxBoundary:
    """Neumann flux boundary: q = specified."""
    def __init__(self, cells, flux_ft3_per_day):
        self.cells = set(cells)
        self.flux = flux_ft3_per_day
        self.type = "specified_flux"


class RiverBoundary:
    """
    River boundary using the Cauchy condition:
        Q = C (h_river - h_cell)

    Where:
        C = conductance (ft²/day)
        h_river = river stage
    """
    def __init__(self, cells, river_stage_ft, conductance):
        self.cells = set(cells)
        self.river_stage_ft = river_stage_ft
        self.conductance = conductance
        self.type = "river"


class RechargeBoundary:
    """Recharge applied over an area."""
    def __init__(self, cells, recharge_ft_per_day):
        self.cells = set(cells)
        self.recharge = recharge_ft_per_day
        self.type = "recharge"


class BoundaryCollection:
    """
    Holds all active boundaries.
    The solver reads `.by_type` dictionaries for fast lookup.
    """
    def __init__(self):
        self.boundaries = []

    def add(self, boundary):
        self.boundaries.append(boundary)

    @property
    def constant_head(self):
        return [b for b in self.boundaries if b.type == "constant_head"]

    @property
    def no_flow(self):
        return [b for b in self.boundaries if b.type == "no_flow"]

    @property
    def specified_flux(self):
        return [b for b in self.boundaries if b.type == "specified_flux"]

    @property
    def river(self):
        return [b for b in self.boundaries if b.type == "river"]

    @property
    def recharge(self):
        return [b for b in self.boundaries if b.type == "recharge"]
