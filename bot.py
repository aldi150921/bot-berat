"""
Bot Telegram Toko Digital
- /start kirim foto + 3 tombol inline di bubble chat
- Pilih menu -> pesan LAMA otomatis diedit (tidak numpuk)
- Tampilan seperti KYC SHOP bot
"""

import logging
import json
import os
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ══════════════════════════════════════════════
#  KONFIGURASI — EDIT BAGIAN INI
# ══════════════════════════════════════════════

BOT_TOKEN  = os.getenv("BOT_TOKEN",  "8899312905:AAEyEOvHCLapJJLPbT7TLI1U4x040j4haFc")
ADMIN_ID   = int(os.getenv("ADMIN_ID",   "8580173749"))
STORE_NAME = os.getenv("STORE_NAME", "ZaeonX Store")
BANK_INFO  = os.getenv("BANK_INFO",  "DANA 089875561517")

# URL foto welcome (ganti dengan foto toko kamu, atau None)
WELCOME_PHOTO = os.getenv("WELCOME_PHOTO", None)

# ══════════════════════════════════════════════
#  PRODUK
# ══════════════════════════════════════════════

PRODUCTS = {
    "P1": {
        "name": "📘 Ebook SEO Masterclass",
        "desc": "Panduan SEO lengkap dari nol sampai rank #1 Google.\n150+ halaman, update 2025.",
        "price": 99_000,
        "category": "📚 Ebook",
        "file_id": None,
    },
    "P2": {
        "name": "🎨 Pack Template Canva 50pcs",
        "desc": "50 template Canva premium siap pakai.\nFeed Instagram & presentasi bisnis.",
        "price": 75_000,
        "category": "🎨 Template",
        "file_id": None,
    },
    "P3": {
        "name": "💻 Source Code Landing Page",
        "desc": "10 desain landing page HTML/CSS/JS modern & responsif.\nSiap upload ke hosting.",
        "price": 150_000,
        "category": "💻 Source Code",
        "file_id": None,
    },
    "P4": {
        "name": "📊 Spreadsheet Keuangan UMKM",
        "desc": "Template Excel otomatis hitung laba-rugi & arus kas.",
        "price": 45_000,
        "category": "🎨 Template",
        "file_id": None,
    },
    "P5": {
        "name": "🚀 Kursus Digital Marketing",
        "desc": "8 jam video + modul PDF.\nBelajar ads, konten & strategi dari nol.",
        "price": 199_000,
        "category": "🎓 Kursus",
        "file_id": None,
    },
}

CATEGORIES = sorted(set(p["category"] for p in PRODUCTS.values()))

AWAITING_PROOF = 1

# ══════════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════════

DB = "db.json"

def db_load():
    if not os.path.exists(DB):
        return {"users": {}, "orders": {}, "n": 0}
    with open(DB) as f:
        return json.load(f)

def db_save(d):
    with open(DB, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

def db_save_user(uid, username, name):
    d = db_load()
    d["users"][str(uid)] = {"uid": uid, "username": username, "name": name}
    db_save(d)

def db_new_order(uid, username, cart, total):
    d = db_load()
    d["n"] += 1
    oid = f"ORD{d['n']:05d}"
    d["orders"][oid] = {
        "oid": oid, "uid": uid, "username": username,
        "cart": cart, "total": total, "status": "pending",
        "at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    db_save(d)
    return oid

def db_update(oid, status):
    d = db_load()
    if oid in d["orders"]:
        d["orders"][oid]["status"] = status
    db_save(d)

def db_get_order(oid):
    return db_load()["orders"].get(oid)

def db_user_orders(uid):
    return [o for o in db_load()["orders"].values() if o["uid"] == uid]

# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════

def rp(n):
    return "Rp {:,}".format(n).replace(",", ".")

def cart(ctx):
    return ctx.user_data.setdefault("cart", {})

def cart_total(c):
    return sum(PRODUCTS[p]["price"] * q for p, q in c.items() if p in PRODUCTS)

def cart_text(c):
    if not c:
        return "Keranjang kosong."
    rows = ["  {}  x{}  =  {}".format(
        PRODUCTS[p]["name"], q, rp(PRODUCTS[p]["price"] * q))
        for p, q in c.items() if p in PRODUCTS]
    rows.append("\nTotal:  {}".format(rp(cart_total(c))))
    return "\n".join(rows)

# ══════════════════════════════════════════════
#  KEYBOARD MENU UTAMA (3 tombol inline)
# ══════════════════════════════════════════════

def kb_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️  Katalog Produk", callback_data="menu:katalog")],
        [
            InlineKeyboardButton("🛒  Keranjang",    callback_data="menu:keranjang"),
            InlineKeyboardButton("📋  Pesanan",      callback_data="menu:pesanan"),
        ],
        [InlineKeyboardButton("📞  Hubungi Kami",   callback_data="menu:kontak")],
    ])

