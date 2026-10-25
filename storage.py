import datetime
import hashlib
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "users.json")
HISTORY_FILE = os.path.join(BASE_DIR, "riwayat_parkir.json")
SALT = "polines-parking-salt"


def hash_password(password):
    return hashlib.sha256((SALT + password).encode()).hexdigest()


def format_rupiah(nilai):
    return f"Rp {nilai:,.0f}".replace(",", ".")


def buat_username(nama):
    return nama.lower().replace(" ", "")


def buat_password(nim):
    return "parkir" + nim[-3:]


def load_users():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(JSON_FILE, "w") as f:
        json.dump(users, f, indent=4)


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


def tambah_riwayat(user, plat, jenis, durasi, member, tarif_dasar,
                   biaya_jam_berikutnya, denda, diskon, total, bayar, kembalian):
    history = load_history()
    history.append({
        "waktu": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "petugas": user["username"],
        "plat": plat,
        "jenis": jenis,
        "durasi": durasi,
        "member": member,
        "tarif_dasar": tarif_dasar,
        "jam_berikutnya": biaya_jam_berikutnya,
        "denda": denda,
        "diskon": diskon,
        "total": total,
        "bayar": bayar,
        "kembalian": kembalian,
    })
    save_history(history)
