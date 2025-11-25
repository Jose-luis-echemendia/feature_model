# 🎓 Maestría en Ciencia de Datos e Inteligencia Artificial

## 📊 Información General

- **Duración:** 2 años (4 semestres)
- **Créditos Totales:** 90
- **Nivel:** Posgrado
- **Modalidad:** Presencial
- **Dominio:** Ciencia de Datos

---

## 🌳 Estructura del Programa (4 Niveles de Profundidad)

```
Maestría en Ciencia de Datos (90 créditos)
│
├─ 📚 Núcleo Fundamental (36 créditos) - OBLIGATORIO
│  ├─ Matemáticas Avanzadas (12 créditos)
│  │  ├─ Álgebra Lineal Computacional (4 créditos) - OBLIGATORIO
│  │  ├─ Cálculo Multivariable (4 créditos) - OBLIGATORIO
│  │  └─ Optimización Matemática (4 créditos) - OBLIGATORIO
│  │
│  ├─ Estadística y Probabilidad (12 créditos)
│  │  ├─ Probabilidad Avanzada (4 créditos) - OBLIGATORIO
│  │  ├─ Inferencia Estadística (4 créditos) - OBLIGATORIO
│  │  └─ Análisis Bayesiano (4 créditos) - OBLIGATORIO
│  │
│  └─ Programación para Ciencia de Datos (12 créditos)
│     ├─ Python Científico (4 créditos) - OBLIGATORIO
│     ├─ Entorno R (4 créditos) - OPCIONAL
│     └─ SQL y Bases de Datos (4 créditos) - OBLIGATORIO
│
├─ 🤖 Machine Learning (24 créditos) - OBLIGATORIO
│  ├─ Aprendizaje Supervisado (8 créditos)
│  │  ├─ Regresión Avanzada (2 créditos)
│  │  ├─ Árboles de Decisión y Ensambles (3 créditos)
│  │  └─ Support Vector Machines (3 créditos)
│  │
│  ├─ Aprendizaje No Supervisado (8 créditos)
│  │  ├─ Clustering (4 créditos)
│  │  └─ Reducción de Dimensionalidad (4 créditos)
│  │
│  └─ Deep Learning (8 créditos)
│     ├─ Redes Neuronales Fundamentales (2 créditos) - OBLIGATORIO
│     └─ Especialización en Arquitecturas (6 créditos) - XOR (elegir 1)
│        ├─ Visión por Computadora (CNN)
│        ├─ Procesamiento de Lenguaje Natural (NLP)
│        └─ Series Temporales (RNN/LSTM)
│
├─ ☁️ Big Data e Infraestructura (12 créditos) - OBLIGATORIO
│  ├─ Tecnologías Distribuidas (6 créditos)
│  │  ├─ Apache Spark (3 créditos) - OBLIGATORIO
│  │  └─ Hadoop Ecosystem (3 créditos) - OPCIONAL
│  │
│  └─ Cloud Computing para ML (6 créditos)
│     ├─ Plataformas Cloud (OR - elegir al menos 1)
│     │  ├─ AWS SageMaker (2 créditos) - OPCIONAL
│     │  ├─ Google Cloud AI (2 créditos) - OPCIONAL
│     │  └─ Azure Machine Learning (2 créditos) - OPCIONAL
│     │
│     └─ MLOps y Deployment (4 créditos) - OBLIGATORIO
│
├─ 🎯 Asignaturas Complementarias (8 créditos) - OR (elegir mínimo 2)
│  ├─ Ética en IA (4 créditos) - OPCIONAL
│  ├─ Visualización de Datos Avanzada (4 créditos) - OPCIONAL
│  ├─ Aprendizaje por Refuerzo (4 créditos) - OPCIONAL
│  ├─ Graph Neural Networks (4 créditos) - OPCIONAL
│  └─ Análisis de Datos Biomédicos (4 créditos) - OPCIONAL
│
└─ 📝 Trabajo de Fin de Maestría (10 créditos) - OBLIGATORIO
   ├─ Propuesta de Investigación (20%)
   ├─ Desarrollo e Implementación (50%)
   └─ Documentación y Defensa (30%)
```

---

## 🔗 Relaciones Entre Features (Constraints)

### Tipo: **REQUIRES** (prerequisitos)

