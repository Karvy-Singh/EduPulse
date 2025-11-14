import imaplib
import email
from email.header import decode_header
import time
import os
from dotenv import load_dotenv

load_dotenv()

imap_host = "imap.gmail.com"
username = os.getenv("username")
password = os.getenv("password")

STATE_FILE = "last_uid.txt"
POLL_INTERVAL = 300 # seconds between checks


def load_last_uid():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        value = f.read().strip()
        return int(value) if value else None


def save_last_uid(uid):
    with open(STATE_FILE, "w") as f:
        f.write(str(uid))


def parse_email(msg):
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8", errors="ignore")

    from_, enc = decode_header(msg.get("From"))[0]
    if isinstance(from_, bytes):
        from_ = from_.decode(enc or "utf-8", errors="ignore")

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in disposition:
                body = part.get_payload(decode=True).decode(errors="ignore")
                break
            elif content_type == "text/html" and "attachment" not in disposition:
                body = part.get_payload(decode=True).decode(errors="ignore")
    else:
        body = msg.get_payload(decode=True).decode(errors="ignore")

    return subject, from_, body


def check_new_mail():
    last_uid = load_last_uid()

    M = imaplib.IMAP4_SSL(imap_host)
    M.login(username, password)
    M.select("INBOX")

    # First run: if we don’t have a last UID yet, initialize it to current last message
    if last_uid is None:
        typ, data = M.uid("search", None, "ALL")
        if typ == "OK" and data[0]:
            uids = data[0].split()
            max_uid = int(uids[-1])
            save_last_uid(max_uid)
            print(f"Initialized last UID to {max_uid}, no old messages processed.")
        else:
            print("No messages in inbox yet.")
        M.close()
        M.logout()
        return

    # Subsequent runs: only fetch UIDs greater than last_uid
    search_criteria = f"(UID {last_uid + 1}:*)"
    typ, data = M.uid("search", None, search_criteria)

    if typ != "OK":
        print("Search failed")
        M.close()
        M.logout()
        return

    uids = data[0].split()
    if not uids:
        print("No new messages.")
        M.close()
        M.logout()
        return

    max_uid_seen = last_uid

    for uid in uids:
        uid_int = int(uid)
        if uid_int <= last_uid:
            continue

        typ, msg_data = M.uid("fetch", uid, "(RFC822)")
        if typ != "OK":
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        subject, from_, body = parse_email(msg)

        print("=" * 60)
        print("New mail!")
        print("UID:", uid_int)
        print("Subject:", subject)
        print("From:", from_)
        print("\nBody:\n", body)
        print("=" * 60)

        if uid_int > max_uid_seen:
            max_uid_seen = uid_int

    # Update stored UID after processing all new ones
    save_last_uid(max_uid_seen)

    M.close()
    M.logout()


if __name__ == "__main__":
    while True:
        try:
            check_new_mail()
        except Exception as e:
            # You probably want better logging in real use
            print("Error while checking mail:", e)

        time.sleep(POLL_INTERVAL)

