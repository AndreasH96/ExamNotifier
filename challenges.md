# Situation analysis

Thing|Date
--------|----
ExamDate|2020-01-14
Course Code|MA2047
MailTime|2020-01-15
Entry appears on HH|2020-01-31

In this situation, the student has mailed 1 day after the exam was being held. CollectMail should be sent on 2020-01-31.

We want to prevent incorrect CollectMails being sent due to earlier runs of the course `MA2047`:

Thing|Date
-----|----
ExamDate|2019-01-14
Course Code|MA2047
MailTime|2020-01-15
Entry appears on HH|Unknown

It can be prevented by sorting the results by closeness in time to MailTime, and only picking the first one.