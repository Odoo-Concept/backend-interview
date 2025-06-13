# repo-template

Este repositorio es una plantilla diseñada para crear nuevos proyectos de cliente en Odoo. Su objetivo es proporcionar una estructura inicial con configuraciones y herramientas predefinidas para facilitar el desarrollo y mantenimiento de proyectos.

## Archivos y carpetas principales

A continuación, se describe brevemente la función de los archivos y carpetas incluidos en este repositorio:

- **main_app/**: Este es el módulo principal de Odoo. Sirve como punto de entrada para el proyecto. **Es importante que al crear un nuevo repositorio, cambies el nombre de este módulo por el nombre del cliente, todo en minúsculas y usando guiones bajos para separar palabras (por ejemplo, `nombre_cliente`).**
  
- **.github/**: Contiene configuraciones para GitHub Actions, como flujos de trabajo automatizados para pruebas y mantenimiento del repositorio.
  
- **.pre-commit-config.yaml**: Configuración para pre-commit, una herramienta que ejecuta verificaciones automáticas antes de realizar commits, como formateo de código y análisis estático.
  
- **.editorconfig**: Define reglas de estilo de código para editores de texto compatibles, como tamaño de indentación y eliminación de espacios en blanco al final de las líneas.
  
- **.gitignore**: Lista de archivos y carpetas que deben ser ignorados por Git.
  
- **.pylintrc** y **.pylintrc-mandatory**: Configuraciones para pylint, una herramienta de análisis estático para código Python. Incluyen reglas opcionales y obligatorias.
  
- **.ruff.toml**: Configuración para Ruff, una herramienta de linting para Python.
  
- **prettier.config.cjs**: Configuración para Prettier, una herramienta de formateo de código.
  
- **eslint.config.cjs**: Configuración para ESLint, una herramienta de análisis estático para JavaScript.
  
- **pyproject.toml**: Archivo de configuración para herramientas de construcción y dependencias en Python.
  
- **LICENSE**: Licencia del proyecto (actualmente Apache 2.0).
  
- **README.rst**: Archivo de documentación para el módulo `main_app`.

## Personalización del módulo `main_app`

El módulo `main_app` es un punto de partida genérico. Para adaptarlo a un cliente específico:

1. Cambia el nombre de la carpeta `main_app` por el nombre del cliente en minúsculas y con guiones bajos (por ejemplo, `nombre_cliente`).
2. Actualiza el archivo `__manifest__.py` dentro del módulo para reflejar el nombre del cliente y otros detalles relevantes.
3. Revisa y personaliza el contenido del archivo `README.rst` para describir el propósito del módulo.

Con esta plantilla, puedes iniciar rápidamente nuevos proyectos de cliente en Odoo con una estructura consistente y herramientas preconfiguradas.
