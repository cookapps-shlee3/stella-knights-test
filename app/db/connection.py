from app.db.session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        # db 연결이 성공한 경우, DB 세션이 시작됨.
        yield db
    finally:
        # db 세션이 시작된 후 api 호출이 마무리 되면 DB 세션을 닫아준다.
        db.close()