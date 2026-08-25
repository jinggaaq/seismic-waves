from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from models import (
    db,
    Produk,
    Admin,
    UkuranProduk,
    Cart,
    Pelanggan,
    Pesanan,
    DetailPesanan
)
from sqlalchemy import text
import uuid


app = Flask(__name__)

# ============================================================
# DEVICE ID
# ============================================================

def get_device_id():

    if "device_id" not in session:

        session["device_id"] = str(uuid.uuid4())

        session.permanent = True

    return session["device_id"]

# ============================================================
# KONFIGURASI
# ============================================================

app.config.from_object(Config)

# Hubungkan SQLAlchemy
db.init_app(app)
@app.context_processor
def cart_count():

    if "session_id" not in session:
        return dict(cart_count=0)

    total_qty = db.session.query(
        db.func.sum(Cart.jumlah)
    ).filter_by(
        session_id=session["session_id"]
    ).scalar() or 0

    return dict(cart_count=total_qty)

# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    produk_home = Produk.query.order_by(Produk.id.desc()).limit(4).all()

    return render_template(
        "index.html",
        produk_home=produk_home
    )

# ============================================================
# CATALOG
# ============================================================

@app.route("/catalog")
def catalog():

    produk = Produk.query.all()

    return render_template(
        "catalog.html",
        produk=produk
    )

# ============================================================
# DETAIL PRODUK
# ============================================================

@app.route("/produk/<int:id>")
def detail_produk(id):
    produk = Produk.query.get_or_404(id)
    return render_template("detail_produk.html", produk=produk)

# ============================================================
# ADD TO CART
# ============================================================

@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():

    # buat session_id jika belum ada
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    session_id = session["session_id"]

    produk_id = int(request.form.get("produk_id"))
    ukuran = request.form.get("size")
    jumlah = int(request.form.get("qty"))

    produk = Produk.query.get_or_404(produk_id)

    # validasi stok
    if jumlah > produk.stok:
        flash("Jumlah melebihi stok tersedia.", "danger")
        return redirect(url_for("detail_produk", id=produk_id))

    # cek apakah produk + ukuran sudah ada di cart
    item = Cart.query.filter_by(
        session_id=session_id,
        produk_id=produk_id,
        ukuran=ukuran
    ).first()

    if item:

        if item.jumlah + jumlah > produk.stok:
            flash("Total jumlah melebihi stok tersedia.", "danger")
            return redirect(url_for("detail_produk", id=produk_id))

        item.jumlah += jumlah

    else:

        item = Cart(
            session_id=session_id,
            produk_id=produk_id,
            ukuran=ukuran,
            jumlah=jumlah
        )

        db.session.add(item)

    db.session.commit()

    # langsung masuk ke halaman cart
    return redirect(url_for("cart"))

@app.route("/cart/update", methods=["POST"])
def update_cart():

    cart_id = int(request.form.get("cart_id"))
    jumlah = int(request.form.get("jumlah"))

    item = Cart.query.get_or_404(cart_id)

    # validasi minimal 1
    if jumlah < 1:
        jumlah = 1

    # validasi stok
    if jumlah > item.produk.stok:
        jumlah = item.produk.stok

    item.jumlah = jumlah

    db.session.commit()

    return redirect(url_for("cart"))

@app.route("/cart/remove/<int:cart_id>")
def remove_cart_item(cart_id):

    item = Cart.query.get_or_404(cart_id)

    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("cart"))


@app.route("/buy-now", methods=["POST"])
def buy_now():

    produk_id = int(request.form.get("produk_id"))
    size = request.form.get("size")
    qty = int(request.form.get("qty"))

    produk = Produk.query.get_or_404(produk_id)

    # Validasi jumlah
    if qty < 1:
        qty = 1

    if qty > produk.stok:
        qty = produk.stok

    # Simpan informasi Buy Now ke session
    session["buy_now"] = {
        "produk_id": produk.id,
        "ukuran": size,
        "jumlah": qty
    }

    total = produk.harga * qty

    return render_template(
        "checkout.html",
        cart_items=[
            {
                "produk": produk,
                "ukuran": size,
                "jumlah": qty
            }
        ],
        total=total,
        buy_now=True
    )
# ============================================================
# ABOUT
# ============================================================

