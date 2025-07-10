import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont
from ui_habbitly import Ui_MainWindow  
import matplotlib.pyplot as plt
from mpl_canvas import MplCanvas


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
    habit_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Habit")
        self.setFixedSize(300, 100)
        self.setStyleSheet("background-color: #242424; color: white;")
        layout = QVBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter habit")
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_and_emit)
        layout.addWidget(self.input)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def save_and_emit(self):
        if self.input.text().strip():
            self.habit_added.emit()
            self.accept()

    def get_habit(self):
        return self.input.text()


class CustomizeDialog(QDialog):
    habits_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customize Habits")
        self.setFixedSize(300, 300)
        self.setStyleSheet("background-color: #242424; color: white;")
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
            new_text, ok = QInputDialog.getText(self, "Edit Habit", "New name:", text=old_text)
            if ok and new_text:
                try:
                    self.cursor.execute("UPDATE habits SET habit = ? WHERE habit = ?", (new_text, old_text))
                    self.conn.commit()
                    self.refresh_list()
                    self.habits_updated.emit()
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Error", "Habit with this name already exists")

    def delete_item(self):
        item = self.list_widget.currentItem()
        if item:
            habit_text = item.text()
            confirm = QMessageBox.question(self, "Confirm Delete",
                                           f"Really delete '{habit_text}'?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    self.cursor.execute("SELECT id FROM habits WHERE habit = ?", (habit_text,))
                    habit_id = self.cursor.fetchone()[0]

                    self.cursor.execute("DELETE FROM habit_dates WHERE habit_id = ?", (habit_id,))

                    self.cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))

                    self.conn.commit()
                    self.refresh_list()
                    self.habits_updated.emit()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to delete habit: {str(e)}")
                    self.conn.rollback()


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

        self.mpl_canvas = MplCanvas(self.frame, width=2.5, height=4.0, dpi=100)
        self.mpl_layout = QVBoxLayout(self.frame)
        self.mpl_layout.setContentsMargins(0, 0, 0, 0)
        self.mpl_layout.addWidget(self.mpl_canvas)

        self.load_habits_for_date(self.current_date)
        self.dateRTFormat = self.current_date.toString(Qt.ISODate)
        print(QDate.currentDate().daysInMonth())
        print(self.dateRTFormat)

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit TEXT NOT NULL,
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

    def calculate_streak(self, habit_id, current_date):
        """Calculate the current streak for a habit"""
        streak = 0
        date_obj = datetime.strptime(current_date, "%Y-%m-%d").date()

        while True:
            self.cursor.execute('''
                SELECT completed FROM habit_dates 
                WHERE habit_id = ? AND habit_date = ?
            ''', (habit_id, date_obj.strftime("%Y-%m-%d")))
            result = self.cursor.fetchone()

            if result and result[0] == 1:
                streak += 1
                date_obj -= timedelta(days=1)
            else:
                break

        return streak

    def update_graph(self):
        l = []
        l2 = []
        selected_date = self.current_date
        for i in range(selected_date.daysInMonth()):
            if i + 1 < 10:
                k = selected_date.toString(f"yyyy-MM-0{i+1}")
            else:
                k = selected_date.toString(f"yyyy-MM-{i+1}")
            self.cursor.execute('''SELECT * FROM habit_dates WHERE habit_date=? AND completed=1''', (k,))
            l.append(len(self.cursor.fetchall()))
            l2.append(i + 1)
        # print(l, l2)
        # if max(l) == 0:
        #     for i in range(selected_date.daysInMonth()):
        #         l.append(5)
        #         l2.append(i + 1)
        self.mpl_canvas.axes.clear()
        self.mpl_canvas.axes.plot(l, l2, color='tab:blue')
        self.mpl_canvas.axes.set_facecolor('#242424')
        self.mpl_canvas.fig.patch.set_facecolor('#242424')
        for spine in self.mpl_canvas.axes.spines.values():
            spine.set_visible(False)
        self.cursor.execute('''SELECT * FROM habits''')
        p = [len(self.cursor.fetchall())]  
        if max(l) == 0:
            self.mpl_canvas.axes.set_xlim(left=0, right=5)
        else:
            self.mpl_canvas.axes.set_xlim(left=0, right=p[0])
        from matplotlib.ticker import MaxNLocator
        self.mpl_canvas.axes.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.mpl_canvas.axes.tick_params(axis='x', colors='white')
        self.mpl_canvas.axes.tick_params(axis='y', colors='white')
        self.mpl_canvas.axes.xaxis.label.set_color('white')
        self.mpl_canvas.axes.yaxis.label.set_color('white')
        self.mpl_canvas.axes.title.set_color('white')
        self.mpl_canvas.fig.tight_layout()
        self.mpl_canvas.draw()

    def load_habits_for_date(self, qdate):
        while self.scrollLayout.count() > 1:
            item = self.scrollLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        selected_str = qdate.toString("yyyy-MM-dd")

        self.cursor.execute('''
            SELECT id, habit FROM habits
            WHERE deleted_date IS NULL AND created_date <= ?
        ''', (selected_str,))

        habits = self.cursor.fetchall()
        self.habits = []

        for habit_id, habit_name in habits:
            habit_widget = QWidget()
            habit_layout = QHBoxLayout()
            habit_widget.setLayout(habit_layout)

            cb = QCheckBox(habit_name)
            cb.setStyleSheet("color: white;")

            streak = self.calculate_streak(habit_id, selected_str)

            streak_label = QLabel(f"🔥 {streak}")
            streak_label.setStyleSheet("color: #FFA500; font-weight: bold;")
            streak_label.setAlignment(Qt.AlignRight)

            habit_layout.addWidget(cb)
            habit_layout.addWidget(streak_label)
            habit_layout.addStretch()

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
                self.load_habits_for_date(self.current_date)
                self.update_graph()

            cb.stateChanged.connect(update_status)
            self.scrollLayout.insertWidget(self.scrollLayout.count() - 1, habit_widget)
            self.habits.append(cb)

        self.update_progress_bar()
        self.update_graph()

    def update_progress_bar(self):
        total = len(self.habits)
        done = sum(1 for cb in self.habits if cb.isChecked())
        percent = round((done / total) * 100) if total else 0
        self.animate_progress(percent)

    def animate_progress(self, target):
        current = self.progressBar.value()
        if current == target:
            return

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
        self.update_graph()

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
                try:
                    self.cursor.execute('''
                        INSERT INTO habits (habit, created_date)
                        VALUES (?, ?)
                    ''', (habit, self.current_date.toString("yyyy-MM-dd")))
                    self.conn.commit()
                    self.reload_habits()
                    self.update_graph()
                except sqlite3.IntegrityError as e:
                    QMessageBox.warning(self, "Error", f"Failed to add habit: {str(e)}")

    def show_customize_dialog(self):
        dialog = CustomizeDialog()
        dialog.habits_updated.connect(self.reload_habits)
        dialog.habits_updated.connect(self.update_graph)
        dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MyApp()
    window.show()
    sys.exit(app.exec_())