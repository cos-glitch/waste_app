# """Reminder notifications for waste collection"""

# import json
# from datetime import date, datetime, time, timedelta

# CHANNEL_ID = "waste_collection_reminders"
# PREFERENCES_NAME = "waste_collection_alarms"
# ACTION_REMINDER = "com.example.wasteapp.COLLECTION_REMINDER"

# # how many days in advance to schedule
# SCHEDULE_DAYS = 200

# def schedule_collection_notifications(app, rules):
#     """Schedules notifications for upcoming collection days"""

#     # from android.app import AlarmManager, PendingIntent
#     # from android.content import Intent
#     # from android.os import Build
#     # from com.example.wasteapp import NotificationReceiver

#     from java import jclass
#     AlarmManager = jclass("android.app.AlarmManager")
#     PendingIntent = jclass("android.app.PendingIntent")
#     Intent = jclass("android.content.Intent")
#     Build = jclass("android.os.Build")

#     NotificationReceiver = jclass(
#         "com.example.wasteapp.NotificationReceiver"
#     )

#     context = app._impl.native.getApplicationContext()

#     alarm_manager = context.getSystemService(context.ALARM_SERVICE)
#     preferences = context.getSharedPreferences(
#         PREFERENCES_NAME,
#         context.MODE_PRIVATE
#     )

#     editor = preferences.edit()

#     old_alarms = preferences.getAll().keySet().toArray()

#     for key in old_alarms:
#         request_code = int(str(key))

#         old_intent = Intent(
#             context,
#             NotificationReceiver
#         )

#         old_intent.setAction(ACTION_REMINDER)

#         old_pending = PendingIntent.getBroadcast(
#             context,
#             request_code,
#             old_intent,
#             PendingIntent.FLAG_NO_CREATE | PendingIntent.FLAG_IMMUTABLE
#         )

#         if old_pending is not None:
#             alarm_manager.cancel(old_pending)
#             old_pending.cancel()

#     editor.clear()

#     today = date.today()
#     end_date = today + timedelta(days=SCHEDULE_DAYS)

#     current_day = today
#     scheduled_count = 0

#     while current_day <= end_date:
#         collections = []

#         for rule in rules:
#             start = rule["start_date"]

#             interval_days = rule["interval_weeks"] * 7

#             days_since_start = (current_day - start).days

#             if days_since_start < 0:
#                 continue

#             if current_day.weekday() != start.weekday():
#                 continue

#             if days_since_start % interval_days != 0:
#                 continue

#             collections.append(rule["type"])

#         if collections:
#             reminder_date = current_day - timedelta(days=1)

#             if reminder_date >= today:
#                 reminder_datetime = datetime.combine(
#                     reminder_date,
#                     time(14, 0)
#                 ).astimezone()

#                 timestamp_ms = int(reminder_datetime.timestamp() * 1000)
#                 now_ms = int(datetime.now().astimezone().timestamp() * 1000)

#                 if timestamp_ms > now_ms:
#                     waste_types = "and ".join(collections)
#                     title = "Bin day tomorrow"
#                     message = f"Time to take out the bins, tomorrow is {waste_types}"

#                     # Collection date gives each alarm a unique ID.
#                     request_code = current_day.toordinal()

#                     intent = Intent(
#                         context,
#                         NotificationReceiver
#                     )

#                     intent.setAction(ACTION_REMINDER)

#                     intent.putExtra("title", title)
#                     intent.putExtra("message", message)
#                     intent.putExtra(
#                         "notification_id",
#                         request_code
#                     )

#                     pending_intent = PendingIntent.getBroadcast(
#                         context,
#                         request_code,
#                         intent,
#                         PendingIntent.FLAG_UPDATE_CURRENT
#                         | PendingIntent.FLAG_IMMUTABLE
#                     )

#                     # Save information for restoring alarms after reboot.
#                     alarm_data = {
#                         "timestamp": timestamp_ms,
#                         "title": title,
#                         "message": message
#                     }

#                     editor.putString(
#                         str(request_code),
#                         json.dumps(alarm_data)
#                     )

#                     # Schedule the alarm.
#                     exact_alarm_allowed = True

#                     if Build.VERSION.SDK_INT >= 31:
#                         exact_alarm_allowed = (
#                             alarm_manager.canScheduleExactAlarms()
#                         )

