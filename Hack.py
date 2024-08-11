from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import os
import streamlit as st
from PIL import Image
import pandas as pd
from streamlit_option_menu import option_menu
import mysql.connector as con
import streamlit_lottie as st_lottie
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from pathlib import Path
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage 
from email.mime.application import MIMEApplication 
from email.mime.multipart import MIMEMultipart
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import smtplib 









genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#backend setup





#------------------SETTINGS-----------------
detection=["Anomaly Detected","Location ","Size","Severity","Infections","Tumors","Cogenital Conditions","Foreign Object","Swelling"]
page_title="Radix"
page_icon=":x_ray:"
layout="centered"



st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
col1, col2, col3 = st.columns(3)


with col1:
    st.write(' ')

with col2:
    st.image("rad.jpeg")

with col3:
    st.write(' ')
st.markdown("<h1 style='text-align: center; color: white;'>AI Enhanced Medical Image (X-Ray) Analysis</h1>", unsafe_allow_html=True)

hide_st_style="""
        <style>
        #MainMenu{visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>"""
st.markdown(hide_st_style,unsafe_allow_html=True)
def get_gemini_response(input_prompt, image ):
    model = genai.GenerativeModel('gemini-1.5-flash') #calling the model
    response = model.generate_content([input_prompt, image[0]])
    st.write(response.text)
    
def input_image_setup(uploaded_file):
    #check if a file has been uploaded
    if uploaded_file is not None:
        #read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type":uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No File Uploaded")


input_prompt = """
You are an expert in analyzing soft copies of X-ray images.

The radiologist will upload X-ray image in JPG, JPEG, or PNG format. Your task is to analyze the image carefully and extract the following detailed information:

1. Is there any anomaly in the image?
2. What is the detected anomaly?
3. Where is it located?
4. How severe is the anomaly?
5. What is the size of the anomaly?

The information should be presented in the following format:

Anomaly Detected? (Specify YES if there's any anomaly else NO)

Detected Anomaly: (name of the anomaly)
Location of the Anomaly: (specify location)

Size: Provide information about the bone density, length of crack, dislocation level, etc., in a manner that is easily understood by a doctor.

Severity: (Low, Intermediate, High, etc.)Provide a detailed explanation of the severity.

Do not provide a diagnostic solution. Instead, focus on analyzing and presenting the information based on the topics outlined above.

Please display the information in a well-defined tabular format with clearly organized rows and columns, as follows:

* Don't print the info present in brackets. But I want the value for each row for sure. Don't confuse
but make sure to give appropriate result values.

| Anomaly Detected | (Specify YES if there's any anomaly else NO) |
| ---------------- | -------- |
| Location | (display location) |
| Size | (display Size Value) |
| Severity | (Severity State) |
| Infections | (Signs of infections) |
| Tumors | (Look for the presence of Tumors) |
| Co-Genital Conditions | (Identify structural abnormalities present from birth) |
| Foreign Object | (Look for presence of foreign objects that may accidently ingested or inserted) |
| Swelling | (Detect thee signs of soft tissue swelling or inflammation) |

Also create a similar table below . Here the language will be passed on as arguemnet. Get to know the language and generate
the text in the language given. If there is any medical term like tibia, a normal human who is unaware of this will feel difficulty 
in understanding so in that case for location, describe in general terms like it's found near to wrist or elbow in 
the chosen language.

provide a summary of the above the information. Don't provide any diagnostic solution. 
It should be for about 50-100 Words. Don't produce any grammatical errors. Include the appropriate
Medical terms then and there. This is for the doctor. Not for any customer/patient

Also provide a summary of the above the information in the chosen language. Don't provide any diagnostic solution. 
It should be for about 50-100 Words. Don't produce any grammatical errors. Include the appropriate
Medical terms then and there. This is for the doctor. Not for any customer/patient

Please ensure a well-defined and organized arrangement of the generated information.

Do not provide an any diagnostic solution. Give me the analysis of it. That's it

Display the following as well: (This should be displayed at the end of the above table)
The above report is generated by the Radix in a bold manner. This should be highlighted as well.


"""



def create_database(db):
    """Create the 'userdb' database if it doesn't exist."""
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS userdb")
    cursor.close()



def insert_patient_record(db, name, age, contact_number, email, address):
    """Insert a new patient record into the 'patients' table."""
    cursor = db.cursor()

    # Select the database
    cursor.execute("USE userdb")

    insert= """
    INSERT INTO patients (name, age, contact_number, email, address)
    VALUES (%s, %s, %s, %s, %s)
    """

    patient_data = (name, age, contact_number, email, address)

    cursor.execute(insert, patient_data)
    db.commit()
    st.write("Patient record inserted successfully.") 

