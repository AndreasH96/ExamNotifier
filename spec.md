# Spec

Features:

- Get mail during the registration-period. One at the beginning, one at the last day to submit for exam.
- Get mail when you can collect your exam.

To get into the program, one sends a mail formatted with one course courseCode per line.
Invalid course codes are not handled, as such we stand defenseless against spam attacks.

## Submit for exam

Combines the TimeEdit-dataset (which exams are running) with HH dataset (when can you submit for it).

`submitMails.py` should be ran periodically each day.
It checks each row in `state.csv` for dudes that should get their respective email. If the boolean expression below is true, send an email.

1. The `firstRegistrationMail` column is `false`
2. The courseCode and examWriteDate is in the HH dataset.

A last-ditch-reminder-mail is sent on the last day you can submit.

## Collect exam

Checks the HH dataset (when you can collect your exam). Also uses the TimeEdit-dataset actually.

`collectMails.py` should be ran periodically each day.

It checks each row in `state.csv` for dudes that should get their respective email. If the boolean expression below is true, send an email.

1. The `collectMail` column is `false`
2. The `courseCode` column is in the HH dataset

### How do we distinguish between different runs of the same course in the same year?

If there are multiple instances of the same course in the HH dataset (ie, the previous run of the course), pick the one exam that was held closest to the mailTime.

Imagine the following. The course `MA2047` is held twice a year. A person registers for ExamNotifier some day after the second run has been held, but before the exam is ready for collection.

$examWriteDate <= mailTime <= collectDate$ (equation 1)

However, $mailTime >= collectDate_{i-1}$, so it looks like the person should get a notification, when it shouldn't. So, we should be able to distinguish between different runs of the same course. We want the following, given equation 1 and the TimeEdit dataset.

`examWriteDate = minValue(mailTime - find(courseCode, timeEditDataset))`

That is, we calculate the examWriteDate based on the distance to the nearest exam. This eliminates the error of duplicate courses I think. `examWriteDate` should be an attribute in `state.csv`, and we should match both the `examWriteDate` and the `courseCode` column. ie:

1. The `firstRegistrationMail` column is `false`
2. The `courseCode` and `examWriteDate` columns are in the HH dataset.


## Optional TODO:
* Add so that a user can have the exams/commands in the subject of the email instead, or that the subject is the command that the user wishes to perform