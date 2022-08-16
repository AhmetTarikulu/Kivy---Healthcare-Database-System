# Kivy---Healthcare-Database-System

This kivy project allows healthcare companies and doctors access MySQL server in a user friendly way.

Features include:

- Recording patient data
- Recording patient appointments
- Managing patient payments
- Recording medication and presciptions

Multiple users with the app can access the database at the same time.

<h2>Setup</h2>

Sofware requires a MySQL server database from a hosting company such as AWS. Follow the instructions after creating hosting the server:

1.  Create a database named "data"
2.  Create 4 tables named : "patients", "appointments", "medication" and "balance"
3.  In "patients" create 3 columns named: "PatientName", "DOB" and "PatientNo"
4.  In "appointments" create 5 columns named: "PatientNo", "Date", "Time", "Doctor" and "Notes"
5.  In "medication" create 4 columns named: "PatientNo", "Date", "Medication" and  "Doctor" 
6.  In "balance" create 6 columns named: "PatientNo", "Date", "Value", "Doctor", "Notes" and "ID"
7.  Update "main.py" with databaseurl = {yourdatabaseurl}

<h3>Note: It is highly likely that the software will not work for your purpose without significant modifications, as it was made for a specific company's needs. It was never meant for publication.<br><br>If you need support please create a case and I'll be in touch.</h3>