#                     if exact_alarm_allowed:
#                         alarm_manager.setExactAndAllowWhileIdle(
#                             AlarmManager.RTC_WAKEUP,
#                             timestamp_ms,
#                             pending_intent
#                         )

#                     else:
#                         # Temporary fallback until exact-alarm access has been granted.
#                         alarm_manager.setAndAllowWhileIdle(
#                             AlarmManager.RTC_WAKEUP,
#                             timestamp_ms,
#                             pending_intent
#                         )

#                     scheduled_count += 1

#         current_day += timedelta(days=1)

#     # Save all scheduled alarm information.
#     editor.apply()

#     return scheduled_count


# # def enable_notifications(app, rules):
# #     """
# #     Request notification and exact-alarm permissions.

# #     Once permissions are granted, schedule collection reminders.
# #     """

# #     from android.app import AlarmManager
# #     from android.content import Intent
# #     from android.content.pm import PackageManager
# #     from android.net import Uri
# #     from android.os import Build
# #     from android.provider import Settings

# #     context = app._impl.native.getApplicationContext()
# #     activity = app._impl.native

# #     notification_permission = (
# #         "android.permission.POST_NOTIFICATIONS"
# #     )


# def enable_notifications(app, rules):
#     """
#     Check notification and exact alarm access.
#     Open Android settings when access is missing.
#     Schedule reminders once access is available.
#     """

#     # from android.app import NotificationManager
#     # from android.content import Intent
#     # from android.os import Build
#     # from android.provider import Settings
#     # from android.net import Uri
#     from java import jclass

#     NotificationManager = jclass(
#         "android.app.NotificationManager"
#     )
#     Intent = jclass("android.content.Intent")
#     Build = jclass("android.os.Build")
#     Settings = jclass("android.provider.Settings")
#     Uri = jclass("android.net.Uri")
#     PackageManager = jclass(
#         "android.content.pm.PackageManager"
#     )

#     activity = app._impl.native
#     context = activity.getApplicationContext()

#     package_name = context.getPackageName()

#     def schedule_if_ready():

#         notification_manager = context.getSystemService(
#             context.NOTIFICATION_SERVICE
#         )

#         if not notification_manager.areNotificationsEnabled():
#             print("Notifications are disabled.")
#             return

#         alarm_manager = context.getSystemService(
#             context.ALARM_SERVICE
#         )

#         if (
#             Build.VERSION.SDK_INT >= 31
#             and not alarm_manager.canScheduleExactAlarms()
#         ):

#             print("Requesting exact alarm access.")

#             intent = Intent(
#                 Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM
#             )

#             intent.setData(
#                 Uri.parse("package:" + package_name)
#             )

#             def exact_alarm_returned(result, data):

#                 if alarm_manager.canScheduleExactAlarms():

#                     schedule_collection_notifications(
#                         app, rules
#                     )

#                 else:
#                     print("Exact alarm access not granted.")

#             app._impl.start_activity(
#                 intent,
#                 on_complete=exact_alarm_returned
#             )

#             return

#         count = schedule_collection_notifications(
#             app, rules
#         )

#         print(f"Scheduled {count} reminders.")

#     # Android 13 and newer.
#     if Build.VERSION.SDK_INT >= 33:

#         from android.content.pm import PackageManager

#         permission = "android.permission.POST_NOTIFICATIONS"

#         if context.checkSelfPermission(permission) != PackageManager.PERMISSION_GRANTED:

#             print("Opening notification settings.")

#             intent = Intent(
#                 Settings.ACTION_APP_NOTIFICATION_SETTINGS
#             )

#             intent.putExtra(
#                 Settings.EXTRA_APP_PACKAGE,
#                 package_name
#             )

#             def notification_settings_returned(result, data):
#                 schedule_if_ready()

#             app._impl.start_activity(
#                 intent,
#                 on_complete=notification_settings_returned
#             )

#             return

#     schedule_if_ready()


#     def schedule_if_permitted():

#         alarm_manager = context.getSystemService(
#             context.ALARM_SERVICE
#         )

#         # Android 12+ requires special exact-alarm access.
#         if (
#             Build.VERSION.SDK_INT >= 31
#             and not alarm_manager.canScheduleExactAlarms()
#         ):

#             settings_intent = Intent(
#                 Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM
#             )

