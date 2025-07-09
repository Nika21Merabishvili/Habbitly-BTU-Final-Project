


import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout,
    QCalendarWidget, QDialogButtonBox, QLineEdit, QPushButton,
    QCheckBox, QListWidget, QInputDialog
)
from PyQt5.QtCore import QDate
from ui_habbitly import Ui_MainWindow


class DatePickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date")
        self.setFixedSize(300, 300)

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(QDate.currentDate())

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def selected_date(self):
        return self.calendar.selectedDate()


class AddHabitDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Habit")
        self.setFixedSize(300, 100)
        layout = QVBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter habit")
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        layout.addWidget(self.input)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def get_habit(self):
        return self.input.text()


class CustomizeDialog(QDialog):
    def __init__(self, habits):
        super().__init__()
        self.setWindowTitle("Customize Habits")
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

    def edit_item(self):
        item = self.list_widget.currentItem()
        if item:
            new_text, ok = QInputDialog.getText(self, "Edit Habit", "New name:", text=item.text())
            if ok and new_text:
                item.setText(new_text)

    def delete_item(self):
        item = self.list_widget.currentItem()
        if item:
            self.list_widget.takeItem(self.list_widget.row(item))


class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.habits = []

        self.scrollLayout = QVBoxLayout(self.scrollAreaWidgetContents)

        today = QDate.currentDate()
        self.dateButton.setText(today.toString("d MMMM yyyy"))
        self.dateButton.clicked.connect(self.show_date_picker)

        self.addButton.clicked.connect(self.show_add_dialog)
        self.cusButton.clicked.connect(self.show_customize_dialog)

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
            if habit:
                cb = QCheckBox(habit)
                cb.setStyleSheet("color: pink;")
                self.scrollLayout.addWidget(cb)
                self.habits.append(habit)

    def show_customize_dialog(self):
        dialog = CustomizeDialog(self.habits)
        dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
