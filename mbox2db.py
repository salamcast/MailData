import mailbox
import csv
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings
import pandas as pd
from sqlalchemy import create_engine, types
from pathlib import Path
from datetime import datetime
import re
import os
import quopri

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# MySQL connection settings
user='root'
passwd='armbian'
host='localhost'
dbname='mailbox'

def clean_html(html):
    """
     remove any html in mail msg
    """
    soup = BeautifulSoup(html, "html.parser")
    return clean_blank_lines(soup.get_text())

def clean_blank_lines(txt):
    return "\n".join(line.strip() for line in txt.splitlines() if line.strip())

def strip_replies(text):
  lines = text.split("\n")
  lines = [l for l in lines if len(l) > 0]
  lines = [line for line in lines if line[0] != ">"]
  return "\n".join(lines)

def clean_body(msg):
    # get msg body
    if msg.is_multipart():
        body = []
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                pl = part.get_payload(decode=True).decode(errors='ignore')
                body.append(pl)
        body = "\n".join(body)
    else:
        body = msg.get_payload(decode=True).decode(errors='ignore')
    body = strip_replies(body)
    return clean_html(body)

def format_date(d):
  """Converts a date string from 'Wed, 27 Dec 2023 20:00:34 -0500'
  to 'YYYY-MM-DD-HH-MM' format.

  Args:
    d: The date string to convert.

  Returns:
    A string representing the date and time in 'YYYY-MM-DD HH:MM' format,
    or d if the input string cannot be parsed.
  """
  
  
  clean=re.sub(r'\s*\([A-Za-z]{3,}\)$', '', d)
  try:
    # Parse the input date string
    datetime_object = datetime.strptime(clean, '%a, %d %b %Y %H:%M:%S %z')

    # Format the datetime object to the desired output format
    output_string = datetime_object.strftime('%Y-%m-%d %H:%M')
    return output_string
  except ValueError:
    return d

def extract_email(text):
  """
  Extracts email addresses from a given string.

  Args:
    text: The input string to search for emails.

  Returns:
    A list of email addresses found in the string.
  """
  if text is None:
     return ['unknown@email_address.uea']
  email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
  emails = re.findall(email_pattern, text)
  
  return emails

def clean_up_string(encoded_string):
  """
  Cleans up a string with MIME Quoted-Printable encoding and removes the
  =?charset?encoding?encoded-text?= wrappers.

  Args:
    encoded_string: The encoded string to clean.

  Returns:
    The decoded and cleaned string.
  """
  cleaned_parts = []
  parts = re.findall(r'=\?([^?]+)\?([QqBb])\?([^?]*)\?=', encoded_string)

  if not parts:
    # If no MIME encoded words are found, try a simple Quoted-Printable decode
    try:
      decoded_bytes = quopri.decodestring(encoded_string)
      return decoded_bytes.decode('utf-8', errors='ignore').strip()
    except Exception:
      return encoded_string.strip()

  for charset, encoding, encoded_text in parts:
    try:
      decoded_bytes = quopri.decodestring(encoded_text.replace('_', ' ')) # Undo space encoding
      decoded_text = decoded_bytes.decode(charset.lower(), errors='ignore')
      cleaned_parts.append(decoded_text)
    except Exception as e:
      print(f"Error decoding part (charset={charset}, encoding={encoding}): {e}")
      # If decoding fails, keep the original encoded part
      cleaned_parts.append(f"=?{charset}?{encoding}?{encoded_text}?=")

  return " ".join(cleaned_parts).strip()


# ===========================================================
mbox_dir=input("Enter mbox: ")
print("this will import the following mbox into MySQL: " + mbox_dir)
mbox= mailbox.mbox(mbox_dir + '/mbox')

csv_file = open(mbox_dir + '.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow([
    'Date', 'To', 'From', 'Subject', 'Body'
])

# need to do some clean up

for msg in mbox:

    subject = clean_up_string(msg['subject'])
    sender = extract_email(msg['from'])
    recipient = extract_email(msg['to'])
    dtime = format_date(msg['date'])

    body = "To: " + ", ".join(recipient) + "\nFrom: " + ", ".join(sender) + "\n=========================================\n" + clean_body(msg)

    csv_writer.writerow([
        dtime, recipient[0], sender[0], subject, body
    ])

csv_file.close()



engine = create_engine('mysql+pymysql://' + user + ':' + passwd + '@' + host + '/' + dbname) 

df = pd.read_csv(mbox_dir + ".csv",sep=',',quotechar='\"',encoding='utf8') 
df.to_sql(Path(mbox_dir).stem,con=engine,index=False,if_exists='append') 
os.remove(mbox_dir + ".csv")