def fetch_all_patients(db):
    """Fetch all records from the 'patients' table."""
    cursor = db.cursor()

    # Select the database
    cursor.execute("USE userdb")

    # Fetch all patients
    select_patients_query = "SELECT * FROM patients"
    cursor.execute(select_patients_query)
    patients = cursor.fetchall()

    return patients       

def fetch_patient_by_id(db, patient_id):
    """Fetch a patient's record from the 'patients' table based on ID."""
    cursor = db.cursor()

    # Select the database
    cursor.execute("USE userdb")

    # Fetch the patient by ID
    select_patient_query = "SELECT * FROM patients WHERE id = %s"
    cursor.execute(select_patient_query, (patient_id,))
    patient = cursor.fetchone()
    
    return patient

def fetch_patient_by_contact(db, contact_number):
    """Fetch a patient's record from the 'patients' table based on contact number."""
    cursor = db.cursor()

    # Select the database
    cursor.execute("USE userdb")

    # Fetch the patient by contact number
    select_patient_query = "SELECT * FROM patients WHERE contact_number = %s"
    cursor.execute(select_patient_query, (contact_number,))
    patient = cursor.fetchone()

    return patient

def delete_patient_record(db, delete_option, delete_value):
    """Delete a patient record from the 'patients' table based on ID, name, or contact number."""
    cursor = db.cursor()

    # Select the database
    cursor.execute("USE userdb")

    # Delete the patient record
    if delete_option == "ID":
        delete_patient_query = "DELETE FROM patients WHERE id = %s"
    elif delete_option == "Name":
        delete_patient_query = "DELETE FROM patients WHERE name = %s"
    elif delete_option == "Contact Number":
        delete_patient_query = "DELETE FROM patients WHERE contact_number = %s"

    cursor.execute(delete_patient_query, (delete_value,))
    db.commit()
    st.write("Patient record deleted successfully.")

def update_patient_record(db):
    """Update a patient's record in the 'patients' table."""

    search_option = st.selectbox("Select search option", ["ID", "Contact Number"], key="search_option")
    search_value = st.text_input("Enter search value", key="search_value")

    if st.button("Search :magic_wand:"):
        if search_option == "ID":
            patient = fetch_patient_by_id(db, search_value)
        elif search_option == "Contact Number":
            patient = fetch_patient_by_contact(db, search_value)
        def drawMyRuler(pdf):
            # Set font and size
            pdf.setFont("Helvetica", 12)

            # Page dimensions (assuming 8.5x11 inches page size)
            page_width = 600  # points (8.5 inches)
            page_height = 700  # points (11 inches)

            # Define spacing and starting positions
            x_start = 100
            y_start = 700
            x_spacing = 100  # Space between x labels
            y_spacing = 100  # Space between y labels

            # Draw horizontal ruler labels
            for i in range(1, 11):  # Drawing 10 labels
                x_position = x_start + (i * x_spacing)
                text = f'x{i * 100}'
                text_width = pdf.stringWidth(text, "Helvetica", 12)
                pdf.drawString(x_position - (text_width / 2), y_start, text)  # Centered text

            # Draw vertical ruler labels
            for i in range(1, 14):  # Drawing 13 labels
                y_position = y_start - (i * y_spacing)
                text = f'y{i * 100}'
                pdf.drawString(10, y_position, text)
        ####
        fileName = "Record.pdf"
        documentTitle = "Patient X-Ray Report"
        title = "RadiX Medical Image (X-RAY) Report"
        subtitle = "By Team PENTAGON"

        column=['Id,Name,Age,Contact,Email,Address']
        data = [str(patient)]
        

        ####


        pdf = canvas.Canvas(fileName) #file_name
        pdf.setTitle(documentTitle) #file_title
        ###
        #Available fonts
        for font in pdf.getAvailableFonts():
            print(font)
        ####
        drawMyRuler(pdf) #Ruler
        ####
        pdf.setFont("Times-Bold", 25)
        pdf.drawCentredString(300,770, title) #Title
        ####
        #pdf.setFillColorRGB(0,0,255) #fontColor
        pdf.setFont("Times-Italic", 12)
        pdf.drawCentredString(270,750, subtitle) #SubTitle
        #####
        pdf.line(40, 730, 550, 730) #Horizontal Rule
        #####
        #Para Text
        text = pdf.beginText(80, 680)
        text.setFont("Times-Roman", 10)
        text.setFillColor(colors.black)
        
        text.textLines(column)
        
        text.textLines(data)    
        pdf.drawText(text)
        #######
        
        pdf.save()
        
        

        if patient:
            st.subheader("Patient Details")
            df = pd.DataFrame([patient], columns=[ 'ID','Name', 'Age', 'Contact Number', 'Email', 'Address'])
            st.dataframe(df)
            st.session_state.edit_patient = patient
        else:
            st.write("Patient not found")

    if 'edit_patient' in st.session_state:
        edit_patient(db)


