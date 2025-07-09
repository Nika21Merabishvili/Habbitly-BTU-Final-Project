import sys
import sqlite3  # ბაზა
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate
from ui_habbitly import Ui_MainWindow  # UI ფაილი

# თარიღის არჩევა
class DatePickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date") #სათაური
        self.setFixedSize(300, 300) #ზოა
        self.calendar = QCalendarWidget(self) #ვიჯეტი
        self.calendar.setGridVisible(True) #ხაზები ჩანდეს კალენდარში
        self.calendar.setSelectedDate(QDate.currentDate()) #დღევანდელი თარიღი
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel) #ok და ცანცელ ფუნქციები
        self.buttonBox.accepted.connect(self.accept) #ოკზე ექსეფთი
        self.buttonBox.rejected.connect(self.reject) #ქენსელზე რეჯექთი
        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def selected_date(self): #არჩევა დეითის მერე დაგვჭირდება
        return self.calendar.selectedDate()

# ჩვევის დამატება
class AddHabitDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Habit") #სათაური
        self.setFixedSize(300, 100) #ზომა
        layout = QVBoxLayout()
        self.input = QLineEdit() #ტექსტის ჩასაწერად Lineedit
        self.input.setPlaceholderText("Enter habit") #Linceedit-ზე მკრთალი ტექსტი placeholder
        save_button = QPushButton("Save") #სეივი რო ექრვას
        save_button.clicked.connect(self.accept) #დაკლიკებისას ექსეფთი
        layout.addWidget(self.input)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def get_habit(self): #გეთერი ჰებითის
        return self.input.text()

# ჩვევების რედაქტირება
class CustomizeDialog(QDialog):
    def __init__(self, habits):
        super().__init__()
        self.setWindowTitle("Customize Habits") #სათაური
        self.setFixedSize(300, 300) #ზომა
        self.habits = habits #ინიციალიზაცია
        self.list_widget = QListWidget() #ლისთვიჯეტი
        self.list_widget.addItems(habits) #აითემების დამატება
        self.edit_btn = QPushButton("Edit") #ერქვას ღილაკს edit
        self.delete_btn = QPushButton("Delete") #delete
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)
        self.setLayout(layout)
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn.clicked.connect(self.delete_item)

    def edit_item(self): #ედითი ყველაფერი მიხვდები ძაან ქომონ სენსია
        item = self.list_widget.currentItem()
        if item:
            new_text, ok = QInputDialog.getText(self, "Edit Habit", "New name:", text=item.text())
            if ok and new_text:
                item.setText(new_text)

    def delete_item(self): #ესეც ქომონ სენსია
        item = self.list_widget.currentItem()
        if item:
            self.list_widget.takeItem(self.list_widget.row(item))

# მთავარი ფანჯარა
class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.conn = sqlite3.connect("habits.db")  # ბაზასთან კავშირი
        self.cursor = self.conn.cursor()
        self.create_table()  # ცხრილის შექმნა
        self.habits = []  # ჩვევების სია
        self.scroll_area = self.scrollArea #სქროლ არეა
        self.scroll_area.setWidgetResizable(True) #იზრდებოდეს და იკლებდეს ზომაშ
        self.scroll_content = self.scrollAreaWidgetContents #სქროლარეაზეკონტენტები ანუ ჩანაწერები
        self.layout = QVBoxLayout(self.scroll_content)
        self.layout.addStretch()  # რომ ზემოდან დაეწყოს
        self.scrollLayout = self.layout
        today = QDate.currentDate()
        self.dateButton.setText(today.toString("d MMMM yyyy")) #ესენიც მარტივებია მიხვდები
        self.dateButton.clicked.connect(self.show_date_picker)
        self.addButton.clicked.connect(self.show_add_dialog)
        self.cusButton.clicked.connect(self.show_customize_dialog)
        self.load_habits()  # ბაზიდან ჩატვირთვა

    def create_table(self): #შექმნა ცხრილში
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit TEXT NOT NULL UNIQUE
            )
        ''')
        self.conn.commit()

    def load_habits(self):  #ცხრილში ჩანს და ირჩევ
        self.cursor.execute("SELECT habit FROM habits")
        rows = self.cursor.fetchall()
        for row in rows:
            habit = row[0]
            cb = QCheckBox(habit)
            cb.setStyleSheet("color: white;")
            self.scrollLayout.takeAt(self.scrollLayout.count() - 1)
            self.scrollLayout.addWidget(cb)
            self.scrollLayout.addStretch()
            self.habits.append(habit)

    def show_date_picker(self):  #თარიღის წამოღება
        dialog = DatePickerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_date = dialog.selected_date()
            self.dateButton.setText(selected_date.toString("d MMMM yyyy"))
            self.getDate() #ტერმინალში პრინტისთვის გვინდა

    def getDate(self): #ტერმინალში პრინტი
        print("Selected date is:", self.dateButton.text())

    def show_add_dialog(self): #ქომონ სენსია
        dialog = AddHabitDialog()
        if dialog.exec_():
            habit = dialog.get_habit()
            if habit and habit not in self.habits:
                try:
                    self.cursor.execute("INSERT INTO habits (habit) VALUES (?)", (habit,))
                    self.conn.commit()
                    cb = QCheckBox(habit)
                    cb.setStyleSheet("color: pink;")
                    self.scrollLayout.takeAt(self.scrollLayout.count() - 1)
                    self.scrollLayout.addWidget(cb)
                    self.scrollLayout.addStretch()
                    self.scroll_area.verticalScrollBar().setValue(0)
                    self.habits.append(habit)
                except sqlite3.IntegrityError:
                    print("Habit already exists in database")

    def show_customize_dialog(self):
        dialog = CustomizeDialog(self.habits)
        dialog.exec_()

# აპის გაშვება
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