@app.route("/about")
def about():
    return render_template("about.html")


# ============================================================
# CART
# ============================================================

@app.route("/cart")
def cart():

    if "session_id" not in session:
        return render_template(
            "cart.html",
            cart_items=[],
            total=0
        )

    cart_items = Cart.query.filter_by(
        session_id=session["session_id"]
    ).all()

    total = sum(
        item.produk.harga * item.jumlah
        for item in cart_items
    )

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )

# ============================================================
# CHECKOUT
# ============================================================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    # ========================================================
    # POST = PROSES PEMESANAN
    # ========================================================

    if request.method == "POST":

        # --------------------------------------------
        # Ambil data pelanggan
        # --------------------------------------------

        email = request.form.get("email", "").strip()
        nama = request.form.get("full_name", "").strip()
        alamat = request.form.get("address", "").strip()
        kota = request.form.get("city", "").strip()
        kode_pos = request.form.get("postal_code", "").strip()
        provinsi = request.form.get("province", "").strip()
        no_hp = request.form.get("phone", "").strip()
        metode = request.form.get("payment_method", "").strip()


        # --------------------------------------------
        # Validasi backend
        # --------------------------------------------

        if not all([
            email,
            nama,
            alamat,
            kota,
            kode_pos,
            provinsi,
            no_hp,
            metode
        ]):

            flash(
                "Semua data checkout wajib diisi.",
                "danger"
            )

            return redirect(url_for("checkout"))


        # --------------------------------------------
        # Konversi metode pembayaran
        # --------------------------------------------

        if metode == "qris":

            metode_db = "QRIS"

        elif metode == "bank_transfer":

            metode_db = "Transfer Bank"

        else:

            flash(
                "Metode pembayaran tidak valid.",
                "danger"
            )

            return redirect(url_for("checkout"))


        # --------------------------------------------
        # Ambil produk yang akan dibeli
        # --------------------------------------------

        cart_items = []

        # ====================================================
        # BUY NOW
        # ====================================================

        if "buy_now" in session:

            buy_now = session["buy_now"]

            produk = Produk.query.get_or_404(
                buy_now["produk_id"]
            )

            jumlah = int(
                buy_now["jumlah"]
            )

            ukuran = buy_now["ukuran"]

            # Cek stok
            if jumlah > produk.stok:

                flash(
                    f"Stok {produk.nama} tidak mencukupi.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "detail_produk",
                        id=produk.id
                    )
                )


            cart_items.append({
                "produk": produk,
                "ukuran": ukuran,
                "jumlah": jumlah
            })


        # ====================================================
        # CART BIASA
        # ====================================================

        else:

            if "session_id" not in session:

                flash(
                    "Keranjang kosong.",
                    "danger"
                )

                return redirect(
                    url_for("cart")
                )


            cart_items = Cart.query.filter_by(
                session_id=session["session_id"]
            ).all()


            if not cart_items:

                flash(
                    "Keranjang kosong.",
                    "danger"
                )

                return redirect(
                    url_for("cart")
                )


        # --------------------------------------------
        # Hitung total
        # --------------------------------------------

        total = sum(
            item["produk"].harga * item["jumlah"]
            if isinstance(item, dict)
            else item.produk.harga * item.jumlah
            for item in cart_items
        )


        # --------------------------------------------
        # Simpan pelanggan
        # --------------------------------------------

        pelanggan = Pelanggan(
            nama=nama,
            alamat=alamat,
            no_hp=no_hp,
            email=email,
            kode_pos=kode_pos,
            kota=kota,
            provinsi=provinsi
        )

        db.session.add(pelanggan)

        # Agar ID pelanggan langsung tersedia
        db.session.flush()

        pelanggan_id = pelanggan.id


        # --------------------------------------------
        # Buat kode pesanan
        # --------------------------------------------

        kode_pesanan = (
            "SW-"
            + uuid.uuid4().hex[:8].upper()
        )


        # --------------------------------------------
        # Simpan pesanan
        # --------------------------------------------

        result = db.session.execute(
            text("""
                INSERT INTO pesanan
                (
                    kode_pesanan,
                    pelanggan_id,
                    device_id,
                    total_harga,
                    metode_pembayaran,
                    status_pesanan
                )
                VALUES
                (
                    :kode_pesanan,
                    :pelanggan_id,
                    :device_id,
                    :total_harga,
                    :metode_pembayaran,
                    'Diproses'
                )
            """),
            {
                "kode_pesanan": kode_pesanan,
                "pelanggan_id": pelanggan_id,
                "device_id": get_device_id(),
                "total_harga": total,
                "metode_pembayaran": metode_db
            }
        )

        pesanan_id = result.lastrowid


        # --------------------------------------------
        # Simpan detail pesanan
        # --------------------------------------------

        for item in cart_items:

            if isinstance(item, dict):

                produk = item["produk"]
                ukuran = item["ukuran"]
                jumlah = item["jumlah"]

            else:

                produk = item.produk
                ukuran = item.ukuran
                jumlah = item.jumlah


            subtotal = produk.harga * jumlah


            db.session.execute(
                text("""
                    INSERT INTO detail_pesanan
                    (
                        pesanan_id,
                        produk_id,
                        ukuran,
                        jumlah,
                        harga,
                        subtotal
                    )
                    VALUES
                    (
                        :pesanan_id,
                        :produk_id,
                        :ukuran,
                        :jumlah,
                        :harga,
                        :subtotal
                    )
                """),
                {
                    "pesanan_id": pesanan_id,
                    "produk_id": produk.id,
                    "ukuran": ukuran,
                    "jumlah": jumlah,
                    "harga": produk.harga,
                    "subtotal": subtotal
                }
            )


            # ----------------------------------------
            # Kurangi stok
            # ----------------------------------------

            produk.stok -= jumlah


        # --------------------------------------------
        # Hapus cart
        # --------------------------------------------

        if "session_id" in session:

            Cart.query.filter_by(
                session_id=session["session_id"]
            ).delete()


        # --------------------------------------------
        # Hapus Buy Now
        # --------------------------------------------

        session.pop(
            "buy_now",
            None
        )


        # --------------------------------------------
        # Simpan database
        # --------------------------------------------

        db.session.commit()


        # --------------------------------------------
        # Simpan data order ke session
        # --------------------------------------------

        session["last_order"] = {
            "kode_pesanan": kode_pesanan,
            "nama": nama,
            "phone": no_hp,
            "total": total,
            "payment": metode_db
        }


        # --------------------------------------------
        # Ke halaman berhasil
        # --------------------------------------------

        return redirect(
            url_for(
                "success",
                kode=kode_pesanan
            )
        )
    # ========================================================
    # GET = TAMPILKAN CHECKOUT
    # ========================================================

    cart_items = []

    # ========================================================
    # BUY NOW
    # ========================================================

    if "buy_now" in session:

        buy_now = session["buy_now"]

        produk = Produk.query.get_or_404(
            buy_now["produk_id"]
        )

        cart_items = [
            {
                "produk": produk,
                "ukuran": buy_now["ukuran"],
                "jumlah": buy_now["jumlah"]
            }
        ]

    # ========================================================
    # CART BIASA
    # ========================================================

    elif "session_id" in session:

        cart_items = Cart.query.filter_by(
            session_id=session["session_id"]
        ).all()

    # --------------------------------------------
    # Hitung total
    # --------------------------------------------

    total = sum(
        item["produk"].harga * item["jumlah"]
        if isinstance(item, dict)
        else item.produk.harga * item.jumlah
        for item in cart_items
    )

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total=total
    )
