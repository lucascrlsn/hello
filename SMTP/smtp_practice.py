import smtplib, ssl

smtp_server = 'smtp.gmail.com'
port = 465
sender = 'lucascrlsn@gmail.com'
password = input('Enter your password here: ')

receiver = 'some email'
message = 'some email'

context = ssl.create_default_context()

with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender, password)
    # send email
    server.sendmail(sender, receiver, message)
    server.quit()
    print('It worked!')
