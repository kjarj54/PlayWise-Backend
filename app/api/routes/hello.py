from fastapi import APIRouter

router = APIRouter(
    prefix="/hello",
    tags=["Hello"]
)

@router.get("/")
def hello_world():
    """
    Endpoint simple de Hello World
    """
    return {"message": "Hello World"}

@router.get("/{name}")
def hello_name(name: str):
    """
    Saludo personalizado
    """
    return {"message": f"Hello {name}!"}