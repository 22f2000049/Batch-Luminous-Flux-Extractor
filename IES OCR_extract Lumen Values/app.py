import os
import pandas as pd
import streamlit as st
from io import BytesIO


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
                st.write(f"Debug: Line after 'TILT=NONE' - {next_line}")  # Optional: comment out for cleaner UI
                try:
                    luminous_flux = float(next_line.split()[1])  # Extract second value
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
        try:
            file_content = uploaded_file.getvalue().decode("utf-8")
            luminous_flux = extract_luminous_flux(file_content)
            if luminous_flux is not None:
                data.append({
                    "Part Number": part_number,
                    "Luminous Flux": round(luminous_flux)
                })
        except Exception as e:
            st.write(f"Error processing {file_name}: {e}")
    return pd.DataFrame(data)


def convert_df_to_csv(df):
    """Convert DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


# Streamlit App
st.title("🔆 Batch Luminous Flux Extractor")
st.write("Upload IES files to extract luminous flux values and download them as a CSV file.")

uploaded_files = st.file_uploader("Upload IES Files", type=["ies"], accept_multiple_files=True)

if uploaded_files:
    df = process_files(uploaded_files)

    if not df.empty:
        st.write("### ✅ Extracted Data")
        st.dataframe(df)

        # Convert to CSV for download
        csv_data = convert_df_to_csv(df)

        st.download_button(
            label="📥 Download CSV File",
            data=csv_data,
            file_name="luminous_flux_data.csv",
            mime="text/csv"
        )
    else:
        st.write("⚠️ No valid luminous flux values found in uploaded files.")
