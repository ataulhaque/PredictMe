import streamlit as st
import pandas as pd
#from io import StringIO
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import sqlite3
from datetime import datetime
import re
from control_panel import main as control_panel_main  # Import the control panel app

# Set page configuration
st.set_page_config(page_title="Get your free Birth Chart", layout="centered", page_icon='🌟')

def calculate_chaldean_number(name):
    """
    Calculate the Chaldean numerology number for a given name.

    Args:
        name (str): The full name to calculate the number for.

    Returns:
        int: The Chaldean numerology number.
    """
    # Chaldean letter-to-number mapping
    chaldean_map = {
        'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
        'B': 2, 'K': 2, 'R': 2,
        'C': 3, 'G': 3, 'L': 3, 'S': 3,
        'D': 4, 'M': 4, 'T': 4,
        'E': 5, 'H': 5, 'N': 5, 'X': 5,
        'U': 6, 'V': 6, 'W': 6,
        'O': 7, 'Z': 7,
        'F': 8, 'P': 8
    }
    
    # Sanitize and process the name
    name = name.upper()  # Convert to uppercase for consistent mapping
    name = ''.join(filter(str.isalpha, name))  # Remove non-alphabetic characters

    # Calculate the Chaldean number
    total_value = sum(chaldean_map.get(letter, 0) for letter in name)
    
    # Reduce to a single digit unless it's 11 or 22 (master numbers)
    while total_value > 9 and total_value not in (11, 22):
        total_value = sum(int(digit) for digit in str(total_value))
    
    return total_value

