"""
Bot Telegram Toko Digital
- /start tampilkan pilihan bahasa dulu
- Setelah pilih bahasa -> foto + 3 tombol inline
- Pilih menu -> pesan LAMA otomatis diedit (tidak numpuk)
- Support: 🇷🇺 Русский | 🇺🇦 Українська | 🇬🇧 English | 🇮🇩 Indonesia | 🇨🇳 中文
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

WELCOME_PHOTO = os.getenv("WELCOME_PHOTO", "AgACAgUAAxkBAAFLk3lqIsOFwMItpCFNV0PYY5t0RSORyQACXhJrG4q-GFXkF28eqyLDpAEAAwIAA3kAAzsE")

# ══════════════════════════════════════════════
#  TERJEMAHAN 5 BAHASA
# ══════════════════════════════════════════════

LANG = {
    "ru": {
        "welcome": (
            "Привет <b>{}</b> 👋\n\n"
            "Добро пожаловать в <b>{}</b>\n"
            "Быстрый и надёжный KYC сервис.\n\n"
            "✅ Товары доставляются мгновенно и автоматически\n"
            "✅ Безопасная и проверенная оплата\n"
            "✅ Поддержка 24/7 готова помочь\n\n"
            "Выберите меню ниже:"
        ),
        "katalog":    "🛍️  Каталог",
        "keranjang":  "🛒  Корзина",
        "pesanan":    "📋  Заказы",
        "kontak":     "📞  Связаться с нами",
        "admin":      "⚙️  Панель администратора",
        "kembali":    "« Назад в меню",
        "pilih_kat":  "🛍️ *Выберите категорию товара:*",
        "semua":      "📦 Все товары",
        "back":       "« Назад",
        "cart_title": "🛒 *Корзина*\n\n{}",
        "cart_empty": "Корзина пуста.",
        "checkout":   "✅ Оформить заказ",
        "kosongkan":  "🗑️ Очистить",
        "order_hist": "📋 *История заказов*\n\nЗаказов пока нет.",
        "order_list": "📋 *История заказов*\n\n",
        "kontak_teks": (
            "📞 *Связаться с нами*\n\n"
            "Админ: @admin_username\n"
            "Время работы: 08.00 - 22.00 WIB\n\n"
            "💳 *Реквизиты оплаты:*\n"
            "`{}`"
        ),
        "checkout_teks": (
            "📋 *Сводка заказа*\n\n"
            "{}\n\n"
            "ID заказа : `{}`\n"
            "Итого     : *{}*\n\n"
            "Перевод на:\n"
            "`{}`\n"
            "Сумма точно: *{}*\n\n"
            "Отправьте фото подтверждения оплаты сюда."
        ),
        "batal":       "❌ Отмена",
        "bukti_ok":    "Подтверждение получено!\n\nID заказа: `{}`\nПроверяется администратором.\nТовар будет отправлен после подтверждения.",
        "send_proof":  "Отправьте фото или файл подтверждения оплаты.",
        "cart_cleared": "🗑️ *Корзина очищена.*",
        "added":       "Добавлено в корзину!",
        "lang_btn":    "🌐 Язык",
    },
    "uk": {
        "welcome": (
            "Привіт <b>{}</b> 👋\n\n"
            "Ласкаво просимо до <b>{}</b>\n"
            "Швидкий та надійний KYC сервіс.\n\n"
            "✅ Товари доставляються миттєво та автоматично\n"
            "✅ Безпечна та перевірена оплата\n"
            "✅ Підтримка 24/7 готова допомогти\n\n"
            "Оберіть меню нижче:"
        ),
        "katalog":    "🛍️  Каталог",
        "keranjang":  "🛒  Кошик",
        "pesanan":    "📋  Замовлення",
        "kontak":     "📞  Зв'язатися з нами",
        "admin":      "⚙️  Панель адміністратора",
        "kembali":    "« Назад до меню",
        "pilih_kat":  "🛍️ *Оберіть категорію товару:*",
        "semua":      "📦 Усі товари",
        "back":       "« Назад",
        "cart_title": "🛒 *Кошик*\n\n{}",
        "cart_empty": "Кошик порожній.",
        "checkout":   "✅ Оформити замовлення",
        "kosongkan":  "🗑️ Очистити",
        "order_hist": "📋 *Історія замовлень*\n\nЗамовлень поки немає.",
        "order_list": "📋 *Історія замовлень*\n\n",
        "kontak_teks": (
            "📞 *Зв'язатися з нами*\n\n"
            "Адмін: @admin_username\n"
            "Години роботи: 08.00 - 22.00 WIB\n\n"
            "💳 *Реквізити оплати:*\n"
            "`{}`"
        ),
        "checkout_teks": (
            "📋 *Підсумок замовлення*\n\n"
            "{}\n\n"
            "ID замовлення : `{}`\n"
            "Разом         : *{}*\n\n"
            "Переказ на:\n"
            "`{}`\n"
            "Сума точно: *{}*\n\n"
            "Надішліть фото підтвердження оплати сюди."
        ),
        "batal":       "❌ Скасувати",
        "bukti_ok":    "Підтвердження отримано!\n\nID замовлення: `{}`\nПеревіряється адміністратором.\nТовар буде надіслано після підтвердження.",
        "send_proof":  "Надішліть фото або файл підтвердження оплати.",
        "cart_cleared": "🗑️ *Кошик очищено.*",
        "added":       "Додано до кошика!",
        "lang_btn":    "🌐 Мова",
    },
    "en": {
        "welcome": (
            "Hello <b>{}</b> 👋\n\n"
            "Welcome to <b>{}</b>\n"
            "Fast &amp; Trusted KYC Service.\n\n"
            "✅ Products delivered instantly &amp; automatically\n"
            "✅ Safe &amp; verified payments\n"
            "✅ 24/7 support ready to help\n\n"
            "Choose a menu below:"
        ),
        "katalog":    "🛍️  Catalog",
        "keranjang":  "🛒  Cart",
        "pesanan":    "📋  Orders",
        "kontak":     "📞  Contact Us",
        "admin":      "⚙️  Admin Panel",
        "kembali":    "« Back to Menu",
        "pilih_kat":  "🛍️ *Choose Product Category:*",
        "semua":      "📦 All Products",
        "back":       "« Back",
        "cart_title": "🛒 *Shopping Cart*\n\n{}",
        "cart_empty": "Cart is empty.",
        "checkout":   "✅ Checkout",
        "kosongkan":  "🗑️ Clear Cart",
        "order_hist": "📋 *Order History*\n\nNo orders yet.",
        "order_list": "📋 *Order History*\n\n",
        "kontak_teks": (
            "📞 *Contact Us*\n\n"
            "Admin: @admin_username\n"
            "Hours: 08.00 - 22.00 WIB\n\n"
            "💳 *Payment Account:*\n"
            "`{}`"
        ),
        "checkout_teks": (
            "📋 *Order Summary*\n\n"
            "{}\n\n"
            "Order ID : `{}`\n"
            "Total    : *{}*\n\n"
            "Transfer to:\n"
            "`{}`\n"
            "Exact amount: *{}*\n\n"
            "Send proof of payment photo here."
        ),
        "batal":       "❌ Cancel",
        "bukti_ok":    "Proof received!\n\nOrder ID: `{}`\nBeing verified by admin.\nProduct sent after confirmation.",
        "send_proof":  "Please send a photo or file as proof of payment.",
        "cart_cleared": "🗑️ *Cart cleared.*",
        "added":       "Added to cart!",
        "lang_btn":    "🌐 Language",
    },
    "id": {
        "welcome": (
            "Halo <b>{}</b> 👋\n\n"
            "Selamat datang di <b>{}</b>\n"
            "Layanan KYC Cepat &amp; Terpercaya.\n\n"
            "✅ Produk terkirim instan &amp; otomatis\n"
            "✅ Pembayaran aman &amp; terverifikasi\n"
            "✅ Support 24/7 siap membantu\n\n"
            "Pilih menu di bawah:"
        ),
        "katalog":    "🛍️  Katalog",
        "keranjang":  "🛒  Keranjang",
        "pesanan":    "📋  Pesanan",
        "kontak":     "📞  Hubungi Kami",
        "admin":      "⚙️  Admin Panel",
        "kembali":    "« Kembali ke Menu",
        "pilih_kat":  "🛍️ *Pilih Kategori Produk:*",
        "semua":      "📦 Semua Produk",
        "back":       "« Kembali",
        "cart_title": "🛒 *Keranjang Belanja*\n\n{}",
        "cart_empty": "Keranjang kosong.",
        "checkout":   "✅ Checkout",
        "kosongkan":  "🗑️ Kosongkan",
        "order_hist": "📋 *Riwayat Pesanan*\n\nBelum ada pesanan.",
        "order_list": "📋 *Riwayat Pesanan*\n\n",
        "kontak_teks": (
            "📞 *Hubungi Kami*\n\n"
            "Admin: @admin_username\n"
            "Jam layanan: 08.00 - 22.00 WIB\n\n"
            "💳 *Rekening Pembayaran:*\n"
            "`{}`"
        ),
        "checkout_teks": (
            "📋 *Ringkasan Order*\n\n"
            "{}\n\n"
            "Order ID : `{}`\n"
            "Total    : *{}*\n\n"
            "Transfer ke:\n"
            "`{}`\n"
            "Nominal tepat: *{}*\n\n"
            "Kirim foto bukti transfer di sini sekarang."
        ),
        "batal":       "❌ Batal",
        "bukti_ok":    "Bukti diterima!\n\nOrder ID: `{}`\nSedang diverifikasi admin.\nProduk dikirim setelah dikonfirmasi.",
        "send_proof":  "Kirim foto atau file bukti transfer ya.",
        "cart_cleared": "🗑️ *Keranjang dikosongkan.*",
        "added":       "Ditambahkan ke keranjang!",
        "lang_btn":    "🌐 Bahasa",
    },
    "zh": {
        "welcome": (
            "你好 <b>{}</b> 👋\n\n"
            "欢迎来到 <b>{}</b>\n"
            "快速可靠的 KYC 服务。\n\n"
            "✅ 产品即时自动发货\n"
            "✅ 安全可靠的支付\n"
            "✅ 24/7 全天候支持\n\n"
            "请选择下方菜单："
        ),
        "katalog":    "🛍️  产品目录",
        "keranjang":  "🛒  购物车",
        "pesanan":    "📋  订单",
        "kontak":     "📞  联系我们",
        "admin":      "⚙️  管理面板",
        "kembali":    "« 返回菜单",
        "pilih_kat":  "🛍️ *选择产品类别：*",
        "semua":      "📦 全部产品",
        "back":       "« 返回",
        "cart_title": "🛒 *购物车*\n\n{}",
        "cart_empty": "购物车为空。",
        "checkout":   "✅ 结账",
        "kosongkan":  "🗑️ 清空购物车",
        "order_hist": "📋 *订单历史*\n\n暂无订单。",
        "order_list": "📋 *订单历史*\n\n",
        "kontak_teks": (
            "📞 *联系我们*\n\n"
            "管理员: @admin_username\n"
            "服务时间: 08.00 - 22.00 WIB\n\n"
            "💳 *付款账户：*\n"
            "`{}`"
        ),
        "checkout_teks": (
            "📋 *订单摘要*\n\n"
            "{}\n\n"
            "订单编号 : `{}`\n"
            "总计     : *{}*\n\n"
            "转账至：\n"
            "`{}`\n"
            "精确金额: *{}*\n\n"
            "请在此发送付款凭证照片。"
        ),
        "batal":       "❌ 取消",
        "bukti_ok":    "凭证已收到！\n\n订单编号: `{}`\n正由管理员核实中。\n确认后将发送产品。",
        "send_proof":  "请发送付款凭证照片或文件。",
        "cart_cleared": "🗑️ *购物车已清空。*",
        "added":       "已加入购物车！",
        "lang_btn":    "🌐 语言",
    },
}

def t(ctx, key):
    """Ambil terjemahan berdasarkan bahasa user"""
    lang = ctx.user_data.get("lang", "id")
    return LANG.get(lang, LANG["id"]).get(key, LANG["id"].get(key, key))

# ══════════════════════════════════════════════
#  PRODUK
# ══════════════════════════════════════════════

PRODUCTS = {
    "P1": {
        "name": "🏛️ Bank",
        "desc": "Panduan SEO lengkap dari nol sampai rank #1 Google.\n150+ halaman, update 2025.",
        "price": 99_000,
        "category": "🏛️ Bank",
        "file_id": None,
    },
    "P2": {
        "name": "💲 Exchange",
        "desc": "50 template Canva premium siap pakai.\nFeed Instagram & presentasi bisnis.",
        "price": 75_000,
        "category": "💲 Exchange",
        "file_id": None,
    },
    "P3": {
        "name": "🪪 Document",
        "desc": "10 desain landing page HTML/CSS/JS modern & responsif.\nSiap upload ke hosting.",
        "price": 150_000,
        "category": "🪪 Document",
        "file_id": None,
    },
    "P4": {
        "name": "☁️ Personal Proxy",
        "desc": "Template Excel otomatis hitung laba-rugi & arus kas.",
        "price": 45_000,
        "category": "☁️ Personal Proxy",
        "file_id": None,
    },
    "P5": {
        "name": "🔗 Verify By Link",
        "desc": "8 jam video + modul PDF.\nBelajar ads, konten & strategi dari nol.",
        "price": 199_000,
        "category": "🔗 Verify By Link",
        "file_id": None,
    },
}

CATEGORIES = [
    "🏛️ Bank",
    "💲 Exchange",
    "🪪 Document",
    "☁️ Personal Proxy",
    "🔗 Verify By Link",
]

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

def cart_text(c, ctx):
    if not c:
        return t(ctx, "cart_empty")
    rows = ["  {}  x{}  =  {}".format(
        PRODUCTS[p]["name"], q, rp(PRODUCTS[p]["price"] * q))
        for p, q in c.items() if p in PRODUCTS]
    rows.append("\nTotal:  {}".format(rp(cart_total(c))))
    return "\n".join(rows)

# ══════════════════════════════════════════════
#  KEYBOARD PILIH BAHASA
# ══════════════════════════════════════════════

def kb_language():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇷🇺 Русский",    callback_data="lang:ru")],
        [InlineKeyboardButton("🇺🇦 Українська", callback_data="lang:uk")],
        [InlineKeyboardButton("🇬🇧 English",    callback_data="lang:en")],
        [InlineKeyboardButton("🇮🇩 Indonesia",  callback_data="lang:id")],
        [InlineKeyboardButton("🇨🇳 中文",        callback_data="lang:zh")],
    ])

# ══════════════════════════════════════════════
#  KEYBOARD MENU UTAMA
# ══════════════════════════════════════════════

def kb_main(ctx):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(ctx, "katalog"),   callback_data="menu:katalog")],
        [
            InlineKeyboardButton(t(ctx, "keranjang"), callback_data="menu:keranjang"),
            InlineKeyboardButton(t(ctx, "pesanan"),   callback_data="menu:pesanan"),
        ],
        [InlineKeyboardButton(t(ctx, "kontak"),    callback_data="menu:kontak")],
        [InlineKeyboardButton(t(ctx, "lang_btn"),  callback_data="menu:lang")],
    ])

def kb_main_admin(ctx):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(ctx, "katalog"),   callback_data="menu:katalog")],
        [
            InlineKeyboardButton(t(ctx, "keranjang"), callback_data="menu:keranjang"),
            InlineKeyboardButton(t(ctx, "pesanan"),   callback_data="menu:pesanan"),
        ],
        [InlineKeyboardButton(t(ctx, "kontak"),    callback_data="menu:kontak")],
        [InlineKeyboardButton(t(ctx, "lang_btn"),  callback_data="menu:lang")],
        [InlineKeyboardButton(t(ctx, "admin"),     callback_data="menu:admin")],
    ])

# ══════════════════════════════════════════════
#  EDIT PESAN UTAMA (agar tidak numpuk)
# ══════════════════════════════════════════════

async def edit_main(query, ctx, teks, kb):
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
#  /start — tampilkan pilih bahasa dulu
# ══════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    db_save_user(u.id, u.username or "", u.full_name)
    ctx.user_data["cart"] = {}

    teks = "🌐 Выберите язык / Оберіть мову / Select language / Pilih Bahasa / 选择语言:"

    if WELCOME_PHOTO:
        msg = await update.message.reply_photo(
            photo=WELCOME_PHOTO,
            caption=teks,
            reply_markup=kb_language()
        )
    else:
        msg = await update.message.reply_text(
            teks,
            reply_markup=kb_language()
        )
    ctx.user_data["main_msg"] = msg.message_id

# ══════════════════════════════════════════════
#  HANDLER PILIH BAHASA
# ══════════════════════════════════════════════

async def cb_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split(":", 1)[1]
    ctx.user_data["lang"] = lang

    u = q.from_user
    kb = kb_main_admin(ctx) if u.id == ADMIN_ID else kb_main(ctx)
    teks = LANG[lang]["welcome"].format(u.first_name, STORE_NAME)

    try:
        if q.message.photo:
            await q.edit_message_caption(
                caption=teks, parse_mode="HTML", reply_markup=kb
            )
        else:
            await q.edit_message_text(
                text=teks, parse_mode="HTML", reply_markup=kb
            )
    except Exception:
        await q.message.reply_text(teks, parse_mode="HTML", reply_markup=kb)

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
        kb = kb_main_admin(ctx) if u.id == ADMIN_ID else kb_main(ctx)
        teks = LANG.get(ctx.user_data.get("lang","id"), LANG["id"])["welcome"].format(u.first_name, STORE_NAME)
        try:
            if q.message.photo:
                await q.edit_message_caption(caption=teks, parse_mode="HTML", reply_markup=kb)
            else:
                await q.edit_message_text(text=teks, parse_mode="HTML", reply_markup=kb)
        except Exception:
            await q.message.reply_text(teks, parse_mode="HTML", reply_markup=kb)

    # ── GANTI BAHASA ──
    elif action == "lang":
        teks = "🌐 Выберите язык / Оберіть мову / Select language / Pilih Bahasa / 选择语言:"
        await edit_main(q, ctx, teks, kb_language())

    # ── KATALOG ──
    elif action == "katalog":
        btns = [[InlineKeyboardButton(cat, callback_data="cat:{}".format(cat))]
                for cat in CATEGORIES]
        btns.append([InlineKeyboardButton(t(ctx, "back"),  callback_data="menu:home")])
        await edit_main(q, ctx, t(ctx, "pilih_kat"), InlineKeyboardMarkup(btns))

    # ── KERANJANG ──
    elif action == "keranjang":
        c = cart(ctx)
        teks = t(ctx, "cart_title").format(cart_text(c, ctx))
        btns = []
        if c:
            btns = [
                [InlineKeyboardButton(t(ctx, "checkout"),  callback_data="checkout")],
                [InlineKeyboardButton(t(ctx, "kosongkan"), callback_data="clear")],
            ]
        btns.append([InlineKeyboardButton(t(ctx, "back"), callback_data="menu:home")])
        await edit_main(q, ctx, teks, InlineKeyboardMarkup(btns))

    # ── PESANAN ──
    elif action == "pesanan":
        orders = sorted(db_user_orders(u.id), key=lambda x: x["at"], reverse=True)
        if not orders:
            teks = t(ctx, "order_hist")
        else:
            icon = {"pending": "⏳", "verifying": "🔍", "paid": "✅", "rejected": "❌"}
            teks = t(ctx, "order_list")
            for o in orders[:8]:
                teks += "{} `{}` — {}\n".format(
                    icon.get(o["status"], "❓"), o["oid"], rp(o["total"]))
        await edit_main(q, ctx, teks,
            InlineKeyboardMarkup([[InlineKeyboardButton(t(ctx, "back"), callback_data="menu:home")]]))

    # ── KONTAK ──
    elif action == "kontak":
        teks = t(ctx, "kontak_teks").format(BANK_INFO)
        await edit_main(q, ctx, teks,
            InlineKeyboardMarkup([[InlineKeyboardButton(t(ctx, "back"), callback_data="menu:home")]]))

    # ── ADMIN ──
    elif action == "admin":
        if u.id != ADMIN_ID:
            await q.answer("Akses ditolak!", show_alert=True)
            return
        d = db_load()
        paid    = [o for o in d["orders"].values() if o["status"] == "paid"]
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
            [InlineKeyboardButton(t(ctx, "back"),   callback_data="menu:home")],
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
    btns.append([InlineKeyboardButton(t(ctx, "back"), callback_data="menu:katalog")])

    judul = cat if cat != "SEMUA" else t(ctx, "semua")
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
        [InlineKeyboardButton("🛒 " + t(ctx, "checkout").replace("✅ ",""), callback_data="add:{}".format(pid))],
        [InlineKeyboardButton(t(ctx, "back"), callback_data="cat:{}".format(p["category"]))],
    ])
    await edit_main(q, ctx, teks, btns)

# ══════════════════════════════════════════════
#  ADD TO CART
# ══════════════════════════════════════════════

async def cb_add(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    pid = q.data.split(":", 1)[1]
    c = cart(ctx)
    c[pid] = c.get(pid, 0) + 1
    await q.answer(t(ctx, "added"), show_alert=False)

# ══════════════════════════════════════════════
#  CLEAR KERANJANG
# ══════════════════════════════════════════════

async def cb_clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    ctx.user_data["cart"] = {}
    await edit_main(q, ctx,
        t(ctx, "cart_cleared"),
        InlineKeyboardMarkup([[InlineKeyboardButton(t(ctx, "back"), callback_data="menu:home")]]))

# ══════════════════════════════════════════════
#  CHECKOUT
# ══════════════════════════════════════════════

async def cb_checkout(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    c = dict(cart(ctx))
    if not c:
        await q.answer(t(ctx, "cart_empty"), show_alert=True)
        return

    u = q.from_user
    total = cart_total(c)
    oid = db_new_order(u.id, u.username or u.full_name, c, total)
    ctx.user_data["pending_order"] = oid
    ctx.user_data["cart"] = {}

    teks = t(ctx, "checkout_teks").format(
        cart_text(c, ctx), oid, rp(total), BANK_INFO, rp(total)
    )

    await edit_main(q, ctx, teks,
        InlineKeyboardMarkup([[InlineKeyboardButton(t(ctx, "batal"), callback_data="menu:home")]]))
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
        InlineKeyboardButton("ACC",  callback_data="acc:{}:{}".format(oid, u.id)),
        InlineKeyboardButton("Tolak",callback_data="tolak:{}:{}".format(oid, u.id)),
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
        await update.message.reply_text(t(ctx, "send_proof"))
        return AWAITING_PROOF

    kb = kb_main_admin(ctx) if u.id == ADMIN_ID else kb_main(ctx)
    await update.message.reply_text(
        t(ctx, "bukti_ok").format(oid),
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
        "✅ Pembayaran Dikonfirmasi!\n\n"
        "Order ID: `{}`\n"
        "Total: {}\n\n"
        "Produk segera dikirimkan. Terima kasih!".format(oid, rp(order["total"])),
        parse_mode="Markdown")

    cap = (q.message.caption or q.message.text or "") + "\n\n✅ SUDAH DI-ACC"
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
        "❌ Pembayaran Ditolak\n\n"
        "Order ID: `{}`\n"
        "Bukti tidak valid atau nominal tidak sesuai.\n"
        "Hubungi admin untuk bantuan.".format(oid),
        parse_mode="Markdown")
    cap = (q.message.caption or q.message.text or "") + "\n\n❌ DITOLAK"
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
        InlineKeyboardMarkup([[InlineKeyboardButton(t(ctx, "back"), callback_data="menu:admin")]]))

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

    app.add_handler(CallbackQueryHandler(cb_lang,     pattern="^lang:"))
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
