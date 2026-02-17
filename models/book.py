from dataclasses import dataclass
from typing import List


CSV_HEADERS = [
    "ID",
    "Polski Tytuł",
    "Autor",
    "ISBN",
    "Cykl",
    "Średnia ocena",
    "Liczba ocen",
    "Czytelnicy",
    "Opinie",
    "Ocena użytkownika",
    "Link",
    "Data przeczytania",
    "Na półkach Główne",
    "Na półkach Pozostałe",
    "Tytuł",
]


@dataclass
class Book:
    book_id: str = ""
    polish_title: str = ""
    author: str = ""
    isbn: str = ""
    cycle: str = ""
    avg_rating: str = ""
    rating_count: str = ""
    readers: str = ""
    opinions: str = ""
    user_rating: str = ""
    link: str = ""
    read_date: str = ""
    main_shelves: str = ""
    other_shelves: str = ""
    title: str = ""

    def to_row(self) -> List[str]:
        return [
            self.book_id,
            self.polish_title,
            self.author,
            self.isbn,
            self.cycle,
            self.avg_rating,
            self.rating_count,
            self.readers,
            self.opinions,
            self.user_rating,
            self.link,
            self.read_date,
            self.main_shelves,
            self.other_shelves,
            self.title,
        ]

    @classmethod
    def from_row(cls, row: List[str]) -> "Book":
        padded = (row + [""] * len(CSV_HEADERS))[: len(CSV_HEADERS)]
        return cls(
            book_id=padded[0],
            polish_title=padded[1],
            author=padded[2],
            isbn=padded[3],
            cycle=padded[4],
            avg_rating=padded[5],
            rating_count=padded[6],
            readers=padded[7],
            opinions=padded[8],
            user_rating=padded[9],
            link=padded[10],
            read_date=padded[11],
            main_shelves=padded[12],
            other_shelves=padded[13],
            title=padded[14],
        )
