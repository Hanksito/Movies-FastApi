from fastapi import Depends, FastAPI, Body, HTTPException, Path, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel,Field
from typing import Coroutine, Optional, List
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer

app = FastAPI()
app.title = "Mi aplicación con  FastAPI"
app.version = "0.0.1"


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != 'admin@gmail.com':
            raise HTTPException(
                status_code=403, detail='Credenciales no son validas')


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
    return JSONResponse(content=movies, status_code=200)


@app.get('/movies/{id}', tags=['movies'], response_model=Movie)
def get_movies(id: int = Path(ge=1,le=2000)) -> Movie:
    for item in movies:
        if item['id'] ==  id:
            return JSONResponse(status_code=200, content=item)

        return JSONResponse(content=[], status_code=404)


@app.get('/movies/', tags=["movies"], response_model=List[Movie], status_code=200)
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)) -> List[Movie]:
    data = [item for item in movies if item['category'] == category]
    return JSONResponse(content=data, status_code=200)


@app.post('/movies', tags=["movies"], response_model=dict, status_code=201)
def create_movies(movie:Movie) -> dict :
    movies.append(movie) 
    return JSONResponse(content={'message': "se ha registrado la pelicula"}, status_code=201)


@app.put('movies/{id}', tags=["movies"], response_model=dict, status_code=201)
def update_movies(id:int, movie:Movie) -> dict :
    for item in movies:
        if item['id'] == id:
            item['title'] = movie.title,
            item['overview'] = movie.overview
            item['year'] = movie.year
            item['rating'] = movie.rating
            item['category'] = movie.category
            return JSONResponse(content={'message': "se ha actualizado la pelicula"}, status_code=201)


@app.delete('movies/{id}', tags=["movies"], response_model=dict, status_code=201)
def delete_movies(id:int) -> dict :
    for item in movies:
        if item['id'] == id:
            movies.remove(item)
            return JSONResponse(content={'message': "se ha eliminado la pelicula"}, status_code=201)
