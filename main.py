import sys
import sqlite3
from datetime import date
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, pyqtSignal, QTimer, Qt
from ui_habbitly import Ui_MainWindow
  # UI ფაილი


# თარიღის არჩევა
class DatePickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date")  # სათაური
        self.setFixedSize(300, 300)  # ზოა
        self.calendar = QCalendarWidget(self)  # ვიჯეტი
        self.calendar.setGridVisible(True)  # ხაზები ჩანდეს კალენდარში
        self.calendar.setSelectedDate(QDate.currentDate())  # დღევანდელი თარიღი
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  # ok და cancel ღილაკები
        self.buttonBox.accepted.connect(self.accept)  # ok-ზე accept
        self.buttonBox.rejected.connect(self.reject)  # cancel-ზე reject
        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def selected_date(self):  # არჩევის შემდეგ დაბრუნდეს არჩეული თარიღი
        return self.calendar.selectedDate()


# ჩვევის დამატება
class AddHabitDialog(QDialog):
    habit_added = pyqtSignal()  # სიგნალი რომ დავამატეთ ჩვევა

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Habit")  # სათაური
        self.setFixedSize(300, 100)  # ზომა
        layout = QVBoxLayout()
        self.input = QLineEdit()  # ტექსტის ჩასაწერად LineEdit
        self.input.setPlaceholderText("Enter habit")  # placeholder
        save_button = QPushButton("Save")  # ღილაკი Save
        save_button.clicked.connect(self.save_and_emit)  # ღილაკზე დაჭერით შესრულება
        layout.addWidget(self.input)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def save_and_emit(self):  # ჩვევის დამატებისას გავუშვათ სიგნალი
        if self.input.text().strip():
            self.habit_added.emit()
            self.accept()

    def get_habit(self):  # გეთერი
        return self.input.text()




