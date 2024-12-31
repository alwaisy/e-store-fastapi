from pydantic import BaseModel


class ProductMutationSchema(BaseModel):
    title: str
    desc: str
    category: str
    img_url: str  # direct url of image
