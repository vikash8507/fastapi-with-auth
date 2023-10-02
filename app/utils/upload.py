import uuid
import base64


def upload_file(base64_data, base_dir="media"):
    eliminator, data = base64_data.split("base64, ")
    ext = eliminator.split("/")[1].replace(";", "")
    file_name = uuid.uuid4()
    file_dir = f"{base_dir}/{file_name}.{ext}"

    with open(file_dir, "wb") as out:
        out.write(base64.b64decode(data))
    return file_dir
