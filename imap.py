import imaplib
import email
from email.header import decode_header


def get_privacy_sell():
    EMAIL = "sexcoachfloripa@gmail.com"
    PASSWORD = "krdi bwzt giuo dqey"  # Use "senha de app" gerada no Google

    # Conectar ao Gmail
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    # Buscar e-mails não lidos
    status, messages = mail.search(None, '(UNSEEN)')

    sells = 0

    for num in messages[0].split():
        status, data = mail.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject, encoding = decode_header(msg["Subject"])[0]
        from_ = msg["from"]

        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")
        print(f"De: {from_}")
        print(f"Assunto: {subject}")

        if "Parabéns! Você fez uma venda" in subject:
            sells += 1
            print('➡ Executando ação...')

    mail.logout()
    return sells
