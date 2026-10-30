package com.example.wasteapp;

import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import org.json.JSONObject;
import java.util.Map;

public class NotificationReceiver extends BroadcastReceiver {
    public static final String CHANNEL_ID = "waste_collection_reminders";
    public static final String PREFERENCES_NAME = "waste_collection_alarms";
    public static final String ACTION_REMINDER = "com.example.wasteapp.COLLECTION_REMINDER";

    @Override 
    public void onReceive(Context context, Intent intent) {
        String action = intent.getAction();

        if (Intent.ACTION_BOOT_COMPLETED.equals(action)) {
            restoreAlarms(context);
            return;
        }

        if (ACTION_REMINDER.equals(action)) {
            showNotification(context, intent);
        }
    }

    private void createNotificationChannel(Context context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {

            NotificationChannel channel =
                new NotificationChannel(
                    CHANNEL_ID,
                    "Waste collection reminders",
                    NotificationManager.IMPORTANCE_DEFAULT
                );

            channel.setDescription(
                "Reminders for upcoming waste collections"
            );

            NotificationManager manager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
            manager.createNotificationChannel(channel);
        }
    }

    private void showNotification(Context context, Intent intent) {
        if (Build.VERSION.SDK_INT >= 33) {

            if (context.checkSelfPermission(
                "android.permission.POST_NOTIFICATIONS"
            ) != PackageManager.PERMISSION_GRANTED) {
                return;
            }
        }

        createNotificationChannel(context);

        String title = intent.getStringExtra("title");
        String message = intent.getStringExtra("message");

        // int notificationId =
        //     intent.getIntExtra("notification_id", 1);
        int notificationId =
            (int) intent.getLongExtra("notification_id", 1L);

        if (title == null) {
            title = "Waste collection reminder";
        }

        if (message == null) {
            message = "You have a waste collection tomorrow.";
        }

        Notification.Builder builder;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {

            builder = new Notification.Builder(
                context,
                CHANNEL_ID
            );

        } else {

            builder = new Notification.Builder(context);
        }

        builder.setSmallIcon(android.R.drawable.ic_dialog_info);

        builder.setContentTitle(title);
        builder.setContentText(message);

        builder.setStyle(
            new Notification.BigTextStyle()
                .bigText(message)
        );

        builder.setAutoCancel(true);

        NotificationManager manager =
            (NotificationManager) context.getSystemService(
                Context.NOTIFICATION_SERVICE
            );

        manager.notify(notificationId, builder.build());

        // Remove the completed reminder from saved alarms
        SharedPreferences preferences =
            context.getSharedPreferences(
                PREFERENCES_NAME,
                Context.MODE_PRIVATE
            );

        preferences.edit()
            .remove(String.valueOf(notificationId))
            .apply();
    }

    private void restoreAlarms(Context context) {

        SharedPreferences preferences =
            context.getSharedPreferences(
                PREFERENCES_NAME,
                Context.MODE_PRIVATE
            );

        AlarmManager alarmManager =
            (AlarmManager) context.getSystemService(
                Context.ALARM_SERVICE
            );

        Map<String, ?> savedAlarms =
            preferences.getAll();

        long now = System.currentTimeMillis();

        for (Map.Entry<String, ?> entry :
            savedAlarms.entrySet()) {

            try {

                int requestCode =
                    Integer.parseInt(entry.getKey());

                JSONObject data = new JSONObject(
                    entry.getValue().toString()
                );
                long timestamp =
                    data.getLong("timestamp");

                String title =
                    data.getString("title");

                String message =
                    data.getString("message");

                if (timestamp <= now) {
                    preferences.edit()
                        .remove(entry.getKey())
                        .apply();

                    continue;
                }

                Intent alarmIntent = new Intent(
                    context,
                    NotificationReceiver.class
                );

                alarmIntent.setAction(ACTION_REMINDER);

                alarmIntent.putExtra("title", title);
                alarmIntent.putExtra("message", message);

                 alarmIntent.putExtra(
                    "notification_id",
                    requestCode
                );

                PendingIntent pendingIntent =
                    PendingIntent.getBroadcast(
                        context,
                        requestCode,
                        alarmIntent,
                        PendingIntent.FLAG_UPDATE_CURRENT
                        | PendingIntent.FLAG_IMMUTABLE
                    );

                if (Build.VERSION.SDK_INT >= 31 &&
                    !alarmManager.canScheduleExactAlarms()) {

                    alarmManager.setAndAllowWhileIdle(
                        AlarmManager.RTC_WAKEUP,
                        timestamp,
                        pendingIntent
                    );

                } else {

                    alarmManager.setExactAndAllowWhileIdle(
                        AlarmManager.RTC_WAKEUP,
                        timestamp,
                        pendingIntent
                    );
                }

            } catch (Exception e) {

                android.util.Log.e(
                    "WasteNotifications",
                    "Failed to restore alarm",
                    e
                );
            }
        }
    }
}
