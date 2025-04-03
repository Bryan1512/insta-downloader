from flask import Flask, request, render_template, send_file
import os
import yt_dlp
import instaloader
import requests  # Asegúrate de importar requests

app = Flask(__name__)

# Carpeta donde se guardarán las descargas
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


def download_instagram_photo(url):
    """Descarga fotos de publicaciones de Instagram."""
    try:
        loader = instaloader.Instaloader()
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        image_paths = []
        # Descarga imágenes de sidecar (varias imágenes)
        for i, image in enumerate(post.get_sidecar_nodes(), start=1):
            image_url = image.display_url
            response = requests.get(image_url)
            if response.status_code == 200:
                image_filename = f"{DOWNLOAD_FOLDER}/photo_{i}.jpg"
                with open(image_filename, "wb") as f:
                    f.write(response.content)
                image_paths.append(image_filename)
            else:
                print(
                    f"Error al descargar la imagen {i}: Código {response.status_code}")
        return image_paths
    except Exception as e:
        print(f"Error al descargar foto: {e}")
        return None


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]

        # Si la URL es de una publicación de fotos
        if "p/" in url:
            image_paths = download_instagram_photo(url)
            if image_paths:
                if isinstance(image_paths, list):  # Si es un carrusel de imágenes
                    return render_template("index.html", images=image_paths)
                return send_file(image_paths[0], as_attachment=True)

        return render_template("index.html", error="No se pudo descargar el contenido.")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
