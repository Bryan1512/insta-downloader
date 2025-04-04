from flask import Flask, request, render_template, send_file
import os
import instaloader
import requests
import re

app = Flask(__name__)

# Carpeta de descargas
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
        for i, image in enumerate(post.get_sidecar_nodes(), start=1):
            image_url = image.display_url
            response = requests.get(image_url)
            if response.status_code == 200:
                image_filename = os.path.join(
                    DOWNLOAD_FOLDER, f"photo_{i}.jpg")
                with open(image_filename, "wb") as f:
                    f.write(response.content)
                image_paths.append(image_filename)
        return image_paths
    except Exception as e:
        print(f"Error al descargar foto: {e}")
        return None


def download_instagram_reel(url):
    """Descarga un Reel de Instagram sin iniciar sesión."""
    try:
        loader = instaloader.Instaloader()

        # Extraer el shortcode del Reel desde la URL
        match = re.search(r"instagram\.com/reel/([^/?]+)", url)
        if not match:
            return None, "URL no válida. Asegúrate de que sea un Reel."

        shortcode = match.group(1)

        # Obtener el Reel sin iniciar sesión
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # Descargar el video
        video_url = post.video_url
        response = requests.get(video_url)
        if response.status_code == 200:
            video_filename = os.path.join(
                DOWNLOAD_FOLDER, f"reel_{shortcode}.mp4")
            with open(video_filename, "wb") as f:
                f.write(response.content)
            return video_filename, None
        else:
            return None, f"Error al descargar el Reel: Código {response.status_code}"
    except Exception as e:
        return None, f"Error al descargar el Reel: {str(e)}"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]

        # Si es una foto o una publicación con varias imágenes
        if "p/" in url:
            image_paths = download_instagram_photo(url)
            if image_paths:
                if isinstance(image_paths, list):
                    return render_template("index.html", images=image_paths)
                return send_file(image_paths[0], as_attachment=True)

        # Si es un Reel
        elif "reel/" in url:
            video_path, error = download_instagram_reel(url)
            if video_path:
                return send_file(video_path, as_attachment=True)
            else:
                return render_template("index.html", error=error)

        return render_template("index.html", error="No se pudo descargar el contenido.")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
