from fastapi import Depends, FastAPI, Body, Path, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel,Field
from typing import Optional, List
from jwt_manager import create_token
from config.database import Session, engine, Base
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder
from middlewares.error_handler import ErrorHandler
from middlewares.jwt_bearer import JWTBearer
app = FastAPI()
app.title = "Mi aplicación con  FastAPI"
app.version = "0.0.1"

app.add_middleware(ErrorHandler)

Base.metadata.create_all(bind=engine)




class User(BaseModel):
    email: str
    password: str

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(default='Mi pelicula',min_length=5, max_length=15)
    overview: str = Field(default='Descripcion de la pelicula',min_length=15, max_length=50)
    year: int = Field(default=2022, le=2022)
    rating: float = Field(ge=1, le=10)
    category: str = Field(min_length=3, max_length=10)
    
    class Config:
        schema_extra = {
            'example':{
                'id':1,
                'title':'Mi pelicula',
                'overview':'Descripcion de la pelicula',
                'year': 2022,
                'rating': 7.8,
                'category': 'accion'
            }
        }
    


movies = [
    {
		"id": 1,
		"title": "Avatar",
		"overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
		"year": "2009",
		"rating": 7.8,
		"category": "Fantasia"
	},
    {
		"id": 2,
		"title": "Avatar",
		"overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
		"year": "2009",
		"rating": 7.8,
		"category": "Acción"
	}
]



@app.post('/login', tags=['auth']) 
def login(user: User): 
    if user.email == "admin@gmail.com" and user.password == 'admin': 
        token = create_token(user.model_dump()) 
        return JSONResponse(status_code=200, content=token)

@app.get('/', tags=['home'])
def message():
    return HTMLResponse('<h1>Hello world</h1>')


@app.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).all()
    return JSONResponse(content=jsonable_encoder(result), status_code=200)


@app.get('/movies/{id}', tags=['movies'], response_model=Movie)
def get_movies(id: int = Path(ge=0, le=2000)) -> Movie:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not result:
        return JSONResponse(content={'mensaje': 'no encontrado'}, status_code=404)
    return JSONResponse(content=jsonable_encoder(result), status_code=200)



@app.get('/movies/', tags=["movies"], response_model=List[Movie], status_code=200)
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)) -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.category == category).all()
    if not result:
        return JSONResponse(content={'mensaje': 'no encontrado'}, status_code=404)
    return JSONResponse(content=jsonable_encoder(result), status_code=200)


@app.post('/movies', tags=["movies"], response_model=dict, status_code=201)
def create_movies(movie:Movie) -> dict :
    db = Session()
    new_movie = MovieModel(**movie.model_dump())
    db.add(new_movie)
    db.commit()
    movies.append(movie) 
    return JSONResponse(content={'message': "se ha registrado la pelicula"}, status_code=201)


@app.put('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def update_movie(id: int, movie: Movie) -> dict:

    db = Session()
    result = db.query(MovieModel).where(MovieModel.id == id).first()

    if result:
        result.title = movie.title
        result.category = movie.overview
        result.overview = movie.overview
        result.rating = movie.rating
        result.year = movie.year
        db.commit()
        return JSONResponse(status_code=201, content={"message": "pelicula actualizada"})

    return JSONResponse(status_code=404, content={'message': 'no se encontro el id'})


@app.delete('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def delete_movie(id: int) -> dict:

    db = Session()
    result = db.query(MovieModel).where(MovieModel.id == id).first()

    if result:
        db.delete(result)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "pelicula eliminada"})

    return JSONResponse(status_code=404, content={'message': 'no se encontro el id'})
