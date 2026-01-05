# 📊 Diagramas del Sistema - Guía de Edición

Esta carpeta contiene los diagramas del sistema en formato **PlantUML (.puml)**, que son archivos de texto plano editables.

## 📁 Archivos Disponibles

### Diagramas Generales del Sistema:
1. **componentes.puml** - Diagrama de componentes del backend Flask
2. **arquitectura.puml** - Diagrama de arquitectura del sistema completo
3. **arquitectura_backend.puml** - Diagrama de arquitectura del backend con tecnologías
4. **arquitectura_fisica.puml** - Diagrama de arquitectura física (deployment)
5. **secuencia.puml** - Diagrama de secuencia del flujo de juego completo

### Diagramas de Flujo:
6. **flujo_modelo_ia.puml** - Diagrama de flujo completo del modelo de IA adaptativo
7. **flujo_modelo_ia_simple.puml** - Versión simplificada del flujo de IA

### Diagramas de Casos de Uso:
8. **casos_de_uso_completo.puml** - Diagrama completo con todos los actores y casos de uso
9. **casos_de_uso_adulto_mayor.puml** - Casos de uso del adulto mayor (HU1, HU4, HU5)
10. **casos_de_uso_terapeuta.puml** - Casos de uso del terapeuta (HU3, HU6)
11. **casos_de_uso_sistema.puml** - Casos de uso automáticos del sistema (HU2, HU7)

### Diagramas de Secuencia por Historia de Usuario:
12. **HU1_seleccion_minijuego.puml** - Selección de minijuego por adulto mayor
13. **HU2_registro_desempeno.puml** - Registro automático de métricas
14. **HU3_ajuste_adaptativo_ia.puml** - Ajuste de dificultad mediante IA
15. **HU4_dificultad_dinamica.puml** - Adaptación dinámica según rendimiento
16. **HU5_interfaz_accesible.puml** - Interacción con interfaz accesible
17. **HU6_historial_progreso.puml** - Consulta de historial por terapeuta
18. **HU7_configuracion_especifica.puml** - Configuración específica por juego

---

## 🛠️ Cómo Editar los Diagramas

### Opción 1: Visual Studio Code (Recomendado) ⭐

1. **Instalar la extensión PlantUML:**
   - Abre VS Code
   - Ve a Extensions (Ctrl+Shift+X)
   - Busca "PlantUML" de jebbs
   - Instala la extensión

2. **Requisito previo - Instalar Java:**
   ```bash
   # Verifica si tienes Java instalado
   java -version
   ```
   Si no tienes Java, descárgalo de: https://www.java.com/download/

3. **Editar y visualizar:**
   - Abre cualquier archivo `.puml` en VS Code
   - Presiona `Alt+D` para vista previa
   - Edita el texto y la vista se actualiza automáticamente
   - Para exportar: Click derecho → PlantUML: Export Current Diagram

### Opción 2: Editor Online (Más Fácil) 🌐

1. **Ir a PlantUML Online Editor:**
   - https://www.plantuml.com/plantuml/uml/

2. **Copiar y pegar:**
   - Abre uno de los archivos `.puml`
   - Copia todo el contenido
   - Pégalo en el editor online
   - Verás el diagrama generado en tiempo real

3. **Editar y descargar:**
   - Modifica el texto según necesites
   - El diagrama se actualiza automáticamente
   - Descarga como PNG, SVG o PDF

### Opción 3: PlantUML Desktop

1. **Descargar PlantUML:**
   - https://plantuml.com/download

2. **Ejecutar con Java:**
   ```bash
   java -jar plantuml.jar componentes.puml
   ```
   - Esto generará una imagen PNG del diagrama

---

## ✏️ Guía Rápida de Edición

### Cambiar Colores
```plantuml
skinparam component {
    BackgroundColor<<controller>> #BBDEFB  ' Cambia este código de color
}
```

### Agregar Componentes
```plantuml
[NuevoComponente] as nuevo <<service>>
```

### Agregar Relaciones
```plantuml
componenteA --> componenteB : descripción
```

### Agregar Notas
```plantuml
note right of componenteA
  Tu nota aquí
end note
```

### Cambiar Título
```plantuml
title Tu Nuevo Título
```

---

## 🎨 Herramientas Alternativas

### Draw.io (diagrams.net)
- Puedes importar archivos PlantUML
- Editor visual más intuitivo
- https://app.diagrams.net/

### Mermaid Live Editor
- Similar a PlantUML pero con sintaxis diferente
- https://mermaid.live/

---

## 📚 Recursos de Aprendizaje

- **Guía de PlantUML:** https://plantuml.com/guide
- **Galería de ejemplos:** https://real-world-plantuml.com/
- **Sintaxis de componentes:** https://plantuml.com/component-diagram
- **Sintaxis de secuencia:** https://plantuml.com/sequence-diagram

---

## 💡 Tips de Edición

1. **Mantén la indentación** para mejor legibilidad
2. **Usa comentarios** con `'` para documentar cambios
3. **Guarda versiones** antes de hacer cambios grandes
4. **Prueba en el editor online** antes de exportar

---

## 🚀 Exportar Diagramas

### Desde VS Code:
1. Click derecho en el archivo `.puml`
2. "PlantUML: Export Current Diagram"
3. Selecciona formato (PNG, SVG, PDF)

### Desde línea de comandos:
```bash
# Exportar a PNG
java -jar plantuml.jar -tpng componentes.puml

# Exportar a SVG (escalable)
java -jar plantuml.jar -tsvg componentes.puml

# Exportar a PDF
java -jar plantuml.jar -tpdf componentes.puml
```

---

## 🔧 Solución de Problemas

**Error: "Graphviz not found"**
- Instala Graphviz: https://graphviz.org/download/
- O usa el modo de renderizado alternativo en PlantUML

**No se actualiza la vista previa en VS Code**
- Presiona `Ctrl+Shift+P` → "PlantUML: Preview Current Diagram"

**Caracteres especiales no se muestran**
- Asegúrate que el archivo esté en UTF-8
- En VS Code: Click en "UTF-8" en la barra inferior

---

¿Necesitas ayuda? Contacta al equipo de desarrollo.
