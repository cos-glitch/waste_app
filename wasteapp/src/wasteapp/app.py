"""
App to track trash days
"""

import toga
from toga.style.pack import COLUMN, ROW
from datetime import date
import calendar


class WasteApp(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.today = date.today()
        self.displayed_year = self.today.year
        self.displayed_month = self.today.month
        self.selected_day = self.today

        main_box = toga.Box(direction=COLUMN,
                            margin=10)
        
        name_label = toga.Label("Next trash day:",
                                margin = (0, 5))
        main_box.add(name_label)

        # month navigation
        navigation = toga.Box(
            direction=ROW,
            margin=5
        )

        previous_button = toga.Button(
            "<",
            on_press=self.previous_month,
            margin=5
        )
        self.month_label = toga.Label(
            "",
            margin=5,
            flex=1
        )

        next_button = toga.Button(
            ">",
            on_press=self.next_month,
            margin=5
        )

        navigation.add(previous_button)
        navigation.add(self.month_label)
        navigation.add(next_button)
        main_box.add(navigation)

        # calendar
        self.calendar_box = toga.Box(
            direction=COLUMN, 
            margin=5)
        
        main_box.add(self.calendar_box)

        self.selected_label = toga.Label(
            "",
            margin=5
        )
        main_box.add(self.selected_label)

        self.render_calendar()


        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
    

    def render_calendar(self):
        self.today = date.today()
        self.calendar_box.clear()

        month_name = date(
            self.displayed_year,
            self.displayed_month,
            1
        ).strftime("%B %Y")

        self.month_label.text = month_name

        # weekday headings
        weekday_box = toga.Box(
            direction=ROW,
            flex=1
        )

        for day_name in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            weekday_box.add(
                toga.Box(
                    children=[
                        toga.Label(
                            day_name,
                            text_align="center"
                        )
                    ],
                    flex=1,
                    margin=2
                )
            )

        self.calendar_box.add(weekday_box)

        # date grid
        weeks = calendar.Calendar(
            firstweekday=0
        ).monthdayscalendar(
            self.displayed_year,
            self.displayed_month
        )

        for week in weeks:
            week_box = toga.Box(
                direction=ROW
            )

            for day in week:
                if day == 0:
                    cell = toga.Box(flex=1, margin=2)
                else:
                    current_date = date(
                        self.displayed_year,
                        self.displayed_month,
                        day
                    )
                    label = str(day)

                    if current_date == self.today:
                        label = f"[{day}]"
                    button = toga.Button(
                        label,
                        on_press=lambda widget, 
                        d=current_date:
                            self.selected_date(d),
                        flex=1,
                        margin=2
                    )

                    cell = button
                week_box.add(cell)
            self.calendar_box.add(week_box)
        self.update_selected_label()

    def selected_date(self, selected_date):
        self.selected_day = selected_date
        self.render_calendar()

    def update_selected_label(self):
        self.selected_label.text = (
            f"Selected date: {self.selected_day.strftime('%d %B %Y')}"
        )

    def previous_month(self, widget):
        if self.displayed_month == 1:
            self.displayed_month = 12
            self.displayed_year -= 1
        else:
            self.displayed_month -= 1

        self.render_calendar()

    def next_month(self, widget):
        if self.displayed_month == 12:
            self.displayed_month = 1
            self.displayed_year += 1
        else:
            self.displayed_month += 1

        self.render_calendar()


def main():
    return WasteApp()
