from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    OptionList,
    Select,
    Static,
)
from textual.widgets.option_list import Option

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


class MenuUtamaScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="panel"):
            yield Static("SISTEM SMART PARKING", classes="title")
            yield Static("POLITEKNIK NEGERI SEMARANG", classes="subtitle")
            yield OptionList(
                Option("Login", id="login"),
                Option("Registrasi", id="registrasi"),
                Option("Keluar", id="keluar"),
                id="menu",
            )
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option.id == "login":
            self.app.push_screen(LoginScreen())
        elif event.option.id == "registrasi":
            self.app.push_screen(RegistrasiScreen())
        elif event.option.id == "keluar":
            self.app.exit()


class RegistrasiScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="panel"):
            yield Static("REGISTRASI PETUGAS", classes="title")
            yield Label("Nama Lengkap Mahasiswa")
            yield Input(placeholder="Nama lengkap", id="nama")
            yield Label("NIM (tanpa titik)")
            yield Input(placeholder="NIM", id="nim")
            yield Static("", id="pesan")
            with Horizontal(classes="buttons"):
                yield Button("Daftar", id="daftar", variant="primary")
                yield Button("Kembali", id="kembali")
        yield Footer()

    @on(Button.Pressed, "#daftar")
    def daftar(self) -> None:
        nama = self.query_one("#nama", Input).value.strip()
        nim = self.query_one("#nim", Input).value.strip()
        pesan = self.query_one("#pesan", Static)

        if not nama or not nim:
            pesan.update("[red]Nama dan NIM wajib diisi.[/red]")
            return

        username = buat_username(nama)
        password = buat_password(nim)
        users = load_users()

        if any(u["username"] == username for u in users):
            pesan.update("[red]Error: Username sudah terdaftar![/red]")
            return

        users.append({
            "nama": nama,
            "nim": nim,
            "username": username,
            "password_hash": hash_password(password),
        })
        save_users(users)

        self.query_one("#nama", Input).value = ""
        self.query_one("#nim", Input).value = ""
        pesan.update(
            "[bold green]Akun berhasil dibuat![/bold green]\n"
            f"Username : [bold]{username}[/bold]\n"
            f"Password : [bold]{password}[/bold]"
        )

    @on(Button.Pressed, "#kembali")
    def kembali(self) -> None:
        self.app.pop_screen()


class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="panel"):
            yield Static("AUTENTIKASI LOGIN", classes="title")
            yield Label("Username")
            yield Input(placeholder="Username", id="username")
            yield Label("Password")
            yield Input(placeholder="Password", password=True, id="password")
            yield Static("", id="pesan")
            with Horizontal(classes="buttons"):
                yield Button("Login", id="login", variant="primary")
                yield Button("Kembali", id="kembali")
        yield Footer()

    @on(Button.Pressed, "#login")
    def login(self) -> None:
        username = self.query_one("#username", Input).value.strip()
        password = self.query_one("#password", Input).value.strip()
        pesan = self.query_one("#pesan", Static)

        users = load_users()
        user = next((u for u in users if u["username"] == username), None)
        if user is None:
            pesan.update("[red]Error: Username petugas tidak terdaftar![/red]")
            return

        if hash_password(password) != user["password_hash"]:
            pesan.update("[red]Error: Password salah! Akses ditolak.[/red]")
            return

        self.app.current_user = user
        self.app.switch_screen(DashboardScreen())

    @on(Button.Pressed, "#kembali")
    def kembali(self) -> None:
        self.app.pop_screen()


class DashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="panel"):
            yield Static("DASHBOARD", classes="title")
            yield Static("", id="selamat", classes="subtitle")
            yield OptionList(
                Option("Transaksi Parkir", id="transaksi"),
                Option("Riwayat Parkir", id="riwayat"),
                Option("Logout", id="logout"),
                id="menu",
            )
        yield Footer()

    def on_mount(self) -> None:
        user = self.app.current_user
        self.query_one("#selamat", Static).update(f"Selamat bertugas, {user['nama']}")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option.id == "transaksi":
            self.app.push_screen(TransaksiScreen())
        elif event.option.id == "riwayat":
            self.app.push_screen(RiwayatScreen())
        elif event.option.id == "logout":
            self.app.current_user = None
            self.app.pop_screen()


class TransaksiScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.tarif = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="panel wide"):
            yield Static("TRANSAKSI PARKIR", classes="title")
            yield Label("Nomor Polisi / Plat Kendaraan")
            yield Input(placeholder="Contoh: H 1234 AB", id="plat")
            yield Label("Jenis Kendaraan")
            yield Select(
                [("Motor", 1), ("Mobil", 2)],
                value=1, allow_blank=False, id="jenis",
            )
            yield Label("Durasi Parkir (jam)")
            yield Input(placeholder="Contoh: 3", id="durasi", type="integer")
            yield Label("Status Stiker Member Kampus")
            yield Select(
                [("Ya", "Ya"), ("Tidak", "Tidak")],
                value="Tidak", allow_blank=False, id="member",
            )
            yield Static("", id="rincian")
            with Horizontal(classes="buttons"):
                yield Button("Hitung Tarif", id="hitung", variant="primary")
                yield Button("Lanjut Pembayaran", id="bayar", variant="success", disabled=True)
                yield Button("Kembali", id="kembali")
        yield Footer()

    @on(Button.Pressed, "#hitung")
    def hitung(self) -> None:
        plat = self.query_one("#plat", Input).value.strip()
        jenis = self.query_one("#jenis", Select).value
        member = self.query_one("#member", Select).value
        durasi_raw = self.query_one("#durasi", Input).value.strip()
        rincian = self.query_one("#rincian", Static)

        if not plat:
            self.app.notify("Plat kendaraan wajib diisi!", severity="error")
            return

        try:
            durasi = int(durasi_raw)
            if durasi < 0:
                raise ValueError
        except ValueError:
            self.app.notify("Durasi harus angka bulat >= 0!", severity="error")
            return

        if jenis == 1:
            nama_jenis, tarif_dasar, tarif_jam = "Motor", 3000, 1000
        else:
            nama_jenis, tarif_dasar, tarif_jam = "Mobil", 6000, 2000

        jam_berikutnya = max(0, durasi - 2)
        biaya_jam_berikutnya = jam_berikutnya * tarif_jam
        denda = 20000 if durasi > 12 else 0
        subtotal = tarif_dasar + biaya_jam_berikutnya + denda
        diskon = subtotal * 30 // 100 if member == "Ya" else 0
        total = subtotal - diskon

        self.tarif = {
            "plat": plat,
            "nama_jenis": nama_jenis,
            "durasi": durasi,
            "member": member,
            "tarif_dasar": tarif_dasar,
            "biaya_jam_berikutnya": biaya_jam_berikutnya,
            "jam_berikutnya": jam_berikutnya,
            "denda": denda,
            "subtotal": subtotal,
            "diskon": diskon,
            "total": total,
        }

        rincian.update(
            "[bold]Rincian Biaya:[/bold]\n"
            f"Tarif Dasar (2 jam pertama) : {format_rupiah(tarif_dasar)}\n"
            f"Jam Berikutnya ({jam_berikutnya} jam)    : {format_rupiah(biaya_jam_berikutnya)}\n"
            f"Denda Inap                  : {format_rupiah(denda)}\n"
            f"Subtotal                    : {format_rupiah(subtotal)}\n"
            f"Diskon Member (30%)         : -{format_rupiah(diskon)}\n"
            f"[bold]Total Tagihan[/bold]               : [bold]{format_rupiah(total)}[/bold]"
        )
        self.query_one("#bayar", Button).disabled = False

    @on(Button.Pressed, "#bayar")
    def bayar(self) -> None:
        if self.tarif is None:
            return
        self.app.push_screen(PembayaranModal(self.tarif["total"]), self.setelah_bayar)

    def setelah_bayar(self, bayar: int | None) -> None:
        if bayar is None:
            return

        t = self.tarif
        kembalian = bayar - t["total"]

        tambah_riwayat(
            self.app.current_user, t["plat"], t["nama_jenis"], t["durasi"],
            t["member"], t["tarif_dasar"], t["biaya_jam_berikutnya"],
            t["denda"], t["diskon"], t["total"], bayar, kembalian,
        )

        struk = (
            f"Plat Kendaraan    : {t['plat']}\n"
            f"Jenis Kendaraan   : {t['nama_jenis']}\n"
            f"Durasi Parkir     : {t['durasi']} jam\n"
            f"Status Member     : {t['member']}\n"
            f"{'-' * 40}\n"
            f"Tarif Dasar       : {format_rupiah(t['tarif_dasar'])}\n"
            f"Jam Berikutnya    : {format_rupiah(t['biaya_jam_berikutnya'])}\n"
            f"Denda Inap        : {format_rupiah(t['denda'])}\n"
            f"Diskon Member     : -{format_rupiah(t['diskon'])}\n"
            f"[bold]Total Tagihan[/bold]     : [bold]{format_rupiah(t['total'])}[/bold]\n"
            f"Uang Dibayar      : {format_rupiah(bayar)}\n"
            f"[green]Kembalian         : {format_rupiah(kembalian)}[/green]"
        )
        self.app.push_screen(StrukModal(struk), self._selesai_struk)

    def _selesai_struk(self, _result) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#kembali")
    def kembali(self) -> None:
        self.app.pop_screen()


