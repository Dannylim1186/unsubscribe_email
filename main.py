from dotenv import load_dotenv
import imaplib
import email
import os
import requests
from bs4 import BeautifulSoup

load_dotenv()

username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

if not username or not password:
    raise ValueError("EMAIL and PASSWORD must be set in the .env file")

# Connecting to email - GMAIL
def connect_to_mail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")
    return mail

def extract_link_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    links = [link["href"] for link in soup.find_all("a", href=True) if "unsubscribe" in link["href"].lower()] 
    return links

def click_link(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            print("Successfully visited", link)
        else:
            print("Failed to visit", link, "error code", response.status_code)
    except Exception as e:
        print("Error with", link, str(e))

def search_for_email():
    # Searching for emails that contain "UNSUBSCRIBE" text
    mail = connect_to_mail()
    status, search_data = mail.search(None, '(BODY "unsubscribe")')
    
    if status != "OK":
        print("Failed to retrieve emails.")
        return

    # Getting the message numbers
    data = search_data[0].split()

    links =[]


    for num in data:
        _, fetch_data = mail.fetch(num, "(RFC822)")
        if fetch_data is None:
            continue

        msg = email.message_from_bytes(fetch_data[0][1])

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_content = part.get_payload(decode=True).decode()
                    links.extend(extract_link_from_html(html_content))
        else:
            content_type = msg.get_content_type()
            content = msg.get_payload(decode=True).decode()

            if content_type == "text/html":
               links.extend(extract_link_from_html(content))

    mail.logout()
    return links

def save_links(links):
    with open(links.txt, "W") as f:
        f.write("\n".join(links))

links = search_for_email()
for link in links:
    click_link(link)

save_links(links)
