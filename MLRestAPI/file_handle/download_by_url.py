import requests
import os
def download_file(url, filename=""):
    try:
        with requests.get(url) as req:
            if filename:
                pass
            else:
                filename = req.url[url.rfind('/')+1:]
            with open(f'{os.getcwd()}/media/uploads/{filename}', 'wb') as f:
            # with open(filename, 'wb') as f:

                for chunk in req.iter_content(chunk_size= 8192):
                    if chunk:
                        f.write(chunk)
            return f'{os.getcwd()}/media/uploads/{filename}'
    except Exception as e:
        print(e)
        return None

google_download_link_template = 'https://drive.google.com/u/3/uc?id=<your ID here>&export=download'
url1_shared_link = 'https://drive.google.com/file/d/1U-yj2juNsm7aSlcyiT4EFiQaYyd-T1AB/view?usp=share_link'
url2_shared_link = 'https://drive.google.com/file/d/1-GaYXXwfKlpJRIGRAyPcLy-xzk4dx41n/view?usp=share_link'
id1 = url1_shared_link.split('/')[5]
id2 = url2_shared_link.split('/')[5]

url1 = 'https://drive.google.com/u/3/uc?id=1U-yj2juNsm7aSlcyiT4EFiQaYyd-T1AB&export=download'
url2 = 'https://drive.google.com/u/3/uc?id=1-GaYXXwfKlpJRIGRAyPcLy-xzk4dx41n&export=download'