| Feature Origen                          | Feature Requerido              | Descripción                                            |
| --------------------------------------- | ------------------------------ | ------------------------------------------------------ |
| Deep Learning                           | Python Científico              | Deep Learning requiere dominio de Python Científico    |
| Visión por Computadora (CNN)            | Álgebra Lineal Computacional   | CNN requiere conocimientos avanzados de álgebra lineal |
| Procesamiento de Lenguaje Natural (NLP) | Probabilidad Avanzada          | NLP requiere fundamentos sólidos en probabilidad       |
| Apache Spark                            | Python Científico              | Spark requiere conocimientos de Python                 |
| Aprendizaje por Refuerzo                | Redes Neuronales Fundamentales | RL requiere fundamentos de redes neuronales            |
| Graph Neural Networks                   | Deep Learning                  | GNN requiere conocimientos de Deep Learning            |

### Tipo: **EXCLUDES** (incompatibles)

| Feature Origen | Feature Excluido  | Descripción                                                 |
| -------------- | ----------------- | ----------------------------------------------------------- |
| Entorno R      | Python Científico | Si se elige R, no se puede cursar Python (son alternativos) |

---

## 📐 Tipos de Features Utilizados

### 🔵 MANDATORY (Obligatorios)

- Núcleo Fundamental completo
- Machine Learning completo
- Big Data e Infraestructura
- Trabajo de Fin de Maestría

### 🟢 OPTIONAL (Opcionales)

- Entorno R (alternativa a Python)
- Hadoop Ecosystem
- Todas las plataformas Cloud (AWS, Google, Azure)
- Todas las asignaturas complementarias

### 🔴 XOR_GROUP (Elegir exactamente 1)

- Especialización en Deep Learning:
  - Visión por Computadora (CNN)
  - NLP
  - Series Temporales (RNN/LSTM)

### 🟡 OR_GROUP (Elegir al menos N)

- **Plataformas Cloud** (mínimo 1 de 3)
- **Asignaturas Complementarias** (mínimo 2 de 5)

---

## 🎯 Especialización en Deep Learning (XOR)

Los estudiantes deben elegir **UNA** de las siguientes especializaciones:

### 1. Visión por Computadora (CNN)

- **Créditos:** 6
- **Temas:** ResNet, YOLO, Segmentación, GANs
- **Frameworks:** PyTorch, TensorFlow
- **Aplicaciones:** Reconocimiento de imágenes, detección de objetos, generación de imágenes

### 2. Procesamiento de Lenguaje Natural (NLP)

- **Créditos:** 6
- **Temas:** Transformers, BERT, GPT, Attention
- **Frameworks:** Hugging Face, spaCy
- **Aplicaciones:** Chatbots, traducción automática, análisis de sentimientos

### 3. Series Temporales (RNN/LSTM)

- **Créditos:** 6
- **Temas:** RNN, LSTM, GRU, Forecasting
- **Aplicaciones:** Finanzas, predicción del clima, IoT

---

## ☁️ Plataformas Cloud (OR Group - Mínimo 1)

Los estudiantes pueden elegir una o más plataformas cloud:

| Plataforma             | Créditos | Servicios Principales                    |
| ---------------------- | -------- | ---------------------------------------- |
| AWS SageMaker          | 2        | S3, EC2, Lambda, SageMaker               |
| Google Cloud AI        | 2        | Vertex AI, BigQuery, Cloud Functions     |
| Azure Machine Learning | 2        | Azure ML, Databricks, Cognitive Services |

---

## 📚 Asignaturas Complementarias (OR Group - Mínimo 2)

Elegir **al menos 2** de las siguientes 5 asignaturas:

### 1. Ética en IA (4 créditos)

- Bias, Fairness, Privacy, Transparency

### 2. Visualización de Datos Avanzada (4 créditos)

- D3.js, Tableau, Power BI, Plotly

### 3. Aprendizaje por Refuerzo (4 créditos)

- Q-Learning, Policy Gradients, Actor-Critic
- **Prerequisito:** Deep Learning

### 4. Graph Neural Networks (4 créditos)

- GCN, GraphSAGE, GAT, Knowledge Graphs
- **Prerequisito:** Deep Learning

### 5. Análisis de Datos Biomédicos (4 créditos)

- Genómica, Diagnóstico, Drug Discovery

---

## 📊 Distribución de Créditos

| Área                        | Créditos | % del Total |
| --------------------------- | -------- | ----------- |
| Núcleo Fundamental          | 36       | 40%         |
| Machine Learning            | 24       | 26.7%       |
| Big Data e Infraestructura  | 12       | 13.3%       |
| Asignaturas Complementarias | 8        | 8.9%        |
| Trabajo de Fin de Maestría  | 10       | 11.1%       |
| **TOTAL**                   | **90**   | **100%**    |

