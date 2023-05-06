Video de Sustentación 

[Video de Sustentación](https://uniandes-my.sharepoint.com/:v:/g/personal/c_huertasc_uniandes_edu_co/EVzV2Rd1vLRMgS2BsgDBxUYBmzWYtspjLgJ08nKpefZ_nQ?e=8MxiaS)

El despliegue de la arquitectura se realizó de dos maneras que llevan al mismo resultado, solo ejecute una de las siguientes opciones para crear la infraestructura que contendrá la aplicación:

* [Despliegue de Infraestructura por Cloud Shell](#despliegue-de-infraestructura-por-cloud-shell)

La arquitectura que se establecio crear es mostrada en la siguiente imagen.

![Infraestructura File Compresor GCP.](https://github.com/camandhuercue/Entrega-1---Sistema-de-Conversi-n-Cloud/blob/main/Entrega_3/imgs/Infraestructura_GCP.jpg "Infraestructura File Compresor GCP.")

# **Despliegue de Infraestructura por Cloud Shell**

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

# **Configuración de SQL**

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

Mientras se crea la instancia de SQL, se instala el cliente de postgres en cualquiera de las instancias de Compute Engine, con la finalidad de entrar al abase de datos y poder crear la base de datos y el esquema a utilizar por el desarrollo. Para ello en la consola como root se ejecuta lo siguiente:

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


## **Creacion de Maquinas Virtuales**
---

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