def kb_main_admin():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️  Katalog Produk", callback_data="menu:katalog")],
        [
            InlineKeyboardButton("🛒  Keranjang",    callback_data="menu:keranjang"),
            InlineKeyboardButton("📋  Pesanan",      callback_data="menu:pesanan"),
        ],
        [InlineKeyboardButton("📞  Hubungi Kami",   callback_data="menu:kontak")],
        [InlineKeyboardButton("⚙️  Admin Panel",    callback_data="menu:admin")],
    ])

def kb_kembali():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("« Kembali ke Menu", callback_data="menu:home")]
    ])

# ══════════════════════════════════════════════
#  TEKS MENU UTAMA
# ══════════════════════════════════════════════

def teks_home(nama):
    return (
        "Halo <b>{}</b>!\n\n"
        "Selamat datang di <b>{}</b>\n"
        "Toko produk digital terpercaya.\n\n"
        "✅ Produk langsung dikirim otomatis\n"
        "✅ Pembayaran aman &amp; terverifikasi\n"
        "✅ Support 24 jam siap membantu\n\n"
        "Pilih menu di bawah:"
    ).format(nama, STORE_NAME)

# ══════════════════════════════════════════════
#  /start — kirim foto + tombol
# ══════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    db_save_user(u.id, u.username or "", u.full_name)
    ctx.user_data["cart"] = {}

    kb = kb_main_admin() if u.id == ADMIN_ID else kb_main()
    teks = teks_home(u.first_name)

if WELCOME_PHOTO:
        msg = await update.message.reply_photo(
            photo=WELCOME_PHOTO,
            caption=teks,
            parse_mode="HTML",
            reply_markup=kb
        )
    else:
        msg = await update.message.reply_text(
            teks,
            parse_mode="HTML",
            reply_markup=kb
        )
    # simpan message_id untuk di-edit nanti
    ctx.user_data["main_msg"] = msg.message_id

# ══════════════════════════════════════════════
#  EDIT PESAN UTAMA (agar tidak numpuk)
# ══════════════════════════════════════════════

async def edit_main(query, ctx, teks, kb):
    """Edit pesan yang sudah ada agar tidak numpuk"""
    try:
        if query.message.photo:
            await query.edit_message_caption(
                caption=teks, parse_mode="Markdown", reply_markup=kb
            )
        else:
            await query.edit_message_text(
                text=teks, parse_mode="Markdown", reply_markup=kb
            )
    except Exception:
        await query.message.reply_text(
            teks, parse_mode="Markdown", reply_markup=kb
        )

# ══════════════════════════════════════════════
#  HANDLER MENU
# ══════════════════════════════════════════════

