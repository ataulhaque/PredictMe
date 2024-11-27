import streamlit as st
import pandas as pd
#from io import StringIO
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import sqlite3

# Set page configuration
st.set_page_config(page_title="Get your free Birth Chart", layout="centered", page_icon='🌟')
###############################################################
# Function to generate and download the PDF
def generate_pdf(full_name, dob, gender, driver, conductor, kunvar, grid):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    # Title and Greeting
    title = Paragraph(f"Namaste, <b>{full_name}</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    intro = Paragraph("Here is your final Birth Chart:", styles["Normal"])
    elements.append(intro)
    elements.append(Spacer(1, 12))

    # Birth Chart Table Data
    data = [
        ["Attribute", "Value"],
        ["Full Name", full_name],
        ["Date of Birth", dob],
        ["Gender", gender],
        ["Driver Value", driver],
        ["Conductor Value", conductor],
        ["Kunvar Value", kunvar if kunvar is not None else "Not Available"],
    ]
    for num, count in grid.items():
        data.append([f"Number {num}", count])

    table = Table(data, colWidths=[200, 200])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Closing Note
    closing = Paragraph(
        "Thank you for choosing us for this service.<br/><b>Predict Me</b>", styles["Normal"]
    )
    elements.append(closing)

    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
################################################################
def save_to_sqlite(first_name, last_name, dob, birth_time, place_of_birth, phone_number, gender):
    # Create a connection to the SQLite database
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            first_name TEXT,
            last_name TEXT,
            dob TEXT,
            birth_time TEXT,
            place_of_birth TEXT,
            phone_number TEXT,
            gender TEXT
        )
    ''')

    # Get user input
    first_name = first_name
    last_name = last_name
    dob = dob
    birth_time = birth_time
    place_of_birth = place_of_birth
    phone_number = phone_number
    gender = gender

    # Convert birth_time to string format
    birth_time_str = birth_time.strftime('%H:%M') if birth_time else None

    # Insert the data into the table
    cursor.execute('''
        INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (first_name, last_name, dob, birth_time_str, place_of_birth, phone_number, gender))

    conn.commit()
    conn.close()

    st.success("All input data validated successfully!")

###############################################################

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
def generate_lo_shu_grid(dob, driver, conductor, kunvar):
    digits = [int(char) for char in dob if char.isdigit()]
    digits.append(driver)
    digits.append(conductor)
    digits.append(kunvar)
    grid = {num: digits.count(num) for num in range(1, 10)}
    return grid

# Function to generate interpretations
def number_interpretations():
    return {
        1: "Leadership, independence, ambition, and self-confidence.",
        2: "Cooperation, sensitivity, and diplomacy.",
        3: "Creativity, joy, and social interaction.",
        4: "Practicality, stability, and responsibility.",
        5: "Freedom, adventure, and adaptability.",
        6: "Love, family, and nurturing.",
        7: "Spirituality, introspection, and analysis.",
        8: "Material success, authority, and power.",
        9: "Compassion, humanitarianism, and selflessness.",
    }

# Function to display color-coded grid
def display_color_coded_grid(grid):
    colors = {
        "missing": "background-color: #f8d7da; color: #721c24;",  # Light red for missing numbers
        "repeated": "background-color: #d4edda; color: #155724;",  # Light green for repeated numbers
        "normal": "",  # Default style
    }
    lo_shu_layout = [
        [4, 9, 2],
        [3, 5, 7],
        [8, 1, 6]
    ]
    styled_data = []
    for row in lo_shu_layout:
        styled_row = []
        for num in row:
            if grid[num] == 0:
                style = colors["missing"]
            elif grid[num] > 1:
                style = colors["repeated"]
            else:
                style = colors["normal"]
            styled_row.append(f'<div style="{style}">{num}: {grid[num]}</div>')
        styled_data.append(styled_row)
    return pd.DataFrame(styled_data)

# Streamlit App Layout
st.title("🌟 Birth Chart Generator 🌟")
st.write("Generate your Birth Chart with interpretations and insights!")

# Input: Full Name
first_name = st.text_input("Enter your First Name:", placeholder="e.g., Mohan")
last_name = st.text_input("Enter your Last Name:", placeholder="e.g., Kumar")

# Input: Date of Birth
dob = st.text_input("Enter your Date of Birth (DD-MM-YYYY):", placeholder="e.g., 25-11-1987")
#dob = st.date_input('Enter your Date of Birth',value="default_value_today")
# Input: Birth Time
birth_time = st.time_input('Enter your Birth Time (HH:MM)')
#birth_time = st.text_input("Enter your Birth Time (HH:MM:SS):", placeholder="e.g., 10:45:00")

#Input: Place of Birth
place_of_birth = st.text_input("Enter your Place of Birth:", placeholder="e.g., New Delhi, India")

#Input: Phone Number
phone_number = st.text_input("Enter your Phone Number:", placeholder="e.g., +91-9876543210")

# Input: Gender
gender = st.radio("Select your Gender:", ["Male", "Female", "NA"], index=2)
#st.image("data/images/lo-Shu-Grid-Numbers-with-planets.png", use_container_width="auto", caption="Lo Shu Grid with Planets", output_format="auto")

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
        grid = generate_lo_shu_grid(dob, driver, conductor, kunvar)
        save_to_sqlite(first_name, last_name, dob, birth_time, place_of_birth, phone_number, gender)
        # Display Full Name
        st.write(f"### Full Name: {full_name}")

        # Display Driver, Conductor, Kunvar
        st.write(f"### Your Driver Value: {driver}")
        st.write(f"### Your Conductor Value: {conductor}")
        if kunvar is not None:
            st.write(f"### Your Kunvar Value: {kunvar}")

        # Display Lo Shu Grid
        st.write("### Your Lo Shu Grid Birth Chart:")
        styled_grid = display_color_coded_grid(grid)
        st.markdown(styled_grid.to_html(escape=False, index=False, header=False), unsafe_allow_html=True)

        # Interpretations for Individual Numbers
        st.write("### Interpretations for Individual Numbers:")
        interpretations = number_interpretations()
        for num, interpretation in interpretations.items():
            count = grid[num]
            if count == 0:
                st.write(f"**{num} (Missing):** {interpretation}")
            elif count > 1:
                st.write(f"**{num} (Repeated {count} times):** {interpretation}")
            else:
                st.write(f"**{num} (Present):** {interpretation}")

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
        st.subheader("To consult further with an Astrologer/Numerologist regarding the generated birth chart, click on the given 'WhatsApp Chat' button to connect and consult.")
        st.markdown("""
        <a aria-label="Chat on WhatsApp" href="https://wa.me/917205467646?text=Namaste%2C%20I%20need%20to%20consult%20regarding%20my%20Birth%20Chart">
        <img alt="Chat on WhatsApp" src="https://image.pngaaa.com/326/2798326-middle.png" width="150" height="auto"/>
        </a>
        """, unsafe_allow_html=True)

        # PDF Download Button
        pdf = generate_pdf(full_name, dob, gender, driver, conductor, kunvar, grid)
        st.download_button(
            label="Download Your Birth Chart as PDF",
            data=pdf,
            file_name="lo_shu_grid_birth_chart.pdf",
            mime="application/pdf",
        )
    except ValueError:
        st.error("Invalid date format. Please enter in DD-MM-YYYY format.")
else:
    st.info("Please fill out all required fields: Full Name, Date of Birth, and Gender.")
