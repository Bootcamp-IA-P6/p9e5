Proyecto de NLP para detección automática de mensajes de odio en comentarios de YouTube.

## Descripción
Modelo de clasificación de texto entrenado para identificar comentarios de odio,
desarrollado como solución para moderar contenido a escala.

## Estructura del proyecto
p9e5/
├── data/          # Dataset (no versionado)
├── notebooks/     # Exploración y entrenamiento
├── src/           # Código fuente modular
├── app/           # Interfaz Streamlit
├── pyproject.toml
└── README.md

## Dataset
Descarga el dataset desde [este enlace](https://drive.google.com/file/d/1bG7fA273jIBgJfc6YS1vsKfr1qRiNUTU/view?usp=sharing)
y colócalo en la carpeta `data/`.

## Instalación
```bash
uv venv venv
source venv/Scripts/activate
uv sync
```

## Uso
```bash
streamlit run app/app.py
```
