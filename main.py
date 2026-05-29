from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database import engine, get_db, Base
import models

# Tabloları oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────── Schemas ───────────────
class BookCreate(BaseModel):
    title:  str
    author: str
    isbn:   str
    genre:  Optional[str] = "Genel"
    year:   Optional[int] = None
    copies: Optional[int] = 1

class MemberCreate(BaseModel):
    name:  str
    email: str
    phone: Optional[str] = ""

class LoanCreate(BaseModel):
    book_id:   int
    member_id: int

# ─────────────── Books ───────────────
@app.get("/books")
def get_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

@app.post("/books", status_code=201)
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if existing:
        raise HTTPException(400, "Bu ISBN zaten kayıtlı")
    new_book = models.Book(
        title=book.title, author=book.author, isbn=book.isbn,
        genre=book.genre, year=book.year,
        copies=book.copies, available=book.copies
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Kitap bulunamadı")
    db.delete(book)
    db.commit()
    return {"message": "Kitap silindi"}

# ─────────────── Members ───────────────
@app.get("/members")
def get_members(db: Session = Depends(get_db)):
    return db.query(models.Member).all()

@app.post("/members", status_code=201)
def add_member(member: MemberCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Member).filter(models.Member.email == member.email).first()
    if existing:
        raise HTTPException(400, "Bu e-posta zaten kayıtlı")
    new_member = models.Member(name=member.name, email=member.email, phone=member.phone)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@app.delete("/members/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(404, "Üye bulunamadı")
    db.delete(member)
    db.commit()
    return {"message": "Üye silindi"}

# ─────────────── Loans ───────────────
@app.get("/loans")
def get_loans(db: Session = Depends(get_db)):
    loans = db.query(models.Loan).all()
    result = []
    for l in loans:
        result.append({
            "id":          l.id,
            "book_id":     l.book_id,
            "member_id":   l.member_id,
            "book_title":  l.book.title,
            "member_name": l.member.name,
            "borrowed_at": l.borrowed_at.isoformat() if l.borrowed_at else None,
            "returned_at": l.returned_at.isoformat() if l.returned_at else None,
        })
    return result

@app.post("/loans", status_code=201)
def borrow_book(loan: LoanCreate, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == loan.book_id).first()
    if not book:
        raise HTTPException(404, "Kitap bulunamadı")
    if book.available < 1:
        raise HTTPException(400, "Mevcut kopya yok")
    member = db.query(models.Member).filter(models.Member.id == loan.member_id).first()
    if not member:
        raise HTTPException(404, "Üye bulunamadı")
    book.available -= 1
    new_loan = models.Loan(book_id=loan.book_id, member_id=loan.member_id)
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return {"id": new_loan.id, "message": "Ödünç verildi"}

@app.put("/loans/{loan_id}/return")
def return_book(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(404, "Kayıt bulunamadı")
    if loan.returned_at:
        raise HTTPException(400, "Zaten iade edilmiş")
    loan.returned_at = datetime.now()
    loan.book.available += 1
    db.commit()
    return {"message": "Kitap iade alındı"}

# ─────────────── Stats ───────────────
@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    books   = db.query(models.Book).all()
    members = db.query(models.Member).all()
    active  = db.query(models.Loan).filter(models.Loan.returned_at == None).count()
    return {
        "total_books":   len(books),
        "total_members": len(members),
        "active_loans":  active,
        "total_copies":  sum(b.copies for b in books),
    }