#             settings_intent.setData(
#                 Uri.parse(
#                     "package:" + context.getPackageName()
#                 )
#             )

#             def settings_returned(result_code, result_data):

#                 if alarm_manager.canScheduleExactAlarms():

#                     count = schedule_collection_notifications(
#                         app, rules
#                     )

#                     print(
#                         f"Successfully scheduled {count} reminders."
#                     )

#                 else:
#                     print("Exact alarm permission was not granted.")

#             app._impl.start_activity(
#                 settings_intent,
#                 on_complete=settings_returned
#             )

#             return

#         # Exact alarm permission already granted.
#         count = schedule_collection_notifications(app, rules)

#         print(f"Successfully scheduled {count} reminders.")

#     # Android 13+ notification permission.
#     if Build.VERSION.SDK_INT >= 33:

#         permission_status = (
#             app._impl._native_checkSelfPermission(
#                 notification_permission
#             )
#         )

#         if permission_status != PackageManager.PERMISSION_GRANTED:

#             def permission_returned(permissions, results):

#                 permission_results = dict(
#                     zip(permissions, results)
#                 )

#                 granted = (
#                     permission_results.get(
#                         notification_permission
#                     ) == PackageManager.PERMISSION_GRANTED
#                 )

#                 if granted:
#                     schedule_if_permitted()
#                 else:
#                     print(
#                         "Notification permission was denied."
#                     )

#             app._impl.request_permissions(
#                 [notification_permission],
#                 on_complete=permission_returned
#             )

#             return

#     # Android versions below 13, or permission already granted.
#     schedule_if_permitted()

# def schedule_test_notification(app, delay_seconds=120):
#     """
#     Schedule a test notification.
#     Default: 2 minutes from now.
#     """

#     # from android.app import AlarmManager, PendingIntent
#     # from android.content import Intent
#     # from android.os import Build

#     # from com.example.wasteapp import NotificationReceiver
#     from java import jclass
#     AlarmManager = jclass("android.app.AlarmManager")
#     PendingIntent = jclass("android.app.PendingIntent")
#     Intent = jclass("android.content.Intent")
#     Build = jclass("android.os.Build")

#     NotificationReceiver = jclass(
#         "com.example.wasteapp.NotificationReceiver"
#     )

#     context = app._impl.native.getApplicationContext()

#     alarm_manager = context.getSystemService(
#         context.ALARM_SERVICE
#     )

#     intent = Intent(
#         context,
#         NotificationReceiver
#     )

#     intent.setAction(ACTION_REMINDER)

#     intent.putExtra(
#         "title",
#         "Waste App test"
#     )

#     intent.putExtra(
#         "message",
#         "Great! Your waste collection notifications are working."
#     )

#     request_code = 999999

#     intent.putExtra(
#         "notification_id",
#         request_code
#     )

#     pending_intent = PendingIntent.getBroadcast(
#         context,
#         request_code,
#         intent,
#         PendingIntent.FLAG_UPDATE_CURRENT
#         | PendingIntent.FLAG_IMMUTABLE
#     )

#     trigger_time = (
#         int(datetime.now().timestamp() * 1000)
#         + delay_seconds * 1000
#     )

#     if Build.VERSION.SDK_INT >= 31:
#         exact_allowed = alarm_manager.canScheduleExactAlarms()
#     else:
#         exact_allowed = True

#     if exact_allowed:
#         alarm_manager.setExactAndAllowWhileIdle(
#             AlarmManager.RTC_WAKEUP,
#             trigger_time,
#             pending_intent
#         )
#     else:
#         alarm_manager.setAndAllowWhileIdle(
#             AlarmManager.RTC_WAKEUP,
#             trigger_time,
#             pending_intent
#         )

#     print(
#         f"Test notification scheduled in {delay_seconds} seconds."
#     )


"""Reminder notifications for waste collection."""

import json
import sys
from datetime import date, datetime, time, timedelta


CHANNEL_ID = "waste_collection_reminders"
PREFERENCES_NAME = "waste_collection_alarms"
ACTION_REMINDER = "com.example.wasteapp.COLLECTION_REMINDER"

SCHEDULE_DAYS = 200
NOTIFICATION_PERMISSION = "android.permission.POST_NOTIFICATIONS"
PERMISSION_REQUEST_CODE = 1001


