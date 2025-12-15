# 📚 Cambios Realizados - Adaptación al Contexto Educativo

## 🎯 Resumen

Se han actualizado todos los datos de semillas (seeds) para reflejar el propósito real de la plataforma: **gestión de variabilidad curricular y diseño de planes de estudio para el sector educativo**.

---

## 📝 Archivos Modificados

### 1. `data_settings.py` - Configuraciones del Sistema

**Antes:** Configuraciones genéricas (mantenimiento, PDF, tareas)

**Ahora:** Configuraciones orientadas a educación:

- ✅ `ENABLE_CURRICULUM_VALIDATION` - Validación de coherencia curricular
- ✅ `MAX_CURRICULUM_VERSIONS` - Control de versiones de planes de estudio
- ✅ `ENABLE_COLLABORATIVE_DESIGN` - Diseño colaborativo de modelos curriculares
- ✅ `AUTO_SAVE_INTERVAL` - Auto-guardado de cambios
- ✅ `ENABLE_LEARNING_ANALYTICS` - Analíticas de aprendizaje
- ✅ `DEFAULT_CREDIT_HOURS` - Créditos académicos por defecto

---

### 2. `data_users.py` - Usuarios del Sistema

**Antes:** Usuarios genéricos (designer, editor, configurator)

**Ahora:** Roles académicos específicos:

#### Usuarios de Producción:

- Diseñadores curriculares (yadira.rodriguez@uci.cu, liany.sobrino@uci.cu)
- Coordinadores académicos
- Jefes de departamento

#### Usuarios de Desarrollo:

- `diseñador.curricular@example.com` - Diseño de planes curriculares
- `coordinador.academico@example.com` - Coordinación académica
- `jefe.carrera@example.com` - Gestión de programas
- `profesor@example.com` - Consulta de planes
- `evaluador.curricular@example.com` - Evaluación y revisión

---

### 3. `data_models.py` - Datos Principales

#### 🎓 **Dominios Académicos** (antes: E-Commerce, Healthcare, IoT)

**Ahora:**

1. **Ingeniería Informática** - Programas de ingeniería en ciencias informáticas
2. **Ciencias Básicas** - Matemáticas, física, química
3. **Formación General** - Humanidades, idiomas
4. **Desarrollo de Software** - Programas especializados
5. **Ciencia de Datos** - IA, Machine Learning
6. **Seguridad Informática** - Ciberseguridad

#### 🏷️ **Etiquetas Pedagógicas** (antes: performance, security, ui)

**Ahora:**

- `fundamentos` - Cursos introductorios
- `avanzado` - Contenido avanzado
- `práctico` / `teórico` - Enfoque del curso
- `obligatorio` / `electivo` - Tipo de asignatura
- `proyecto` - Basado en proyectos
- `certificacion` - Preparación para certificaciones
- `investigacion` - Componente investigativo
- `practica_profesional` - Pasantías

#### 📚 **Recursos Educativos**

**Antes:** Videos y PDFs genéricos sobre feature models

**Ahora:**

- Video: "Introducción a Feature Models en Educación" (20 min)
- PDF: "Guía de Diseño Curricular con Feature Models"
- Video: "Programación Orientada a Objetos - Conceptos Fundamentales" (45 min)
- PDF: "Estructuras de Datos - Material de Estudio"
- Quiz: "Validación Curricular" (15 min)
- Laboratorios: "Base de Datos - Prácticos"

#### 🎯 **Planes de Estudio** (antes: E-Commerce, Healthcare)

**Ahora:**

##### **Plan 1: Ingeniería en Ciencias Informáticas**

- **Duración:** 5 años, 240 créditos
- **Estructura:**

  - **Ciclo Básico** (60 créditos)

    - Matemática I y II (con prerequisitos)
    - Fundamentos de Programación
    - Estructuras de Datos

  - **Ciclo Profesional** (120 créditos)

    - Ingeniería de Software
    - Bases de Datos
    - Redes de Computadoras
    - **Especialización (XOR):**
      - Desarrollo de Software
      - Ciencia de Datos
      - Seguridad Informática

  - **Electivas (OR - mínimo 3):**

    - Desarrollo Móvil
    - Computación en la Nube
    - IoT, Blockchain, VR/AR

  - **Práctica Profesional** (12 créditos)
  - **Trabajo de Diploma** (30 créditos)

##### **Plan 2: Desarrollo Web Full Stack**

- **Duración:** 6 meses
- **Estructura:**

  - **Frontend** (120 horas)

    - HTML/CSS, JavaScript
    - Framework (XOR): React / Vue.js / Angular

  - **Backend** (100 horas)

    - Node.js, Bases de Datos, APIs

  - **Opcionales (OR):**

    - DevOps, Testing, Seguridad

  - **Proyecto Final** (80 horas)

---

### 4. `seeders.py` - Funciones de Seeding

**Cambios en logging:**

- "Sembrando dominios..." → "Sembrando dominios académicos..."
- "Tags sembrados" → "Etiquetas pedagógicas sembradas"
- "Modelos sembrados" → "Planes de estudio sembrados"

---

