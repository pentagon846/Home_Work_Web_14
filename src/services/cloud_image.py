import hashlib

import cloudinary
import cloudinary.uploader

from src.conf.config import settings


class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @staticmethod
    def generate_name_avatar(email: str):
        """
    The generate_name_avatar function takes an email address as input and returns a unique name for the avatar image.
    The function uses the SHA256 hash of the email address to generate a 12-character string, which is then used as part of
    the filename for the avatar image.

    :param email: str: Tell the function that it will be receiving a string as an argument
    :return: A string that is the name of an avatar
    :doc-author: Trelent
    """
        name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
        return f"web19/{name}"

    @staticmethod
    def upload(file, public_id: str):
        """
    The upload function takes a file and public_id as arguments.
    The function then uploads the file to Cloudinary using the public_id provided.
    If no public_id is provided, one will be generated automatically.

    :param file: Upload the file to cloudinary
    :param public_id: str: Specify the public id of the image
    :return: A dictionary with the following keys:
    :doc-author: Trelent
    """
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return r

    @staticmethod
    def get_url_for_avatar(public_id, r):
        """
    The get_url_for_avatar function takes in a public_id and an r (which is the result of a cloudinary.api.resource call)
    and returns the URL for that avatar image, which will be used to display it on the page.

    :param public_id: Identify the image in cloudinary
    :param r: Get the version of the image
    :return: The url of the avatar image
    :doc-author: Trelent
    """
        src_url = cloudinary.CloudinaryImage(public_id) \
            .build_url(width=250, height=250, crop='fill', version=r.get('version'))
        return src_url
