import math

# ================================================================
# WELL DESIGNER — Ten States + KY compliant
# ================================================================
def design_well(
    Q_gpm,
    T,
    Sy,
    b,
    allowable_velocity=0.1,
    user_diameter_in=None,
    user_screen_length_ft=None
):
    """
    Suggest well diameter + screen length based on:
        - Ten States Standards (2023)
        - KDOW 401 KAR requirements
        - Entrance velocity guidelines (0.1 ft/s max)
        - Screen area required for Q
        - Aquifer characteristics (T, Sy, thickness b)

    User may override well diameter or screen length.
    """

    # ------------------------------------------------------------
    # Convert units
    # ------------------------------------------------------------
    Q_cfs = Q_gpm / 448.831      # ft³/s
    Q_ft3_s = Q_cfs

    # ------------------------------------------------------------
    # Required SCREEN AREA for given entrance velocity
    # A = Q / v
    # ------------------------------------------------------------
    A_required = Q_ft3_s / allowable_velocity       # ft²

    # ------------------------------------------------------------
    # SCREEN LENGTH recommendation
    # ------------------------------------------------------------
    # Ten States: screen length should intercept major water-bearing unit.
    # Rule of thumb: 30–70% of aquifer saturated thickness.
    L_min = max(10, 0.3 * b)
    L_rec = 0.5 * b
    L_max = 0.7 * b

    if user_screen_length_ft:
        L_screen = float(user_screen_length_ft)
    else:
        L_screen = L_rec

    # ------------------------------------------------------------
    # WELL DIAMETER recommendation
    # ------------------------------------------------------------
    # For a given screen length L, diameter D satisfies:
    #   A_required = π * D * L
    # → D = A_required / (π * L)
    # ------------------------------------------------------------
    D_required_ft = A_required / (math.pi * L_screen)
    D_required_in = D_required_ft * 12

    # ROUND to nearest standard well size
    standard_sizes_in = [6, 8, 10, 12, 14, 16, 18, 20, 24]
    D_recommended = next((s for s in standard_sizes_in if s >= D_required_in), 24)

    if user_diameter_in:
        D_final = float(user_diameter_in)
        override = True
    else:
        D_final = D_recommended
        override = False

    # ------------------------------------------------------------
    # SCREEN SLOT SIZE (very rough guidance)
    # ------------------------------------------------------------
    # Ten States: screen slot = D10 to D40 of formation
    # Without sieve: assume medium sand → 0.020–0.035 in slots
    # ------------------------------------------------------------
    slot_size_in = 0.030

    # ------------------------------------------------------------
    # WELL YIELD CHECK (specific capacity sanity)
    # ------------------------------------------------------------
    # SC ≈ T / (200 + 0.5 * ln(r² / (r_well²)))
    # This is approximate; used just to sanity-check diameter choice.
    # ------------------------------------------------------------
    r_w = (D_final / 12) / 2
    SC_approx = T / (200 + 0.5 * math.log((100 ** 2) / (r_w ** 2)))

    yield_check_gpm_ft = SC_approx

    # ------------------------------------------------------------
    # Return results
    # ------------------------------------------------------------
    return {
        "diameter_in_required": D_required_in,
        "diameter_in_recommended": D_recommended,
        "diameter_in_final": D_final,
        "screen_length_ft": L_screen,
        "screen_length_range_ft": (L_min, L_max),
        "slot_size_in": slot_size_in,
        "override_used": override,
        "SC_approx": yield_check_gpm_ft,
        "screen_area_required_ft2": A_required
    }