# ============================================================
# RIWAYAT PEMBELIAN
# ============================================================

@app.route("/riwayat")
def riwayat():

    # Ambil device ID dari browser/device saat ini
    device_id = get_device_id()

    # Ambil pesanan yang dibuat dari device ini
    pesanan_list = Pesanan.query.filter_by(
        device_id=device_id
    ).order_by(
        Pesanan.tanggal_pesanan.desc()
    ).all()

    return render_template(
        "riwayat.html",
        pesanan_list=pesanan_list
    )
   

# ============================================================
# SUCCESS
# ============================================================

@app.route("/success")
def success():

    # Ambil data order terakhir
    order = session.get("last_order")

    # Jika tidak ada data order,
    # jangan izinkan membuka halaman success secara langsung
    if not order:
        return redirect(url_for("home"))

    return render_template(
        "success.html",
        order=order
    )


# ============================================================
# TEST DATABASE
# ============================================================

@app.route("/test-db")
def test_db():

    jumlah_produk = Produk.query.count()

    return f"Database berhasil terhubung! Jumlah produk: {jumlah_produk}"


# ============================================================
# ADMIN LOGIN / REDIRECT
# ============================================================

@app.route("/admin")
def admin():

    # Jika belum login
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    # Jika sudah login
    return redirect(url_for("admin_dashboard"))


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    # Jika admin sudah login,
    # langsung arahkan ke dashboard
    if "admin_id" in session:
        return redirect(url_for("admin_dashboard"))

    # Jika form login dikirim
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Cari admin berdasarkan username
        admin = Admin.query.filter_by(
            username=username
        ).first()

        # Cek username dan password
        if admin and admin.check_password(password):

            # Simpan data admin ke session
            session["admin_id"] = admin.id
            session["admin_username"] = admin.username
            session["admin_nama"] = admin.nama

            flash(
                "Login berhasil. Selamat datang!",
                "success"
            )

            return redirect(
                url_for("admin_dashboard")
            )

        # Jika login gagal
        flash(
            "Username atau password salah.",
            "danger"
        )

    return render_template(
        "admin/login.html"
    )

    

# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    # Proteksi halaman admin
    if "admin_id" not in session:
        return redirect(
            url_for("admin_login")
        )

    # --------------------------------------------------------
    # TOTAL PRODUK
    # --------------------------------------------------------

    total_produk = Produk.query.count()

    # --------------------------------------------------------
    # TOTAL STOK
    # --------------------------------------------------------

    total_stok = db.session.query(
        db.func.sum(Produk.stok)
    ).scalar() or 0

    # --------------------------------------------------------
    # TOTAL KATEGORI
    # --------------------------------------------------------

    total_kategori = db.session.query(
        db.func.count(
            db.func.distinct(Produk.kategori)
        )
    ).scalar() or 0

    # --------------------------------------------------------
    # PRODUK STOK MENIPIS
    # --------------------------------------------------------

    produk_stok_menipis = Produk.query.filter(
        Produk.stok <= 5
    ).count()

    # --------------------------------------------------------
    # PRODUK TERBARU
    # --------------------------------------------------------

    produk_terbaru = Produk.query.order_by(
        Produk.id.desc()
    ).limit(5).all()

    # --------------------------------------------------------
    # TAMPILKAN DASHBOARD
    # --------------------------------------------------------

    return render_template(
        "admin/dashboard.html",

        total_produk=total_produk,

        total_stok=total_stok,

        total_kategori=total_kategori,

        produk_stok_menipis=produk_stok_menipis,

        produk_terbaru=produk_terbaru,

        admin_nama=session.get(
            "admin_nama"
        )
    )


# ============================================================
# ADMIN - DAFTAR PRODUK
# ============================================================

@app.route("/admin/produk")
def admin_produk():

    # Proteksi halaman
    if "admin_id" not in session:
        return redirect(
            url_for("admin_login")
        )

    # Ambil seluruh produk
    produk = Produk.query.order_by(
        Produk.id.desc()
    ).all()

    return render_template(
        "admin/produk.html",

        produk=produk,

        admin_nama=session.get(
            "admin_nama"
        )
    )


# ============================================================
# ADMIN - TAMBAH PRODUK
# ============================================================

