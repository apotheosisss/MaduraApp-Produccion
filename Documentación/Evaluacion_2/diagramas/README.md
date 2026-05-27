# Diagramas — fuentes Mermaid

Esta carpeta contiene las **fuentes Mermaid** de los diagramas embebidos en los documentos de las vistas 4+1. Se mantienen separados por si se requiere exportarlos a formato PNG/SVG (por ejemplo, para incluirlos en una presentación PowerPoint o un PDF compilado).

> **Nota:** los diagramas ya están embebidos directamente en los archivos `.md` de las vistas. Esta carpeta es opcional — solo necesaria si se requieren los diagramas como imágenes independientes.

---

## 🖼️ Exportar Mermaid a PNG/SVG

### Opción 1 — Mermaid Live Editor (UI web)

1. Abrir https://mermaid.live
2. Copiar el bloque mermaid (sin los ``` que lo encierran).
3. Click en "Export" → PNG / SVG.

### Opción 2 — Mermaid CLI

```bash
# Instalar mermaid-cli (Node.js requerido)
npm install -g @mermaid-js/mermaid-cli

# Convertir un .mmd a PNG
mmdc -i diagrama.mmd -o diagrama.png -t default -b white

# Convertir todos los .mmd de la carpeta
for f in *.mmd; do
  mmdc -i "$f" -o "${f%.mmd}.png" -t default -b white
done
```

### Opción 3 — Extensión VSCode

Instalar "Markdown Preview Mermaid Support" + "Mermaid Markdown Syntax Highlighting" en VSCode. Permite previsualización directa y export desde el preview.

---

## 📋 Inventario de diagramas embebidos

| Documento fuente | Tipo de diagrama |
|------------------|-----------------|
| `01_Vista_Logica.md` | Class diagram (UML) |
| `01_Vista_Logica.md` | Component diagram |
| `02_Vista_Procesos.md` | Sequence diagram — CU-01 Escaneo con cámara |
| `02_Vista_Procesos.md` | Flowchart — flujo completo con bifurcaciones |
| `02_Vista_Procesos.md` | State diagram — máquina de estados `ScanState` |
| `02_Vista_Procesos.md` | Graph LR — concurrencia inter-sistemas |
| `03_Vista_Desarrollo.md` | Layered architecture — Backend |
| `03_Vista_Desarrollo.md` | MVVM architecture — Frontend |
| `03_Vista_Desarrollo.md` | CI/CD flow |
| `04_Vista_Fisica.md` | Deployment diagram — topología cloud |
| `04_Vista_Fisica.md` | Deployment diagram — UML stereotypes |
| `05_Vista_Escenarios.md` | Use case diagram |
| `06_Mockups_y_Wireframes.md` | State diagram — flujo de navegación |
| `09_Procedimientos_Backup.md` | Graph LR — flujo de backup/restore |

---

*Si se necesita un diagrama en particular como imagen aislada, exportarlo siguiendo las opciones de arriba y guardarlo aquí con nombre descriptivo (ej. `vista_logica_componentes.png`).*
