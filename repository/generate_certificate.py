from PIL import Image, ImageDraw, ImageFont
import qrcode
from .templates_config import coordinates_for_templates

domain = "http://localhost:8000"


def generic_certificate_maker(**kwargs):
    id = str(kwargs.get("id"))
    completion_date = str(kwargs.get("request").completion_date)
    issued_by = str(kwargs.get("request").issued_by).title()
    designation = str(kwargs.get("request").designation).title()
    name = str(kwargs.get("name")).title()
    url = f'{domain}/admin/verify_certificate/{id}'
    qr_code = qrcode.QRCode(box_size=6)
    qr_code.add_data(url)
    qr_code.make()
    qr_image = qr_code.make_image()
    template_id = kwargs.get("request").select_template
    open_image = Image.open("templates/certificate"+str(template_id)+".png")
    draw_image = ImageDraw.Draw(open_image)
    open_image.paste(qr_image,
                     coordinates_for_templates[template_id]["qr_code"])
    name_font = ImageFont.truetype('font/Amsterdam.ttf',
                                   coordinates_for_templates
                                   [template_id]["name_font"])
    completion_date_font = ImageFont.truetype('font/Poppins-Medium.ttf',
                                              coordinates_for_templates
                                              [template_id]["completion_date_font"])
    issued_by_font = ImageFont.truetype('font/Amsterdam.ttf',
                                        coordinates_for_templates
                                        [template_id]["issued_by_font"])
    designation_font = ImageFont.truetype('font/Poppins-Medium.ttf',
                                          coordinates_for_templates
                                          [template_id]["designation_font"])
    draw_image.text(coordinates_for_templates[template_id]["name"],
                    name, font=name_font,
                    fill=(69, 69, 69), anchor='mm')
    draw_image.text(coordinates_for_templates[template_id]["completion_date"],
                    completion_date, font=completion_date_font,
                    fill=(69, 69, 69), anchor='mm')
    draw_image.text(coordinates_for_templates[template_id]["issued_by"],
                    issued_by, font=issued_by_font,
                    fill=(69, 69, 69), anchor='mm')
    draw_image.text(coordinates_for_templates[template_id]["designation"],
                    designation, font=designation_font,
                    fill=(69, 69, 69), anchor='mm')
    img_reduced_size = open_image.resize((1000, 720))
    img_reduced_size.save(f"certificates/{id}_certificate.png")