@app.route(
    "/admin/produk/tambah",
    methods=["GET", "POST"]
)
def admin_tambah_produk():

    # Proteksi halaman
    if "admin_id" not in session:
        return redirect(
            url_for("admin_login")
        )

    # --------------------------------------------------------
    # JIKA FORM DIKIRIM
    # --------------------------------------------------------

    if request.method == "POST":

        # Ambil data form
        nama = request.form.get("nama")
        kategori = request.form.get("kategori")
        harga = request.form.get("harga")
        deskripsi = request.form.get("deskripsi")
        folder = request.form.get("folder")
        stok = request.form.get("stok")

        # Ambil semua ukuran yang dicentang
        ukuran = request.form.getlist(
            "ukuran"
        )

        # ----------------------------------------------------
        # VALIDASI FIELD
        # ----------------------------------------------------

        if (
            not nama
            or not kategori
            or not harga
            or not folder
            or not stok
        ):

            flash(
                "Semua field wajib diisi.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_tambah_produk"
                )
            )

        # ----------------------------------------------------
        # KONVERSI HARGA DAN STOK
        # ----------------------------------------------------

        try:

            harga = int(harga)
            stok = int(stok)

        except ValueError:

            flash(
                "Harga dan stok harus berupa angka.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_tambah_produk"
                )
            )

        # ----------------------------------------------------
        # VALIDASI NILAI NEGATIF
        # ----------------------------------------------------

        if harga < 0 or stok < 0:

            flash(
                "Harga dan stok tidak boleh negatif.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_tambah_produk"
                )
            )

        # ----------------------------------------------------
        # BUAT PRODUK BARU
        # ----------------------------------------------------

        produk = Produk(
            nama=nama,
            kategori=kategori,
            harga=harga,
            deskripsi=deskripsi,
            folder=folder,
            stok=stok
        )

        db.session.add(produk)

        # ----------------------------------------------------
        # FLUSH
        # ----------------------------------------------------
        # Agar ID produk sudah tersedia sebelum
        # ukuran produk dibuat.

        db.session.flush()

        # ----------------------------------------------------
        # SIMPAN UKURAN
        # ----------------------------------------------------

        for ukuran_item in ukuran:

            if ukuran_item.strip():

                ukuran_produk = UkuranProduk(
                    produk_id=produk.id,
                    ukuran=ukuran_item.strip()
                )

                db.session.add(
                    ukuran_produk
                )

        # ----------------------------------------------------
        # SIMPAN KE DATABASE
        # ----------------------------------------------------

        db.session.commit()

        flash(
            "Produk berhasil ditambahkan.",
            "success"
        )

        return redirect(
            url_for("admin_produk")
        )

    # --------------------------------------------------------
    # TAMPILKAN FORM TAMBAH PRODUK
    # --------------------------------------------------------

    return render_template(
        "admin/tambah_produk.html",

        admin_nama=session.get(
            "admin_nama"
        )
    )


# ============================================================
# ADMIN - EDIT PRODUK
# ============================================================

@app.route(
    "/admin/produk/edit/<int:id>",
    methods=["GET", "POST"]
)
def admin_edit_produk(id):

    # Proteksi halaman
    if "admin_id" not in session:
        return redirect(
            url_for("admin_login")
        )

    # Ambil produk berdasarkan ID
    produk = Produk.query.get_or_404(id)

    # --------------------------------------------------------
    # JIKA FORM DIKIRIM
    # --------------------------------------------------------

    if request.method == "POST":

        # Ambil data dari form
        nama = request.form.get("nama")
        kategori = request.form.get("kategori")
        harga = request.form.get("harga")
        deskripsi = request.form.get("deskripsi")
        folder = request.form.get("folder")
        stok = request.form.get("stok")

        # Ambil ukuran
        ukuran = request.form.getlist(
            "ukuran"
        )

        # ----------------------------------------------------
        # VALIDASI
        # ----------------------------------------------------

        if (
            not nama
            or not kategori
            or not harga
            or not folder
            or not stok
        ):

            flash(
                "Semua field wajib diisi.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_edit_produk",
                    id=id
                )
            )

        # ----------------------------------------------------
        # KONVERSI HARGA DAN STOK
        # ----------------------------------------------------

        try:

            harga = int(harga)
            stok = int(stok)

        except ValueError:

            flash(
                "Harga dan stok harus berupa angka.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_edit_produk",
                    id=id
                )
            )

        # ----------------------------------------------------
        # VALIDASI NILAI NEGATIF
        # ----------------------------------------------------

        if harga < 0 or stok < 0:

            flash(
                "Harga dan stok tidak boleh negatif.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_edit_produk",
                    id=id
                )
            )

        # ----------------------------------------------------
        # UPDATE DATA PRODUK
        # ----------------------------------------------------

        produk.nama = nama
        produk.kategori = kategori
        produk.harga = harga
        produk.deskripsi = deskripsi
        produk.folder = folder
        produk.stok = stok

        # ----------------------------------------------------
        # HAPUS UKURAN LAMA
        # ----------------------------------------------------

        UkuranProduk.query.filter_by(
            produk_id=produk.id
        ).delete()

        # ----------------------------------------------------
        # TAMBAHKAN UKURAN BARU
        # ----------------------------------------------------

        for ukuran_item in ukuran:

            if ukuran_item.strip():

                ukuran_produk = UkuranProduk(
                    produk_id=produk.id,
                    ukuran=ukuran_item.strip()
                )

                db.session.add(
                    ukuran_produk
                )

        # ----------------------------------------------------
        # SIMPAN PERUBAHAN
        # ----------------------------------------------------

        db.session.commit()

        flash(
            "Produk berhasil diperbarui.",
            "success"
        )

        return redirect(
            url_for("admin_produk")
        )

    # --------------------------------------------------------
    # TAMPILKAN FORM EDIT
    # --------------------------------------------------------

    return render_template(
        "admin/edit_produk.html",

        produk=produk,

        admin_nama=session.get(
            "admin_nama"
        )
    )