async def cb_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    action = q.data.split(":", 1)[1]
    u = q.from_user

    # ── HOME ──
    if action == "home":
        kb = kb_main_admin() if u.id == ADMIN_ID else kb_main()
        await edit_main(q, ctx, teks_home(u.first_name), kb)

    # ── KATALOG ──
    elif action == "katalog":
        btns = [[InlineKeyboardButton(cat, callback_data="cat:{}".format(cat))]
                for cat in CATEGORIES]
        btns.append([InlineKeyboardButton("📦 Semua Produk", callback_data="cat:SEMUA")])
        btns.append([InlineKeyboardButton("« Kembali", callback_data="menu:home")])
        await edit_main(q, ctx,
            "🛍️ *Pilih Kategori Produk:*\n\nKami punya berbagai produk digital.",
            InlineKeyboardMarkup(btns)
        )

    # ── KERANJANG ──
    elif action == "keranjang":
        c = cart(ctx)
        teks = "🛒 *Keranjang Belanja*\n\n{}".format(cart_text(c))
        btns = []
        if c:
            btns = [
                [InlineKeyboardButton("✅ Checkout", callback_data="checkout")],
                [InlineKeyboardButton("🗑️ Kosongkan", callback_data="clear")],
            ]
        btns.append([InlineKeyboardButton("« Kembali", callback_data="menu:home")])
        await edit_main(q, ctx, teks, InlineKeyboardMarkup(btns))

    # ── PESANAN ──
    elif action == "pesanan":
        orders = sorted(db_user_orders(u.id), key=lambda x: x["at"], reverse=True)
        if not orders:
            teks = "📋 *Riwayat Pesanan*\n\nBelum ada pesanan."
        else:
            icon = {"pending": "⏳", "verifying": "🔍", "paid": "✅", "rejected": "❌"}
            teks = "📋 *Riwayat Pesanan*\n\n"
            for o in orders[:8]:
                teks += "{} `{}` — {}\n".format(
                    icon.get(o["status"], "❓"), o["oid"], rp(o["total"]))
        await edit_main(q, ctx, teks,
            InlineKeyboardMarkup([[InlineKeyboardButton("« Kembali", callback_data="menu:home")]]))

    # ── KONTAK ──
    elif action == "kontak":
        teks = (
            "📞 *Hubungi Kami*\n\n"
            "Admin: @admin_username\n"
            "Jam layanan: 08.00 - 22.00 WIB\n\n"
            "💳 *Rekening Pembayaran:*\n"
            "`{}`"
        ).format(BANK_INFO)
        await edit_main(q, ctx, teks,
            InlineKeyboardMarkup([[InlineKeyboardButton("« Kembali", callback_data="menu:home")]]))

    # ── ADMIN ──
    elif action == "admin":
        if u.id != ADMIN_ID:
            await q.answer("Akses ditolak!", show_alert=True)
            return
        d = db_load()
        paid = [o for o in d["orders"].values() if o["status"] == "paid"]
        pending = [o for o in d["orders"].values() if o["status"] in ("pending", "verifying")]
        teks = (
            "⚙️ *Admin Panel*\n\n"
            "Pengguna    : {}\n"
            "Total Order : {}\n"
            "Selesai     : {}\n"
            "Pending     : {}\n"
            "Pendapatan  : {}"
        ).format(
            len(d["users"]), len(d["orders"]),
            len(paid), len(pending),
            rp(sum(o["total"] for o in paid))
        )
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Semua Order", callback_data="adm:orders")],
            [InlineKeyboardButton("« Kembali", callback_data="menu:home")],
        ])
        await edit_main(q, ctx, teks, btns)

# ══════════════════════════════════════════════
#  KATEGORI & PRODUK
# ══════════════════════════════════════════════

async def cb_kategori(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cat = q.data.split(":", 1)[1]

    filtered = {k: v for k, v in PRODUCTS.items()
                if cat == "SEMUA" or v["category"] == cat}

    btns = [[InlineKeyboardButton(
                "{} — {}".format(v["name"], rp(v["price"])),
                callback_data="prod:{}".format(k))]
             for k, v in filtered.items()]
    btns.append([InlineKeyboardButton("« Kembali", callback_data="menu:katalog")])

    judul = cat if cat != "SEMUA" else "Semua Produk"
    await edit_main(q, ctx,
        "📂 *{}*\n\nPilih produk:".format(judul),
        InlineKeyboardMarkup(btns)
    )

async def cb_produk(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    pid = q.data.split(":", 1)[1]
    p = PRODUCTS.get(pid)
    if not p:
        await q.answer("Produk tidak ditemukan.", show_alert=True)
        return

    teks = (
        "*{}*\n\n"
        "Kategori : {}\n"
        "Harga    : *{}*\n\n"
        "{}"
    ).format(p["name"], p["category"], rp(p["price"]), p["desc"])

    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Tambah ke Keranjang", callback_data="add:{}".format(pid))],
        [InlineKeyboardButton("« Kembali", callback_data="cat:{}".format(p["category"]))],
    ])
    await edit_main(q, ctx, teks, btns)

