# YouTube Hate Speech Detector

Proyecto de NLP para detección automática de mensajes de odio en comentarios de YouTube.
Desarrollado como solución de moderación automática de contenido a escala.

## Contexto del problema

YouTube recibe millones de comentarios diarios. Un equipo de moderadores humanos
no puede escalar al mismo ritmo que crece la plataforma. Este sistema actúa como
primer filtro automático para detectar contenido explícitamente ofensivo,
permitiendo a los moderadores centrarse en los casos ambiguos.

## Equipo

- Gabriela Hernandez
- Paloma Gomez

## Estructura del proyecto

```
p9e5/
├── data/
│   ├── raw/                          # Dataset original, nunca se modifica
│   └── processed/                    # Dataset limpio listo para entrenar
├── notebooks/
│   ├── 01_eda.ipynb                  # Análisis exploratorio de datos
│   ├── 02_preprocessing.ipynb        # Preprocesamiento de texto
│   └── 03_modeling.ipynb             # Entrenamiento y evaluación de modelos
├── src/
│   ├── model.joblib                  # Modelo final serializado
│   └── vectorizer.joblib             # Vectorizador TF-IDF serializado
├── app/
│   ├── app.py                        # Interfaz Streamlit
│   └── samples/
│       ├── sample_comments.txt       # Archivo de ejemplo para análisis por lotes (.txt)
│       └── sample_comments.csv       # Archivo de ejemplo para análisis por lotes (.csv)
├── pyproject.toml                    # Dependencias del proyecto
└── README.md
```

## Instalación

Requisitos: Python 3.10+, uv

```bash
git clone https://github.com/tu-usuario/p9e5.git
cd p9e5
uv venv venv
source venv/Scripts/activate  # Windows
uv sync
```

## Dataset

Descarga el dataset desde [este enlace](https://drive.google.com/file/d/1bG7fA273jIBgJfc6YS1vsKfr1qRiNUTU/view?usp=sharing)
y colócalo en `data/raw/youtoxic_english_1000.csv`.

## Uso

```bash
uv run streamlit run app/app.py
```

La app se abre automáticamente en `http://localhost:8501`.

## Flujo del proyecto

### 1. EDA
- Análisis de distribución de etiquetas
- Wordcloud de comentarios tóxicos vs no tóxicos
- Matriz de correlación entre subcategorías
- Análisis crítico de la calidad del etiquetado

### 2. Preprocesamiento
- Limpieza con expresiones regulares (URLs, menciones, hashtags, números)
- Eliminación de stopwords en inglés
- Lematización con WordNet
- Decisión documentada de descartar stemming

### 3. Modelado
- Vectorización TF-IDF con 500 features y bigramas
- Logistic Regression como baseline
- Random Forest con regularización
- Data augmentation con reemplazo por sinónimos
- Optimización de hiperparámetros con Optuna

### Modelo final

| Métrica | Valor |
|---|---|
| Accuracy test | 59.5% |
| Diferencia train/test | 3.63pp |
| Precision tóxicos | 76% |
| Recall tóxicos | 17% |

## Interfaz Streamlit

La aplicación web permite usar el modelo sin conocimientos técnicos. Incluye cuatro pestañas:

### Análisis individual
- Entrada de texto libre con ejemplos rápidos precargados
- Indicador visual de toxicidad (gauge) con porcentaje de confianza
- Resultado codificado por color: rojo (tóxico) / verde (seguro)
- Palabras y n-gramas más influyentes en la clasificación
- Umbral de decisión ajustable desde el panel lateral

### Análisis por lotes
- Pegado directo de múltiples comentarios
- Carga de archivos `.txt` (un comentario por línea) o `.csv` (columna `comment`)
- Detección automática de columna en archivos CSV
- Archivos de ejemplo descargables directamente desde la interfaz
- Tabla de resultados exportable en CSV
- Gráfico de distribución tóxico/seguro

### Historial de sesión
- Registro automático de todos los análisis realizados en la sesión
- 4 métricas clave: total analizados, tóxicos, seguros y porcentaje medio de toxicidad
- Gráfico de evolución temporal con puntos coloreados por resultado
- Gráfico circular con desglose tóxico/seguro
- Exportación del historial completo en CSV

### Panel lateral
- Umbral de clasificación ajustable (0.0 — 1.0)
- Toggle para activar/desactivar preprocesado de texto
- Toggle para mostrar/ocultar palabras influyentes
- Contador de textos analizados en la sesión actual

## Limitaciones conocidas

El modelo usa TF-IDF, una representación de bolsa de palabras que no considera
el contexto completo de una frase. Esto genera falsos negativos en casos como
"i fucking hate you" donde las palabras aparecen en contextos variados en el dataset.

El modelo es efectivo para detectar patrones de odio explícito y sistemático.
Para detectar odio contextual o implícito sería necesario un modelo basado
en transformers como BERT.

## Modelo Transformer — DistilBERT

El modelo transformer fue entrenado en Kaggle con GPU T4 debido a incompatibilidades
de PyTorch con Python 3.14 en Windows.

- Notebook de entrenamiento: [Kaggle](https://www.kaggle.com/code/agabrielahernandezb/notebook562ed730ab)
- Modelo publicado: [Hugging Face](https://huggingface.co/Gabriela-Her/p9e5-hate-speech-detector)

### Comparativa de modelos

| Métrica        | Random Forest | DistilBERT |
|----------------|---------------|------------|
| Accuracy       | 59.5%         | 76%        |
| Recall tóxicos | 17%           | 71%        |
| F1 tóxicos     | 0.28          | 0.73       |

## Tecnologías

- Python 3.10+
- scikit-learn
- NLTK
- pandas / numpy
- Optuna
- Streamlit
- Plotly
- uv

## Ramas

| Rama | Descripción |
|---|---|
| `main` | Código estable en producción |
| `develop` | Rama de integración |
| `feature/streamlit-app` | Implementación completa de la app Streamlit |

## Próximos pasos

- Despliegue en Hugging Face Spaces
- Soporte multiidioma (español)
