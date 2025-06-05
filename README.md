# Backend

- **Service:** `users`  

[![users](https://codecov.io/gh/emotion-analyzer/backend/branch/develop/graph/badge.svg?token=2NYBBD0MQJ)](https://codecov.io/gh/emotion-analyzer/backend)

- **Service:** `analyzer` 

[![analyzer](https://codecov.io/gh/emotion-analyzer/backend/branch/develop/graph/badge.svg?token=2NYBBD0MQJ)](https://codecov.io/gh/emotion-analyzer/backend)

## 📌 Descripción
> Consultar documentacion de API en https://docs.google.com/document/u/0/d/10Zm-g5byCYIC16gqPxft8NlaIF1dNFdCHV5fKHiCpzw/edit?tab=t.0&pli=1&authuser=0#heading=h.6j7uy3t38onn

> El modelo presente incluye los siguientes modulos
> * users, para registro y logeo de usuarios (necesario para acceder a los otros modulos).
> * scraper para obtener posts de Reddit y Bluesky.
> * analyzer, para analisis emocional de textos aislados o grupos de los mismos.

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


## 📌 Agregado de contenedores
1. Crear carpeta con archivo de Dockerfile correspondiente al nuevo modulo
2. En _docker-compose.yml_ agregar

```
  <module_name>:
    build:
      context: <folder_name>
    container_name: <module_name>
    ...
    networks:
      - kong-network
```

3. En _gateway/kong.yml_ agregar 

```
- name: <module_name>
  url: http://<module_name>:<module_port>
  routes:
  - name: <module>-route
    paths:
    - <route/to/access/module>
```

y al final (esto se puede obviar inicialmente)

```
plugins:
- name: jwt
  service: <module_name>
  config:
    uri_param_names: []
    cookie_names: []
    claims_to_verify:
      - exp
    run_on_preflight: false
```

El sistema se puede acceder mediante
http://localhost:8000/<route/to/access/module>

**IMPORTANTE**

kong quita la ruta especificada en paths. Una ruta accedida como
```
<route/to/access/module/endpoint>
```
desde afuera del modulo, se convierte en
```
</endpoint>
```
dentro del mismo.