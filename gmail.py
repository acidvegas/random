#!/usr/bin/env python
import smtplib,sys
with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
	server.login('username@gmail.com','password')
	server.sendmail('username@gmail.com','target@mail.com',' '.join(sys.argv[1:]))