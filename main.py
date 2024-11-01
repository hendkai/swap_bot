import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Globale Variablen
folder_entry = None
selected_swaps = []
swap_checkboxes = []
swap_list = []
result_label = None
frame = None

def run_command(command):
    """ Executes a shell command with sudo and returns the result. """
    try:
        output = subprocess.check_output(f"sudo {command}", shell=True, stderr=subprocess.STDOUT)
        return output.decode().strip()
    except subprocess.CalledProcessError as e:
        return e.output.decode().strip()

def list_swap_files():
    """ Lists existing swap files. """
    return run_command("swapon --show=NAME --noheadings")

def create_and_activate_swapfile(path, size, swappiness, priority, auto_priority):
    """ Creates and activates a swap file with custom swappiness and priority on a BTRFS filesystem. """
    swapfile_path = os.path.join(path, f"swapfile_{size}M")
    swappiness_priority_command = f"sysctl vm.swappiness={swappiness} && sysctl vm.vfs_cache_pressure=50"
    if not auto_priority:
        swappiness_priority_command += f" && sysctl vm.admin_reserve_kbytes={priority * 32768}"
    run_command(swappiness_priority_command)
    os.truncate(swapfile_path, size * 1024 * 1024)
    run_command(f"chattr +C {swapfile_path} && fallocate -l {size}M {swapfile_path} && chmod 0600 {swapfile_path} && mkswap {swapfile_path} && swapon {swapfile_path}")
    add_swap_entry_to_fstab(swapfile_path)  # Add entry to /etc/fstab

def add_swap_entry_to_fstab(swapfile_path):
    """ Adds an entry for the swap file to /etc/fstab to activate it at boot. """
    with open('/etc/fstab', 'a') as fstab:
        fstab.write(f"{swapfile_path} none swap defaults 0 0\n")

def delete_selected_swaps():
    global result_label

    """ Deletes selected swap files. """
    for swap in selected_swaps:
        delete_swap_file(swap)
    selected_swaps.clear()  # Clear the list of selected swaps
    result_label.config(text="Selected swap files deleted.")
    refresh_swap_list()  # Refresh the list of swap files

def delete_swap_file(path):
    """ Deactivates and deletes a swap file. """
    run_command(f"swapoff {path}")
    os.remove(path)
    remove_swap_entry_from_fstab(path)  # Remove entry from /etc/fstab

def remove_swap_entry_from_fstab(swapfile_path):
    """ Removes the entry for the swap file from /etc/fstab. """
    with open('/etc/fstab', 'r') as fstab:
        lines = fstab.readlines()

    with open('/etc/fstab', 'w') as fstab:
        for line in lines:
            if not line.startswith(swapfile_path):
                fstab.write(line)

def select_folder():
    global folder_entry
    selected_path = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, selected_path)

def toggle_swap(swap):
    """ Toggle the selection state of a swap file. """
    if swap in selected_swaps:
        selected_swaps.remove(swap)
    else:
        selected_swaps.append(swap)

def show_swappiness_info():
    info_text = "Swappiness controls the tendency of the kernel to swap out processes' memory pages to the swap space. A lower value (e.g., 10) makes the kernel avoid swapping as much as possible, while a higher value (e.g., 100) makes the kernel more aggressive in swapping out memory. The default value is usually around 60-70."
    show_info_window("Swappiness Info", info_text)

def show_priority_info():
    info_text = "Priority determines the order in which swap areas are used. A lower value (e.g., 1) gives the swap space higher priority, while a higher value (e.g., 32768) gives it lower priority. The default value is usually 32767."
    show_info_window("Priority Info", info_text)

def show_info_window(title, info_text):
    info_window = tk.Toplevel(root)
    info_window.title(title)
    info_label = ttk.Label(info_window, text=info_text, wraplength=400, justify="left")
    info_label.pack(padx=10, pady=10)

