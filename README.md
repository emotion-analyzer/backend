# Backend

## 📌 Descripción
> Consultar documentacion de API en https://docs.google.com/document/u/0/d/10Zm-g5byCYIC16gqPxft8NlaIF1dNFdCHV5fKHiCpzw/edit?tab=t.0&pli=1&authuser=0#heading=h.6j7uy3t38onn

> El modelo presente incluye los siguientes modulos
> * users, para registro y logeo de usuarios (necesario para acceder a los otros modulos)
> * scraper para obtener posts de reddit

## 📌 Ejecución

1. Clonar el repositorio, ingresar al backend:
```bash
git clone https://github.com/nicolas-vazquez/emotion-analyzer.git
cd backend
```

2. Correr la app:
```bash
docker-compose up
```

3. (Opcional para cada modulo excepto _gateway_) Instalar dependencias y ejecutar tests/lint :
```bash
pip install --upgrade
pip install -r requirements.txt
nox
```

## 📌 Agregado de contenedores
1. Crear carpeta con archivo de Dockerfile correspondiente al nuevo modulo
2. En _docker-compose.yml_ agregar

```
  <module_name>:
    build:
      context: <folder_name>
    container_name: <module_name>
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
http://localhost:8000/<path_to_endpoint>

**IMPORTANTE**

kong quita la ruta especificada en paths. Una ruta accedida como
```
<route/to/access/module>
```
desde afuera del modulo, se convierte en el endpoint
```
</module>
```
dentro del mismo.