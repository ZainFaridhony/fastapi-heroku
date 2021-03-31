import shutil
from . import schemas, models, jwttoken, oauth2
from fastapi import FastAPI, Depends, Response, status, UploadFile, File
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from .hash import Hash

app = FastAPI()

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/user', status_code=status.HTTP_201_CREATED, tags=['Users'])
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'User already exist')

    new_user = models.User(name=request.name, email=request.email, password=Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get('/user/{id}', tags=['Users'])
def get_user(id, response: Response, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User not Found')
    return user

@app.post('/login', tags=['Authentication'])
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user or not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Invalid Credentials')

    access_token = jwttoken.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Upload File
# @app.post('/note', status_code=status.HTTP_201_CREATED, tags=['Notes'])
# def create_note(title:str, note:str, file: UploadFile = File(...),db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
#     user = db.query(models.User).filter(models.User.email == get_current_user).first()
#     with open("media/"+file.filename, "wb") as image:
#         shutil.copyfileobj(file.file, image)

#     note_url = str("media/"+file.filename)

#     new_note = models.Note(title=title, note=note, note_file=note_url, user_id=user.id)
#     db.add(new_note)
#     db.commit()
#     db.refresh(new_note)

#     return new_note

@app.post('/note', status_code=status.HTTP_201_CREATED, tags=['Notes'])
def create_note(request: schemas.Note, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.email == get_current_user).first()
    new_note = models.Note(title=request.title, note=request.note, note_file=request.note_file, user_id=user.id)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note

@app.get('/notes', tags=['Notes'])
def get_notes(db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    notes = db.query(models.Note).all()
    return notes

@app.get('/note/{id}', tags=['Notes'])
def get_note_by_id(id, response: Response, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    note = db.query(models.Note).filter(models.Note.id == id).first()
    if not note:
        response.status_code = status.HTTP_404_NOT_FOUND
    return note

@app.put('/note/{id}', tags=['Notes'])
def update_note(id, request: schemas.Note, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    note = db.query(models.Note).filter(models.Note.id == id)
    if not note.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Note not Found')
    note.update(request)
    db.commit()

    return 'UPDATED'

@app.delete('/note/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Notes'])
def delete_note(id, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    note = db.query(models.Note).filter(models.Note.id == id)
    if not note.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Note not Found')
    note.delete(synchronize_session=False)
    db.commit()

    return 'DELETE'
