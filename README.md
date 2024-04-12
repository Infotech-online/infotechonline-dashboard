# Infotech Online

## Descripción
Infotech Online es un ecommerce que utiliza el modelo de ventas de dropshipping. Está desarrollado en WordPress con el plugin de Woocommerce. La tienda cuenta con varios proveedores, pero solo dos de ellos (Ingram e Intcomex) disponen de API para conectar su catálogo de productos en tiempo real con nuestra tienda.

## Dashboard
El dashboard se encarga de comunicar la API de nuestra tienda (Woocommerce) con las APIs de los proveedores. Se actualiza la disponibilidad y el precio del producto en tiempo real. Está desarrollado en Python con el framework web Flask. Para la comunicación entre el frontend y el backend, se utiliza jQuery con consultas AJAX.

## Almacenamiento de Datos
Para minimizar el tiempo de ejecución, se almacena el estado actual de los productos en archivos JSON. Sin estos archivos, sería necesario realizar consultas a la API de Woocommerce por cada producto que se va a actualizar, lo que ralentizaría el proceso. Por esta razón, se guarda la información o estado actual de cada producto en formato JSON.

### Archivos JSON
- `ingram_products.json`: Contiene la información de los productos proporcionados por el proveedor Ingram.
- `intcomex_products.json`: Contiene la información de los productos proporcionados por el proveedor Intcomex.
- `logs.json`: Guarda la información de cada proceso realizado, como actualizaciones o la adición de nuevos productos al archivo JSON.
