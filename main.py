import os
import argparse

from PIL import Image, ExifTags
from PIL.ImageFile import ImageFile


# ©Carl Su
# shot on CAMERA_NAME with LENS_NAME, ISO, F, SPEED

def get_exif(file: str, tags: str) -> str:
    result = ""
    img: ImageFile = Image.open(file)
    exif = img.getexif()
    if exif is None:
        print('Sorry, image has no exif data.')
        return ""

    ifd = exif.get_ifd(ExifTags.IFD.Exif)

    try:
        if 'm' in tags:
            model = exif[ExifTags.Base.Model].strip()
            result += f"Shot on {model}. "
    except:
        pass

    try:
        if 'l' in tags:
            lens = ifd[ExifTags.Base.LensModel].strip()
            result = result.replace(". ", " ")
            result += f"with {lens}. "
    except:
        pass

    if 'f' in tags:
        try:
            focal_len = float(ifd[ExifTags.Base.FocalLength])
            focal_len35 = float(ifd.get(ExifTags.Base.FocalLengthIn35mmFilm, 0))
            if 0 < focal_len35 != focal_len:
                result += "{:g}mm ({:g}mm in FF), ".format(focal_len, focal_len35)
            else:
                result += "{:g}mm, ".format(focal_len)

        except:
            pass

    if 'e' in tags:
        try:
            aperture = float(ifd[ExifTags.Base.FNumber])
            if len(result) == 5:
                result = "f/{:g}, ".format(aperture)
            else:
                result += "f/{:g}, ".format(aperture)
        except:
            pass

        try:
            shutter_speed_fac = float(ifd[ExifTags.Base.ExposureTime])
            if shutter_speed_fac < 0.25:
                shutter_speed = "1/{:g}".format(1 / shutter_speed_fac)
            else:
                shutter_speed = shutter_speed_fac
            result += f"{shutter_speed}s, "
        except:
            pass

        try:
            iso = ifd[ExifTags.Base.ISOSpeedRatings]
            result += f"ISO {iso}"
        except:
            pass

    print(result)
    return result


def print_exif(file: str):
    img = Image.open(file)
    img_exif = img.getexif()
    print(type(img_exif))

    if img_exif is None:
        print('Sorry, image has no exif data.')
        return

    for key, val in img_exif.items():
        if key in ExifTags.TAGS:
            print(f'{ExifTags.TAGS[key]}: {val}')
        else:
            print(f'{key}: {val}')

    print("\n#####IFD#####")
    for ifd_id in ExifTags.IFD:
        print('>>>>>>>>>', ifd_id.name, '<<<<<<<<<<')
        try:
            ifd = img_exif.get_ifd(ifd_id)

            if ifd_id == ExifTags.IFD.GPSInfo:
                resolve = ExifTags.GPSTAGS
            else:
                resolve = ExifTags.TAGS

            for k, v in ifd.items():
                tag = resolve.get(k, k)
                print(tag, v)
        except KeyError:
            pass


def get_image_files():
    cwd = os.getcwd()
    image_files = [f for f in os.listdir(cwd) if f.endswith(('.jpg', '.png'))]
    return image_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A script that watermark all photos in this working dir.")
    parser.add_argument("-c", "--copyright", type=str, help="copyright information")
    parser.add_argument("-m", "--model", action="store_true", help="show camera model")
    parser.add_argument("-l", "--lens", action="store_true", help="show lens model")
    parser.add_argument("-e", "--exposure", action="store_true", help="show exposure info")
    parser.add_argument("-f", "--focal", action="store_true", help="show focal length")
    args = parser.parse_args()
    tags = ""
    files = get_image_files()
    if args.exposure:
        tags += 'e'
    if args.focal:
        tags += 'f'
    if args.lens:
        tags += "l"
    if args.model:
        tags += "m"

    for path in files:
        get_exif(path, tags)
