import svgwrite
import os

def make_well_diagram(diameter_in, screen_length_ft, gravel_thickness_ft, outfile="report/well_diagram.png"):
    os.makedirs("report", exist_ok=True)

    dwg = svgwrite.Drawing("report/well_diagram.svg", size=("400px", "800px"))
    
    # Scales
    scale = 8  # pixels per ft

    total_depth_px = (screen_length_ft + 20) * scale
    casing_width_px = diameter_in * 1.5

    # Casing (blue)
    dwg.add(dwg.rect(insert=(150, 20),
                     size=(casing_width_px, total_depth_px),
                     fill="none", stroke="blue", stroke_width=4))

    # Screen (green)
    screen_y = total_depth_px - screen_length_ft * scale
    dwg.add(dwg.rect(insert=(150, screen_y),
                     size=(casing_width_px, screen_length_ft * scale),
                     fill="none", stroke="green", stroke_width=4))

    # Gravel pack (orange band)
    gravel_outer = casing_width_px + (gravel_thickness_ft * scale)
    dwg.add(dwg.rect(insert=(150 - gravel_outer/2, screen_y),
                     size=(gravel_outer + casing_width_px, screen_length_ft * scale),
                     fill="none", stroke="orange", stroke_width=3))

    dwg.add(dwg.text("Casing", insert=(150, 15)))
    dwg.add(dwg.text("Screen", insert=(150, screen_y - 5)))
    dwg.add(dwg.text("Gravel Pack", insert=(150 - gravel_outer/2, screen_y - 20)))

    dwg.save()

    # Convert SVG → PNG
    try:
        import cairosvg
        cairosvg.svg2png(url="report/well_diagram.svg", write_to=outfile)
    except:
        pass

    return outfile
