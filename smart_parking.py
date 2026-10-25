import sys

from storage import (
    buat_password,
    buat_username,
    format_rupiah,
    hash_password,
    load_history,
    load_users,
    save_users,
    tambah_riwayat,
)


def tahap1_registrasi():
    print("=" * 50)
    print("REGISTRASI & INISIALISASI AKUN PETUGAS".center(50))
    print("=" * 50)

    users = load_users()
    usernames_terdaftar = [u["username"] for u in users]

    while True:
        nama = input("Nama Lengkap Mahasiswa : ").strip()
        nim = input("NIM (tanpa titik)      : ").strip()

        username_terdaftar = buat_username(nama)
        password_terdaftar = buat_password(nim)

        if username_terdaftar in usernames_terdaftar:
            print("Error: Username sudah terdaftar! Silakan masukkan ulang.")
            print()
            continue

        users.append({
            "nama": nama,
            "nim": nim,
            "username": username_terdaftar,
            "password_hash": hash_password(password_terdaftar),
        })
        save_users(users)

        print("\nAkun petugas berhasil dibuat:")
        print(f"  Username : {username_terdaftar}")
        print(f"  Password : {password_terdaftar}")
        print()

        break


def tahap2_login():
    print("=" * 50)
    print("AUTENTIKASI LOGIN".center(50))
    print("=" * 50)

    users = load_users()

    username = input("Username : ").strip()
    user = next((u for u in users if u["username"] == username), None)
    if user is None:
        print("Error: Username petugas tidak terdaftar!")
        return None

    password = input("Password : ").strip()
    if hash_password(password) != user["password_hash"]:
        print("Error: Password salah! Akses ditolak.")
        return None

    print(f"Login Berhasil! Selamat Bertugas, {user['nama']}.")
    print()
    return user


def tahap3_transaksi(user):
    print("=" * 50)
    print("TRANSAKSI & PERHITUNGAN TARIF PARKIR".center(50))
    print("=" * 50)

    plat = input("Nomor Polisi / Plat Kendaraan : ").strip()
    jenis = int(input("Jenis Kendaraan (1=Motor, 2=Mobil) : "))
    durasi = int(input("Durasi Parkir dalam Jam            : "))
    member = input("Status Stiker Member Kampus (Ya/Tidak) : ").strip()

    if jenis == 1:
        nama_jenis = "Motor"
        tarif_dasar = 3000
        tarif_jam = 1000
    elif jenis == 2:
        nama_jenis = "Mobil"
        tarif_dasar = 6000
        tarif_jam = 2000
    else:
        print("Error: Jenis kendaraan tidak valid!")
        sys.exit()

    jam_berikutnya = max(0, durasi - 2)
    biaya_jam_berikutnya = jam_berikutnya * tarif_jam

    denda = 20000 if durasi > 12 else 0

    subtotal = tarif_dasar + biaya_jam_berikutnya + denda

    if member == "Ya":
        diskon = subtotal * 30 // 100
    else:
        diskon = 0

    total = subtotal - diskon

    print()
    print("Rincian Biaya:")
    print(f"  Tarif Dasar (2 jam pertama) : {format_rupiah(tarif_dasar)}")
    print(f"  Jam Berikutnya ({jam_berikutnya} jam)    : {format_rupiah(biaya_jam_berikutnya)}")
    print(f"  Denda Inap                   : {format_rupiah(denda)}")
    print(f"  Subtotal                     : {format_rupiah(subtotal)}")
    print(f"  Diskon Member (30%)          : -{format_rupiah(diskon)}")
    print(f"  Total Tagihan                : {format_rupiah(total)}")
    print()

    while True:
        bayar = int(input("Nominal Uang Bayar : "))
        if bayar < total:
            kekurangan = total - bayar
            print("Transaksi gagal!")
            print(f"  Uang Anda kurang sebesar {format_rupiah(kekurangan)}.")
            print("  Silakan masukkan ulang nominal pembayaran.")
            print()
        else:
            kembalian = bayar - total
            print()
            print("=" * 50)
            print("          STRUK PEMBAYARAN RESMI")
            print("=" * 50)
            print(f"  Plat Kendaraan    : {plat}")
            print(f"  Jenis Kendaraan   : {nama_jenis}")
            print(f"  Durasi Parkir     : {durasi} jam")
            print(f"  Status Member     : {member}")
            print("-" * 50)
            print(f"  Tarif Dasar       : {format_rupiah(tarif_dasar)}")
            print(f"  Jam Berikutnya    : {format_rupiah(biaya_jam_berikutnya)}")
            print(f"  Denda Inap        : {format_rupiah(denda)}")
            print(f"  Diskon Member     : -{format_rupiah(diskon)}")
            print(f"  Total Tagihan     : {format_rupiah(total)}")
            print(f"  Uang Dibayar      : {format_rupiah(bayar)}")
            print(f"  Kembalian         : {format_rupiah(kembalian)}")
            print("=" * 50)
            print("Terima kasih telah menggunakan layanan kami!")

            tambah_riwayat(
                user, plat, nama_jenis, durasi, member,
                tarif_dasar, biaya_jam_berikutnya, denda, diskon,
                total, bayar, kembalian,
            )

            break


def tampilkan_riwayat():
    print("=" * 50)
    print("RIWAYAT PARKIR".center(50))
    print("=" * 50)

    history = load_history()

    if not history:
        print("Belum ada riwayat transaksi.")
        print()
        return

    print(f"{'WAKTU':<20} {'PETUGAS':<20} {'PLAT':<12} {'JENIS':<7} {'TOTAL':>10}")
    print("-" * 72)

    for r in history:
        print(
            f"{r['waktu']:<20} "
            f"{r['petugas']:<20} "
            f"{r['plat']:<12} "
            f"{r['jenis']:<7} "
            f"{format_rupiah(r['total']):>10}"
        )

    print("-" * 72)
    print(f"Total transaksi: {len(history)}")
    print()


def main():
    print("SISTEM SMART PARKING & REGISTRASI MEMBER MAHASISWA")
    print("POLITEKNIK NEGERI SEMARANG")
    print()

    while True:
        print("=" * 50)
        print("              MENU UTAMA")
        print("=" * 50)
        print("  [1] Login")
        print("  [2] Registrasi")
        print("  [3] Keluar")
        print("-" * 50)

        pilihan = input("Pilih menu (1/2/3) : ").strip()

        if pilihan == "1":
            user = tahap2_login()
            if user is not None:
                dashboard(user)
        elif pilihan == "2":
            tahap1_registrasi()
        elif pilihan == "3":
            print("Terima kasih! Program selesai.")
            break
        else:
            print("Pilihan tidak valid! Silakan pilih 1, 2, atau 3.")
            print()


def dashboard(user):
    while True:
        print("=" * 50)
        print(f"  DASHBOARD - {user['nama'].upper()}")
        print("=" * 50)
        print("  [1] Transaksi Parkir")
        print("  [2] Riwayat Parkir")
        print("  [3] Logout")
        print("-" * 50)

        pilihan = input("Pilih menu (1/2/3) : ").strip()

        if pilihan == "1":
            tahap3_transaksi(user)
        elif pilihan == "2":
            tampilkan_riwayat()
        elif pilihan == "3":
            print("Logout berhasil.")
            print()
            break
        else:
            print("Pilihan tidak valid! Silakan pilih 1, 2, atau 3.")
            print()


if __name__ == "__main__":
    main()