def android_classes():
    """Load Android Java classes through Chaquopy."""
    from java import jclass

    return {
        "AlarmManager": jclass("android.app.AlarmManager"),
        "PendingIntent": jclass("android.app.PendingIntent"),
        "Intent": jclass("android.content.Intent"),
        "Build": jclass("android.os.Build"),
        "NotificationReceiver": jclass(
            "com.example.wasteapp.NotificationReceiver"
        ),
        "Settings": jclass("android.provider.Settings"),
        "Uri": jclass("android.net.Uri"),
        "PackageManager": jclass(
            "android.content.pm.PackageManager"
        ),
    }


def schedule_collection_notifications(app, rules):
    """Schedule reminders for upcoming collection days."""

    if sys.platform != "android":
        print("Android notifications unavailable on this platform.")
        return 0

    classes = android_classes()

    AlarmManager = classes["AlarmManager"]
    PendingIntent = classes["PendingIntent"]
    Intent = classes["Intent"]
    NotificationReceiver = classes["NotificationReceiver"]

    context = app._impl.native.getApplicationContext()

    alarm_manager = context.getSystemService(
        context.ALARM_SERVICE
    )

    preferences = context.getSharedPreferences(
        PREFERENCES_NAME,
        context.MODE_PRIVATE
    )

    # Cancel previously scheduled reminders.
    old_alarms = preferences.getAll().keySet().toArray()

    for key in old_alarms:
        request_code = int(str(key))

        old_intent = Intent(context, NotificationReceiver)
        old_intent.setAction(ACTION_REMINDER)

        old_pending = PendingIntent.getBroadcast(
            context,
            request_code,
            old_intent,
            PendingIntent.FLAG_NO_CREATE
            | PendingIntent.FLAG_IMMUTABLE
        )

        if old_pending is not None:
            alarm_manager.cancel(old_pending)
            old_pending.cancel()

    editor = preferences.edit()
    editor.clear()

    today = date.today()
    end_date = today + timedelta(days=SCHEDULE_DAYS)

    current_day = today
    scheduled_count = 0

    while current_day <= end_date:

        collections = []

        for rule in rules:
            start = rule["start_date"]
            interval_days = rule["interval_weeks"] * 7

            days_since_start = (current_day - start).days

            if days_since_start < 0:
                continue

            if current_day.weekday() != start.weekday():
                continue

            if days_since_start % interval_days != 0:
                continue

            collections.append(rule["type"])

        if collections:

            reminder_date = current_day - timedelta(days=1)

            if reminder_date >= today:

                # Midday on the day before collection.
                reminder_datetime = datetime.combine(
                    reminder_date,
                    time(12, 0)
                ).astimezone()

                timestamp_ms = int(
                    reminder_datetime.timestamp() * 1000
                )

                now_ms = int(
                    datetime.now().astimezone().timestamp() * 1000
                )

                if timestamp_ms > now_ms:

                    waste_types = " and ".join(collections)

                    title = "Bin day tomorrow"
                    message = (
                        f"Time to take out the bins! "
                        f"Tomorrow is {waste_types}."
                    )

                    request_code = current_day.toordinal()

                    intent = Intent(
                        context,
                        NotificationReceiver
                    )

                    intent.setAction(ACTION_REMINDER)
                    intent.putExtra("title", title)
                    intent.putExtra("message", message)
                    intent.putExtra(
                        "notification_id",
                        request_code
                    )

                    pending_intent = PendingIntent.getBroadcast(
                        context,
                        request_code,
                        intent,
                        PendingIntent.FLAG_UPDATE_CURRENT
                        | PendingIntent.FLAG_IMMUTABLE
                    )

                    alarm_manager.setExactAndAllowWhileIdle(
                        AlarmManager.RTC_WAKEUP,
                        timestamp_ms,
                        pending_intent
                    )

                    # Store reminder information for reboot recovery.
                    alarm_data = {
                        "timestamp": timestamp_ms,
                        "title": title,
                        "message": message
                    }

                    editor.putString(
                        str(request_code),
                        json.dumps(alarm_data)
                    )

                    scheduled_count += 1

        current_day += timedelta(days=1)

    # Persist reminder information.
    if not editor.commit():
        print("WARNING: Could not save reminder information.")

    return scheduled_count


