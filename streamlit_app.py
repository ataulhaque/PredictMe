import streamlit as st
import pandas as pd
from io import StringIO

# Function to calculate Driver value
def calculate_driver(day):
    return sum(map(int, str(day)))

# Function to calculate Conductor value
def calculate_conductor(dob):
    digits = [int(char) for char in dob if char.isdigit()]
    while len(digits) > 1:
        digits = [sum(map(int, str(sum(digits))))]
    return digits[0]

# Function to calculate Kunvar value
def calculate_kunvar(year, gender):
    if gender == "NA":
        return None  # Cannot calculate Kunvar for unspecified gender
    year_sum = sum(map(int, str(year)))
    while year_sum >= 10:
        year_sum = sum(map(int, str(year_sum)))
    if gender == "Male":
        kunvar = 11 - year_sum
    elif gender == "Female":
        kunvar = 4 + year_sum
    while kunvar >= 10:
        kunvar = sum(map(int, str(kunvar)))
    return kunvar

# Function to generate Lo Shu Grid
def generate_lo_shu_grid(dob):
    digits = [int(char) for char in dob if char.isdigit()]
    grid = {num: digits.count(num) for num in range(1, 10)}
    return grid

# Function to display Final Lo Shu Grid with Driver, Conductor, Kunvar
def display_final_grid(grid, driver, conductor, kunvar):
    lo_shu_layout = [
        [4, 9, 2],
        [3, 5, 7],
        [8, 1, 6]
    ]
    table = []
    for row in lo_shu_layout:
        table.append([f"{num}: {grid[num]}" for num in row])
    # Append Driver, Conductor, Kunvar at the bottom
    table.append([f"Driver: {driver}", f"Conductor: {conductor}", f"Kunvar: {kunvar if kunvar is not None else 'N/A'}"])
    return pd.DataFrame(table)

# Streamlit App Layout
st.title("🌟 Enhanced Lo Shu Grid Numerology Calculator 🌟")
st.write("Discover your personalized Lo Shu Grid Birth Chart, Driver, Conductor, and Kunvar values!")

# Input: Full Name
first_name = st.text_input("Enter your First Name:", placeholder="e.g., Mohan")
last_name = st.text_input("Enter your Last Name:", placeholder="e.g., Kumar")

# Input: Date of Birth
dob = st.text_input("Enter your Date of Birth (DD-MM-YYYY):", placeholder="e.g., 25-11-1987")

# Input: Gender
gender = st.radio("Select your Gender:", ["Male", "Female", "NA"], index=2)

if first_name and last_name and dob:
    try:
        # Validate input
        dob_parsed = pd.to_datetime(dob, format="%d-%m-%Y")
        st.success("Valid Date of Birth!")

        # Full Name
        full_name = f"{first_name} {last_name}"

        # Extract components
        day = dob_parsed.day
        month = dob_parsed.month
        year = dob_parsed.year

        # Calculate values
        driver = calculate_driver(day)
        conductor = calculate_conductor(dob)
        kunvar = calculate_kunvar(year, gender)

        if gender == "NA":
            st.warning("Gender not specified. Kunvar value cannot be calculated. Please provide Male or Female.")

        # Generate Lo Shu Grid
        grid = generate_lo_shu_grid(dob)

        # Display Full Name
        st.write(f"### Full Name: {full_name}")

        # Display Driver, Conductor, Kunvar
        st.write(f"### Your Driver Value: {driver}")
        st.write(f"### Your Conductor Value: {conductor}")
        if kunvar is not None:
            st.write(f"### Your Kunvar Value: {kunvar}")

        # Display Lo Shu Grid
        st.write("### Your Lo Shu Grid:")
        st.table(display_final_grid(grid, driver, conductor, kunvar))

        # Final Birth Chart
        st.write("### Final Birth Chart:")
        final_chart = pd.DataFrame([
            {"Attribute": "Full Name", "Value": full_name},
            {"Attribute": "Date of Birth", "Value": dob},
            {"Attribute": "Gender", "Value": gender},
            {"Attribute": "Driver Value", "Value": driver},
            {"Attribute": "Conductor Value", "Value": conductor},
            {"Attribute": "Kunvar Value", "Value": kunvar if kunvar is not None else "Not Available"}
        ] + [{"Attribute": f"Number {num}", "Value": count} for num, count in grid.items()])

        st.table(final_chart)

        # Downloadable Report
        csv = StringIO()
        final_chart.to_csv(csv, index=False)
        st.download_button(
            label="Download Your Birth Chart",
            data=csv.getvalue(),
            file_name="lo_shu_grid_birth_chart.csv",
            mime="text/csv"
        )
    except ValueError:
        st.error("Invalid date format. Please enter in DD-MM-YYYY format.")
else:
    st.info("Please fill out all required fields: Full Name, Date of Birth, and Gender.")
