def estimate_well_cost(diameter_in, depth_ft, screen_length_ft, drilling_cost_per_ft=55, screen_cost_per_ft=45):
    drilling = depth_ft * drilling_cost_per_ft
    screen_cost = screen_length_ft * screen_cost_per_ft

    mobilization = 2500
    development = screen_length_ft * 35

    total = drilling + screen_cost + mobilization + development

    return {
        "drilling": drilling,
        "screen_cost": screen_cost,
        "development": development,
        "mobilization": mobilization,
        "total_cost": total
    }


def pump_energy_cost(Q_gpm, HP, hours_per_day, electricity_rate_per_kWh=0.12):
    kW = HP * 0.746
    kWh_day = kW * hours_per_day
    cost_per_day = kWh_day * electricity_rate_per_kWh
    cost_per_year = cost_per_day * 365

    return {
        "kW": kW,
        "kWh_day": kWh_day,
        "daily_cost": cost_per_day,
        "annual_cost": cost_per_year
    }