# ============================================================
# ADMIN - HAPUS PRODUK
# ============================================================

@app.route(
    "/admin/produk/hapus/<int:id>",
    methods=["POST"]
)
def admin_hapus_produk(id):

    # Proteksi halaman
    if "admin_id" not in session:
        return redirect(
            url_for("admin_login")
        )

    # Cari produk
    produk = Produk.query.get_or_404(id)

    # Hapus produk
    db.session.delete(produk)

    # Simpan perubahan
    db.session.commit()

    flash(
        "Produk berhasil dihapus.",
        "success"
    )

    return redirect(
        url_for("admin_produk")
    )

# ============================================================
# ADMIN PESANAN
# ============================================================

@app.route("/admin/pesanan")
def admin_pesanan():

    # --------------------------------------------------------
    # PROTEKSI ADMIN
    # --------------------------------------------------------

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))


    # --------------------------------------------------------
    # FILTER STATUS
    # --------------------------------------------------------

    status_filter = request.args.get("status")


    # --------------------------------------------------------
    # AMBIL PESANAN DARI DATABASE
    # --------------------------------------------------------

    query = Pesanan.query

    if status_filter:

        # Jika admin memilih filter tertentu,
        # tampilkan sesuai status yang dipilih

        query = query.filter(
            Pesanan.status_pesanan == status_filter
        )

    else:

        # Jika tidak memilih filter,
        # jangan tampilkan pesanan yang sudah selesai

        query = query.filter(
            Pesanan.status_pesanan != "Selesai"
        )


    pesanan_list = query.order_by(
        Pesanan.tanggal_pesanan.desc()
    ).all()


    # --------------------------------------------------------
    # STATISTIK PESANAN
    # --------------------------------------------------------

    total_pesanan = Pesanan.query.count()

    pesanan_diproses = Pesanan.query.filter_by(
        status_pesanan="Diproses"
    ).count()

    pesanan_dikirim = Pesanan.query.filter_by(
        status_pesanan="Diserahkan ke Ekspedisi"
    ).count()

    pesanan_selesai = Pesanan.query.filter_by(
        status_pesanan="Selesai"
    ).count()


    # --------------------------------------------------------
    # TAMPILKAN HALAMAN
    # --------------------------------------------------------

    return render_template(
        "admin/pesanan.html",

        admin_nama=session.get("admin_nama"),

        pesanan_list=pesanan_list,

        total_pesanan=total_pesanan,

        pesanan_diproses=pesanan_diproses,

        pesanan_dikirim=pesanan_dikirim,

        pesanan_selesai=pesanan_selesai
    )
# ============================================================
# ADMIN KIRIM PESANAN
# ============================================================

