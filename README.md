# API Portfolio Data y Dividendos

Proyecto de APIs para portfolios y dividendos desarrollado con Django y Django REST Framework. Incluye múltiples APIs REST y testing. 

## Características Principales
* **ViewSets y Router** — endpoints CRUD generados automáticamente
* **Campos calculados** — precio medio ponderado, YOC y dividendo anual sin guardar en BD
* **Yahoo Finance** — precio de mercado en tiempo real por ticker
* **Tests con pytest** — cobertura de lógica de negocio
* **Endpoints personalizados** — resumen de portfolio, alertas sin dividendos, las 3 posiciones que han proporcionado mas dividendos y más...

## Stack Tecnológico
* **Backend:** Python 3.x, Django 6.x
* **API:** Django REST Framework
* **API Externa:** Yahoo Finance


## Tests
```bash
pytest
```
Incluye tests de las funciones basicas del proyecto

## Instalación rápida
1. Crear y activar el entorno virtual
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar migraciones: `python manage.py migrate`
4. Levantar el servidor: `python manage.py runserver`