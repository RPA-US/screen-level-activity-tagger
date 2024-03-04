import tkinter as tk
from tkinter import ttk, filedialog, Canvas, Scrollbar, messagebox
from PIL import Image, ImageTk
import pandas as pd
import os
import re


class ImageTagger(tk.Tk):
    '''
    Main application window
    '''

    def __init__(self):
        super().__init__()
        self.title("Image Tagger")
        self.geometry("1280x720")

        self.df = pd.DataFrame()
        self.images_by_cluster = {}
        self.current_cluster = None
        self.current_image_index = 0

        self.image_column_name = None
        self.images_directory = None

        self.create_widgets()

    '''
    Create the widgets for the main window
    '''

    def create_widgets(self):
        load_csv_button = tk.Button(self, text="Cargar CSV", command=self.open_csv)
        load_csv_button.pack()

        select_dir_button = tk.Button(self, text="Seleccionar directorio de imágenes",
                                      command=self.select_images_directory)
        select_dir_button.pack()

        self.cluster_selector = ttk.Combobox(self, state="readonly")
        self.cluster_selector.pack()
        self.cluster_selector.bind("<<ComboboxSelected>>", self.on_cluster_selected)

        self.previews_frame = tk.Frame(self)
        self.previews_frame.pack(fill=tk.X)

        self.previews_canvas = Canvas(self.previews_frame, height=100)
        self.previews_scrollbar = Scrollbar(self.previews_frame, orient="horizontal",
                                            command=self.previews_canvas.xview)
        self.previews_canvas.configure(xscrollcommand=self.previews_scrollbar.set)

        self.previews_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.previews_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.previews_container = tk.Frame(self.previews_canvas)
        self.previews_canvas.create_window((0, 0), window=self.previews_container, anchor="nw")

        self.image_counter_label = tk.Label(self, text="")
        self.image_counter_label.pack()

        self.image_display = tk.Label(self)
        self.image_display.pack()

        self.manual_tag_entry = tk.Entry(self)
        self.manual_tag_entry.pack()

        self.precision_label = tk.Label(self, text="Precisión: 0%")
        self.precision_label.pack()

        tag_button = tk.Button(self, text="Etiquetar", command=self.assign_manual_tag)
        tag_button.pack()

        navigation_frame = tk.Frame(self)
        navigation_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        reset_button = tk.Button(navigation_frame, text="⚠️ Reset", command=self.confirm_reset)
        reset_button.pack(side=tk.RIGHT, padx=20)

        prev_button = tk.Button(navigation_frame, text="Anterior", command=self.prev_image)
        prev_button.pack(side=tk.LEFT, padx=20)

        next_button = tk.Button(navigation_frame, text="Siguiente", command=self.next_image)
        next_button.pack(side=tk.LEFT, padx=20)

    '''
    Open a file dialog to select a CSV file
    '''

    def open_csv(self):
        self.filepath = filedialog.askopenfilename(
            title="Selecciona un archivo CSV",
            filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*"))
        )
        if self.filepath:
            self.load_csv(self.filepath)

    '''
    Load a CSV file and populate the combobox with the unique values of the 'activity_label' column
    '''

    def load_csv(self, filepath):
        try:
            self.df = pd.read_csv(filepath, encoding='utf-8', sep=';')
            self.image_column_name = self.detect_image_column(self.df)
            if not self.image_column_name:
                messagebox.showerror("Error", "No se pudo detectar la columna de imágenes en el archivo CSV.")
                return
            self.images_by_cluster = self.df.groupby('activity_label')[self.image_column_name].apply(list).to_dict()
            self.images_by_cluster = {str(k): v for k, v in self.images_by_cluster.items()}
            print('CSV Cargado. Clusteres: ', self.images_by_cluster)
            self.update_cluster_selector()
        except Exception as e:
            messagebox.showerror("Error al cargar CSV", str(e))

    '''
    Save the changes made to the CSV file
    '''

    def save_changes(self):
        try:
            self.df.to_csv(self.filepath, index=False, sep=';',
                           encoding='utf-8')  # Usa el mismo path y configuración que al cargar
            print("Cambios guardados exitosamente.")
        except Exception as e:
            print(f"Error al guardar los cambios: {e}")

    '''
    Open a file dialog to select a directory containing the images
    '''

    def select_images_directory(self):
        directory = filedialog.askdirectory(title="Selecciona el directorio de imágenes")
        print(f'Directorio seleccionado: {directory}')
        if directory:
            self.images_directory = directory
            self.update_cluster_selector()

    '''
    Detect the column containing the image paths in the dataframe
    '''
    def detect_image_column(self, dataframe):
        for col in dataframe.columns:
            if dataframe[col].dtype == 'object' and dataframe[col].str.contains(r'\.(jpg|jpeg|png)$', regex=True).any():
                return col
        return None

    '''
    Update the values of the cluster combobox
    '''
    def update_cluster_selector(self):
        if self.images_by_cluster:
            cluster_ids = sorted(self.images_by_cluster.keys())
            self.cluster_selector['values'] = cluster_ids
            print(f"Clústeres actualizados: {cluster_ids}")
        else:
            print("Aún no se han cargado los clústeres.")

    '''
    Event handler for when a cluster is selected from the combobox
    '''

    def on_cluster_selected(self, event):
        self.current_cluster = self.cluster_selector.get()
        print(f'Cluster seleccionado: {self.current_cluster}')
        self.current_image_index = 0
        self.update_previews()
        self.show_images()

    '''
    Update the previews of the images for the current cluster
    '''

    def update_previews(self):
        for widget in self.previews_container.winfo_children():
            widget.destroy()
        print(f'Cluster actual: {self.current_cluster}',
              f'Imagenes por cluster: {self.images_by_cluster}', f'Directorio de imagenes: {self.images_directory}')
        if self.current_cluster in self.images_by_cluster and self.images_directory:
            for img_index, img_name in enumerate(self.images_by_cluster[self.current_cluster]):
                img_path = os.path.join(self.images_directory, img_name)
                print(f'Imagen: {img_path}')
                self.add_preview(img_path, img_index)

        self.previews_container.update_idletasks()
        self.previews_canvas.config(scrollregion=self.previews_canvas.bbox("all"))

    '''
    Add a preview of an image to the previews container
    '''

    def add_preview(self, img_path, img_index):
        if os.path.exists(img_path):
            img = Image.open(img_path)
            img.thumbnail((100, 100))
            img_tk = ImageTk.PhotoImage(img)

            frame = tk.Frame(self.previews_container)
            frame.pack(side=tk.LEFT, padx=5)

            label_img = tk.Label(frame, image=img_tk)
            label_img.image = img_tk
            label_img.pack()

            activity_manual_value = self.df.loc[
                self.df[self.image_column_name].apply(lambda x: os.path.basename(x)) == os.path.basename(
                    img_path), 'activity_manual'].values[0]
            if pd.isna(activity_manual_value):
                activity_manual_value = "NA"
            label_text = tk.Label(frame, text=f"#{img_index + 1} - {activity_manual_value}")
            label_text.pack()

    '''
    Show the images for the current cluster
    '''

    def show_images(self):
        if self.current_cluster in self.images_by_cluster and self.images_directory:
            img_names = self.images_by_cluster[self.current_cluster]
            if img_names:
                img_path = os.path.join(self.images_directory,
                                        img_names[self.current_image_index])
                self.display_image(img_path)
                self.update_image_counter()

    '''
    Display an image in the image display label
    '''

    def display_image(self, img_path):
        print(f'Imagen a mostrar: {img_path}')
        if os.path.exists(img_path):
            img = Image.open(img_path)
            img = img.resize((800, 600))
            img_tk = ImageTk.PhotoImage(img)
            self.image_display.configure(image=img_tk)
            self.image_display.image = img_tk

    '''
    Show the previous image in the current cluster
    '''

    def prev_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
        else:
            self.current_image_index = len(self.images_by_cluster[self.current_cluster]) - 1
        self.show_images()

    '''
    Show the next image in the current cluster
    '''

    def next_image(self):
        if self.current_image_index < len(self.images_by_cluster[self.current_cluster]) - 1:
            self.current_image_index += 1
        else:
            self.current_image_index = 0
        self.show_images()

    '''
    Update the image counter label with the current image index and the total number of images in the current cluster
    '''

    def update_image_counter(self):
        total_images = len(self.images_by_cluster[self.current_cluster])
        self.image_counter_label.config(text=f"Imagen {self.current_image_index + 1} de {total_images}")

    '''
    Calculate the precision of the manual tags and update the precision label
    '''

    def calculate_and_update_precision(self):

        correct_assignments = 0
        attempted_manual_tags = 0

        for manual, label in zip(self.df['activity_manual'], self.df['activity_label']):
            if pd.notna(
                    manual) and manual != 'NA':
                attempted_manual_tags += 1
                if str(label) == letter_to_number_mapping.get(manual, ''):
                    correct_assignments += 1

        precision = (correct_assignments / attempted_manual_tags) * 100 if attempted_manual_tags > 0 else 0
        self.precision_label.config(text=f"Precisión: {precision:.2f}%")

    '''
    Assign the manual tag to the current image
    '''

    def assign_manual_tag(self):
        manual_tag = self.manual_tag_entry.get()
        print(f'Etiqueta manual: {manual_tag}')
        if self.current_cluster in self.images_by_cluster:
            selected_image_name = self.images_by_cluster[self.current_cluster][self.current_image_index]
            self.df.loc[self.df[self.image_column_name] == selected_image_name, 'activity_manual'] = manual_tag
            self.update_previews()
            self.calculate_and_update_precision()
            self.save_changes()

    '''
    Reset the manual tags in the dataframe
    '''

    def reset_manual_tags(self):
        self.df['activity_manual'] = 'NA'
        self.update_previews()
        self.calculate_and_update_precision()
        self.save_changes()
        messagebox.showinfo('Reset completado', 'Se ha ejercido un reset sobre las etiquetas manuales')

    '''
    Confirm the reset of the manual tags
    '''

    def confirm_reset(self):
        confirm = messagebox.askyesno('Confirmar reset', '¿Estás seguro de que deseas resetear las etiquetas manuales?')
        if confirm:
            self.reset_manual_tags()


if __name__ == "__main__":
    letter_to_number_mapping = {'A': '0', 'B': '1', 'C': '2', 'D': '3', 'E': '4', 'F': '5', 'G': '6', 'H': '7',
                                'I': '8', 'J': '9'}
    app = ImageTagger()
    app.mainloop()
