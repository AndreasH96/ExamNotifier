# ExamNotifier

A hobby project in Python using Beautiful Soup 4 and Pandas which notifies you when you can pick up you exam from service center at Halmstad University.

# Features

## Signing Up

A student should be able to sign up by sending an email to `ExamNotifier@gmail.com`, formatted with one course-courseCode per line. Like this:

```
MA8080
FÖ1002
```

The Gmail-API makes a POST to a web service, which stores the info for later. We allow only signing up from a student email.

Upon registering, we send back a disclaimer-email that says that there are no guarantees for this program.

The Signing-Up-program should always be running and listening on a port for a POST-request.

## Collect exam

This program should be runned periodically, ideally once a day. It checks for when the exams are ready for collection, and mails everyone in the `state.csv` accordingly. Should not be too hard to implement.

## Registration-Notification

When an exam is ready for registration in Ladok, you should receive an email about that. This requires the merging of two datasets:

1. [Which week that the exams are running](https://www.hh.se/student/innehall-a-o/tenta.html)
2. [Which courses that are ran on each particular week](https://cloud.timeedit.net/hh/web/schema/ri1Q5052.html)

Should hopefully not be too hard to implement. After all, we don't want the KJ-tragedy to happen again.

The Registration-Notification program should also be ran periodically, ideally once a day.

# Technical details

## State

The "State" is a file `state.csv` that holds some state for emails. We don't want to send duplicate emails, and as such we keep track of who we have sent mail to, and about what.

The structure should be a little bit like this.

name              |email                 |courseCode  |registrationMail|collectMail
------------------|----------------------|------|----------------|-----------
Jakob Lindskog    |jaklin16@student.hh.se|MA2020|False           |False
Jakob Lindskog    |jaklin16@student.hh.se|FÖ1002|True            |False
Andreas Häggström |andhag16@student.hh.se|MA2020|False           |False

which allows easier translation to pandas dataframes than a hierarchical JSON.