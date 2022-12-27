from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from hashing import Hash
import models
from .generate_certificate import generic_certificate_maker
from PIL import Image, ImageDraw, ImageFont
import qrcode
import schemas
import csv
import codecs
import img2pdf
import os
import shutil
import datetime

domain = "http://localhost:8000"


def upload_insert_csvfile_into_db(db, request, file):
    validated_csv_file = validate_csv(file)
    if not validated_csv_file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="csv only")
    return get_csv_data(db, request, validated_csv_file)


def validate_csv(csvfile):
    if not csvfile.filename.endswith(".csv"):
        return False
    return csvfile


def show_all_certificates(db: Session):
    certificates = db.query(models.UploadDetails).all()
    return certificates


def find_certificate(id: int, db: Session):
    certificate_id = db.query(models.UploadDetails.id,
                              models.UploadDetails.name,
                              models.UploadDetails.completion_date,
                              models.UploadDetails.issued_by,
                              models.UploadDetails.designation).filter(
                              models.UploadDetails.id == id).first()
    if certificate_id:
        return certificate_id
    else:
        return 'Not Found'


def verify_certificate(id: int, db: Session):
    certificate_id = db.query(models.UploadDetails.id,
                              models.UploadDetails.name,
                              models.UploadDetails.completion_date,
                              models.UploadDetails.issued_by,
                              models.UploadDetails.designation).filter(
                              models.UploadDetails.id == int(id)).first()
    if not certificate_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"certificate with id {id} not found")
    else:
        return f"certificate with id {id} exists with" \
               f"the following details : "\
               f" ID = {certificate_id['id']}" \
               f" Certificate Given to = {str(certificate_id['name'])}," \
               f" Certificate Issued by = {str(certificate_id['issued_by'])},"


def update_details(id: int, name, db: Session):
    query = db.query(models.UploadDetails).filter(
                     models.UploadDetails.id == id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with {id} does not exist')
    db.query(models.UploadDetails).filter(
             models.UploadDetails.id == id).update({
                                            models.UploadDetails.name: name})
    db.commit()
    return "User Updated"


def delete_record(id: int, db: Session):
    query = db.query(models.UploadDetails).filter(
                     models.UploadDetails.id == id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'certificate with {id} is not available')
    db.query(models.UploadDetails).filter(
             models.UploadDetails.id == id).delete()
    db.commit()
    return "Record Deleted"


def download_certificate():
    if os.path.exists("certificates"):
        with open("Downloads/certificate_list.pdf", "wb") as f:
            f.write(img2pdf.convert(["certificates/"+i[0:]
                                    for i in os.listdir("certificates/")
                                    if i.endswith(".png")]))
            return "Downloads/certificate_list.pdf"
    return True


def download_single_certificate(id: int, db: Session):

    if os.path.exists('certificates'):
        shutil.rmtree('certificates/')
        os.mkdir('certificates')
    else:
        os.mkdir('certificates')

    query = db.query(models.UploadDetails.id,
                     models.UploadDetails.completion_date,
                     models.UploadDetails.issued_by,
                     models.UploadDetails.designation,
                     models.UploadDetails.name).filter(
                     models.UploadDetails.id == id).first()
    print(query)
    if query:
        id = str(query['id'])
        completion_date = str(query['completion_date'])
        issued_by = str(query['issued_by']).title()
        designation = str(query['designation']).title()
        name = str(query['name']).title()
        url = f'{domain}/admin/verify_certificate/{id}'
        qr_code = qrcode.QRCode(box_size=6)
        qr_code.add_data(url)
        qr_code.make()
        qr_image = qr_code.make_image()
        open_image = Image.open("templates/certificate3.png")
        draw_image = ImageDraw.Draw(open_image)
        open_image.paste(qr_image, (1580, 1050))
        my_font = ImageFont.truetype('font/Amsterdam.ttf', 240)
        my_font2 = ImageFont.truetype('font/Poppins-Medium.ttf', 40)
        my_font3 = ImageFont.truetype('font/Poppins-Medium.ttf', 40)
        my_font4 = ImageFont.truetype('font/Poppins-Medium.ttf', 35)
        draw_image.text((820, 690), name, font=my_font, fill=(69, 69, 69),
                        anchor='mm')
        draw_image.text((375, 1120), completion_date,
                        font=my_font2, fill=(69, 69, 69), anchor='mm')
        draw_image.text((1200, 1120), issued_by, font=my_font3,
                        fill=(69, 69, 69), anchor='mm')
        draw_image.text((1200, 1200), designation, font=my_font4,
                        fill=(20, 20, 20), anchor='mm')
        img_reduced_size = open_image.resize((1000, 720))
        img_reduced_size.save(f"certificates/{id}_certificate.png")
        return download_certificate()
    else:
        return {'response': False}


def create_user(request: schemas.User, db: Session):

    new_user = models.User(name=request.name, email=request.email,
                           password=Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"user added": new_user, "success": True}


def get_csv_data(db: Session, request, csvfile):

    if os.path.exists('certificates'):
        shutil.rmtree('certificates/')
        os.mkdir('certificates')
    else:
        os.mkdir('certificates')

    csvReader = csv.DictReader(codecs.iterdecode(csvfile.file, 'utf-8'))
    try:
        get_last_id = db.query(models.UploadDetails.id).order_by(
                               models.UploadDetails.created_on.
                               desc()).limit(1).one()
        get_last_id = get_last_id["id"]
        # csv_data = []
    except NoResultFound:
        get_last_id = 0
    for row in csvReader:
        user_input = models.UploadDetails(completion_date=request.
                                          completion_date,
                                          issued_by=request.issued_by,
                                          designation=request.designation,
                                          name=row['Name'],
                                          email=row['Email'],
                                          created_on=datetime.datetime.
                                          utcnow())
        db.add(user_input)
        # csv_data.append({
        #     "completion_date": request.completion_date,
        #     "issued_by": request.issued_by,
        #     "designation": request.designation,
        #     "name": row['Name'],
        #     "email": row['Email']
        # })
        
        get_last_id = get_last_id + 1
        generic_certificate_maker(id=get_last_id, request=request,
                                  name=row['Name'], email=row['Email'])
    db.commit()
 
    # return {"data uploaded": csv_data, "success": True}
    return {"success": True}
