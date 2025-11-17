import math

def pump_selection(Q_gpm, pumping_level_ft, ground_elev_ft=0, discharge_elev_ft=0):
    """
    Compute TDH + recommended pump HP
    Inputs:
        Q_gpm
        pumping_level_ft   (water level during pumping)
        discharge_elev_ft  (elevation of discharge point)
    """

    # Static lift
    static_lift_ft = discharge_elev_ft - pumping_level_ft

    if static_lift_ft < 0:
        static_lift_ft = abs(static_lift_ft)

    # Assume friction loss (simple)
    friction_ft = 5 + 0.01 * Q_gpm

    TDH = static_lift_ft + friction_ft

    # Pump efficiency assumption
    eff = 0.67

    # HP = (Q gpm * TDH ft * 0.000189) / eff
    HP = (Q_gpm * TDH * 0.000189) / eff

    # Round to standard pump HP
    std = [5, 7.5, 10, 15, 20, 25, 30, 40, 50]
    HP_rec = next((h for h in std if h >= HP), 50)

    return {
        "static_lift_ft": static_lift_ft,
        "friction_loss_ft": friction_ft,
        "TDH_ft": TDH,
        "HP_calc": HP,
        "HP_recommended": HP_rec,
        "efficiency": eff,
        "notes": "HP selection uses standard well pump formula with typical efficiency of 67%."
    }
