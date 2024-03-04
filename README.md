# Screen-Level Activity Tagger

El "Screen-Level Activity Tagger" es una herramienta interactiva de escritorio para la anotación manual de actividades en imágenes. Permite a los usuarios cargar un conjunto de imágenes y un archivo CSV correspondiente que contiene metadatos, y proporciona una interfaz para etiquetar las imágenes con anotaciones manuales.

## Requisitos

- Python 3.9 (lanzado en la versión 3.9.10)
- Tkinter (usualmente viene con Python)
- PIL (Python Imaging Library)
- Pandas
- ...

Crea tu entorno virtual de Python y ejecuta `pip install -r requirements.txt`

## Configuración del Proyecto

Para ejecutar el proyecto, necesitas tener una estructura de directorios específica:

- Screen-Level Activity Tagger/
  - logs/
    - log_de_ejemplo.csv
  - resources/
    - imagenes_del_log_de_ejemplo/
      - imagen1.png
      - imagen2.png
      - ...
