import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Globale Variable für folder_entry und die Liste der ausgewählten Swap-Dateien
folder_entry = None
selected_swaps = []
swap_checkboxes = []  # Definieren Sie swap_checkboxes als globale Variable
swap_list = []  # Definieren Sie swap_list als globale Variable

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
    swappiness_command = f"sysctl vm.swappiness={swappiness}"
    run_command(swappiness_command)
    priority_command = f"sysctl vm.vfs_cache_pressure=50"  # Default value
    if not auto_priority:
        priority_command = f"sysctl vm.vfs_cache_pressure=50 && sysctl vm.admin_reserve_kbytes={priority * 32768}"
    run_command(priority_command)
    run_command(f"truncate -s 0 {swapfile_path}")
    run_command(f"chattr +C {swapfile_path}")
    run_command(f"fallocate -l {size}M {swapfile_path}")
    run_command(f"chmod 0600 {swapfile_path}")
    run_command(f"mkswap {swapfile_path}")
    run_command(f"swapon {swapfile_path}")

def delete_selected_swaps():
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

def select_folder():
    global folder_entry  # Verwenden Sie die globale folder_entry-Variable
    selected_path = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, selected_path)

def toggle_swap(swap):
    """ Toggle the selection state of a swap file. """
    if swap in selected_swaps:
        selected_swaps.remove(swap)
    else:
        selected_swaps.append(swap)

def create_gui():
    """ Creates the Tkinter GUI for Swap File Management. """
    global folder_entry  # Deklarieren Sie folder_entry als global
    global swap_checkboxes  # Deklarieren Sie swap_checkboxes als global
    global swap_list  # Deklarieren Sie swap_list als global
    def create_and_activate():
        path = folder_entry.get()
        size = size_entry.get()
        swappiness = swappiness_entry.get()
        priority = priority_entry.get()
        auto_priority = auto_priority_var.get()
        create_and_activate_swapfile(path, int(size), swappiness, priority, auto_priority)
        result_label.config(text="Swap file created and activated.")
        refresh_swap_list()  # Refresh the list of swap files

    def refresh_swap_list():
        swap_list = list_swap_files().split("\n")
        for checkbox in swap_checkboxes:
            checkbox.destroy()
        swap_checkboxes.clear()
        for i, swap in enumerate(swap_list):
            if swap:
                swap_checkbox = ttk.Checkbutton(frame, text=swap, command=lambda s=swap: toggle_swap(s))
                swap_checkbox.grid(row=8 + i, column=0, padx=10, pady=5, columnspan=2, sticky="w")
                swap_checkboxes.append(swap_checkbox)

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

    root = tk.Tk()
    root.title("swap_bot")  # Setzen Sie den Titel des Tkinter-Fensters auf "swap_bot"
    root.geometry("800x600+300+200")  # Setzen Sie die Fenstergröße und Position

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

    swappiness_label = ttk.Label(frame, text="Swappiness (0-100):")
    swappiness_label.grid(row=2, column=0, padx=10, pady=5)

    swappiness_entry = ttk.Entry(frame, width=10)
    swappiness_entry.grid(row=2, column=1, padx=10, pady=5)

    swappiness_info_button = ttk.Button(frame, text="?", command=show_swappiness_info)
    swappiness_info_button.grid(row=2, column=2, padx=5, pady=5)

    priority_label = ttk.Label(frame, text="Priority (1-32768):")
    priority_label.grid(row=3, column=0, padx=10, pady=5)

    priority_entry = ttk.Entry(frame, width=10)
    priority_entry.grid(row=3, column=1, padx=10, pady=5)

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

    root.mainloop()

if __name__ == "__main__":
    create_gui()
