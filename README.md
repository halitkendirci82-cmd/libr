📚 도서관 관리 시스템

⚠️ 이 페이지는 터키어로 제작되었습니다.

FastAPI (백엔드) + Gradio (프론트엔드) + SQLite (데이터베이스)로 개발된 도서관 관리 애플리케이션입니다.

📁 파일 구조
library_v2/
├── app/
│   ├── main.py        → FastAPI REST API
│   ├── models.py      → 데이터베이스 테이블 (Book, Member, Loan)
│   ├── database.py    → SQLite 연결
│   ├── ui.py          → Gradio 인터페이스
│   └── library.db     → 데이터베이스 (자동 생성)
└── requirements.txt

🚀 설치 방법
1. 패키지 설치
bashpip install fastapi uvicorn sqlalchemy gradio requests pydantic
2. 폴더 이동
bashcd library_v2\app
3. 터미널 1 — API 실행
bashpython -m uvicorn main:app --reload --port 8000
✅ INFO: Uvicorn running on http://127.0.0.1:8000 가 보여야 합니다
4. 터미널 2 — 인터페이스 실행 (새 터미널: Ctrl + Shift + `)
bashpython ui.py
✅ Running on local URL: http://127.0.0.1:7860 가 보여야 합니다

🌐 주소
서비스URLGradio 인터페이스http://127.0.0.1:7860API 문서http://127.0.0.1:8000/docs

⚠️ 주의사항

두 터미널이 항상 열려 있어야 합니다. 하나라도 닫히면 앱이 작동하지 않습니다.
library.db 파일은 처음 실행 시 자동으로 생성됩니다. 삭제하지 마세요.
API 터미널이 닫히면 Gradio에서 ❌ HTTPConnectionPool 오류가 발생합니다 → 터미널 1을 다시 실행하세요.


✨ 주요 기능
탭기능📖 도서 (Kitaplar)추가, 목록, 삭제 — 장르 / 연도 / 권수 관리👥 회원 (Üyeler)추가, 목록, 삭제 — 이메일 & 전화번호📋 대출 (Ödünç)대출 / 반납 — 날짜 기록통계전체 도서, 회원, 활성 대출 수

🔌 API 엔드포인트
GET    /books                → 도서 목록
POST   /books                → 도서 추가
DELETE /books/{id}           → 도서 삭제

GET    /members              → 회원 목록
POST   /members              → 회원 추가
DELETE /members/{id}         → 회원 삭제

GET    /loans                → 전체 대출 기록
POST   /loans                → 도서 대출
PUT    /loans/{id}/return    → 도서 반납

GET    /stats                → 통계
