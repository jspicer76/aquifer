def build_stress_periods(transient_config, wells):
    """
    Convert JSON stress-period definitions into internal model-ready format.
    """
    sps = []

    for sp in transient_config["stress_periods"]:
        pumping_dict = {}
        for p in sp["pumping"]:
            well_id = p["well_id"]
            q = p["rate_gpm"] / 448.831  # convert to cfs
            pumping_dict[well_id] = q

        sps.append({
            "duration_hours": sp["duration_hours"],
            "time_steps": sp["time_steps"],
            "pumping": pumping_dict,
            "recharge_in_per_day": sp.get("recharge_in_per_day", 0),
            "river_head": sp.get("river_head_ft", None)
        })

    return sps
