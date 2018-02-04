#!/usr/bin/env python3
"""toy smtplib"""

import base64
import socket


class SMTPError(BaseException):
    def __init__(self, err='SMTP Error'):
        BaseException.__init__(self, err)


class ToySMTP:
    def __init__(self, host='localhost', port=25):
        self.host = host
        self.port = port
        self.auth = False
        self.connect()

    def connect(self):
        """creat TCP socket"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        # receive 220
        err, msg = self.getreply()
        if err != 220:
            print(msg)

        # helo
        self.interact("HELO", "toy", 250)

    def disconnect(self):
        """disconnect"""
        self.putcmd("QUIT")
        self.sock.close()

    def putcmd(self, cmd, args=""):
        """send cmd to server"""
        if args == "":
            data = "%s\r\n" % cmd
        else:
            data = "%s %s\r\n" % (cmd, args)
        self.sock.sendall(data.encode())

    def getreply(self):
        """receive reply from server"""
        recv = self.sock.recv(1024).decode()
        err, msg = recv.split(' ', 1)
        return int(err), msg

    def interact(self, cmd, args, code):
        """interact with server"""
        self.putcmd(cmd, args)
        err, msg = self.getreply()
        if err != code:
            raise SMTPError(msg)  # raise error

    def login(self, username, password):
        """AUTH LOGIN"""
        try:
            username = base64.b64encode(username.encode()).decode()
            password = base64.b64encode(password.encode()).decode()
            self.interact("AUTH LOGIN", "", 334)
            self.interact(username, "", 334)
            self.interact(password, "", 235)
            self.auth = True
        except SMTPError as err:
            print(err.args[0])

    def send_mail(self, from_addr, to_addr, subject, content):
        """send mail"""
        if not self.auth:
            print('Error: No authentication.')
            return
        try:
            self.interact("MAIL FROM: ", "<%s>" % from_addr, 250)
            self.interact("RCPT TO: ", "<%s>" % to_addr, 250)
            self.interact("DATA", "", 354)

            message = 'FROM:' + from_addr + '\r\n'  # header
            message += 'TO:' + to_addr + '\r\n'
            message += 'SUBJECT:' + subject + '\r\n'
            message += '\r\n'
            message += content  # content
            message += '\r\n.\r\n'  # end sign

            self.interact(message, "", 250)

        except SMTPError as err:
            print(err.args[0])


def test():
    """a test"""
    username = input('Username:')
    password = input('Password:')
    smtp = ToySMTP(host="smtp.163.com")

    # auth login
    smtp.login(username, password)

    # send plain text mail
    from_addr = username
    to_addr = username
    subject = 'hello, world!'
    content = 'a test email sent from ToySMTP.'
    smtp.send_mail(from_addr, to_addr, subject, content)
    smtp.disconnect()


if __name__ == '__main__':
    test()