async def cb_add(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    pid = q.data.split(":", 1)[1]
    c = cart(ctx)
    c[pid] = c.get(pid, 0) + 1
    p = PRODUCTS.get(pid, {})
    await q.answer("Ditambahkan ke keranjang!", show_alert=False)

# ══════════════════════════════════════════════
#  CLEAR KERANJANG
# ══════════════════════════════════════════════

async def cb_clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    ctx.user_data["cart"] = {}
    await edit_main(q, ctx,
        "🗑️ *Keranjang dikosongkan.*",
        InlineKeyboardMarkup([[InlineKeyboardButton("« Kembali", callback_data="menu:home")]]))

# ══════════════════════════════════════════════
#  CHECKOUT
# ══════════════════════════════════════════════

async def cb_checkout(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    c = dict(cart(ctx))
    if not c:
        await q.answer("Keranjang kosong!", show_alert=True)
        return

    u = q.from_user
    total = cart_total(c)
    oid = db_new_order(u.id, u.username or u.full_name, c, total)
    ctx.user_data["pending_order"] = oid
    ctx.user_data["cart"] = {}

    teks = (
        "📋 *Ringkasan Order*\n\n"
        "{}\n\n"
        "Order ID : `{}`\n"
        "Total    : *{}*\n\n"
        "Transfer ke:\n"
        "`{}`\n"
        "Nominal tepat: *{}*\n\n"
        "Kirim foto bukti transfer di sini sekarang."
    ).format(cart_text(c), oid, rp(total), BANK_INFO, rp(total))

    await edit_main(q, ctx, teks,
        InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="menu:home")]]))
    return AWAITING_PROOF