def edit_patient(db):
    """Edit a patient's record in the 'patients' table."""

    st.subheader("Edit Patient Details")
    new_name = st.text_input("Enter new name", value=st.session_state.edit_patient[1])
    new_age = st.number_input("Enter new age", value=st.session_state.edit_patient[2])
    new_contact = st.text_input("Enter new contact number", value=st.session_state.edit_patient[3])
    new_email = st.text_input("Enter new email", value=st.session_state.edit_patient[4])
    new_address = st.text_input("Enter new address", value=st.session_state.edit_patient[5])

    if st.button("Update :roller_coaster:"):
        patient_id = st.session_state.edit_patient[0]
        update_patient_info(db, patient_id, new_name, new_age, new_contact, new_email, new_address)
        


def update_patient_info(db, patient_id, new_name, new_age, new_contact, new_email, new_address):
    """Update a patient's record in the 'patients' table."""
    cursor = db.cursor()

    # Select the database
    cursor.execute("USE userdb")

    # Update the patient record
    update_patient_query = """
    UPDATE patients
    SET name = %s, age = %s, contact_number = %s, email = %s, address = %s
    WHERE id = %s
    """
    patient_data = (new_name, new_age, new_contact, new_email, new_address, patient_id)

    cursor.execute(update_patient_query, patient_data)
    db.commit()
    st.write("Patient record updated successfully.")
def message(subject="",text="", attachment1=None,attachment=None): 
    
    # build message contents 
    msg = MIMEMultipart() 
      
    # Add Subject 
    msg['Subject'] = subject   
      
    # Add text contents 
    msg.attach(MIMEText(text))   
  
    
    # We do the same for 
    # attachments as we did for images 
    if attachment1 is not None: 
          
        # Check whether we have the 
        # lists of attachments or not! 
        if type(attachment1) is not list: 
            
              # if it isn't a list, make it one 
            attachment1 = [attachment1]   
  
        for one_attachment1 in attachment1: 
  
            with open(one_attachment1, 'rb') as f: 
                
                # Read in the attachment 
                # using MIMEApplication 
                file = MIMEApplication( 
                    f.read(), 
                    name=os.path.basename(one_attachment1) 
                ) 
            file['Content-Disposition'] ='/path/to/your/attachment.txt' 
              
            # At last, Add the attachment to our message object 
            msg.attach(file) 

    if attachment is not None: 
          
        # Check whether we have the 
        # lists of attachments or not! 
        if type(attachment) is not list: 
            
              # if it isn't a list, make it one 
            attachment = [attachment]   
  
        for one_attachment in attachment: 
  
            with open(one_attachment, 'rb') as f: 
                
                # Read in the attachment 
                # using MIMEApplication 
                file = MIMEApplication( 
                    f.read(), 
                    name=os.path.basename(one_attachment) 
                ) 
            file['Content-Disposition'] = '/path/to/your/attachment.txt'
            # At last, Add the attachment to our message object 
            msg.attach(file) 
    return msg 
  

db = con.connect(host='localhost',user='root',password='root@123',database='patient')

