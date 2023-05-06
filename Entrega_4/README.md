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
La IP asignada por Google se debe de configurar en la variable de entorno del Dockerfile en Backend.

## **Creación de Tópico**

Para crear un tópico, al cual las tareas de compirmir se subirán, se ejecuta el siguiente comando en la consola de Google Cloud:

```bash
gcloud pubsub topics create {nombre_del_topico}
```

El nombre del tópico se debe de actualiza en la variable de entorno del Dockerfile en Backend.

## **Creación de Cuenta de Servicio**

Se debe de crear una cuenta de servico con la finalidad de que las máquinas que se crean en el autoscaling tengan permisos de leer el tópico y escribir en el bucket. Por temas de facilidad y tiempo, se asignan roles de administración tanto para pub/sub como para cloud storage. Esto se hace desde "IAM y Adminbistración" > "Cuentas de Servicio", se da clic en crear una cuenta de servicio, se asigna un nombre para tal cuenta y se da clic en "crear y continuar". En los roles buscamos "Cloud Storage" y agregamos "Administrador de Almacenamiento", luego agregamos otro rol y buscamos "Pub/Sub" y agregamos "Administrador de Pub/Sub". Con esto ya creamos nuestra cuenta de servicio para asignar a la plantilla de instancia.


## **Creación de Plantilla de Instancias**

Para este punto, nos dirigimos a Cloud Engine y seleccionamos "Plantilla de Instancia". En este punto es importante:

- Asignar Un nombre de Plantilla.
- Seleccionar Serie N1, y como tipo de máquina f1-micro.
- En la sección "Identidad y acceso a la API" seleccionar la cuenta de servicio creada anteriormente.
- En opciones avanzadas, seleccionar "Herramientas de redes" y agregar la red creada en la sección de VPC.
- Por último, en la sección de Administración > Automatización se debe de pegar las siguientes secuencias de inicio

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
git clone https://github.com/camandhuercue/Entrega-1---Sistema-de-Conversi-n-Cloud.git
cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_4/Backend/
docker compose up -d
```

También se puede usar el siguiente comando en la consola de Google 

```bash
gcloud compute instance-templates create {nombre_plantilla} --project={nombre_proyecto} --machine-type=f1-micro --network-interface=network-tier=PREMIUM,subnet={nombre_subnet} --metadata=startup-script=sudo\ install\ -m\ 0755\ -d\ /etc/apt/keyrings$'\n'curl\ -fsSL\ https://download.docker.com/linux/debian/gpg\ \|\ sudo\ gpg\ --dearmor\ -o\ /etc/apt/keyrings/docker.gpg$'\n'sudo\ chmod\ a\+r\ /etc/apt/keyrings/docker.gpg$'\n'echo\ \\$'\n'\ \ \"deb\ \[arch=\"\$\(dpkg\ --print-architecture\)\"\ signed-by=/etc/apt/keyrings/docker.gpg\]\ https://download.docker.com/linux/debian\ \\$'\n'\ \ \"\$\(.\ /etc/os-release\ \&\&\ echo\ \"\$VERSION_CODENAME\"\)\"\ stable\"\ \|\ \\$'\n'\ \ sudo\ tee\ /etc/apt/sources.list.d/docker.list\ \>\ /dev/null$'\n'sudo\ apt-get\ update$'\n'sudo\ apt-get\ install\ docker-ce\ docker-ce-cli\ containerd.io\ docker-buildx-plugin\ docker-compose-plugin\ -y$'\n'git\ clone\ https://github.com/camandhuercue/Entrega-1---Sistema-de-Conversi-n-Cloud.git$'\n'cd\ Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_4/Backend/$'\n'docker\ compose\ up\ -d --maintenance-policy=MIGRATE --provisioning-model=STANDARD --service-account={nombre_cuenta_de_servicio} --scopes=https://www.googleapis.com/auth/cloud-platform --region=us-central1 --create-disk=auto-delete=yes,boot=yes,device-name={nombre_plantilla},image=projects/debian-cloud/global/images/debian-11-bullseye-v20230411,mode=rw,size=10,type=pd-balanced --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --reservation-affinity=any
```


## **Creacion de Grupo de Instancias**

Para este punto, vamos a "Compute Engine" > Grupo de instancias y creamos un grupo de instancias.

- Asignar Un nombre de Grupo.
- Seleccionamos la plantilla que creamos anteriormente.
- Seleccionamos varias zonas
- Seleccionamos 1 instancia mínima, 3 máximo.
- poner 600 segundos para coldown
- Creamos los signal que dispara la creación de las máquinas virtuales, para esto en base a las pruebas de carga se puede observar que la RAM es lo que más se consume, para ello usaremos un umbral del 60% del uso de la RAM y un 50% de CPU.

Los comandos se muestran a continuación 

```bash
gcloud beta compute instance-groups managed create {nombre_de_grupo} --project={nombre_de_proyecto} --base-instance-name={nombre_de_grupo} --size=1 --template={nombre_de_plantilla} --zone=us-central1-a --target-distribution-shape=EVEN --instance-redistribution-type=PROACTIVE --list-managed-instances-results=PAGELESS --no-force-update-on-repair && gcloud compute instance-groups managed set-named-ports grupo-backend --project={nombre_del_proyecto} --region=us-central1 --named-ports=flask:8080 && gcloud beta compute instance-groups managed set-autoscaling {nombre_de_grupo} --project={nombre_del_proyecto} --zone=us-central1-a --cool-down-period=600 --max-num-replicas=3 --min-num-replicas=1 --mode=on --target-cpu-utilization=0.5 --update-stackdriver-metric=compute.googleapis.com/instance/memory/balloon/ram_used --stackdriver-metric-utilization-target=60.0 --stackdriver-metric-utilization-target-type=gauge
```

**Nota**: Tener presente que la creación de la imagen de Docker puede tardar aproximadamente 5 minutos debido a que la máquina es muy pequeña en procesamiento.

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
```