def refresh_swap_list():
    global frame
    for checkbox in swap_checkboxes:
        checkbox.destroy()
    swap_list = list_swap_files().split("\n")
    swap_checkboxes.clear()
    for i, swap in enumerate(swap_list):
        if swap:
            swap_checkbox = ttk.Checkbutton(frame, text=swap, command=lambda s=swap: toggle_swap(s))
            swap_checkbox.grid(row=9 + i, column=0, padx=10, pady=5, columnspan=2, sticky="w")
            swap_checkboxes.append(swap_checkbox)

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(self.tooltip, text=self.text, background="yellow", relief="solid", borderwidth=1, wraplength=200)
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def create_gui():
    global folder_entry, swap_checkboxes, swap_list, result_label, frame

    def create_and_activate():
        path = folder_entry.get()
        size = size_entry.get()
        swappiness = swappiness_entry.get()
        priority = priority_entry.get()
        auto_priority = auto_priority_var.get()
        create_and_activate_swapfile(path, int(size), swappiness, priority, auto_priority)
        result_label.config(text="Swap file created and activated.")
        refresh_swap_list()

    root = tk.Tk()
    root.title("swap_bot")
    root.geometry("800x600+300+200")

    frame = ttk.Frame(root)
    frame.grid(row=0, column=0, padx=10, pady=10)

    folder_label = ttk.Label(frame, text="Select Folder:")
    folder_label.grid(row=0, column=0, padx=10, pady=5)

    folder_entry = ttk.Entry(frame, width=40)
    folder_entry.grid(row=0, column=1, padx=10, pady=5)

    select_folder_button = ttk.Button(frame, text="Browse", command=select_folder)
    select_folder_button.grid(row=0, column=2, padx=10, pady=5)

    size_label = ttk.Label(frame, text="Swap File Size (in MB):")
    size_label.grid(row=1, column=0, padx=10, pady=5)

    size_entry = ttk.Entry(frame, width=10)
    size_entry.grid(row=1, column=1, padx=10, pady=5)

    ToolTip(size_entry, "Enter the size of the swap file in megabytes (MB).")

    swappiness_label = ttk.Label(frame, text="Swappiness (0-100):")
    swappiness_label.grid(row=2, column=0, padx=10, pady=5)

    swappiness_entry = ttk.Entry(frame, width=10)
    swappiness_entry.grid(row=2, column=1, padx=10, pady=5)

    ToolTip(swappiness_entry, "Enter the swappiness value (0-100). Lower values reduce swapping, higher values increase swapping.")

    swappiness_info_button = ttk.Button(frame, text="?", command=show_swappiness_info)
    swappiness_info_button.grid(row=2, column=2, padx=5, pady=5)

    priority_label = ttk.Label(frame, text="Priority (1-32768):")
    priority_label.grid(row=3, column=0, padx=10, pady=5)

    priority_entry = ttk.Entry(frame, width=10)
    priority_entry.grid(row=3, column=1, padx=10, pady=5)

    ToolTip(priority_entry, "Enter the priority value (1-32768). Lower values give higher priority, higher values give lower priority.")

    auto_priority_var = tk.BooleanVar()
    auto_priority_var.set(False)
    auto_priority_checkbox = ttk.Checkbutton(frame, text="Auto Priority", variable=auto_priority_var)
    auto_priority_checkbox.grid(row=3, column=2, padx=5, pady=5)

    priority_info_button = ttk.Button(frame, text="?", command=show_priority_info)
    priority_info_button.grid(row=3, column=3, padx=5, pady=5)

    create_button = ttk.Button(frame, text="Create and Activate Swap", command=create_and_activate)
    create_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    result_label = ttk.Label(frame, text="")
    result_label.grid(row=5, column=0, columnspan=4, pady=10)

    swap_list_label = ttk.Label(frame, text="Select Swap Files to Delete:")
    swap_list_label.grid(row=6, column=0, columnspan=2, pady=10)

    refresh_swap_list()  # Refresh the list of swap files

    delete_selected_button = ttk.Button(frame, text="Delete Selected Swap Files", command=delete_selected_swaps)
    delete_selected_button.grid(row=6, column=2, columnspan=2, padx=10, pady=5)

    # Step-by-step guide
    guide_text = (
        "Step-by-Step Guide:\n"
        "1. Select a folder where the swap file should be created.\n"
        "2. Enter the desired size of the swap file in megabytes (MB).\n"
        "3. Adjust the swappiness (0-100) and priority (1-32768) settings for the swap file, or enable automatic priority settings.\n"
        "4. Click the 'Create and Activate Swap' button to create and activate the swap file.\n"
        "5. Select swap files from the list of existing ones and delete them using the 'Delete Selected Swap Files' button."
    )
    guide_label = ttk.Label(frame, text=guide_text, wraplength=400, justify="left")
    guide_label.grid(row=7, column=0, columnspan=4, pady=10)

    root.mainloop() 

if __name__ == "__main__":
    create_gui()
