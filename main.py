import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout,
    QCalendarWidget, QDialogButtonBox, QLineEdit, QPushButton,
    QCheckBox, QListWidget, QInputDialog, QScrollArea, QWidget
)
from PyQt5.QtCore import QDate
from ui_habbitly import Ui_MainWindow

#viyenebt Qdialogs radgan popup gvinda
class DatePickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date") #satauri
        self.setFixedSize(300, 300) #size

        self.calendar = QCalendarWidget(self) #Qcalendars vighebt
        self.calendar.setGridVisible(True) #calendarshi xazebi chandes
        self.calendar.setSelectedDate(QDate.currentDate()) #dghevandeli date

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel) #ok da cancel functions
        self.buttonBox.accepted.connect(self.accept) #okze accept
        self.buttonBox.rejected.connect(self.reject) #cancelze reject

        layout = QVBoxLayout() #es dzaan ezia mixvdebi
        layout.addWidget(self.calendar)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def selected_date(self):    #dro ro terminalshi wamovighot magistvis selects vamatebs da bazashic dagvchirdeba
        return self.calendar.selectedDate()


class AddHabitDialog(QDialog):   #add ghilaki habbit
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Habit") #satauri
        self.setFixedSize(300, 100) #zoma
        layout = QVBoxLayout()
        self.input = QLineEdit() #teqshi linedit gvinda
        self.input.setPlaceholderText("Enter habit") #mkrtalad ro chandes placeholder
        save_button = QPushButton("Save") #save ghilaki
        save_button.clicked.connect(self.accept) #daclikcbisas saveze accept
        layout.addWidget(self.input) #ameebs mixvdebi
        layout.addWidget(save_button)
        self.setLayout(layout)

    def get_habit(self):    #get habbit bazistvis da mainappistvis
        return self.input.text()


class CustomizeDialog(QDialog): #custom button
    def __init__(self, habits):
        super().__init__()
        self.setWindowTitle("Customize Habits") #eseni igivea rac wina ghilakebshi da mixvdebi yvelafers
        self.setFixedSize(300, 300)
        self.habits = habits
        self.list_widget = QListWidget()
        self.list_widget.addItems(habits)
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)
        self.setLayout(layout)
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn.clicked.connect(self.delete_item)

    def edit_item(self):  #customizes shignis edit
        item = self.list_widget.currentItem()  #vighebt shignis items
        if item:
            new_text, ok = QInputDialog.getText(self, "Edit Habit", "New name:", text=item.text()) #mogvaq teqsti da vcvlis
            if ok and new_text: #tu uve axali teqsti chawerilia vcvlit
                item.setText(new_text)

    def delete_item(self): #delete customizeshi
        item = self.list_widget.currentItem()
        if item:
            self.list_widget.takeItem(self.list_widget.row(item))


class MyApp(QMainWindow, Ui_MainWindow):  #eseni dzaan common senseia mixvdebi
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.conn = sqlite3.connect("habits.db")  #მიმდევრობა bazastan
        self.cursor = self.conn.cursor()
        self.create_table()

        self.habits = []

        # --- Scroll area with top alignment ---
        self.scroll_area = self.scrollArea  # უკვე UI-ში გაქვს scrollArea
        self.scroll_area.setWidgetResizable(True)

        # კონტეინერი ვიჯეტი (scrollAreaWidgetContents უკვე გაქვს UI-ში)
        self.scroll_content = self.scrollAreaWidgetContents

        # მთავარი ლეიაუტი ჩვევებისთვის
        self.layout = QVBoxLayout(self.scroll_content)

        # stretch რათა ყველა checkBox ზემოდან იყოს და ქვემოთ დაიწიოს სივრცე
        self.layout.addStretch()

        # მაგ ლეიაუტს მივანიჭებთ, როგორც habit-ების ლეიაუტს
        self.scrollLayout = self.layout

        today = QDate.currentDate()
        self.dateButton.setText(today.toString("d MMMM yyyy"))
        self.dateButton.clicked.connect(self.show_date_picker)

        self.addButton.clicked.connect(self.show_add_dialog)
        self.cusButton.clicked.connect(self.show_customize_dialog)

        self.load_habits()  #bazidan chawera

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit TEXT NOT NULL UNIQUE
            )
        ''')
        self.conn.commit()

    def load_habits(self):  #apshi chawera checkmarkebit bazidan
        self.cursor.execute("SELECT habit FROM habits")
        rows = self.cursor.fetchall()
        for row in rows:
            habit = row[0]
            cb = QCheckBox(habit)
            cb.setStyleSheet("color: pink;")

            # დინამურად დაამატე checkBox-ები ზემოდან
            self.scrollLayout.takeAt(self.scrollLayout.count() - 1)
            self.scrollLayout.addWidget(cb)
            self.scrollLayout.addStretch()

            self.habits.append(habit)

    def show_date_picker(self):
        dialog = DatePickerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_date = dialog.selected_date()
            self.dateButton.setText(selected_date.toString("d MMMM yyyy"))
            self.getDate()

    def getDate(self):
        print("Selected date is:", self.dateButton.text())

    def show_add_dialog(self):
        dialog = AddHabitDialog()
        if dialog.exec_():
            habit = dialog.get_habit()
            if habit and habit not in self.habits:
                try:
                    self.cursor.execute("INSERT INTO habits (habit) VALUES (?)", (habit,))
                    self.conn.commit()
                    cb = QCheckBox(habit)
                    cb.setStyleSheet("color: pink;")

                    # stretch-ს მოვხსნით დროებით
                    self.scrollLayout.takeAt(self.scrollLayout.count() - 1)
                    self.scrollLayout.addWidget(cb)
                    self.scrollLayout.addStretch()

                    # scroll ზემოთ
                    self.scroll_area.verticalScrollBar().setValue(0)

                    self.habits.append(habit)
                except sqlite3.IntegrityError:
                    print("Habit already exists in database")

    def show_customize_dialog(self):
        dialog = CustomizeDialog(self.habits)
        dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
