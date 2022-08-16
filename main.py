import kivy
from datetime import date, datetime
import random
import mysql.connector
from kivy.app import App
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.factory import Factory
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import os, sys
from kivy.core.text import LabelBase
from kivy.config import Config
Config.set('graphics', 'resizable', False)

def show_error():
    show = Errorpop()
    window=Popup(title="Error", content=show, size_hint = (None,None), size=(400,100))
    window.open()
def nearest(items, pivot):
    return min([i for i in items if i >= pivot], key=lambda x: abs(x - pivot))
class Errorpop(FloatLayout):
    pass
    
databaseurl = None # Enter Database URL
class loginscreen(Screen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    def on_enter(self, *args):
        patientscreen.username=None
        patientscreen.password=None
        patientinfo.username=None
        patientinfo.password=None
        doctorinfo.username=None
        doctorinfo.password=None
    def check(self):
        try:
            db=mysql.connector.connect(host=databaseurl, user=self.username.text,password=self.password.text)
            patientscreen.username=self.username.text
            patientscreen.password=self.password.text
            patientinfo.username=self.username.text
            patientinfo.password=self.password.text
            doctorinfo.username=self.username.text
            doctorinfo.password=self.password.text
            db.close()
            self.username.text = ""
            self.password.text = ""
            return True
        except:
            show_error()
            return False
class patientscreen(Screen):
    username=None
    password=None
    patientgrid=ObjectProperty(None)
    newname=ObjectProperty(None)
    newdob=ObjectProperty(None)
    searchpatient=ObjectProperty(None)
    showdoctor=ObjectProperty(None)
    new_patient_button=ObjectProperty(None)
    def on_enter(self, *args):
        if self.showdoctor.active == True:
            self.show_doctors()
        else:
            self.newname.disabled = False
            self.newdob.disabled = False
            self.new_patient_button.disabled = False
            self.patientgrid.clear_widgets()
            db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM patients")
            for row in cursor:
                layout= FloatLayout(size=self.size)
                button=Factory.PatientButton(text=f"{row['PatientName']}\nD.O.B. {row['DOB']}       Patient No: {row['PatientNo']}")
                trash=Factory.PatientDelete()
                trash.bind(on_press=self.show_sure)
                button.bind(on_press=self.patientbutton)
                layout.ids[row['PatientNo']] = trash
                layout.add_widget(button)
                layout.add_widget(trash)
                self.patientgrid.add_widget(layout)
            db.close()
    def newpatient(self):
        try:
            date = datetime.strptime(self.newdob.text, "%d/%m/%Y").strftime("%Y-%m-%d")
            pno=random.randint(0,99999)
            db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
            cursor = db.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM patients WHERE PatientNo={pno}")
            data="error"
            for row in cursor:
                data = row
            while data != "error":
                data="error"
                pno=random.randint(0,99999)
                cursor.reset()
                cursor.execute(f"SELECT * FROM patients WHERE PatientNo={pno}")
                for row in cursor:
                    data = row
            cursor.reset()
            cursor.execute(f"INSERT INTO patients (PatientName, DOB, PatientNo) VALUES ('{self.newname.text}','{date}', {pno})")
            db.commit()
            db.close()
            self.on_enter()
        except:
            show_error()
    def patientbutton(self, instance):
        patientinfo.patientid = int(instance.text[-5:])
    def doctorbutton(self, instance):
        doctorinfo.docname = instance.text
    def search(self):
        self.patientgrid.clear_widgets()
        db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
        cursor = db.cursor(dictionary=True)
        if self.showdoctor.active == False:
            cursor.execute("SELECT * FROM patients")
            results=[]
            for row in cursor:
                if self.searchpatient.text.casefold() in row['PatientName'].casefold():
                    results.append(row)
            for row in results:
                layout= FloatLayout(size=self.size)
                button=Factory.PatientButton(text=f"{row['PatientName']}\nD.O.B. {row['DOB']}       Patient No: {row['PatientNo']}")
                trash=Factory.PatientDelete()
                trash.bind(on_press=self.show_sure)
                button.bind(on_press=self.patientbutton)
                layout.ids[row['PatientNo']] = trash
                layout.add_widget(button)
                layout.add_widget(trash)
                self.patientgrid.add_widget(layout)
        elif self.showdoctor.active == True:
            cursor.reset()
            cursor.execute("SELECT * FROM mysql.user")
            doctors = []
            for row in cursor:
                doctors.append(row['User'])
            doctors.remove('mysql.infoschema')
            doctors.remove('mysql.session')
            doctors.remove('mysql.sys')
            doctors.remove('rdsadmin')
            for row in doctors:
                if self.searchpatient.text.casefold() in row.casefold():
                    layout= FloatLayout(size=self.size)
                    button=Factory.DoctorButton(text=row)
                    button.bind(on_press=self.doctorbutton)
                    layout.add_widget(button)
                    self.patientgrid.add_widget(layout)
        db.close()
    def show_sure(self, instance, *args):
        for id, widget in instance.parent.ids.items():
            if widget.__self__ == instance:
                show = FloatLayout()
                btn1 = Button(pos_hint={"center_y":0.4,"right":0.45},size_hint=(0.3,0.6),text= "Delete")
                btn1.bind(on_press=self.deletepatient)
                btn2 = Button(pos_hint={"center_y":0.4,"x":0.55}, size_hint=(0.3,0.6), text= "Cancel")
                btn2.bind(on_press=self.closepopup)
                show.add_widget(btn1)
                show.add_widget(btn2)
                self.window=Popup(title="Are you sure to delete patient?", content=show, size_hint = (None,None), size=(300,100))
                self.window.open()
                self.deleteid = id
    def closepopup(self, *args):
        Popup.dismiss(self.window)
    def deletepatient(self, instance, *args):
        db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
        cursor = db.cursor(dictionary=True)
        cursor.execute(f"DELETE FROM patients WHERE PatientNo = {self.deleteid}")
        cursor.execute(f"DELETE FROM appointments WHERE PatientNo = {self.deleteid}")
        cursor.execute(f"DELETE FROM medication WHERE PatientNo = {self.deleteid}")
        cursor.execute(f"DELETE FROM balance WHERE PatientNo = {self.deleteid}")
        db.commit()
        db.close()
        self.on_enter()
        self.closepopup()
    def show_doctors(self):
        if self.showdoctor.active == True:
            self.newname.disabled = True
            self.newdob.disabled = True
            self.new_patient_button.disabled = True
            self.patientgrid.clear_widgets()
            db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM mysql.user")
            doctors = []
            for row in cursor:
                doctors.append(row['User'])
            doctors.remove('mysql.infoschema')
            doctors.remove('mysql.session')
            doctors.remove('mysql.sys')
            doctors.remove('rdsadmin')
            for row in doctors:
                layout= FloatLayout(size=self.size)
                button=Factory.DoctorButton(text=row)
                button.bind(on_press=self.doctorbutton)
                layout.add_widget(button)
                self.patientgrid.add_widget(layout)
            db.close()
        if self.showdoctor.active == False:
            self.on_enter()
class patientinfo(Screen):
    username=None
    password=None
    patientid=None
    agrid=ObjectProperty(None)
    mgrid=ObjectProperty(None)
    pgrid=ObjectProperty(None)

    adate=ObjectProperty(None)
    atime=ObjectProperty(None)
    adoctor=ObjectProperty(None)
    anote=ObjectProperty(None)

    mdate=ObjectProperty(None)
    mmedication=ObjectProperty(None)
    mdoctor=ObjectProperty(None)

    pdate=ObjectProperty(None)
    pvalue=ObjectProperty(None)
    pdoctor=ObjectProperty(None)
    pnote=ObjectProperty(None)

    totalbalance=ObjectProperty(None)

    meditextinput=ObjectProperty(None)
    savedlabel=ObjectProperty(None)

    namelabel=ObjectProperty(None)
    doblabel=ObjectProperty(None)
    applabel=ObjectProperty(None)
    def on_enter(self, *args):
        self.adate.text=self.atime.text=self.adoctor.text=self.anote.text=self.mdate.text=self.mmedication.text=self.mdoctor.text=self.pdate.text=self.pvalue.text=self.pdoctor.text=self.pnote.text =""

        self.agrid.clear_widgets()
        self.mgrid.clear_widgets()
        self.pgrid.clear_widgets()

        self.adoctor.values= self.get_doctors()
        self.adoctor.text = 'Doctor'

        self.mdoctor.values= self.get_doctors()
        self.mdoctor.text = 'Doctor'

        self.pdoctor.values= self.get_doctors()
        self.pdoctor.text = 'Doctor'

        db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
        cursor = db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM appointments WHERE PatientNo={self.patientid}")
        appdates={}
        for row in cursor:
            layout= FloatLayout(size=self.size)
            button=Factory.PatientButton(size_hint= (0.98, 0.9), text=f"Date: {row['Date']}     Time: {row['Time']}\nDoctor: {row['Doctor']}     Notes: {row['Notes']}")
            new = {row['Date']:row['Time']}
            appdates |=new
            layout.add_widget(button)
            trash=Factory.appdelete()
            trash.bind(on_press=self.deleteapp)
            layout.ids[button.text] = trash
            layout.add_widget(trash)
            self.agrid.add_widget(layout)
        try:
            nextvisit = nearest(appdates.keys(), date.today())
            self.applabel.text = f"Next Apointment:\n{nextvisit} {appdates[nextvisit]}"
        except:
            self.applabel.text = f"Next Apointment: None"
        cursor.reset()
        cursor.execute(f"SELECT * FROM medication WHERE PatientNo={self.patientid}")
        for row in cursor:
            layout= FloatLayout(size=self.size)
            button=Factory.PatientButton(size_hint= (0.98, 0.9), text=f"Date: {row['Date']}     Doctor: {row['Doctor']}\nMedication: {row['Medication']}")
            layout.add_widget(button)
            trash=Factory.meddelete()
            trash.bind(on_press=self.deletemed)
            layout.ids[button.text] = trash
            layout.add_widget(trash)
            self.mgrid.add_widget(layout)
        cursor.reset()
        cursor.execute(f"SELECT * FROM balance WHERE PatientNo={self.patientid}")
        balance=0
        for row in cursor:
            layout= FloatLayout(size=self.size)
            button=Factory.PatientButton(size_hint= (0.98, 0.9), text=f"Date: {row['Date']}     Value: {row['Value']}\nDoctor: {row['Doctor']}     Notes: {row['Notes']}")
            layout.add_widget(button)
            balance += int(row["Value"])
            trash=Factory.paydelete()
            trash.bind(on_press=self.deletepay)
            layout.ids[row['ID']] = trash
            layout.add_widget(trash)
            self.pgrid.add_widget(layout)
        self.totalbalance.text = f"Payments ({balance})"
        cursor.reset()
        cursor.execute(f"SELECT * FROM patients WHERE PatientNo={self.patientid}")
        for row in cursor:
            self.namelabel.text = str(row['PatientName'])
            self.doblabel.text = f"Date of Birth: {row['DOB']}"
            self.meditextinput.text = row['medinfo']
            self.savedlabel.opacity = 1
        db.close()
    def newappointment(self):
        try:
            date = datetime.strptime(self.adate.text, "%d/%m/%Y").strftime("%Y-%m-%d")
            print(date)
            datetime.strptime(self.atime.text, "%H:%M")
            db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
            cursor = db.cursor(dictionary=True)
            cursor.execute(f"INSERT INTO appointments (PatientNo, Date, Time, Doctor, Notes) VALUES ('{self.patientid}', '{date}', '{self.atime.text}', '{self.adoctor.text}', '{self.anote.text}')")
            db.commit()
            db.close()
            self.on_enter()
        except:
            show_error()
    def newmedication(self):
        try:
            date = datetime.strptime(self.mdate.text, "%d/%m/%Y").strftime("%Y-%m-%d")
            db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
            cursor = db.cursor(dictionary=True)
            cursor.execute(f"INSERT INTO medication (PatientNo, Date, Medication, Doctor) VALUES ('{self.patientid}', '{date}', '{self.mmedication.text}', '{self.mdoctor.text}')")
            db.commit()
            db.close()
            self.on_enter()
        except:
            show_error()
    def newbalance(self):
        try:
            date = datetime.strptime(self.pdate.text, "%d/%m/%Y").strftime("%Y-%m-%d")
            pno=random.randint(0,99999)
            db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
            cursor = db.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM balance WHERE ID={pno}")
            print(cursor)
            while cursor.rowcount != 0:
                pno=random.randint(0,99999)
                cursor.reset()
                cursor.execute(f"SELECT * FROM balance WHERE ID={pno}")
            cursor.reset()
            cursor.execute(f"INSERT INTO balance (PatientNo, Date, Value, Doctor, Notes, ID) VALUES ('{self.patientid}', '{date}', '{self.pvalue.text}', '{self.pdoctor.text}', '{self.pnote.text}', {pno})")
            db.commit()
            db.close()
            self.on_enter()
        except:
            show_error()
    def deleteapp(self, instance):
        for id, widget in instance.parent.ids.items():
            if widget.__self__ == instance:
                date = find_between(id, "Date: ", "     Time: ")
                time = find_between(id, "     Time: ", "\nDoctor: ")
                doctor = find_between(id, "\nDoctor: ", "     Notes: ")
                db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
                cursor = db.cursor(dictionary=True)
                cursor.execute(f"DELETE FROM appointments WHERE Date = '{date}' AND Time = '{time}' AND Doctor = '{doctor}' AND PatientNo = {self.patientid}")
                db.commit()
                db.close()
                self.on_enter()
    def deletemed(self, instance):
        for id, widget in instance.parent.ids.items():
            if widget.__self__ == instance:
                date = find_between(id, "Date: ", "     Doctor: ")
                doctor = find_between(id, "     Doctor: ", "\nMedication: ")
                medication = id.partition("\nMedication: ")[2]
                db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
                cursor = db.cursor(dictionary=True)
                cursor.execute(f"DELETE FROM medication WHERE Date = '{date}' AND Doctor = '{doctor}' AND Medication= '{medication}' AND PatientNo = {self.patientid}")
                db.commit()
                db.close()
                self.on_enter()
    def deletepay(self, instance):
        for id, widget in instance.parent.ids.items():
            if widget.__self__ == instance:
                db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
                cursor = db.cursor(dictionary=True)
                cursor.execute(f"DELETE FROM balance WHERE ID = {id}")
                db.commit()
                db.close()
                self.on_enter()
    def meditext(self):
        self.meditextinput.bind(on_text=self.unsavedlabel)
        self.savedlabel.opacity = 1
        db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
        cursor = db.cursor(dictionary=True)
        cursor.execute(f"UPDATE patients SET medinfo='{self.meditextinput.text}'WHERE PatientNo={self.patientid}")
        db.commit()
        db.close()
    def unsavedlabel(self):
        self.savedlabel.opacity = 0
        self.meditextinput.unbind(on_text=self.unsavedlabel)
    def get_doctors(self):
        db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM mysql.user")
        doctors = []
        for row in cursor:
            doctors.append(row['User'])
        doctors.remove('mysql.infoschema')
        doctors.remove('mysql.session')
        doctors.remove('mysql.sys')
        doctors.remove('rdsadmin')
        return doctors
class doctorinfo(Screen):
    docname=None
    patientgrid = ObjectProperty(None)
    username=None
    password=None
    doctorlabel=ObjectProperty(None)
    def on_enter(self, *args):
        self.patientgrid.clear_widgets()
        self.doctorlabel.text = f"{self.docname}'s Patients"
        db=mysql.connector.connect(host=databaseurl, user=self.username,password=self.password, db="data")
        cursor = db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM patients")
        for row in cursor:
            cursor.reset()
            cursor.execute(f"SELECT * FROM appointments WHERE Doctor='{self.docname}' AND PatientNo = {row['PatientNo']}")
            appdates={}
            for appointment in cursor:
                new = {appointment['Date']:appointment['Time']}
                appdates |=new
            try:
                nextvisit = nearest(appdates.keys(), date.today())
            except:
                nextvisit = "None"
            cursor.reset()
            cursor.execute(f"SELECT * FROM balance WHERE Doctor='{self.docname}' AND PatientNo = {row['PatientNo']}")
            balance=0
            for payment in cursor:
                balance += int(payment["Value"])
            if nextvisit != "None" or balance != 0:
                layout= FloatLayout(size=self.size)
                button=Factory.PatientButton(text=f"Name: {row['PatientName']}\nNext Appointment: {nextvisit.strftime('%d/%m/%Y')} {str(appdates[nextvisit])[:-3]}   Balance: {balance}")
                button.bind(on_press=self.patientbutton)
                layout.ids[row['PatientNo']] = button
                layout.add_widget(button)
                self.patientgrid.add_widget(layout)
            db.close()
    def patientbutton(self, instance):
        for id, widget in instance.parent.ids.items():
            if widget.__self__ == instance:
                patientinfo.patientid = id
class WindowManager(ScreenManager):
    pass
def find_between(s, start, end):
    return (s.split(start))[1].split(end)[0]
class App(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(loginscreen(name='login'))
        sm.add_widget(patientscreen(name='patient'))
        sm.add_widget(patientinfo(name='info'))
        sm.add_widget(doctorinfo(name='doctorinfo'))
        return sm
    def resource_path(self=None, relative_path=None):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

        
kv = Builder.load_file(App.resource_path(relative_path="my.kv"))
LabelBase.register(name='Cabal', fn_regular=App.resource_path(relative_path='cabal.ttf'), fn_bold=App.resource_path(relative_path="cabal_bold.ttf"))
LabelBase.register(name='Montserrat', fn_regular=App.resource_path(relative_path='Montserrat-Regular.ttf'), fn_bold=App.resource_path(relative_path="Montserrat-Bold.ttf"))
if __name__ == "__main__":
    App().run()