def enable_notifications(app, rules):
    """
    Request notification permission and exact-alarm access.
    Schedule reminders once both are available.
    """

    if sys.platform != "android":
        print("Android notifications unavailable on this platform.")
        return

    classes = android_classes()

    Intent = classes["Intent"]
    Build = classes["Build"]
    Settings = classes["Settings"]
    Uri = classes["Uri"]
    PackageManager = classes["PackageManager"]

    activity = app._impl.native
    context = activity.getApplicationContext()

    package_name = context.getPackageName()

    # 1. Android 13+: request notification permission.
    if Build.VERSION.SDK_INT >= 33:

        permission_status = context.checkSelfPermission(
            NOTIFICATION_PERMISSION
        )

        if permission_status != PackageManager.PERMISSION_GRANTED:

            print("Requesting notification permission.")

            activity.requestPermissions(
                [NOTIFICATION_PERMISSION],
                PERMISSION_REQUEST_CODE
            )

            # The user must grant permission before continuing.
            # Call enable_notifications again after returning.
            return

    # 2. Check whether notifications are enabled.
    notification_manager = context.getSystemService(
        context.NOTIFICATION_SERVICE
    )

    if not notification_manager.areNotificationsEnabled():
        print("Notifications are disabled in Android settings.")
        return

    # 3. Check exact-alarm access.
    alarm_manager = context.getSystemService(
        context.ALARM_SERVICE
    )

    if (
        Build.VERSION.SDK_INT >= 31
        and not alarm_manager.canScheduleExactAlarms()
    ):

        print("Requesting exact-alarm access.")

        settings_intent = Intent(
            Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM
        )

        settings_intent.setData(
            Uri.parse("package:" + package_name)
        )

        def exact_alarm_returned(result, data):

            if alarm_manager.canScheduleExactAlarms():

                count = schedule_collection_notifications(
                    app, rules
                )

                print(f"Scheduled {count} reminders.")

            else:
                print("Exact-alarm access was not granted.")

        app._impl.start_activity(
            settings_intent,
            on_complete=exact_alarm_returned
        )

        return

    # 4. Both permissions are available.
    count = schedule_collection_notifications(app, rules)

    print(f"Successfully scheduled {count} reminders.")


def schedule_test_notification(app, delay_seconds=120):
    """Schedule a test notification, defaulting to two minutes."""

    if sys.platform != "android":
        print("Android notifications unavailable on this platform.")
        return

    classes = android_classes()

    AlarmManager = classes["AlarmManager"]
    PendingIntent = classes["PendingIntent"]
    Intent = classes["Intent"]
    Build = classes["Build"]
    NotificationReceiver = classes["NotificationReceiver"]
    PackageManager = classes["PackageManager"]

    activity = app._impl.native
    context = activity.getApplicationContext()

    # Check notification permission.
    if Build.VERSION.SDK_INT >= 33:

        if context.checkSelfPermission(
            NOTIFICATION_PERMISSION
        ) != PackageManager.PERMISSION_GRANTED:

            print("Notification permission has not been granted.")
            return

    notification_manager = context.getSystemService(
        context.NOTIFICATION_SERVICE
    )

    if not notification_manager.areNotificationsEnabled():
        print("Notifications are disabled.")
        return

    alarm_manager = context.getSystemService(
        context.ALARM_SERVICE
    )

    # Exact alarms are required for this test.
    if (
        Build.VERSION.SDK_INT >= 31
        and not alarm_manager.canScheduleExactAlarms()
    ):
        print("Exact-alarm access has not been granted.")
        return

    intent = Intent(
        context,
        NotificationReceiver
    )

    intent.setAction(ACTION_REMINDER)

    request_code = 999999

    intent.putExtra("title", "Waste App test")
    intent.putExtra(
        "message",
        "Great! Your waste collection notifications are working."
    )
    intent.putExtra("notification_id", request_code)

    pending_intent = PendingIntent.getBroadcast(
        context,
        request_code,
        intent,
        PendingIntent.FLAG_UPDATE_CURRENT
        | PendingIntent.FLAG_IMMUTABLE
    )

    trigger_time = (
        int(datetime.now().timestamp() * 1000)
        + delay_seconds * 1000
    )

    alarm_manager.setExactAndAllowWhileIdle(
        AlarmManager.RTC_WAKEUP,
        trigger_time,
        pending_intent
    )

    print(
        f"Test notification scheduled in {delay_seconds} seconds."
    )

