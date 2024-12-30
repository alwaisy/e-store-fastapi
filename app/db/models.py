from sqlmodel import SQLModel


class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: int
    title: str
    desc: str
    category: str
    img_url: str # direct url of image
    