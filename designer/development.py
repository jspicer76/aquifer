def estimate_well_development_time(screen_length_ft, diameter_in):
    """
    EPA rule-of-thumb:
        0.5 to 1.5 hours per ft of screen for airlifting/surge block
        0.25–0.75 hours per ft for jetting
    """

    airlift_hr = screen_length_ft * 1.0
    jetting_hr = screen_length_ft * 0.45

    return {
        "airlift_hours": airlift_hr,
        "jetting_hours": jetting_hr,
        "range_hours": (jetting_hr, airlift_hr),
        "notes": (
            "EPA Development Guide: Screen development time is primarily a "
            "function of screen length and formation permeability."
        )
    }
