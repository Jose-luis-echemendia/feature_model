
# Roles y Permisos del Sistema 🎭

Este documento detalla las funciones, operaciones y responsabilidades de cada rol dentro de la plataforma. Comprender estos roles es clave para gestionar el ciclo de vida del diseño curricular de manera efectiva y segura.

---

## 👑 `ADMIN` (Administrador del Sistema)

**Misión:** ¡Control total! El guardián de la plataforma, responsable de su salud, configuración y gestión de usuarios.

| Tabla Afectada        | Crear (POST) | Leer (GET) | Actualizar (PUT/PATCH) | Eliminar (DELETE) | Notas Adicionales                               |
| --------------------- | :----------: | :--------: | :--------------------: | :---------------: | ----------------------------------------------- |
| **`User`**            |      ✅       |     ✅     |           ✅           |         ✅        | Puede crear, modificar y eliminar cualquier usuario. |
| **`Domain`**          |      ✅       |     ✅     |           ✅           |         ✅        | Gestiona las áreas de conocimiento.             |
| **`FeatureModel`**    |      ✅       |     ✅     |           ✅           |         ✅        | Tiene acceso y control sobre todos los modelos. |
| **`Resource` / `Tag`**|      ✅       |     ✅     |           ✅           |         ✅        | Controla todos los activos y metadatos.         |
| **`Configuration`**   |      ✅       |     ✅     |           ✅           |         ✅        | Puede intervenir en cualquier configuración.      |

---

## 🎨 `MODEL_DESIGNER` (Diseñador / Propietario de Modelos)

**Misión:** El arquitecto creativo. Idea, diseña y lidera la construcción de las plantillas maestras (`FeatureModel`).

| Tabla Afectada                 | Crear (POST) | Leer (GET) | Actualizar (PUT/PATCH) | Eliminar (DELETE) | Notas Adicionales                                                              |
| ------------------------------ | :----------: | :--------: | :--------------------: | :---------------: | ------------------------------------------------------------------------------ |
| **`FeatureModel`**             |      ✅       |     ✅     |           ✅           |         ✅        | Solo sobre los modelos de su propiedad (`owner_id`).                             |
| **`FeatureModelVersion`**      |      ✅       |     ✅     |           ✅           |         ✅        | Puede cambiar el estado de `DRAFT` ➡️ `IN_REVIEW`.                              |
| **`Feature`, `Relation`, `Group`** |      ✅       |     ✅     |           ✅           |         ✅        | Edición completa dentro de sus propios modelos.                                |
| **`Resource` / `Tag`**         |      ✅       |     ✅     |           ✅           |         ✅        | Puede crear y asociar nuevos recursos y etiquetas.                             |
| **`FeatureModelCollaborator`** |      ✅       |     ✅     |           ✅           |         ✅        | 🤝 ¡Clave! Puede invitar y quitar `MODEL_EDITOR`s de sus proyectos.            |
| **`Configuration`**            |      ❌       |     ✅     |           ❌           |         ❌        | Puede ver configuraciones, pero su rol no es crearlas.                         |

---

## ✍️ `MODEL_EDITOR` (Editor / Colaborador de Modelos)

**Misión:** El especialista colaborador. Aporta su conocimiento editando modelos a los que ha sido invitado.

| Tabla Afectada                 | Crear (POST) | Leer (GET) | Actualizar (PUT/PATCH) | Eliminar (DELETE) | Notas Adicionales                                                                |
| ------------------------------ | :----------: | :--------: | :--------------------: | :---------------: | -------------------------------------------------------------------------------- |
| **`FeatureModel`**             |      ❌       |     ✅     |           ✅           |         ❌        | Solo puede leer y actualizar modelos donde es colaborador. No puede crear ni borrar. |
| **`FeatureModelVersion`**      |      ✅       |     ✅     |           ✅           |         ✅        | 🚫 No puede cambiar el estado a `IN_REVIEW`.                                      |
| **`Feature`, `Relation`, `Group`** |      ✅       |     ✅     |           ✅           |         ✅        | Edición completa, pero solo dentro de los modelos permitidos.                    |
| **`Resource` / `Tag`**         |      ✅       |     ✅     |           ✅           |         ✅        | Puede contribuir con nuevos recursos y etiquetas.                                |
| **`FeatureModelCollaborator`** |      ❌       |     ✅     |           ❌           |         ❌        | Puede ver quién más colabora, pero no gestionar la lista.                          |

---

## ✅ `REVIEWER` (Revisor / Publicador)

**Misión:** El guardián de la calidad. Valida y aprueba los modelos antes de que puedan ser utilizados.

| Tabla Afectada                 | Crear (POST) | Leer (GET) | Actualizar (PUT/PATCH) | Eliminar (DELETE) | Notas Adicionales                                                                    |
| ------------------------------ | :----------: | :--------: | :--------------------: | :---------------: | ------------------------------------------------------------------------------------ |
| **`FeatureModel`**             |      ❌       |     ✅     |           ❌           |         ❌        | Su función no es editar el contenido, solo leerlo para evaluarlo.                    |
| **`FeatureModelVersion`**      |      ❌       |     ✅     |           ✅           |         ❌        | 🎯 ¡Acción principal! Cambia el estado: `IN_REVIEW` ➡️ `PUBLISHED` o `DRAFT`.         |
| **`Feature`, `Relation`, etc.**|      ❌       |     ✅     |           ❌           |         ❌        | Puede inspeccionar todos los componentes del modelo para su correcta evaluación.     |

---

## 🔧 `CONFIGURATOR` (Configurador / Asesor)

**Misión:** El constructor práctico. Utiliza las plantillas aprobadas (`PUBLISHED`) para ensamblar soluciones finales (`Configuration`).

| Tabla Afectada        | Crear (POST) | Leer (GET) | Actualizar (PUT/PATCH) | Eliminar (DELETE) | Notas Adicionales                                                                    |
| --------------------- | :----------: | :--------: | :--------------------: | :---------------: | ------------------------------------------------------------------------------------ |
| **`FeatureModel`**    |      ❌       |     ✅     |           ❌           |         ❌        | 📖 Solo puede leer modelos en estado `PUBLISHED`.                                     |
| **`Configuration`**   |      ✅       |     ✅     |           ✅           |         ✅        | ✨ ¡Su función principal! Crea, modifica y elimina sus propias configuraciones. |
| **`Resource` / `Tag`**|      ❌       |     ✅     |           ✅           |         ❌        | Puede ver los recursos y etiquetas, y etiquetar sus propias `Configurations`.       |

---

## 👓 `VIEWER` (Observador / Lector)

**Misión:** El espectador. Consulta la información pública y final sin poder alterarla.

| Tabla Afectada                 | Crear (POST) | Leer (GET) | Actualizar (PUT/PATCH) | Eliminar (DELETE) | Notas Adicionales                                                                |
| ------------------------------ | :----------: | :--------: | :--------------------: | :---------------: | -------------------------------------------------------------------------------- |
| **`FeatureModel` (Publicado)** |      ❌       |     ✅     |           ❌           |         ❌        | Puede ver las plantillas de cursos que la institución ofrece.                      |
| **`Configuration` (Pública)**  |      ❌       |     ✅     |           ❌           |         ❌        | Puede consultar itinerarios o planes de estudio ya definidos.                     |
| **Cualquier otra tabla**       |      ❌       |     ❌     |           ❌           |         ❌        | Acceso muy restringido, solo a los productos finales y públicos del sistema. |