import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import urllib.parse

def pcd_coordinates(num_holes, pcd_diameter, center_x=0, center_y=0, start_angle_deg=0):
    coords = []
    for i in range(num_holes):
        angle_deg = start_angle_deg + (360 / num_holes) * i
        angle_rad = np.radians(angle_deg)
        x = center_x + (pcd_diameter / 2) * np.cos(angle_rad)
        y = center_y + (pcd_diameter / 2) * np.sin(angle_rad)
        coords.append((x, y))
    return coords

def format_coords_text(coords):
    lines = ["PCD Hole Coordinates:"]
    for idx, (x, y) in enumerate(coords, 1):
        lines.append(f"Hole {idx}: X = {x:.4f}, Y = {y:.4f}")
    return "\n".join(lines)

def create_pdf(coords_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, coords_text)

    # Get the PDF as a byte string
    pdf_output = pdf.output(dest='S').encode('latin1')

    # Write the byte string to BytesIO
    pdf_buffer = BytesIO(pdf_output)

    return pdf_buffer

st.title("CNC PCD (Pitch Circle Diameter) Calculator")

with st.form("pcd_form"):
    num_holes = st.number_input("Number of holes", min_value=2, value=6, step=1)
    pcd_diameter = st.number_input("PCD (Pitch Circle Diameter)", min_value=1.0, value=100.0)
    center_x = st.number_input("Center X coordinate", value=0.0)
    center_y = st.number_input("Center Y coordinate", value=0.0)
    start_angle_deg = st.number_input("Starting angle (degrees)", value=0.0)
    submitted = st.form_submit_button("Calculate and Show Design")

if submitted:
    coords = pcd_coordinates(num_holes, pcd_diameter, center_x, center_y, start_angle_deg)
    coords_text = format_coords_text(coords)
    st.subheader("Hole Coordinates (X, Y):")
    st.text(coords_text)

    # WhatsApp shareable link
    wa_text = urllib.parse.quote(coords_text)
    wa_link = f"https://wa.me/?text={wa_text}"
    st.markdown(f"[Share on WhatsApp]({wa_link})", unsafe_allow_html=True)

    # PDF download
    pdf_buffer = create_pdf(coords_text)
    st.download_button(
        label="Download coordinates as PDF",
        data=pdf_buffer,
        file_name="pcd_coordinates.pdf",
        mime="application/pdf"
    )

    # Plotting
    fig, ax = plt.subplots(figsize=(6,6))
    circle = plt.Circle((center_x, center_y), pcd_diameter/2, color='blue', fill=False, linestyle='--', label='PCD')
    ax.add_artist(circle)
    xs, ys = zip(*coords)
    ax.scatter(xs, ys, color='red', s=80, label='Holes')
    for idx, (x, y) in enumerate(coords, 1):
        ax.annotate(str(idx), (x, y), textcoords="offset points", xytext=(0,10), ha='center')
    ax.scatter([center_x], [center_y], color='green', s=100, label='Center')
    ax.set_aspect('equal', 'box')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("PCD Hole Pattern")
    ax.legend()
    plt.grid(True)
    st.pyplot(fig)
