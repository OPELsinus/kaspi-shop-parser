from pathlib import Path
from typing import Union, List


# ? tested
def smtp_send(
        *args,
        subject: str,
        url: str,
        to: Union[list, str],
        username: str,
        password: str = None,
        html: str = None,
        attachments: List[Union[Path, str]] = None
) -> None:
    import smtplib
    from email.mime.application import MIMEApplication
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    body = ' '.join([str(i) for i in args])
    with smtplib.SMTP(url, 25) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        if password:
            smtp.login(username, password)

        msg = MIMEMultipart('alternative')
        msg["From"] = username
        msg["To"] = ';'.join(to) if type(to) is list else to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, 'plain'))

        if html:
            msg.attach(MIMEText(html, 'html'))

        if attachments and isinstance(attachments, list):
            for each in attachments:
                path = Path(each).resolve()
                with open(path.__str__(), 'rb') as f:
                    part = MIMEApplication(f.read(), Name=path.name)
                    part['Content-Disposition'] = 'attachment; filename="%s"' % path.name
                    msg.attach(part)

        smtp.send_message(msg=msg)


def alt_smtp_send(
        url: str,
        username: str,
        password: Union[str, None],
        to: Union[list, str],
        subject: str,
        body: Union[str, List, None],
        html: str = None,
        attachments: List[Union[Path, str]] = None,
        sep=' '
) -> None:
    import smtplib
    from email.mime.application import MIMEApplication
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    body = sep.join([str(i) for i in body]) if isinstance(body, list) else body
    with smtplib.SMTP(url, 25) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        if password:
            smtp.login(username, password)

        msg = MIMEMultipart('alternative')
        msg["From"] = username
        msg["To"] = ';'.join(to) if type(to) is list else to
        msg["Subject"] = subject
        if body:
            msg.attach(MIMEText(body, 'plain'))

        if html:
            msg.attach(MIMEText(html, 'html'))

        if attachments and isinstance(attachments, list):
            for each in attachments:
                path = Path(each).resolve()
                with open(path.__str__(), 'rb') as f:
                    part = MIMEApplication(f.read(), Name=path.name)
                    part['Content-Disposition'] = 'attachment; filename="%s"' % path.name
                    msg.attach(part)

        smtp.send_message(msg=msg)


if __name__ == '__main__':
    test_attachment = Path('test_attachment')
    test_attachment.write_text('test')
    alt_smtp_send(
        '172.16.10.5',
        'rpa.robot@magnum.kz',
        None,
        'assanov.b@magnum.kz',
        'test string',
        ['test', 'message'],
        None,
        [test_attachment],
        '\n'
    )
    alt_smtp_send(
        '172.16.10.5',
        'rpa.robot@magnum.kz',
        None,
        'assanov.b@magnum.kz',
        'test html',
        None,
        '<h6>test html</h6><hr>',
        [test_attachment],
        '\n'
    )