class PembayaranModal(ModalScreen):
    def __init__(self, total: int) -> None:
        super().__init__()
        self.total = total

    def compose(self) -> ComposeResult:
        with Vertical(classes="panel modal"):
            yield Static("PEMBAYARAN", classes="title")
            yield Static(f"Total Tagihan : {format_rupiah(self.total)}")
            yield Label("Nominal Uang Bayar")
            yield Input(placeholder="Contoh: 50000", id="nominal", type="integer")
            yield Static("", id="error")
            with Horizontal(classes="buttons"):
                yield Button("Bayar", id="bayar", variant="primary")
                yield Button("Batal", id="batal", variant="error")

    @on(Button.Pressed, "#bayar")
    def bayar(self) -> None:
        raw = self.query_one("#nominal", Input).value.strip()
        error = self.query_one("#error", Static)

        try:
            nominal = int(raw)
        except ValueError:
            error.update("[red]Masukkan nominal angka yang valid.[/red]")
            return

        if nominal < self.total:
            error.update(
                f"[red]Transaksi gagal! Uang kurang "
                f"{format_rupiah(self.total - nominal)}.[/red]"
            )
            return

        self.dismiss(nominal)

    @on(Button.Pressed, "#batal")
    def batal(self) -> None:
        self.dismiss(None)

    def on_input_submitted(self, _event: Input.Submitted) -> None:
        self.bayar()


class StrukModal(ModalScreen):
    def __init__(self, struk: str) -> None:
        super().__init__()
        self.struk = struk

    def compose(self) -> ComposeResult:
        with Vertical(classes="panel modal"):
            yield Static("STRUK PEMBAYARAN RESMI", classes="title")
            yield Static(self.struk, id="struk")
            with Horizontal(classes="buttons"):
                yield Button("Selesai", id="selesai", variant="primary")

    @on(Button.Pressed, "#selesai")
    def selesai(self) -> None:
        self.dismiss(None)


class RiwayatScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="panel wide"):
            yield Static("RIWAYAT PARKIR", classes="title")
            yield DataTable(id="tabel")
            with Horizontal(classes="buttons"):
                yield Button("Kembali", id="kembali")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#tabel", DataTable)
        table.add_columns("Waktu", "Petugas", "Plat", "Jenis", "Total")
        history = load_history()
        if not history:
            table.add_row("-", "-", "Belum ada riwayat", "-", "-")
        else:
            for r in history:
                table.add_row(
                    r["waktu"], r["petugas"], r["plat"],
                    r["jenis"], format_rupiah(r["total"]),
                )
        table.cursor_type = "row"

    @on(Button.Pressed, "#kembali")
    def kembali(self) -> None:
        self.app.pop_screen()


class SmartParkingApp(App):
    TITLE = "Smart Parking Polines"
    SUB_TITLE = "Sistem E-Parking Terpadu"

    CSS = """
    Screen {
        align: center middle;
    }
    .panel {
        width: 72;
        height: auto;
        padding: 1 3;
        border: round $primary;
        background: $surface;
    }
    .panel.wide {
        width: 96;
    }
    .modal {
        width: 62;
    }
    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
    }
    .subtitle {
        text-align: center;
        color: $text-muted;
    }
    Label {
        margin-top: 1;
    }
    #rincian, #error, #pesan {
        height: auto;
        margin-top: 1;
    }
    OptionList {
        height: auto;
        margin-top: 1;
    }
    .buttons {
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    .buttons Button {
        margin: 0 1;
    }
    DataTable {
        height: 16;
        margin-top: 1;
    }
    """

    def on_mount(self) -> None:
        self.current_user = None
        self.push_screen(MenuUtamaScreen())


if __name__ == "__main__":
    SmartParkingApp().run()
