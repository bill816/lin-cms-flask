"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from flask import request
from lin.jwt import login_required
from lin.redprint import Redprint

from app.extension.file.local_uploader import LocalUploader

file_api = Redprint("file")


@file_api.route("", methods=["POST"])
@login_required
def post_file():
    files = request.files
    print("1. cms/file post file function")
    uploader = LocalUploader(files)
    ret = uploader.upload()
    print("2. cms file end post file function")
    return ret
