import math

def design_gravel_pack(
        aquifer_D10_mm,
        aquifer_D50_mm,
        screen_slot_in=0.030,
        desired_thickness_in=4.0
    ):
    """
    USGS / Driscoll gravel pack selection:
        GP_D50 = 4–6 × aquifer D50
        GP_D10 = 4–6 × aquifer D10
        Porosity expected: 0.22–0.38 (clean filter gravel)
    """

    GP_D50 = 5 * aquifer_D50_mm
    GP_D10 = 5 * aquifer_D10_mm

    # Recommended filter pack porosity
    porosity = 0.30

    # Convert thickness to ft
    thickness_ft = desired_thickness_in / 12

    return {
        "GP_D10_mm": GP_D10,
        "GP_D50_mm": GP_D50,
        "porosity": porosity,
        "thickness_ft": thickness_ft,
        "slot_size_in": screen_slot_in,
        "notes": (
            "Gravel pack D10 and D50 follow USGS filter design criteria:\n"
            "Filter D50 = 4–6 × aquifer D50\n"
            "Filter D10 = 4–6 × aquifer D10\n"
            "Porosity ~0.30 for clean well-rounded gravel."
        )
    }
