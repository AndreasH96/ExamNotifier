# ExamNotifier
A hobby project in Python using Beautiful Soup 4 and Pandas which notifies you when you can pick up you exam from service center at Halmstad University.

# Thoughts about how the project should be

## Signing Up
A student should be able to sign up by sending an email to `ExamNotifier@gmail.com`, formatted with one course-code per line. Like this:
```
MA8080
FÖ1002
```
The Gmail-API makes a POST to a web service, which stores the info for later. We allow only signing up from a student email.

Upon registering, we send back a disclaimer-email that says that there are no guarantees for this program.

## Picking up exam

This program should be runned periodically. It checks for when the exams are ready for pickup, and mails everyone in the JSON-file accordingly.
Should not be too hard to implement.

## Sign-Up-Nofication

When an exam is ready for sign-up in Ladok, you should receive an email about that. This requires the merging of two datasets:

1. [Which week that the exams are running](https://www.hh.se/student/innehall-a-o/tenta.html)
2. [Which courses that are ran on each particular week](https://cloud.timeedit.net/hh/web/schema/ri1Q5052.html)

Should hopefully not be too hard to implement. After all, we don't want the KJ-tragedy to happen again.