async def terima_bukti(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    oid = ctx.user_data.get("pending_order")
    if not oid:
        return ConversationHandler.END

    u = update.effective_user
    order = db_get_order(oid)
    db_update(oid, "verifying")

    caption = (
        "BUKTI BAYAR MASUK\n\n"
        "Order  : {}\n"
        "User   : {} (@{})\n"
        "Total  : {}\n"
        "Waktu  : {}"
    ).format(
        oid, u.full_name, u.username or "-",
        rp(order["total"]),
        datetime.now().strftime("%d/%m/%Y %H:%M")
    )

    tombol = InlineKeyboardMarkup([[
        InlineKeyboardButton("ACC", callback_data="acc:{}:{}".format(oid, u.id)),
        InlineKeyboardButton("Tolak", callback_data="tolak:{}:{}".format(oid, u.id)),
    ]])

    if update.message.photo:
        await ctx.bot.send_photo(ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption, reply_markup=tombol)
    elif update.message.document:
        await ctx.bot.send_document(ADMIN_ID,
            document=update.message.document.file_id,
            caption=caption, reply_markup=tombol)
    else:
        await update.message.reply_text("Kirim foto atau file bukti transfer ya.")
        return AWAITING_PROOF

    kb = kb_main_admin() if u.id == ADMIN_ID else kb_main()
    await update.message.reply_text(
        "Bukti diterima!\n\n"
        "Order ID: `{}`\n"
        "Sedang diverifikasi admin.\n"
        "Produk dikirim setelah dikonfirmasi.".format(oid),
        parse_mode="Markdown",
        reply_markup=kb
    )
    return ConversationHandler.END

# ══════════════════════════════════════════════
#  ADMIN ACC / TOLAK
# ══════════════════════════════════════════════

async def cb_acc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID:
        await q.answer("Bukan admin!", show_alert=True)
        return
    await q.answer()
    parts = q.data.split(":")
    oid = parts[1]
    uid = int(parts[2])
    order = db_get_order(oid)
    if not order:
        return
    db_update(oid, "paid")

    for pid in order["cart"]:
        p = PRODUCTS.get(pid)
        if p and p.get("file_id"):
            await ctx.bot.send_document(uid, document=p["file_id"],
                caption="Terima kasih sudah belanja di {}!\n{}".format(
                    STORE_NAME, p["name"]))

    await ctx.bot.send_message(uid,
        "Pembayaran Dikonfirmasi!\n\n"
        "Order ID: `{}`\n"
        "Total: {}\n\n"
        "Produk segera dikirimkan. Terima kasih!".format(oid, rp(order["total"])),
        parse_mode="Markdown")

    cap = (q.message.caption or q.message.text or "") + "\n\nSUDAH DI-ACC"
    try:
        await q.edit_message_caption(cap)
    except Exception:
        pass

async def cb_tolak(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID:
        await q.answer("Bukan admin!", show_alert=True)
        return
    await q.answer()
    parts = q.data.split(":")
    oid = parts[1]
    uid = int(parts[2])
    db_update(oid, "rejected")
    await ctx.bot.send_message(uid,
        "Pembayaran Ditolak\n\n"
        "Order ID: `{}`\n"
        "Bukti tidak valid atau nominal tidak sesuai.\n"
        "Hubungi admin untuk bantuan.".format(oid),
        parse_mode="Markdown")
    cap = (q.message.caption or q.message.text or "") + "\n\nDITOLAK"
    try:
        await q.edit_message_caption(cap)
    except Exception:
        pass

# ══════════════════════════════════════════════
#  ADMIN ORDERS
# ══════════════════════════════════════════════

async def cb_adm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID:
        await q.answer("Akses ditolak!", show_alert=True)
        return
    await q.answer()
    d = db_load()
    orders = sorted(d["orders"].values(), key=lambda x: x["at"], reverse=True)[:15]
    icon = {"pending": "⏳", "verifying": "🔍", "paid": "✅", "rejected": "❌"}
    teks = "📋 *15 Order Terbaru:*\n\n"
    for o in orders:
        teks += "{} `{}` @{} {}\n".format(
            icon.get(o["status"], "❓"), o["oid"],
            o["username"] or "-", rp(o["total"]))
    await edit_main(q, ctx, teks,
        InlineKeyboardMarkup([[InlineKeyboardButton("« Kembali", callback_data="menu:admin")]]))

# ══════════════════════════════════════════════
#  ADMIN UPLOAD FILE
# ══════════════════════════════════════════════

async def admin_file(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if update.message.document:
        fid = update.message.document.file_id
        fn = update.message.document.file_name
    elif update.message.photo:
        fid = update.message.photo[-1].file_id
        fn = "photo"
    else:
        return
    await update.message.reply_text(
        "File: `{}`\n\nfile_id:\n`{}`\n\nSalin ke PRODUCTS di bot.py".format(fn, fid),
        parse_mode="Markdown"
    )

# ══════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler("bot.log")]
)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_checkout = ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_checkout, pattern="^checkout$")],
        states={
            AWAITING_PROOF: [MessageHandler(
                filters.PHOTO | filters.Document.ALL, terima_bukti)]
        },
        fallbacks=[CommandHandler("start", cmd_start)],
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(conv_checkout)

    app.add_handler(CallbackQueryHandler(cb_menu,     pattern="^menu:"))
    app.add_handler(CallbackQueryHandler(cb_kategori, pattern="^cat:"))
    app.add_handler(CallbackQueryHandler(cb_produk,   pattern="^prod:"))
    app.add_handler(CallbackQueryHandler(cb_add,      pattern="^add:"))
    app.add_handler(CallbackQueryHandler(cb_clear,    pattern="^clear$"))
    app.add_handler(CallbackQueryHandler(cb_acc,      pattern="^acc:"))
    app.add_handler(CallbackQueryHandler(cb_tolak,    pattern="^tolak:"))
    app.add_handler(CallbackQueryHandler(cb_adm,      pattern="^adm:"))

    app.add_handler(MessageHandler(
        (filters.Document.ALL | filters.PHOTO) & filters.User(ADMIN_ID), admin_file
    ))

    print("Bot {} aktif!".format(STORE_NAME))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