# ჩვევების რედაქტირება (დამატება/წაშლა)
class CustomizeDialog(QDialog):
    habits_updated = pyqtSignal()  # ჩვევების განახლების სიგნალი

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customize Habits")
        self.setFixedSize(300, 300)
        self.conn = sqlite3.connect("habits.db")
        self.cursor = self.conn.cursor()
        self.list_widget = QListWidget()
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)
        self.setLayout(layout)
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn.clicked.connect(self.delete_item)
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        self.cursor.execute("SELECT habit FROM habits WHERE deleted_date IS NULL")
        habits = self.cursor.fetchall()
        for row in habits:
            self.list_widget.addItem(row[0])

    def edit_item(self):
        item = self.list_widget.currentItem()
        if item:
            old_text = item.text()
            new_text, ok = QInputDialog.getText(self, "Edit Habit", "ახალი სახელი:", text=old_text)
            if ok and new_text:
                try:
                    self.cursor.execute("UPDATE habits SET habit = ? WHERE habit = ?", (new_text, old_text))
                    self.conn.commit()
                    self.refresh_list()
                    self.habits_updated.emit()
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Error", "ასეთი ჩვევა უკვე არსებობს")

    def delete_item(self):
        item = self.list_widget.currentItem()
        if item:
            habit_text = item.text()
            confirm = QMessageBox.question(self, "Confirm Delete", f"ნამდვილად წავშალოთ '{habit_text}'?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.cursor.execute("UPDATE habits SET deleted_date = date('now') WHERE habit = ?", (habit_text,))
                self.conn.commit()
                self.refresh_list()
                self.habits_updated.emit()


# მთავარი ფანჯარა
class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.conn = sqlite3.connect("habits.db")
        self.cursor = self.conn.cursor()
        self.create_table()
        self.scroll_area = self.scrollArea
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = self.scrollAreaWidgetContents
        self.layout = QVBoxLayout(self.scroll_content)
        self.layout.addStretch()
        self.scrollLayout = self.layout
        self.current_date = QDate.currentDate()
        self.dateButton.setText(self.current_date.toString("d MMMM yyyy"))
        self.dateButton.clicked.connect(self.show_date_picker)
        self.addButton.clicked.connect(self.show_add_dialog)
        self.cusButton.clicked.connect(self.show_customize_dialog)
        self.load_habits_for_date(self.current_date)

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit TEXT NOT NULL UNIQUE,
                created_date TEXT NOT NULL DEFAULT (date('now')),
                deleted_date TEXT DEFAULT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habit_dates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_date TEXT NOT NULL,
                habit_id INTEGER NOT NULL,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (habit_id) REFERENCES habits(id),
                UNIQUE(habit_date, habit_id)
            )
        ''')

        self.conn.commit()

    def load_habits_for_date(self, qdate):
        while self.scrollLayout.count() > 1:
            item = self.scrollLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.habits = []
        selected_str = qdate.toString("yyyy-MM-dd")

        self.cursor.execute('''
            SELECT id, habit FROM habits
            WHERE created_date <= ? AND (deleted_date IS NULL OR deleted_date > ?)
        ''', (selected_str, selected_str))

        habits = self.cursor.fetchall()

        for habit_id, habit_name in habits:
            cb = QCheckBox(habit_name)
            cb.setStyleSheet("color: white;")

            self.cursor.execute('''
                SELECT completed FROM habit_dates
                WHERE habit_date = ? AND habit_id = ?
            ''', (selected_str, habit_id))
            result = self.cursor.fetchone()

            if result and result[0] == 1:
                cb.setChecked(True)

            def update_status(state, habit_id=habit_id):
                completed = 1 if state == Qt.Checked else 0
                self.cursor.execute('''
                    INSERT INTO habit_dates (habit_date, habit_id, completed)
                    VALUES (?, ?, ?)
                    ON CONFLICT(habit_date, habit_id) DO UPDATE SET completed = ?
                ''', (selected_str, habit_id, completed, completed))
                self.conn.commit()
                self.update_progress_bar()

            cb.stateChanged.connect(update_status)
            self.scrollLayout.insertWidget(self.scrollLayout.count() - 1, cb)
            self.habits.append(cb)

        self.update_progress_bar()

    def update_progress_bar(self):
        total = len(self.habits)
        done = sum(1 for cb in self.habits if cb.isChecked())
        percent = round((done / total) * 100) if total else 0
        self.animate_progress(percent)

    def animate_progress(self, target):
        current = self.progressBar.value()
        if current == target:
            return  # თუ უკვე იგივე მნიშვნელობაა, არ ვანიმიროთ

        step = 1 if target > current else -1

        def step_up():
            nonlocal current
            current += step
            self.progressBar.setValue(current)
            if current == target:
                timer.stop()

        timer = QTimer(self)
        timer.timeout.connect(step_up)
        timer.start(10)

    def reload_habits(self):
        self.load_habits_for_date(self.current_date)

    def show_date_picker(self):
        dialog = DatePickerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_date = dialog.selected_date()
            self.current_date = selected_date
            self.dateButton.setText(selected_date.toString("d MMMM yyyy"))
            self.load_habits_for_date(selected_date)

    def show_add_dialog(self):
        dialog = AddHabitDialog()
        dialog.habit_added.connect(self.reload_habits)
        if dialog.exec_():
            habit = dialog.get_habit()
            if habit:
                today_str = self.current_date.toString("yyyy-MM-dd")

                # შემოწმება: არსებობს თუ არა ჩვევა სადაც deleted_date IS NULL
                self.cursor.execute(
                    "SELECT id FROM habits WHERE habit = ? AND deleted_date IS NULL", (habit,)
                )
                existing = self.cursor.fetchone()

                if existing:
                    print("Habit already exists in database")
                else:
                    # თუ მსგავსი ჩვევა წაშლილია, ავააქტიუროთ (deleted_date=NULL)
                    self.cursor.execute(
                        "SELECT id FROM habits WHERE habit = ? AND deleted_date IS NOT NULL", (habit,)
                    )
                    deleted_habit = self.cursor.fetchone()

                    if deleted_habit:
                        self.cursor.execute(
                            "UPDATE habits SET deleted_date = NULL WHERE id = ?", (deleted_habit[0],)
                        )
                    else:
                        self.cursor.execute(
                            "INSERT INTO habits (habit, created_date) VALUES (?, ?)", (habit, today_str)
                        )
                    self.conn.commit()
                    self.reload_habits()

    def show_customize_dialog(self):
        dialog = CustomizeDialog()
        dialog.habits_updated.connect(self.reload_habits)
        dialog.exec_()


# აპის გაშვება
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