create_database(db)
cursor = db.cursor()
cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                age INT,
                contact_number VARCHAR(15),
                address VARCHAR(255),
                email VARCHAR(255)
            );
        ''')
db.commit()


menu = ["Home","upload","Add patient Record","Show patient Records", "Search and Edit Patient","Delete Patients Record","Send_Mail"]
options = st.sidebar.radio("MENU:dart:",menu)
if options=="Home":
     col1, col2, col3 = st.columns(3)
     with col1:
        st.write(' ')

     with col2:
        st.write("Welcome to Home Page")

     with col3:
        st.write(' ')

elif options== "upload":

    uploaded_file = st.file_uploader("Upload the softcopy of the X-Ray image in JPG, JPEG or PNG Format", type = ["jpg", "jpeg", "png"])
    image = ""
    select_language=["English","Tamil","Hindi","Telugu","Malayalam"]
    st.selectbox(select_language)
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width = 250)
    submitted=st.button("Generate")
    if submitted:
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(input_prompt,image_data) 
        def drawMyRuler(pdf):
            # Set font and size
            pdf.setFont("Helvetica", 12)

            # Page dimensions (assuming 8.5x11 inches page size)
            page_width = 600  # points (8.5 inches)
            page_height = 700  # points (11 inches)

            # Define spacing and starting positions
            x_start = 100
            y_start = 700
            x_spacing = 100  # Space between x labels
            y_spacing = 100  # Space between y labels

            # Draw horizontal ruler labels
            for i in range(1, 11):  # Drawing 10 labels
                x_position = x_start + (i * x_spacing)
                text = f'x{i * 100}'
                text_width = pdf.stringWidth(text, "Helvetica", 12)
                pdf.drawString(x_position - (text_width / 2), y_start, text)  # Centered text

            # Draw vertical ruler labels
            for i in range(1, 14):  # Drawing 13 labels
                y_position = y_start - (i * y_spacing)
                text = f'y{i * 100}'
                pdf.drawString(10, y_position, text)
        ####
        fileName = "Result.pdf"
        documentTitle = "Patient X-Ray Report"
        title = "RadiX Medical Image (X-RAY) Report"
        subtitle = "By Team PENTAGON"
        result=str(response)

        ####


        pdf = canvas.Canvas(fileName) #file_name
        pdf.setTitle(documentTitle) #file_title
        ###
        #Available fonts
        for font in pdf.getAvailableFonts():
            print(font)
        ####
        drawMyRuler(pdf) #Ruler
        ####
        pdf.setFont("Times-Bold", 25)
        pdf.drawCentredString(300,770, title) #Title
        ####
        #pdf.setFillColorRGB(0,0,255) #fontColor
        pdf.setFont("Times-Italic", 12)
        pdf.drawCentredString(270,750, subtitle) #SubTitle
        #####
        pdf.line(40, 730, 550, 730) #Horizontal Rule
        #####
        #Para Text
        text = pdf.beginText(80, 680)
        text.setFont("Times-Roman", 8)
        text.setFillColor(colors.black)   
        text.textLines(result)
        pdf.drawText(text)
        #######
        
        pdf.save()
          
        st.success("Data Saved!")
    
elif options == "Add patient Record":
    st.subheader("Enter patient details :woman_in_motorized_wheelchair:")
    id=st.number_input("Enter ID of patient",key = "ID",value = 1)
    name = st.text_input("Enter name of patient",key = "name")
    age = st.number_input("Enter age of patient",key = "age",value = 1)
    contact = st.text_input("Enter contact of patient",key = "contact")
    email = st.text_input("Enter Email of patient",key = "email")
    address = st.text_input("Enter Address of patient",key= "address")
    if st.button("add patient record"):
        cursor = db.cursor()
        select_query = """
        SELECT * FROM patients WHERE contact_number=%s
         """
        cursor.execute(select_query,(contact,))
        existing_patient = cursor.fetchone()
        if existing_patient:
            st.warning("A patient with the same contact number already exist")
        else:  
            insert_patient_record(db, name, age, contact, email, address)
    

elif options=="Show patient Records":
    
    patients = fetch_all_patients(db)
    if patients:
        st.subheader("All patients Records :magic_wand:")
        df = pd.DataFrame(patients, columns=['ID', 'Name', 'Age', 'Contact Number', 'Email', 'Address'])
        st.dataframe(df)
        
    else:
        st.write("No patients found")


elif options == "Search and Edit Patient":
        update_patient_record(db)
           


elif options == "Delete Patients Record":
    st.subheader("Search a patient to delate :skull_and_crossbones:")
    delete_option = st.selectbox("Select delete option", ["ID", "Name", "Contact Number"], key="delete_option")
    delete_value = st.text_input("Enter delete value", key="delete_value")

    if st.button("Delete"):
        delete_patient_record(db, delete_option, delete_value)
elif options =="Send_Mail":
    smtp = smtplib.SMTP('smtp.gmail.com', 587) 
    smtp.ehlo() 
    smtp.starttls() 
  
# Login with your email and password 
    
    smtp.login('231501045@rajalakshmi.edu.in','9841632080')
    to=st.text_input("TO",key="to")
    file1=st.text_input("file1",key="f1")
    file2=st.text_input("file2",key="f2")
    submit=st.button("Send")
    if submit:
        msg = message("Report From Radix", "patient_record",file1,file2) 
  
# Make a list of emails, where you wanna send mail 
        
# Provide some data to the sendmail function! 
        smtp.sendmail(from_addr="hello@gmail.com",to_addrs=to, msg=msg.as_string()) 
  
 # Finally, don't forget to close the connection 
        smtp.quit()
        st.write("Sent!!!!!")

      
db.close()