# Function to generate and download the PDF
def generate_pdf(full_name, chaldean_number, dob, gender, driver, conductor, kuaa, grid, interpretations):
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
        ["Numerology Number for name", chaldean_number],
        ["Driver Value", driver],
        ["Conductor Value", conductor],
        ["kuaa Value", kuaa if kuaa is not None else "Not Available"],
    ]
    for num, count in grid.items():
        data.append([f"{num} - {interpretations[num]}", "Missing" if count == 0 else "Available" if count == 1 else f"Repeated {count} times"])

    table = Table(data, colWidths=[300, 100])
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
            phone_number TEXT UNIQUE,
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
    #birth_time_str = birth_time.strftime('%H:%M') if birth_time else None
    #birth_time_str = birth_time

    # Insert the data into the table
    cursor.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,))
    if cursor.fetchone():
        st.warning("Record already exists for this phone number.")
    else:
        cursor.execute('''
            INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, dob, birth_time, place_of_birth, phone_number, gender))

    conn.commit()
    conn.close()

# Function to calculate Driver value
def calculate_driver(day):
    return sum(map(int, str(day)))

# Function to calculate Conductor value
def calculate_conductor(dob):
    digits = [int(char) for char in dob if char.isdigit()]
    while len(digits) > 1:
        digits = [sum(map(int, str(sum(digits))))]
    return digits[0]

# Function to calculate kuaa value
def calculate_kuaa(year, gender):
    if gender == "NA":
        return None  # Cannot calculate kuaa for unspecified gender
    year_sum = sum(map(int, str(year)))
    while year_sum >= 10:
        year_sum = sum(map(int, str(year_sum)))
    if gender == "Male":
        kuaa = 11 - year_sum
    elif gender == "Female":
        kuaa = 4 + year_sum
    while kuaa >= 10:
        kuaa = sum(map(int, str(kuaa)))
    return kuaa

# Function to generate Lo Shu Grid
def generate_lo_shu_grid(dob, driver, conductor, kuaa):
    digits = [int(char) for char in dob if char.isdigit()]
    digits.append(driver)
    digits.append(conductor)
    digits.append(kuaa)
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
        "normal": "background-color: #d1ecf1; color: #0c5460;",  # Light blue for normal numbers
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
            styled_row.append(f'<div style="{style}">{num}: ({grid[num]})</div>')
        styled_data.append(styled_row)
    # Convert styled_data to a DataFrame with custom size
    df = pd.DataFrame(styled_data)
    df.style.set_properties(subset=df.columns, **{'background-color': 'white', 'color': 'black', 'border-color': 'black', 'border-width': '1px', 'border-style': 'solid'})
    df.style.set_properties(subset=df.columns, **{'font-size': '16px', 'font-family': 'Arial'})
    return df
###############################################################################
###############################################################################
def main_app():

    # Streamlit App Layout
    st.title("🌟 :orange[Birth Chart Generator] :sunflower: 🌟")
    st.write(":rainbow[Generate your Birth Chart with interpretations and insights!]")

    # Input: Full Name
    first_name = st.text_input(":blue[Enter your First Name:]", placeholder="e.g., Mohan")
    last_name = st.text_input(":blue[Enter your Last Name:]", placeholder="e.g., Kumar")

    # Input: Date of Birth
    dob = st.text_input(":blue[Enter your Date of Birth (DD-MM-YYYY)]:", placeholder="e.g., 25-11-1987")
    #dob = st.date_input('Enter your Date of Birth',value="default_value_today")
    # Input: Birth Time
    #birth_time = st.time_input('Enter your Birth Time (HH:MM:SS)', value="now" )
    birth_time = st.text_input(":blue[Enter your Birth Time (HH:MM:SS):]", placeholder="e.g., 10:45:00")

    #Input: Place of Birth
    place_of_birth = st.text_input(":blue[Enter your Place of Birth (New Delhi, India)]:", placeholder="e.g., New Delhi, India")

    #Input: Phone Number
    phone_number = st.text_input(":blue[Enter your Phone Number (+91-9876543210):]", placeholder="e.g., +91-9876543210")

    # Input: Gender
    gender = st.radio("Select your Gender:", ["Male", "Female", "NA"], index=2)
    st.image("data/images/lo-Shu-Grid-Numbers-with-planets.png", use_container_width="auto", caption="Lo Shu Grid with Planets", output_format="auto")

    if first_name and last_name and dob and birth_time and phone_number:
        try:
            # Validate dob
            dob_parsed = pd.to_datetime(dob, format="%d-%m-%Y")
            #st.success("Valid Date of Birth!")
            # Extract components
            day = dob_parsed.day
            month = dob_parsed.month
            year = dob_parsed.year

            # Calculate values
            driver = calculate_driver(day)
            conductor = calculate_conductor(dob)
        except ValueError:
            st.error("Invalid date format. Please enter in DD-MM-YYYY format.")
        
        try:
            #validate birth_time
            birth_time_parsed = datetime.strptime(birth_time, "%H:%M:%S")
            #st.success("Valid Birth Time!")
        except ValueError:
            st.error("Invalid Birth Time. Please enter in HH:MM:SS format.")

        #validate phone_number
        phone_pattern = r"^\+\d+-\d{10}$"  # Regex for +91-9876543210 format
        if re.match(phone_pattern, phone_number):
            st.success("Valid Phone Number!")
        else:
            st.error("Invalid Phone Number. Please enter in this +91-9876543210 format.")

        # Full Name
        full_name = f"{first_name} {last_name}"
        if full_name:
            chaldean_number = calculate_chaldean_number(full_name)
        else:
            st.error("Name required!")

        if gender == "NA":
            st.warning("Gender not specified. kuaa value cannot be calculated. Please provide Male or Female.")
        
        #Calculate Kuaa number
        kuaa = calculate_kuaa(year, gender)

        # Generate Lo Shu Grid
        grid = generate_lo_shu_grid(dob, driver, conductor, kuaa)

        if first_name and last_name and dob and birth_time and place_of_birth and gender in ['Male', 'Female'] and phone_number and re.match(phone_pattern, phone_number):
            save_to_sqlite(first_name, last_name, dob, birth_time, place_of_birth, phone_number, gender)
            st.success("All input data validated and saved successfully!")
        else:
            st.error("Please ensure all fields are filled correctly.")
        
        # Display Full Name
        st.write(f"#### Full Name: :blue-background[{full_name}] :sunflower:")
        # Display Driver, Conductor, kuaa
        st.write(f"#### Your Driver Value: :blue-background[{driver}] :hibiscus:")
        st.write(f"#### Your Conductor Value: :blue-background[{conductor}] :tulip:")
        if kuaa is not None:
            st.write(f"#### Your kuaa Value: :blue-background[{kuaa}] :cherry_blossom:")
        st.write(f"#### Numerology Number for :orange[{full_name}]: :blue-background[{chaldean_number}] :rose:")

        # Display Lo Shu Grid
        st.write("### :rainbow[Your Birth Chart:]")
        styled_grid = display_color_coded_grid(grid)
        st.markdown(styled_grid.to_html(escape=False, index=False, header=False), unsafe_allow_html=True)

        # Interpretations for Individual Numbers
        st.write("### :rainbow[Interpretation of your Birth Chart Numbers:]")
        interpretations = number_interpretations()
        for num, interpretation in interpretations.items():
            count = grid[num]
            if count == 0:
                st.write(f"**{num} :red[(Missing)]:** {interpretation}")
            elif count > 1:
                st.write(f"**{num} :green[(Repeated] :blue-background[{count}] times):** {interpretation}")
            else:
                st.write(f"**{num} :blue[(Present)]:** {interpretation}")

        # Final Birth Chart
        # st.write("### :rainbow[Final Birth Chart:]")
        # final_chart = pd.DataFrame([
        #     {"Attribute": "Full Name", "Value": full_name},
        #     {"Attribute": "Date of Birth", "Value": dob},
        #     {"Attribute": "Gender", "Value": gender},
        #     {"Attribute": "Numerology Number for name", "Value": chaldean_number},
        #     {"Attribute": "Driver Value", "Value": driver},
        #     {"Attribute": "Conductor Value", "Value": conductor},
        #     {"Attribute": "kuaa Value", "Value": kuaa if kuaa is not None else "Not Available"}
        # ] + [{"Attribute": f"{num} - {interpretations[num]}", "Value": "Missing" if count == 0 else "Available" if count == 1 else f"Repeated {count} times"} for num, count in grid.items()])

        # st.table(final_chart) 
        
        st.info("To consult with an Astrologer/Numerologist, click on 'WhatsApp Chat' button below.")
        st.markdown("""
        <a aria-label="Chat on WhatsApp" href="https://wa.me/917205467646?text=Namaste%2C%20I%20need%20to%20consult%20regarding%20my%20Birth%20Chart">
        <img alt="Chat on WhatsApp" src="https://image.pngaaa.com/326/2798326-middle.png" width="150" height="auto"/>
        </a><br/><br/>
        """, unsafe_allow_html=True)

        # PDF Download Button with dynamic file name
        pdf = generate_pdf(full_name, chaldean_number, dob, gender, driver, conductor, kuaa, grid, interpretations)
        pdf_file_name = f"{full_name.replace(' ', '_')}_Birth_Chart.pdf"  # Generate dynamic file name
        st.download_button(
            label="Download Your Birth Chart as PDF",
            data=pdf,
            file_name=pdf_file_name,
            mime="application/pdf",
        )
    else:
        st.info("Please fill out all required fields: Full Name, Date of Birth, and Gender.")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Main App", "Control Panel"])

if page == "Main App":
    main_app()
elif page == "Control Panel":
    control_panel_main()  # Render the admin control panel

# Footer Section
st.markdown("""
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/ionicons/2.0.1/css/ionicons.min.css">
    <link rel="stylesheet" href="data/css/footer.css">
</head>
<div class="footer-basic">
        <footer>
            <ul class="list-inline">
                <li class="list-inline-item"><a href="/">Home</a></li>
                <li class="list-inline-item"><a href="/Services">Services</a></li>
                <li class="list-inline-item"><a href="/About_Us">About</a></li>
            </ul>
            <p class="copyright">Company Name ©2024</p>
        </footer>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/js/bootstrap.bundle.min.js"></script>
""", unsafe_allow_html=True)