from fastapi import APIRouter, status, HTTPException
from fastapi import UploadFile, File, Depends, Form
from database.database import get_db
from fastapi.responses import FileResponse
from repository import admin
import schemas
import datetime
from sqlalchemy.orm import Session

router = APIRouter(
    tags=['admin'],
    prefix='/admin'
)


@router.post('/user')
def create_user(name: str = Form(), email: str = Form(),
                password: str = Form(), db: Session = Depends(get_db)):
    request = {"name": name, "email": email, "password": password}
    request = schemas.User(**request)
    return admin.create_user(request, db)


@router.post('/upload_csv', status_code=status.HTTP_201_CREATED)
def upload_insert_csvfile_into_db(db: Session = Depends(get_db),
                                  completion_date: datetime.date = Form(),
                                  issued_by: str = Form(),
                                  designation: str = Form(),
                                  file: UploadFile = File(...),
                                  select_template: int = Form()):
    request = {"completion_date": completion_date, "issued_by": issued_by,
               "designation": designation, "select_template": select_template}
    # validating and serializing uploaded user data
    request = schemas.UploadBase(**request)
    return admin.upload_insert_csvfile_into_db(db, request, file)


@router.get('/show_all_certificates')
def show_all_certificates(db: Session = Depends(get_db)):
    return admin.show_all_certificates(db)


@router.post('/find_certificate')
def find_certificate(id: int = Form(), db: Session = Depends(get_db)):
    return admin.find_certificate(id, db)


@router.get('/verify_certificate/{id}')
def verify_certificate(id, db: Session = Depends(get_db)):
    return admin.verify_certificate(id, db)


@router.put('/update_details')
def update_details(id: int = Form(), name: str = Form(),
                   db: Session = Depends(get_db)):
    return admin.update_details(id, name, db)


@router.delete('/delete_certificate')
def delete_user(id: int = Form(), db: Session = Depends(get_db)):
    return admin.delete_user(id, db)


@router.get('/download_certificate')
def download_certificate():
    return FileResponse(admin.download_certificate(),
                        media_type="application/pdf", filename='download.pdf')


@router.post('/download_single_certificate')
def download_single_certificate(id: int = Form(),
                                db: Session = Depends(get_db)):
    if admin.download_single_certificate(id, db) == {'response': False}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Certificate with {id} is not available")
    return FileResponse(admin.download_single_certificate(id, db),
                        media_type="application/pdf", filename="download.pdf")

