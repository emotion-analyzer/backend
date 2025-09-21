# Backend

## 📌 Descripción
> Consultar documentacion de API en https://docs.google.com/document/u/0/d/10Zm-g5byCYIC16gqPxft8NlaIF1dNFdCHV5fKHiCpzw

> El modelo presente incluye los siguientes modulos
> * users: maneja todo lo relacionado a usuarios (registro, inicio de session, actualizacion de detalles, etc.)
> * scraper: para obtener posts de Reddit y Bluesky. Modular para permitir incorporacion de nuevas redes sociales.
> * query_processor: coordina el scraper y analyzer y realiza el mapeo final de los estados afectivos a un set de emociones mas reducido.
> * analyzer: realiza el analisis emocional de los textos recibidos 

## 📌 Ejecución

1. Clonar el repositorio:
```bash
git clone git@github.com:emotion-analyzer/backend.git
```

2. Correr la app  (**IMPORTANTE**: para usar una base de datos local, descomentar DATABASE_URL=...)
```bash
docker compose up
```

Algunos modulos requieren de credenciales especificas. Consultar _test.env_ 

(Opcional). Instalar dependencias y ejecutar tests/lint :
```bash
cd <service>
pip install --upgrade pip
pip install -r requirements.txt -r dev-requirements.txt
nox
```

(Opcional). Para ejecucion local de modulos especificos  :
```bash
cd <service>
fastapi run --reload
```
De forma predeterminada esto carga el .env especificado en **APP_ENV** o bien _test.env_