@app.route(
    "/admin/pesanan/<int:id>/kirim",
    methods=["GET", "POST"]
)
def admin_kirim_pesanan(id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    pesanan = Pesanan.query.get_or_404(id)

    pesanan.status_pesanan = "Diserahkan ke Ekspedisi"

    db.session.commit()

    flash(
        "Pesanan berhasil diserahkan ke ekspedisi.",
        "success"
    )

    return redirect(
        url_for("admin_pesanan")
    )

# ============================================================
# ADMIN PELANGGAN
# ============================================================
# ============================================================
# ADMIN PELANGGAN
# ============================================================

@app.route("/admin/pelanggan")
def admin_pelanggan():

    # --------------------------------------------------------
    # PROTEKSI ADMIN
    # --------------------------------------------------------

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))


    # --------------------------------------------------------
    # AMBIL PELANGGAN YANG MEMILIKI PESANAN SELESAI
    # --------------------------------------------------------

    pelanggan_list = (
        Pelanggan.query
        .join(Pesanan)
        .filter(
            Pesanan.status_pesanan == "Selesai"
        )
        .distinct()
        .order_by(
            Pelanggan.id.desc()
        )
        .all()
    )


    # --------------------------------------------------------
    # STATISTIK
    # --------------------------------------------------------

    total_pelanggan = len(pelanggan_list)

    total_pesanan = Pesanan.query.filter_by(
        status_pesanan="Selesai"
    ).count()


    # --------------------------------------------------------
    # TAMPILKAN HALAMAN
    # --------------------------------------------------------

    return render_template(
        "admin/pelanggan.html",

        admin_nama=session.get("admin_nama"),

        pelanggan_list=pelanggan_list,

        total_pelanggan=total_pelanggan,

        pelanggan_aktif=total_pelanggan,

        total_pesanan=total_pesanan
    )
# ============================================================
# ADMIN DETAIL PELANGGAN
# ============================================================

@app.route("/admin/pelanggan/<int:id>/detail")
def admin_detail_pelanggan(id):

    # --------------------------------------------------------
    # PROTEKSI ADMIN
    # --------------------------------------------------------

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))


    # --------------------------------------------------------
    # AMBIL DATA PELANGGAN
    # --------------------------------------------------------

    pelanggan = Pelanggan.query.get_or_404(id)


    # --------------------------------------------------------
    # AMBIL PESANAN SELESAI MILIK PELANGGAN
    # --------------------------------------------------------

    pesanan_list = Pesanan.query.filter_by(
        pelanggan_id=pelanggan.id,
        status_pesanan="Selesai"
    ).order_by(
        Pesanan.tanggal_pesanan.desc()
    ).all()


    # --------------------------------------------------------
    # TOTAL PEMBELIAN
    # --------------------------------------------------------

    total_pembelian = sum(
        pesanan.total_harga
        for pesanan in pesanan_list
    )


    # --------------------------------------------------------
    # TAMPILKAN DETAIL
    # --------------------------------------------------------

    return render_template(
        "admin/detail_pelanggan.html",

        pelanggan=pelanggan,

        pesanan_list=pesanan_list,

        total_pembelian=total_pembelian,

        admin_nama=session.get("admin_nama")
    )
# ============================================================
# ADMIN DETAIL PESANAN
# ============================================================

@app.route("/admin/pesanan/<int:id>/detail")
def admin_detail_pesanan(id):

    # --------------------------------------------------------
    # PROTEKSI ADMIN
    # --------------------------------------------------------

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))


    # --------------------------------------------------------
    # AMBIL DATA PESANAN
    # --------------------------------------------------------

    pesanan = Pesanan.query.get_or_404(id)


    # --------------------------------------------------------
    # TAMPILKAN DETAIL
    # --------------------------------------------------------

    return render_template(
        "admin/detail_pesanan.html",

        pesanan=pesanan,

        admin_nama=session.get("admin_nama")
    )


# ============================================================
# ADMIN SELESAIKAN PESANAN
# ============================================================

@app.route(
    "/admin/pesanan/<int:id>/selesai",
    methods=["GET", "POST"]
)
def admin_selesaikan_pesanan(id):

    # --------------------------------------------------------
    # PROTEKSI ADMIN
    # --------------------------------------------------------

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))


    # --------------------------------------------------------
    # AMBIL PESANAN
    # --------------------------------------------------------

    pesanan = Pesanan.query.get_or_404(id)


    # --------------------------------------------------------
    # UBAH STATUS
    # --------------------------------------------------------

    pesanan.status_pesanan = "Selesai"

    db.session.commit()


    flash(
        "Pesanan berhasil ditandai sebagai selesai.",
        "success"
    )


    return redirect(
        url_for("admin_pesanan")
    )
# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    # Hapus semua session
    session.clear()

    flash(
        "Anda telah logout.",
        "success"
    )

    return redirect(
        url_for("admin_login")
    )

# ============================================================
# CEK ROUTE
# ============================================================
print("====================================")
print("ROUTE ADMIN DETAIL PELANGGAN:")
print(app.url_map)
print("====================================")
# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)