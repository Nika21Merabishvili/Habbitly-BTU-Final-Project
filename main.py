import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QCalendarWidget, QDialogButtonBox, QVBoxLayout
from PyQt5.QtCore import QDate
from ui_habbitly import Ui_MainWindow


#ამას წავშლით მარა გასარკვევი რო იყოს
class DatePickerDialog(QDialog):
    def __init__(self, parent=None):
        
        super().__init__(parent)
        self.setWindowTitle("Select Date")  #popupის სათაური
        self.setFixedSize(300, 300)  #ზომა

        self.calendar = QCalendarWidget(self)   #ვიღებთ QCalen... widgets da vanichebt calendars selfit
        self.calendar.setGridVisible(True)     #ხაზები რო ჩანდეს თვითონ კალენდარშ
        self.calendar.setSelectedDate(QDate.currentDate()) #დღევანდელი თარიღი ჩანდეს თავდაპირველად
        self.calendar.setStyleSheet("color: white;")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel) #cancel da ok functions
        self.buttonBox.accepted.connect(self.accept) #ok-ზე accept აბრუნებს

        self.buttonBox.rejected.connect(self.reject) #cancel-ზე reject აბრუნებს (ორივე შემთხვევაშ საწყის გვერდზე გვაბრუნებს)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        self.buttonBox.setFont(font)
        self.buttonBox.setStyleSheet("color:white;")

        # ესენი ძაან basic არის მიხვდები თვითონაც
        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def selected_date(self):     #(არჩეული თარიღის დაბრუნება/გადაცემა)
        return self.calendar.selectedDate()


class MyApp(QMainWindow, Ui_MainWindow):
 def __init__(self):
  super().__init__()
  self.setupUi(self)  # UI დიზაინის დაყენება

  # ვანიშნებთ დღეს და ვსვამთ dateButton-ზე ტექსტად
  today = QDate.currentDate()
  self.dateButton.setText(today.toString("d MMMM yyyy"))  # მაგ. "9 July 2025"

  # ღილაკზე დაჭერისას კალენდრის popup გამოჩნდება
  self.dateButton.clicked.connect(self.show_date_picker)

 # popup კალენდრის ჩვენება
 def show_date_picker(self):
  dialog = DatePickerDialog(self)  # popup ფანჯრის შექმნა
  if dialog.exec_() == QDialog.Accepted:  # თუ OK-ს დააჭირა
   selected_date = dialog.selected_date()  # აიღე არჩეული თარიღი
   self.dateButton.setText(selected_date.toString("d MMMM yyyy"))  # ღილაკზე შეცვალე ტექსტი
   self.getDate()  # ბეჭდავს არჩეულ თარიღს ტერმინალში

 # ფუნქცია რომელიც ბეჭდავს მიმდინარე თარიღს ტერმინალში
 def getDate(self):
  print("Selected date is:", self.dateButton.text())


app = QApplication(sys.argv)
window = MyApp()
window.show()
sys.exit(app.exec())