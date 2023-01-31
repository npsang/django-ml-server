test_url = "https://drive.google.com/u/0/uc?id=1U-yj2juNsm7aSlcyiT4EFiQaYyd-T1AB&export=download"
import requests
def download_file(url, filename=""):
    try:
        with requests.get(url) as req:
            if filename:
                pass
            else:
                filename = req.url[url.rfind('/')+1:]
            with open(filename, 'wb') as f:
                for chunk in req.iter_content(chunk_size= 8192):
                    if chunk:
                        f.write(chunk)
            return filename
    except Exception as e:
        print(e)
        return None