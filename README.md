# Backend

Este es el modulo de _backend_ de Pulse Affect: una herramienta que utiliza modelos de inteligencia artificial para realizar analisis
emocional orientado al lenguaje castellano. Se recomienda una GPU con capacidad CUDA para una mejor experiencia, pero no es 
necesaria.

## 📌 API
> [Link](https://docs.google.com/document/u/0/d/10Zm-g5byCYIC16gqPxft8NlaIF1dNFdCHV5fKHiCpzw)

## 📌 Modulos
> La arquitectura presente incluye los siguientes modulos
> * users: maneja todo lo relacionado a usuarios (registro, inicio de session, actualizacion de detalles, etc.)
> * scraper: para obtener posts de Reddit y Bluesky. Modular para permitir incorporacion de nuevas redes sociales.
> * query_processor: coordina el scraper y analyzer y realiza el mapeo final de los estados afectivos a un set de emociones mas reducido.
> * analyzer: realiza el analisis emocional de los textos recibidos 
> * el resto de los elementos se pueden consultar en el diagrama de arquitectura

## 📌 Ejecución
1. Clonar el repositorio:
```bash
git clone git@github.com:emotion-analyzer/backend.git
```

2. Correr la app 
```bash
docker compose up
```

Algunos modulos requieren de credenciales especificas. Consultar _test.env_

Se recomienda asi mismo modificar toda credencial de acceso presente en el _docker-compose_ previo al lanzamiento.
