from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Produk(db.Model):
    __tablename__ = "produk"

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50), nullable=False)
    harga = db.Column(db.Integer, nullable=False)
    deskripsi = db.Column(db.Text)
    folder = db.Column(db.String(100), nullable=False)
    stok = db.Column(db.Integer, default=0)

    ukuran_produk = db.relationship(
        "UkuranProduk",
        backref="produk",
        lazy=True,
        cascade="all, delete-orphan"
    )


class UkuranProduk(db.Model):
    __tablename__ = "ukuran_produk"

    id = db.Column(db.Integer, primary_key=True)
    produk_id = db.Column(
        db.Integer,
        db.ForeignKey("produk.id"),
        nullable=False
    )
    ukuran = db.Column(db.String(5), nullable=False)

class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    produk_id = db.Column(
        db.Integer,
        db.ForeignKey("produk.id"),
        nullable=False
    )
    ukuran = db.Column(db.String(10), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    produk = db.relationship("Produk", backref="cart_items")

class Admin(db.Model):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# ============================================================
# PELANGGAN
# ============================================================

class Pelanggan(db.Model):
    __tablename__ = "pelanggan"

    id = db.Column(db.Integer, primary_key=True)

    nama = db.Column(
        db.String(100),
        nullable=False
    )

    alamat = db.Column(
        db.Text,
        nullable=False
    )

    no_hp = db.Column(
        db.String(20),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        nullable=False
    )

    kode_pos = db.Column(
        db.String(10)
    )

    kota = db.Column(
        db.String(100)
    )

    provinsi = db.Column(
        db.String(100)
    )

    pesanan = db.relationship(
        "Pesanan",
        backref="pelanggan",
        lazy=True
    )


# ============================================================
# PESANAN
# ============================================================

class Pesanan(db.Model):
    __tablename__ = "pesanan"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    kode_pesanan = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    pelanggan_id = db.Column(
        db.Integer,
        db.ForeignKey("pelanggan.id"),
        nullable=False
    )

    # ========================================================
    # DEVICE ID
    # Digunakan untuk membedakan riwayat setiap device/browser
    # ========================================================

    device_id = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    total_harga = db.Column(
        db.Integer,
        nullable=False
    )

    metode_pembayaran = db.Column(
        db.String(50),
        nullable=False
    )

    status_pesanan = db.Column(
        db.String(50),
        nullable=False,
        default="Diproses"
    )

    tanggal_pesanan = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    ekspedisi = db.Column(
        db.String(100)
    )

    no_resi = db.Column(
        db.String(100)
    )

    detail_pesanan = db.relationship(
        "DetailPesanan",
        backref="pesanan",
        lazy=True,
        cascade="all, delete-orphan"
    )


# ============================================================
# DETAIL PESANAN
# ============================================================

class DetailPesanan(db.Model):
    __tablename__ = "detail_pesanan"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pesanan_id = db.Column(
        db.Integer,
        db.ForeignKey("pesanan.id"),
        nullable=False
    )

    produk_id = db.Column(
        db.Integer,
        db.ForeignKey("produk.id"),
        nullable=False
    )

    ukuran = db.Column(
        db.String(10)
    )

    jumlah = db.Column(
        db.Integer,
        nullable=False
    )

    harga = db.Column(
        db.Integer,
        nullable=False
    )

    subtotal = db.Column(
        db.Integer,
        nullable=False
    )

    produk = db.relationship(
        "Produk",
        backref="detail_pesanan"
    )