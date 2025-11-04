import os
import time
import requests
import customtkinter as ctk
from tkinter import messagebox
from dotenv import load_dotenv
import subprocess
import platform

# ---------- CONFIG ----------
load_dotenv()
FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY")
API_URL = "https://api.freepik.com/v1/ai/image-upscaler-precision-v2"

if not FREEPIK_API_KEY:
    raise ValueError("❌ Missing FREEPIK_API_KEY in .env file")

# ---------- macOS Helpers ----------
def mac_notify(title, message):
    """Send a native macOS notification"""
    if platform.system() == "Darwin":
        subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}"'])

def mac_open_url(url):
    """Open URL in Safari"""
    if platform.system() == "Darwin":
        subprocess.run(["open", url])

# ---------- UI Setup ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("🖼️ Freepik AI Image Upscaler (macOS)")
app.geometry("640x440")

title_label = ctk.CTkLabel(app, text="🖼️ Freepik AI Image Upscaler", font=("SF Pro Rounded", 22, "bold"))
title_label.pack(pady=20)

url_entry = ctk.CTkEntry(app, placeholder_text="Paste image URL here...", width=520, height=40)
url_entry.pack(pady=10)

status_label = ctk.CTkLabel(app, text="Ready to upscale.", font=("SF Pro", 14))
status_label.pack(pady=20)

result_entry = ctk.CTkEntry(app, placeholder_text="Upscaled image URL will appear here...", width=520, height=40)
result_entry.pack(pady=10)

# ---------- Upscale Logic ----------
def upscale_from_url():
    image_url = url_entry.get().strip()
    if not image_url:
        messagebox.showwarning("Input Required", "Please paste an image URL first.")
        return

    try:
        status_label.configure(text="🚀 Submitting to Freepik...", text_color="cyan")
        app.update()

        payload = {
            "image": image_url,
            "sharpen": 7,
            "smart_grain": 7,
            "ultra_detail": 30,
            "flavor": "photo",
            "scale_factor": 4
        }

        headers = {
            "x-freepik-api-key": FREEPIK_API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(API_URL, json=payload, headers=headers)
        data = response.json()

        if response.status_code != 200 or "data" not in data:
            messagebox.showerror("Error", f"Upscaling failed:\n{data}")
            return

        task_id = data["data"].get("task_id")
        if not task_id:
            messagebox.showerror("Error", f"No task_id found:\n{data}")
            return

        poll_url = f"{API_URL}/{task_id}"
        status_label.configure(text="⏳ Processing on Freepik servers...", text_color="yellow")
        app.update()

        for i in range(30):  # ~90s total wait
            time.sleep(3)
            poll_response = requests.get(poll_url, headers=headers)
            poll_data = poll_response.json()
            print(f"Poll {i}: {poll_data}")

            if "data" in poll_data:
                task = poll_data["data"]
                task_status = task.get("status", "").upper()

                if task_status in ("FINISHED", "COMPLETED") and "generated" in task:
                    image_urls = task["generated"]
                    if image_urls:
                        img_url = image_urls[0]
                        result_entry.delete(0, "end")
                        result_entry.insert(0, img_url)
                        app.clipboard_clear()
                        app.clipboard_append(img_url)

                        status_label.configure(
                            text="✅ Upscale complete! URL copied to clipboard.",
                            text_color="lightgreen"
                        )

                        print("✅ UPSCALED URL:", img_url)
                        mac_notify("Upscale Complete", "The image has been upscaled successfully!")
                        mac_open_url(img_url)  # comment out if you don’t want Safari to open
                        return

                elif task_status == "FAILED":
                    messagebox.showerror("Error", "Freepik reported a failure for this task.")
                    status_label.configure(text="Upscaling failed.", text_color="red")
                    return

        messagebox.showerror("Timeout", "Upscaling took too long or didn’t finish.")
        status_label.configure(text="Upscaling timed out.", text_color="red")

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")
        status_label.configure(text="Error occurred.", text_color="red")

# ---------- Buttons ----------
upscale_button = ctk.CTkButton(app, text="🚀 Upscale Image", command=upscale_from_url)
upscale_button.pack(pady=10)

quit_button = ctk.CTkButton(app, text="Exit", command=app.destroy, fg_color="gray")
quit_button.pack(pady=15)

app.mainloop()
