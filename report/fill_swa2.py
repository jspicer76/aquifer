from docx import Document


def fill_swa2_form(results, inputs):
    """Create a minimal SWA-2-style document from key model outputs."""
    doc = Document()
    doc.add_heading(
        "SWA-2: Groundwater Source Approval - Kentucky 401 KAR 8:020",
        level=1,
    )

    doc.add_heading("Section 1 - Well Data", level=2)
    doc.add_paragraph(f"Well Depth: {inputs['aquifer']['b_ft']} ft")
    doc.add_paragraph(f"Pumping Rate: {inputs['pumping_test']['Q_gpm']} gpm")

    doc.add_heading("Section 2 - Pumping Test Results", level=2)
    doc.add_paragraph(f"Transmissivity (T): {results['T']:.2f} ft^2/day")
    doc.add_paragraph(f"Storativity (S): {results['S']:.4f}")
    doc.add_paragraph(f"Specific Yield (Sy): {results['Sy']:.4f}")

    doc.add_heading("Section 3 - Aquifer Adequacy", level=2)
    sustainable = results.get("sustainable_yield")
    if sustainable is not None:
        doc.add_paragraph(f"Calculated sustainable yield: {sustainable:.1f} gpm")
    else:
        doc.add_paragraph("Calculated sustainable yield: N/A (not provided)")

    doc.add_heading("Attachments", level=2)
    doc.add_paragraph("- Drawdown curves")
    doc.add_paragraph("- Contour maps")
    doc.add_paragraph("- WHP zones")
    doc.add_paragraph("- Geologic logs")
    doc.add_paragraph("- Pumping test tables")

    doc.save("report/SWA2_form.docx")
