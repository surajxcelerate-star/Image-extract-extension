import os
import time
import requests
import customtkinter as ctk
from tkinter import messagebox
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image, ImageTk

# ---------- CONFIG ----------
load_dotenv()
FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY")
API_URL = "https://api.freepik.com/v1/ai/image-upscaler-precision-v2"
# ----------------------------

if not FREEPIK_API_KEY:
    raise ValueError("❌ Missing FREEPIK_API_KEY in .env file")

# ----- UI Setup -----
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("🖼️ Freepik AI Image Upscaler")
app.geometry("640x520")

title_label = ctk.CTkLabel(app, text="🖼️ Freepik AI Image Upscaler", font=("Arial Rounded MT Bold", 22))
title_label.pack(pady=20)

url_entry = ctk.CTkEntry(app, placeholder_text="Paste image URL here...", width=520, height=40)
url_entry.pack(pady=10)

preview_label = ctk.CTkLabel(app, text="(Image preview will appear here)", width=400, height=220)
preview_label.pack(pady=10)

status_label = ctk.CTkLabel(app, text="Ready to upscale.", font=("Arial", 14))
status_label.pack(pady=15)

# ----- Helper -----
def show_preview():
    image_url = url_entry.get().strip()
    if not image_url:
        messagebox.showwarning("Input Required", "Please paste an image URL first.")
        return
    try:
        status_label.configure(text="Loading preview...", text_color="white")
        app.update()
        resp = requests.get(image_url, timeout=10)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content))
            img.thumbnail((400, 220))
            photo = ImageTk.PhotoImage(img)
            preview_label.configure(image=photo, text="")
            preview_label.image = photo
            status_label.configure(text="Preview loaded.", text_color="lightgreen")
        else:
            messagebox.showerror("Error", f"Unable to fetch image: HTTP {resp.status_code}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load preview:\n{e}")

# ----- Upscale Function -----
def upscale_from_url():
    image_url = url_entry.get().strip()
    if not image_url:
        messagebox.showwarning("Input Required", "Please paste an image URL first.")
        return

    try:
        status_label.configure(text="Submitting to Freepik...", text_color="cyan")
        app.update()

        payload = {
            "image": image_url,  # ✅ Direct URL
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

        print("STATUS:", response.status_code)
        print("RAW RESPONSE:", response.text)

        if response.status_code != 200 or "data" not in data:
            messagebox.showerror("Error", f"Upscaling failed:\n{data}")
            return

        task_id = data["data"].get("task_id")
        if not task_id:
            messagebox.showerror("Error", f"No task_id found in response:\n{data}")
            return

        # ✅ Poll the correct endpoint
        poll_url = f"{API_URL}/{task_id}"
        status_label.configure(text="Processing image on Freepik servers...", text_color="yellow")
        app.update()

        for i in range(20):  # ~60 seconds max
            time.sleep(3)
            poll_response = requests.get(poll_url, headers=headers)
            poll_data = poll_response.json()
            print(f"Poll {i}: {poll_data}")

            if "data" in poll_data:
                task = poll_data["data"]
                if task.get("status") == "COMPLETED" and "generated" in task:
                    image_urls = task["generated"]
                    if image_urls:
                        img_url = image_urls[0]
                        img_response = requests.get(img_url)
                        file_name = os.path.basename(image_url.split("?")[0]) or "upscaled_image.png"
                        if not file_name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                            file_name += ".png"
                        save_path = os.path.join(os.getcwd(), f"upscaled_{file_name}")

                        with open(save_path, "wb") as f:
                            f.write(img_response.content)

                        status_label.configure(
                            text=f"✅ Upscaled image saved:\n{save_path}",
                            text_color="lightgreen"
                        )
                        messagebox.showinfo("Success", f"Upscaled image saved to:\n{save_path}")
                        return

            if poll_data.get("data", {}).get("status") == "FAILED":
                messagebox.showerror("Error", "Freepik reported a failure for this task.")
                return

        messagebox.showerror("Timeout", "Upscaling took too long or didn’t finish.")
        status_label.configure(text="Upscaling timed out.", text_color="red")

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")
        status_label.configure(text="Error occurred.", text_color="red")

# ----- Buttons -----
preview_button = ctk.CTkButton(app, text="🔍 Preview Image", command=show_preview)
preview_button.pack(pady=5)

upscale_button = ctk.CTkButton(app, text="🚀 Upscale Image", command=upscale_from_url)
upscale_button.pack(pady=5)

quit_button = ctk.CTkButton(app, text="Exit", command=app.destroy, fg_color="gray")
quit_button.pack(pady=15)

app.mainloop()
