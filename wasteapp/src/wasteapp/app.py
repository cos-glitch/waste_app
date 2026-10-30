"""
App to track trash days
"""

import toga
from toga.style.pack import COLUMN, ROW, Pack
from datetime import date
import calendar
import json
from pathlib import Path
from .notifications import enable_notifications
from .notifications import schedule_test_notification


WASTE_TYPES = [
    "General waste",
    "Food waste",
    "Cardboard recycling",
    "Plastic recycling",
    "Glass recycling",
    "Metal recycling"
]


class WasteApp(toga.App):
    def startup(self):
        """
        Main window of the wasteapp.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.today = date.today()
        self.displayed_year = self.today.year
        self.displayed_month = self.today.month
        self.selected_day = self.today

        # load collection schedule
        self.collection_rules = self.load_collection_rules()


        main_box = toga.Box(direction=COLUMN,
                            margin=10)

        # FOR TESTING, REMOVE
        # test_notification_button = toga.Button(
        #     "Test notification (2 minutes)",
        #     on_press=self.test_notification,
        #     margin=5
        # )
        # main_box.add(test_notification_button)
        
        # name_label = toga.Label("Waste collection calendar:",
        #                         margin = (0, 5))
        # main_box.add(name_label)

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
            flex=1,
            text_align = "center",
            font_weight="bold",
            font_size=20
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
            margin=2,
            flex=1)
        
        main_box.add(self.calendar_box)

        self.selected_label = toga.Label(
            "",
            margin=(10, 5)
        )
        main_box.add(self.selected_label)

        self.collection_list = toga.Box(
            direction=COLUMN,
            margin=5,
            height=120
        )

        main_box.add(self.collection_list)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = toga.ScrollContainer(
            content=main_box,
            horizontal=False,
            vertical=True,
            style=Pack(flex=1)
        )

        self.render_calendar()
        self.main_window.show()

        # enable collection reminders
        enable_notifications(
            self,
            self.collection_rules
        )


    def load_collection_rules(self):
        """Load the collection rules from the json file"""
        rules_file = Path(__file__).parent / "collection_rules.json"

        with rules_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        rules = []

        for rule in data["rules"]:
            start_date = date.fromisoformat(rule["start_date"])

            rules.append({
                "type": rule["type"],
                "start_date": start_date,
                "interval_weeks": int(rule["interval_weeks"]),
                "weekday": rule["weekday"].lower(),
                "colour": rule["colour"],
            })

            # ensure the date occurs on the right weekday
            expected_weekday = start_date.strftime("%A").lower()
            if rule["weekday"].lower() != expected_weekday:
                print(
                    f"Warning: {rule['type']} starts on "
                    f"{expected_weekday}, not {rule['weekday']}."
                )

        return rules

    def collection_rules_for_day(self, day):
        """Return all collection rules that apply on a date."""
        collections = []

        for rule in self.collection_rules:
            start = rule["start_date"]
            interval_days = rule["interval_weeks"] * 7

            days_since_start = (day - start).days

            if days_since_start < 0:
                continue

            # Ensure the collection is on the correct weekday
            # and the correct recurring week.
            if day.weekday() != start.weekday():
                continue

            if days_since_start % interval_days != 0:
                continue

            collections.append(rule)

        return collections


    def collection_for_day(self, day):
        """Return waste type for a date"""
        return [
            rule["type"]
            for rule in self.collection_rules_for_day(day)
        ]

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
            flex=1,
            margin=0
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
                direction=ROW,
                flex=1
            )

            for day in week:
                if day == 0:
                    week_box.add(
                        toga.Box(flex=1, margin=2)
                    )
                    continue

                current_date = date(
                    self.displayed_year,
                    self.displayed_month,
                    day
                )
                collections = self.collection_rules_for_day(current_date)

                is_today = current_date == self.today
                is_selected = current_date == self.selected_day

                colour_row = toga.Box(
                    direction=ROW,
                    height=8,
                    flex=1,
                    # margin=(0,0,0,4),
                    margin=0,
                    align_items="center"
                )

                if collections:
                    for rule in collections:
                        colour_row.add(
                            toga.Box(
                                flex=1,
                                background_color=rule["colour"]
                            )
                        )
                else:
                    colour_row.add(
                        toga.Box(
                            flex=1,
                            background_color="#EEEEEE"
                        )
                    )

                button = toga.Button(
                    str(day),
                    on_press=lambda widget, d=current_date:
                        self.selected_date(d),
                    flex=1,
                    margin=0
                )

                if is_today:
                    button.style.background_color = "#2583E8"
                    button.style.color = "#FFFFFF"
                elif is_selected:
                    button.style.background_color = "#DCEBFA"

                cell = toga.Box(
                    direction=COLUMN,
                    flex=1,
                    margin=1,
                    align_items="center"
                )
                cell.add(colour_row)
                cell.add(button)
                week_box.add(cell)
            self.calendar_box.add(week_box)
        self.update_selected_label()

    def selected_date(self, selected_date):
        self.selected_day = selected_date
        self.render_calendar()

    def update_selected_label(self):
        day = self.selected_day

        self.selected_label.text = (
            f"Collections for {day.strftime('%A, %d %B %Y')}"
        )

        self.collection_list.clear()

        collections = self.collection_rules_for_day(day)

        if not collections:
            self.collection_list.add(
                toga.Label("No waste collection scheduled.")
            )
            return

        for rule in collections:
            colour_swatch = toga.Box(
                width=18,
                height=18,
                background_color=rule["colour"],
                margin=(0, 8, 0, 0)
            )

            collection_row = toga.Box(
                direction=ROW,
                margin=3,
                align_items="center"
            )
            collection_row.add(colour_swatch)
            collection_row.add(
                toga.Label(rule["type"], flex=1)
            )

            self.collection_list.add(collection_row)

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

    # def send_notification(self, title, message):
    #     PythonActivity = autoclass('org.beeware.android.MainActivity')
    #     NotificationManager = autoclass('android.app.NotificationManager')
    #     NotificationBuilder = autoclass('android.app.Notification$Builder')

    #     String = autoclass('java.lang.String')

    #     activity = PythonActivity.singletonThis
    #     manager = activity.getSystemService(activity.NOTIFICATION_SERVICE)

    #     builder = NotificationBuilder(activity)
    #     builder.setContentTitle(String(title))
    #     builder.setContentText(String(message))
    #     builder.setSmallIcon(activity.getApplicationInfo().icon)
    #     builder.setAutoCancel(True)

    #     notification = builder.build()
    #     manager.notify(1, notification)

    def test_notification(self, widget):
        schedule_test_notification(self, 120)


def main():
    return WasteApp(
        icon="icons/myicon"
    )
