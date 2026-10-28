# 도서관 대출 시스템 — 아래 클래스를 완성하세요. (클래스·메서드 이름은 바꾸지 마세요)

BOOKS = ("B001", "B002", "B003", "B004", "B005")
LOAN_DAYS = 14      # 대출 기간
MAX_LOANS = 3       # 1인 최대 대출 권수


def _valid_day(day):
    # 1 이상의 정수만 허용 (True/False, 실수, 문자열은 거절)
    return type(day) is int and day >= 1


def _valid_name(name):
    return isinstance(name, str)


class LibraryLoan:
    def __init__(self):
        self.loans = {}         # book_id -> (name, 빌린 날)
        self.suspensions = {}   # name -> [(정지 시작일, 정지 마지막 날), ...]

    def _due(self, book_id):
        return self.loans[book_id][1] + LOAN_DAYS

    def _books_of(self, name):
        return [b for b, (who, _) in self.loans.items() if who == name]

    def _is_suspended(self, name, day):
        return any(start <= day <= end for start, end in self.suspensions.get(name, []))

    def borrow(self, book_id, name, day):
        if book_id not in BOOKS:                    # 1. 없는 책
            return False
        if not _valid_day(day):                     # 2. 잘못된 날짜
            return False
        if not _valid_name(name):
            return False
        if book_id in self.loans:                   # 3. 이미 대출 중
            return False
        mine = self._books_of(name)
        if len(mine) >= MAX_LOANS:                  # 4. 3권 초과
            return False
        if any(day > self._due(b) for b in mine):   # 5. 기한 지난 책 보유
            return False
        if self._is_suspended(name, day):           # 6. 대출 정지 기간
            return False
        self.loans[book_id] = (name, day)
        return True

    def return_book(self, book_id, name, day):
        if not _valid_day(day) or not _valid_name(name):
            return -1
        if book_id not in BOOKS or book_id not in self.loans:
            return -1
        who, borrowed_day = self.loans[book_id]
        if who != name:                             # 남이 빌린 책
            return -1
        if day < borrowed_day:                      # 빌린 날보다 이른 반납
            return -1
        overdue = max(0, day - self._due(book_id))
        del self.loans[book_id]
        if overdue > 0:
            # 반납한 날부터 연체 일수만큼 대출 정지 (겹치는 기간은 합쳐서 더 늦게 끝나는 쪽을 따름)
            self.suspensions.setdefault(name, []).append((day, day + overdue - 1))
        return overdue

    def get_loans(self, name):
        if not _valid_name(name):
            return []
        result = [(b, self._due(b)) for b in self._books_of(name)]
        return sorted(result, key=lambda x: (x[1], x[0]))