### 5. `main.py` - Orquestador Principal

**Actualización de mensajes:**

```
📝 CREDENCIALES DE PRUEBA:
  Admin:                admin@example.com / admin123
  Diseñador Curricular: diseñador.curricular@example.com / designer123
  Coordinador Académico: coordinador.academico@example.com / editor123
  Jefe de Carrera:      jefe.carrera@example.com / config123
  Profesor:             profesor@example.com / viewer123
  Evaluador Curricular: evaluador.curricular@example.com / reviewer123
```

---

### 6. `README.md` - Documentación

**Secciones actualizadas:**

- ✅ Título adaptado al contexto educativo
- ✅ Descripción detallada de dominios académicos
- ✅ Documentación completa de planes de estudio de ejemplo
- ✅ Tabla de configuraciones educativas
- ✅ Ejemplos de personalización para contexto académico

---

## 🎓 Conceptos Educativos Implementados

### Tipos de Features en Contexto Curricular

| Tipo Feature  | Uso Educativo                     | Ejemplo                        |
| ------------- | --------------------------------- | ------------------------------ |
| `MANDATORY`   | Asignatura obligatoria            | Matemática I                   |
| `OPTIONAL`    | Asignatura electiva               | Desarrollo Móvil               |
| `XOR_GROUP`   | Elegir una especialización        | Especialización (Dev/Data/Sec) |
| `OR_GROUP`    | Elegir mínimo N asignaturas       | Electivas (min 3 de 5)         |
| `ALTERNATIVE` | Una opción dentro de un grupo XOR | React / Vue / Angular          |

### Propiedades Curriculares

Los features ahora incluyen propiedades educativas:

- `creditos` - Créditos académicos de la asignatura
- `semestre` - Semestre en que se cursa
- `prerequisitos` - Asignaturas previas requeridas
- `horas_teoricas` / `horas_practicas` - Distribución de horas
- `duracion_años` / `duracion_meses` - Duración del programa

---

## 🚀 Uso de los Nuevos Datos

### Ejecutar Seeding

```bash
# En desarrollo (con datos educativos completos)
docker-compose -f docker-compose.dev.yml exec backend python -m app.seed.main

# Verificar en logs
docker-compose -f docker-compose.dev.yml logs backend | grep "🌱"
```

### Datos Creados

Al ejecutar el seeding en modo desarrollo, se crean:

- ✅ 6 usuarios de desarrollo con roles académicos
- ✅ 6 dominios académicos
- ✅ 10 etiquetas pedagógicas
- ✅ 6 recursos educativos
- ✅ 2 planes de estudio completos:
  - Ingeniería en Ciencias Informáticas (5 años)
  - Desarrollo Web Full Stack (6 meses)

---

## 📊 Estadísticas

| Métrica                 | Antes                      | Ahora                      |
| ----------------------- | -------------------------- | -------------------------- |
| Dominios                | 5 genéricos                | 6 académicos               |
| Tags                    | 10 técnicos                | 10 pedagógicos             |
| Recursos                | 4 genéricos                | 6 educativos               |
| Feature Models          | 2 (E-Commerce, Healthcare) | 2 (Ingeniería, Full Stack) |
| Features por modelo     | 7-4                        | 15-10                      |
| Profundidad jerárquica  | 2 niveles                  | 4 niveles                  |
| Configuraciones sistema | 4                          | 10                         |

---

## ✅ Validación

Para verificar que los cambios se aplicaron correctamente:

1. **Ejecutar seeding:**

   ```bash
   docker-compose -f docker-compose.dev.yml exec backend python -m app.seed.main
   ```

2. **Verificar en la API:**

   - GET `/api/v1/domains` - Debe mostrar dominios académicos
   - GET `/api/v1/tags` - Debe mostrar etiquetas pedagógicas
   - GET `/api/v1/feature-models` - Debe mostrar planes de estudio

3. **Login con usuarios académicos:**
   - `diseñador.curricular@example.com` / `designer123`
   - `jefe.carrera@example.com` / `config123`

---

## 🎯 Próximos Pasos Sugeridos

1. **Ampliar planes de estudio:**

   - Agregar más programas de grado
   - Incluir maestrías y doctorados
   - Programas de certificación profesional

2. **Reglas curriculares:**

   - Implementar prerequisitos (requires)
   - Definir exclusiones (excludes)
   - Validar créditos mínimos/máximos

3. **Recursos educativos:**

   - Integrar con LMS (Moodle, Canvas)
   - Agregar más contenidos multimedia
   - Asociar recursos a features específicos

4. **Itinerarios personalizados:**
   - Generar rutas de aprendizaje
   - Considerar perfil del estudiante
   - Exportar a formatos estándar

---

## 📚 Referencias

- **Tesis:** "Plataforma para la Configuración de Modelos de Características Aplicada al Diseño Curricular"
- **Autores:** José Luis Echemendía López, Ernes Valdés Díaz
- **Tutora:** M. Sc. Yadira Ramírez Rodríguez
- **Institución:** Universidad de las Ciencias Informáticas (UCI)

---

**Fecha de actualización:** 24 de noviembre de 2025
