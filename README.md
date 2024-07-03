# Proyecto Data Engineering

## Pasos para ejecutar:

- Descarga el zip y ábrelo en Visual Studio Code.
- Abre una terminal:
  - **Abrir entorno virtual (VENV):** `python -m venv venv`
  - **Activar el entorno virtual (VENV):** `source venv/bin/activate` (también podría ser `Scripts` en lugar de `bin`)
  - **Instalar los requisitos en el entorno virtual (VENV):** `pip install -r requirements.txt`
  - **Ejecutar desde la carpeta del proyecto:** `python Proyecto_Data_Engineering`
  - **Ejecutar el docker airflow:** `docker compose up --build`
  - **Desactivar el entorno virtual (VENV):** `deactivate`
  - **Ejecutar el docker airflow:** `docker compose down`
- Luego, puedes eliminar las carpetas `__pycache__` y `venv`.