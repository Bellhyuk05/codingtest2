# 도서관 대출 웹 서버 — 대출 규칙은 전부 solution.py의 LibraryLoan이 처리합니다.
import threading

from flask import Flask, jsonify, request, send_from_directory

from solution import LibraryLoan

app = Flask(__name__, static_folder="static")
lib = LibraryLoan()          # 서버가 살아 있는 동안 대출 기록을 기억
lock = threading.Lock()


def parse_day(text):
    # 화면에서 받은 글자를 숫자로만 바꿔서 그대로 넘김 (맞는 날짜인지는 solution.py가 판단)
    text = (text or "").strip()
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


def form():
    data = request.get_json(silent=True) or {}
    return (
        str(data.get("book_id", "")).strip(),
        str(data.get("name", "")).strip(),
        parse_day(str(data.get("day", ""))),
    )


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/borrow")
def borrow():
    book_id, name, day = form()
    with lock:
        ok = lib.borrow(book_id, name, day)
    return jsonify(ok=ok)


@app.post("/api/return")
def return_book():
    book_id, name, day = form()
    with lock:
        overdue = lib.return_book(book_id, name, day)
    return jsonify(ok=overdue != -1, overdue=overdue)


@app.get("/api/loans")
def loans():
    name = request.args.get("name", "").strip()
    with lock:
        items = lib.get_loans(name)
    return jsonify(loans=[{"book_id": b, "due": d} for b, d in items])


@app.post("/api/reset")
def reset():
    global lib
    with lock:
        lib = LibraryLoan()
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
