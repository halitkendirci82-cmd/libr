import gradio as gr
import requests

API = "http://localhost:8000"

def fmt(ok, msg):
    return f"✅ {msg}" if ok else f"❌ {msg}"

# ─── refresh functions ───
def refresh_books():
    try:
        books = requests.get(f"{API}/books").json()
        return [[b["id"], b["title"], b["author"], b["isbn"],
                 b["genre"], b["year"] or "—", b["copies"], b["available"]] for b in books]
    except:
        return []

def refresh_members():
    try:
        members = requests.get(f"{API}/members").json()
        return [[m["id"], m["name"], m["email"], m["phone"] or "—",
                 str(m["joined_at"])[:10]] for m in members]
    except:
        return []

def refresh_loans():
    try:
        loans = requests.get(f"{API}/loans").json()
        return [[l["id"], l["book_title"], l["member_name"],
                 str(l["borrowed_at"])[:10],
                 str(l["returned_at"])[:10] if l["returned_at"] else "Aktif 📖"] for l in loans]
    except:
        return []

def get_stats():
    try:
        s = requests.get(f"{API}/stats").json()
        return (f"📚 {s['total_books']} kitap",
                f"👥 {s['total_members']} üye",
                f"📖 {s['active_loans']} aktif ödünç",
                f"🗂 {s['total_copies']} kopya")
    except:
        return "—", "—", "—", "—"

def book_choices():
    try:
        books = requests.get(f"{API}/books").json()
        return [(f"{b['title']} (#{b['id']}) — {b['available']} kopya", b["id"]) for b in books]
    except:
        return []

def member_choices():
    try:
        members = requests.get(f"{API}/members").json()
        return [(f"{m['name']} (#{m['id']})", m["id"]) for m in members]
    except:
        return []

def loan_choices():
    try:
        loans = requests.get(f"{API}/loans").json()
        return [(f"#{l['id']} — {l['book_title']} → {l['member_name']}", l["id"])
                for l in loans if not l["returned_at"]]
    except:
        return []

# ─── book actions ───
def add_book(title, author, isbn, genre, year, copies):
    if not title or not author or not isbn:
        return "⚠️ Başlık, yazar ve ISBN zorunlu!", refresh_books()
    try:
        r = requests.post(f"{API}/books", json={
            "title": title, "author": author, "isbn": isbn,
            "genre": genre,
            "year": int(year) if year else None,
            "copies": int(copies) if copies else 1
        })
        ok = r.status_code == 201
        msg = f"'{title}' eklendi" if ok else r.json().get("detail", "Hata")
        return fmt(ok, msg), refresh_books()
    except Exception as e:
        return fmt(False, str(e)), refresh_books()

def delete_book(book_id):
    if not book_id:
        return "⚠️ ID girin", refresh_books()
    try:
        r = requests.delete(f"{API}/books/{int(book_id)}")
        return fmt(r.status_code == 200, "Kitap silindi"), refresh_books()
    except Exception as e:
        return fmt(False, str(e)), refresh_books()

# ─── member actions ───
def add_member(name, email, phone):
    if not name or not email:
        return "⚠️ Ad ve e-posta zorunlu!", refresh_members()
    try:
        r = requests.post(f"{API}/members", json={"name": name, "email": email, "phone": phone})
        ok = r.status_code == 201
        msg = f"'{name}' eklendi" if ok else r.json().get("detail", "Hata")
        return fmt(ok, msg), refresh_members()
    except Exception as e:
        return fmt(False, str(e)), refresh_members()

def delete_member(member_id):
    if not member_id:
        return "⚠️ ID girin", refresh_members()
    try:
        r = requests.delete(f"{API}/members/{int(member_id)}")
        return fmt(r.status_code == 200, "Üye silindi"), refresh_members()
    except Exception as e:
        return fmt(False, str(e)), refresh_members()

# ─── loan actions ───
def borrow(book_id, member_id):
    if not book_id or not member_id:
        return "⚠️ Kitap ve üye seçin", refresh_loans(), gr.Dropdown(choices=loan_choices())
    try:
        r = requests.post(f"{API}/loans", json={"book_id": book_id, "member_id": member_id})
        ok = r.status_code == 201
        msg = "Ödünç verildi" if ok else r.json().get("detail", "Hata")
        return fmt(ok, msg), refresh_loans(), gr.Dropdown(choices=loan_choices())
    except Exception as e:
        return fmt(False, str(e)), refresh_loans(), gr.Dropdown(choices=loan_choices())

def return_book(loan_id):
    if not loan_id:
        return "⚠️ Kayıt seçin", refresh_loans(), gr.Dropdown(choices=loan_choices())
    try:
        r = requests.put(f"{API}/loans/{loan_id}/return")
        ok = r.status_code == 200
        msg = "İade alındı" if ok else r.json().get("detail", "Hata")
        return fmt(ok, msg), refresh_loans(), gr.Dropdown(choices=loan_choices())
    except Exception as e:
        return fmt(False, str(e)), refresh_loans(), gr.Dropdown(choices=loan_choices())

def refresh_dropdowns():
    return gr.Dropdown(choices=book_choices()), gr.Dropdown(choices=member_choices()), gr.Dropdown(choices=loan_choices())