---

## 📅 Plan de Estudios por Semestre

### Semestre 1 (Fundamentos)

- Matemáticas Avanzadas (12 créditos)
- Estadística y Probabilidad (12 créditos)
- Programación para Ciencia de Datos (12 créditos)
- **Total:** 36 créditos

### Semestre 2 (Machine Learning Básico)

- Aprendizaje Supervisado (8 créditos)
- Aprendizaje No Supervisado (8 créditos)
- **Total:** 16 créditos

### Semestre 3 (Avanzado y Especialización)

- Deep Learning + Especialización (8 créditos)
- Big Data e Infraestructura (12 créditos)
- Asignaturas Complementarias (8 créditos)
- **Total:** 28 créditos

### Semestre 4 (Investigación)

- Trabajo de Fin de Maestría (10 créditos)
- **Total:** 10 créditos

---

## 🛠️ Tecnologías y Herramientas Cubiertas

### Lenguajes de Programación

- Python (NumPy, Pandas, Matplotlib, Scikit-learn)
- R (opcional: dplyr, ggplot2, tidyverse)
- SQL (consultas avanzadas, optimización)

### Machine Learning

- Scikit-learn, XGBoost, LightGBM
- PyTorch, TensorFlow, Keras
- Hugging Face (NLP)

### Big Data

- Apache Spark (RDD, DataFrames, MLlib)
- Hadoop (HDFS, MapReduce, Hive)

### Cloud Platforms

- AWS: SageMaker, S3, EC2, Lambda
- Google Cloud: Vertex AI, BigQuery
- Azure: Azure ML, Databricks

### MLOps

- Docker, Kubernetes
- CI/CD para ML
- Monitoring y logging

---

## 🎓 Perfil del Egresado

Al completar la maestría, el estudiante será capaz de:

✅ Diseñar e implementar soluciones completas de ciencia de datos  
✅ Aplicar técnicas avanzadas de machine learning y deep learning  
✅ Trabajar con grandes volúmenes de datos usando tecnologías distribuidas  
✅ Desplegar modelos de ML en producción usando cloud computing  
✅ Especializarse en visión por computadora, NLP o series temporales  
✅ Considerar aspectos éticos en el desarrollo de sistemas de IA  
✅ Realizar investigación aplicada en ciencia de datos

---

## 🔍 Características Técnicas del Modelo

### Profundidad Jerárquica

- **Nivel 1:** Maestría en Ciencia de Datos (raíz)
- **Nivel 2:** 5 áreas principales (Núcleo, ML, Big Data, Complementarias, Tesis)
- **Nivel 3:** 15+ módulos específicos
- **Nivel 4:** 40+ asignaturas y componentes individuales

### Tipos de Grupos

- **3 XOR Groups:** Especialización en Deep Learning
- **2 OR Groups:** Plataformas Cloud, Asignaturas Complementarias

### Relaciones

- **6 Requires:** Prerequisitos entre asignaturas
- **1 Excludes:** Python vs R (alternativos)

### Variabilidad

- Múltiples paths de configuración según especialización
- Flexibilidad en elección de plataformas cloud
- Opciones de asignaturas complementarias según intereses

---

## 📝 Ejemplo de Configuración

### Configuración 1: Especialización en NLP + Cloud AWS

```
✅ Núcleo Fundamental (todos los módulos)
✅ Machine Learning (todos los módulos)
  └─ Deep Learning → NLP
✅ Big Data
  ✅ Apache Spark
  ✅ AWS SageMaker
  ✅ MLOps
✅ Complementarias (elegir 2):
  ✅ Ética en IA
  ✅ Aprendizaje por Refuerzo
✅ Trabajo de Fin de Maestría
```

### Configuración 2: Especialización en Visión + Multi-Cloud

```
✅ Núcleo Fundamental (todos los módulos)
✅ Machine Learning (todos los módulos)
  └─ Deep Learning → Visión por Computadora (CNN)
✅ Big Data
  ✅ Apache Spark
  ✅ AWS SageMaker
  ✅ Google Cloud AI
  ✅ MLOps
✅ Complementarias (elegir 2):
  ✅ Visualización de Datos Avanzada
  ✅ Graph Neural Networks
✅ Trabajo de Fin de Maestría
```

---

**Fecha de creación:** 24 de noviembre de 2025  
**Autor:** Sistema de Seeding - Feature Models Platform
