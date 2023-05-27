Video de Sustentación 

[Video de Sustentación](https://uniandes-my.sharepoint.com/:v:/g/personal/c_huertasc_uniandes_edu_co/EVzV2Rd1vLRMgS2BsgDBxUYBmzWYtspjLgJ08nKpefZ_nQ?e=8MxiaS)

El despliegue de la arquitectura se realizó de dos maneras que llevan al mismo resultado, solo ejecute una de las siguientes opciones para crear la infraestructura que contendrá la aplicación:

* [Despliegue de Infraestructura por Cloud Shell](#despliegue-de-infraestructura-por-cloud-shell)

La arquitectura que se establecio crear es mostrada en la siguiente imagen.

![Infraestructura File Compresor GCP.](https://github.com/camandhuercue/Entrega-1---Sistema-de-Conversi-n-Cloud/blob/main/img/Arquitectura-Cloud.png "Infraestructura File Compresor GCP.")

# **Despliegue de Infraestructura por Cloud Shell/Console**

Ejecute los siguientes comando configurar la region y zona:

```bash
gcloud config set project {project_name}
```

```bash
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
```

Cree las variables de entorno con el id del poyecto, la region y la zona.

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=$(gcloud config get-value compute/region)
export ZONE=$(gcloud config get-value compute/zone)
export PRIVATENET='net-pruebas'
export PRIVATESUBNET='subnet-pruebas'
export FIREWALL_ALLOW_SSH='privatenet-allow-ssh'
export FIREWALL_ALLOW_INTERNAL='privatenet-allow-internal'
export FRONTEND='frontend'
export BACKEND='backend'
export WORKER='worker'
export FILE_SERVER='file-server'

```

## **Creacion de VPC**
---

Ejecute el siguiente comando para crear una red privada

```bash
gcloud compute networks create $PRIVATENET --subnet-mode=custom
```

Ejecutar el sigueinte comando para crear una subred privada **<name_privatesubnet>** 

```bash
gcloud compute networks subnets create $PRIVATESUBNET \
--network=$PRIVATENET \
 --region=$REGION \
 --range=172.16.0.0/24
```

## **Creacion de reglas de Firewall**
---

Ejecute el siguiente comando para permitir el acceso a todas las maquinas desde local.

```bash
gcloud compute firewall-rules create $FIREWALL_ALLOW_SSH \
--direction=INGRESS \
--priority=1000 \
--network=$PRIVATENET \
--action=ALLOW \
--rules=tcp:22,tcp:8080,tcp:5001 \
--source-ranges=0.0.0.0/0
```

Ejecute el siguiente comando para permitir todas las comunicaciones entre las redes internas.

```bash
gcloud compute firewall-rules create $FIREWALL_ALLOW_INTERNAL \
 --direction=INGRESS \
 --priority=1000 \
 --network=$PRIVATENET \
 --action=ALLOW \
 --rules=tcp:0-65535,udp:0-65535,icmp \
 --source-ranges=172.16.0.0/24
```

## **Configuración de SQL**

Dentro de los archivos de Terraform tambien se deja la opcion de crear la instancia que soportara a Cloud SQL sin embargo este proceso tarda alrededor de 18 Minutos a comparacion de lo 5 Minutos que tarda al crearse por consola. En caso de querer probar que se puede desplegar la instancia SQL con Terraform descomnete el modulo que se encuentra en el archivo ***cloud-sql.tf***

Con respecto a la instancia de SQL, se crea con el servio de Cloud SQL de Google, seleccionando como motor Postgres. Las características son las siguientes:

- Versión: 14.
- Ambiente: Desarrollo.
- Region y Zona: US Central 1 - a.
- VCPU: 1
- RAM: 4
- SSD: 10GB sin aumentos automáticos.
- Sin IP pública y se crea una conexión privada entre Google y nuestra VPC con rango 172.16.2.0/14.
- Sin Copias de seguridad ni protección de eliminación.
- Se deja el restante por defecto.

> **Nota:** 
Desde este punto se debe ejecutar tanto al desplegar con Cloud Shell como con Terraform.

Mientras se crea la instancia de SQL, se instala el cliente de postgres en cualquiera de las instancias de Compute Engine (se puede usar la misma instancia que se creará en el punto de "Creacion de Instancias Para Compilar Imagenes"), con la finalidad de entrar a la base de datos y poder crear la base de datos y el esquema a utilizar por el desarrollo. Para ello en la consola como root se ejecuta lo siguiente:

```bash
apt-get update && apt-get install postgresql-client -y
```

Una vez instalado el cliente, conectarse a la base de datos con el siguiente comando:


```bash
psql -h {ip-db} -U postgres
```

La contraseña que estamos utilizando para la base de datos es SuP3r$3cUr#P$$!!

Una vez en la base de datos ejecutamos lo siguiente para poder configurarla según se necesita en el desarrollo:

```bash
CREATE DATABASE compress_database;
\connect compress_database;
CREATE SCHEMA compress_schema;
```
La IP asignada por Google se debe de configurar en la variable de entorno del Dockerfile en Backend.

## **Configuración de Zona DNS Privada**

Para mantener las modificaciones de código al mínimo y con el objetivo de poder automatizar el despliegue de las funcionalidades como lo son Cloud Functions y Autoscaling, se decide la creación de una zona privada de DNS para apuntar a la instancia de SQL. Para ello nos dirigimos al servicio de Cloud DNS y creamos una zona:

- Seleccionamos un nombre descriptivo.
- Seleccionamos que sea una zona privada.
- Asignamos un dominio, en este caso es soluciones.cloud

El restante se deja por default. Una vez la zona esté arriba, entramos en ella y agregamos un estandar:

- Es del tipo A
- En nuestro caso, seleccionamos el nombre de dominio sql.soluciones.cloud y apuntamos a la IP que nos asignó la SQL.

Este mismo dominio ya se encuentra en el código desarrollado.

## **Creación de Tópico**

Para crear un tópico, al cual las tareas de compirmir se subirán, se ejecuta el siguiente comando en la consola de Google Cloud:

```bash
gcloud pubsub topics create {nombre_del_topico}
```

El nombre del tópico se debe de actualiza en la variable de entorno del Dockerfile en Backend.

## **Creación de Cuenta de Servicio**

Se debe de crear una cuenta de servico con la finalidad de que las máquinas que se crean en el autoscaling tengan permisos de leer el tópico y escribir en el bucket. Por temas de facilidad y tiempo, se asignan roles de administración tanto para pub/sub como para cloud storage. Esto se hace desde "IAM y Adminbistración" > "Cuentas de Servicio", se da clic en crear una cuenta de servicio, se asigna un nombre para tal cuenta y se da clic en "crear y continuar". En los roles buscamos "Cloud Storage" y agregamos "Administrador de Almacenamiento", luego agregamos otro rol y buscamos "Pub/Sub" y agregamos "Administrador de Pub/Sub", por último buscamos "Artifact Registry" y seleccionamos "Administrador de Artifact Regitry". Con esto ya creamos nuestra cuenta de servicio para asignar a la plantilla de instancia.

## **Creacion de Instancias Para Compilar Imagenes**

Como el objetivo principal es crear instancias de Cloud Run, debemos de publicar nuestras imagenes en Artifact Registry, para ello necesitamos una instancia de Compute Engine donde se compilará las imagenes de Docker para poder desplegarlas posteriormente. Para ello se debe de crear una instancia del tamaño que se acomode a las necesidades de lo que deseen realizar. Recordar que esta instancia debe de pertenecer a la red creada anteriormente y tener asignada la cuenta de servicio que se creó en el paso anterior. Una vez creada, ejecutar los siguientes comandos para poder crear las imagenes de Docker y cargarlas en Arctifacts Registry.

Instalación Docker 

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

```bash
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

```bash
sudo apt-get update
```

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```



## **Creacion de Función para Worker**

El worker en esta ocasión funcionará sobre una función en Cloud Function, para esto crearemos una función con las siguientes características al momento de la creación:

- Versión 2
- Estar en la misma región que lo anterior.
- Tener como trigger el pub/sub creado en el paso anterior, ya que esta tarea se dispara con la carga de una nueva tarea.
- Para mantener las restricciones iniciales, se crea con solo 614MB de RAM y un solo núcleo. Al igual que el grupo de auto-scaling, se mantienen la restricción de mínimo una sola maquina 3 máximo. Es importante que en este punto, en la sección de "Cuenta de servicio del entorno de ejecución" que encontramos en  "Configuración del entorno de ejecución, la compilación, las conexiones y la seguridad" se seleccione la cuenta de servicio.
- Con respecto al tráfico, como solo se perminten conexiones internas a la base de datos, se crea una red específica para la Función y se asocia a la red interna creada anteriormente, esto con la finalidad de que la función alcance la SQL.

Con respecto al entorno de ejecución, utilizaremos la última versión de python disponible que es la 3.11 y subiremos la carpeta comprimida que se encuentra en la sección de Function de la presente entrega.


## **Creacion de Maquinas Virtuales**

Ejecute el siguiente comando para crear las máquinas virtuales necesarias para la ejecución de la aplicación.

```bash
gcloud compute instances create $FRONTEND \
--subnet $PRIVATESUBNET \
--zone $ZONE \
--private-network-ip 172.16.0.4 \
--machine-type f1-micro

gcloud compute instances create $BACKEND \
--subnet $PRIVATESUBNET \
--zone $ZONE \
--private-network-ip 172.16.0.5 \
--machine-type f1-micro
```