# ─── UI ───
with gr.Blocks(title="Kütüphane Yönetim Sistemi") as demo:

    gr.Markdown("# 📚 Kütüphane Yönetim Sistemi")

    with gr.Row():
        s1 = gr.Textbox(label="Kitaplar",  interactive=False)
        s2 = gr.Textbox(label="Üyeler",    interactive=False)
        s3 = gr.Textbox(label="Ödünçler",  interactive=False)
        s4 = gr.Textbox(label="Kopyalar",  interactive=False)

    stat_btn = gr.Button("↻ İstatistik Yenile", variant="secondary")
    stat_btn.click(fn=get_stats, outputs=[s1, s2, s3, s4])

    with gr.Tabs():

        # ── KİTAPLAR ──
        with gr.Tab("📖 Kitaplar"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Kitap Ekle")
                    b_title  = gr.Textbox(label="Başlık *")
                    b_author = gr.Textbox(label="Yazar *")
                    b_isbn   = gr.Textbox(label="ISBN *")
                    b_genre  = gr.Dropdown(
                        label="Tür",
                        choices=["Genel","Roman","Bilim","Tarih","Felsefe","Teknoloji","Şiir","Biyografi"],
                        value="Genel"
                    )
                    b_year   = gr.Number(label="Yıl", precision=0)
                    b_copies = gr.Number(label="Kopya Sayısı", precision=0, value=1)
                    add_book_btn = gr.Button("➕ Kitap Ekle", variant="primary")
                    book_status  = gr.Textbox(label="Durum", interactive=False)

                with gr.Column(scale=2):
                    gr.Markdown("### Koleksiyon")
                    book_table = gr.Dataframe(
                        headers=["#", "Başlık", "Yazar", "ISBN", "Tür", "Yıl", "Kopya", "Mevcut"],
                        datatype=["number","str","str","str","str","str","number","number"],
                        interactive=False
                    )
                    refresh_books_btn = gr.Button("↻ Listeyi Yenile", variant="secondary")
                    b_del_id  = gr.Number(label="Silinecek Kitap ID (#)", precision=0)
                    del_book_btn = gr.Button("🗑 Kitap Sil", variant="stop")

            add_book_btn.click(fn=add_book,
                inputs=[b_title, b_author, b_isbn, b_genre, b_year, b_copies],
                outputs=[book_status, book_table])
            del_book_btn.click(fn=delete_book,
                inputs=[b_del_id],
                outputs=[book_status, book_table])
            refresh_books_btn.click(fn=refresh_books, outputs=book_table)

        # ── ÜYELER ──
        with gr.Tab("👥 Üyeler"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Üye Ekle")
                    m_name  = gr.Textbox(label="Ad Soyad *")
                    m_email = gr.Textbox(label="E-posta *")
                    m_phone = gr.Textbox(label="Telefon")
                    add_mem_btn = gr.Button("➕ Üye Ekle", variant="primary")
                    mem_status  = gr.Textbox(label="Durum", interactive=False)

                with gr.Column(scale=2):
                    gr.Markdown("### Üye Listesi")
                    mem_table = gr.Dataframe(
                        headers=["#", "Ad", "E-posta", "Telefon", "Katılım"],
                        datatype=["number","str","str","str","str"],
                        interactive=False
                    )
                    refresh_mem_btn = gr.Button("↻ Listeyi Yenile", variant="secondary")
                    m_del_id  = gr.Number(label="Silinecek Üye ID (#)", precision=0)
                    del_mem_btn = gr.Button("🗑 Üye Sil", variant="stop")

            add_mem_btn.click(fn=add_member,
                inputs=[m_name, m_email, m_phone],
                outputs=[mem_status, mem_table])
            del_mem_btn.click(fn=delete_member,
                inputs=[m_del_id],
                outputs=[mem_status, mem_table])
            refresh_mem_btn.click(fn=refresh_members, outputs=mem_table)

        # ── ÖDÜNÇ ──
        with gr.Tab("📋 Ödünç İşlemleri"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Kitap Ödünç Ver")
                    l_book   = gr.Dropdown(label="Kitap Seç",  choices=book_choices())
                    l_member = gr.Dropdown(label="Üye Seç",   choices=member_choices())
                    borrow_btn  = gr.Button("📤 Ödünç Ver", variant="primary")
                    loan_status = gr.Textbox(label="Durum", interactive=False)

                with gr.Column():
                    gr.Markdown("### Kitap İade Al")
                    l_loan  = gr.Dropdown(label="Aktif Ödünç", choices=loan_choices())
                    return_btn    = gr.Button("📥 İade Al", variant="primary")
                    return_status = gr.Textbox(label="Durum", interactive=False)

            refresh_drop_btn = gr.Button("↻ Listeleri Yenile", variant="secondary")
            gr.Markdown("### Tüm Kayıtlar")
            loan_table = gr.Dataframe(
                headers=["#", "Kitap", "Üye", "Ödünç Tarihi", "İade"],
                datatype=["number","str","str","str","str"],
                interactive=False
            )
            refresh_loan_btn = gr.Button("↻ Kayıtları Yenile", variant="secondary")

            borrow_btn.click(fn=borrow,
                inputs=[l_book, l_member],
                outputs=[loan_status, loan_table, l_loan])
            return_btn.click(fn=return_book,
                inputs=[l_loan],
                outputs=[return_status, loan_table, l_loan])
            refresh_drop_btn.click(fn=refresh_dropdowns,
                outputs=[l_book, l_member, l_loan])
            refresh_loan_btn.click(fn=refresh_loans, outputs=loan_table)

    # ilk yüklemede verileri çek
    demo.load(fn=get_stats,        outputs=[s1, s2, s3, s4])
    demo.load(fn=refresh_books,    outputs=book_table)
    demo.load(fn=refresh_members,  outputs=mem_table)
    demo.load(fn=refresh_loans,    outputs=loan_table)

if __name__ == "__main__":
    demo.launch(server_port=7860)