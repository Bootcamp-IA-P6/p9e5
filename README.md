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
│   └── app.py                        # Interfaz Streamlit
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
python -m streamlit run app/app.py
```

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

## Limitaciones conocidas

El modelo usa TF-IDF, una representación de bolsa de palabras que no considera
el contexto completo de una frase. Esto genera falsos negativos en casos como
"i fucking hate you" donde las palabras aparecen en contextos variados en el dataset.

El modelo es efectivo para detectar patrones de odio explícito y sistemático.
Para detectar odio contextual o implícito sería necesario un modelo basado
en transformers como BERT.

## Tecnologías

- Python 3.10+
- scikit-learn
- NLTK
- pandas / numpy
- Optuna
- Streamlit
- uv