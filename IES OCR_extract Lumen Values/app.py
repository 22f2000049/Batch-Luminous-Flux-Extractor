import os
import pandas as pd
import streamlit as st
from io import StringIO, BytesIO
from xlsxwriter import Workbook

def extract_luminous_flux(file_content):
    """
    Extract luminous flux from an IES file content.
    The value is expected to be the line immediately after "TILT=NONE".
    """
    lines = file_content.splitlines()
    for i, line in enumerate(lines):
        if "TILT=NONE" in line:
            if i + 1 < len(lines):  # Ensure the next line exists
                next_line = lines[i + 1]
                st.write(f"Debug: Line after 'TILT=NONE' - {next_line}")  # Debugging line to display next line
                try:
                    luminous_flux = float(next_line.split()[1])  # Extract second value in the line
                    return luminous_flux
                except (ValueError, IndexError):
                    st.write("Error: Could not parse luminous flux from the line.")
                    return None
            else:
                st.write("Error: No line found after 'TILT=NONE'.")
                return None
    st.write("Error: 'TILT=NONE' not found in file.")
    return None

def process_files(uploaded_files):
    """Process uploaded IES files and extract luminous flux."""
    data = []
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        part_number = os.path.splitext(file_name)[0]
        file_content = uploaded_file.getvalue().decode("utf-8")
        luminous_flux = extract_luminous_flux(file_content)
        if luminous_flux is not None:
            data.append({
                "Part Number": part_number,
                "Luminous Flux": round(luminous_flux)
            })
    return pd.DataFrame(data)

def save_to_excel(dataframe):
    """Save the dataframe to an Excel file and return as bytes."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Luminous Flux')
    output.seek(0)
    return output

# Streamlit App
st.title("Batch Luminous Flux Extractor")
st.write("Upload your IES files to extract and round luminous flux values.")

uploaded_files = st.file_uploader("Upload IES Files", accept_multiple_files=True, type=["ies"])

if uploaded_files:
    df = process_files(uploaded_files)

    if not df.empty:
        st.write("### Extracted Data")
        st.dataframe(df)

        # Save to Excel
        excel_file = save_to_excel(df)

        st.download_button(
            label="Download Excel File",
            data=excel_file,
            file_name="luminous_flux_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.write("No valid luminous flux values were found in the uploaded files.")
