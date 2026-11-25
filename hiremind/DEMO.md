# Demo en vivo: 3 usuarios a la vez

Una sola laptop corre HireMind y el modelo. Los otros 2 usuarios entran desde su celular o laptop por el navegador, en el mismo WiFi o hotspot. **No hace falta llevar 3 computadoras.**

```
 Laptop principal (16 GB)                       Celular / laptop 2 y 3
 ┌──────────────────────────────┐   WiFi o      ┌───────────────────────┐
 │ LM Studio · Qwen3-4B ×3      │   hotspot     │ navegador              │
 │ HireMind  0.0.0.0:8000  ◄────┼───────────────┤ http://192.168.x.x:8000│
 └──────────────────────────────┘               └───────────────────────┘
```

Todo lo prepara y lo revisa un solo comando:

```bash
cd hiremind
python demo.py            # Windows: py demo.py
```

---

## 1. En casa, una sola vez (con internet)

1. **Traer el código**
   ```bash
   git clone git@github.com:DanMeraDev/hiremind.git    # o, si ya está: git pull
   cd hiremind/hiremind
   ```
2. **Instalar** si la laptop no los tiene: Python 3.12+, Node.js 20+ y [LM Studio](https://lmstudio.ai). Abra LM Studio una vez para que se instale el comando `lms`, y luego cierre y abra la terminal.
3. **Descargar el modelo** (≈2,5 GB): `lms get qwen/qwen3-4b-2507`
4. **Correo** (opcional): el archivo `.env` no está en git porque tiene la contraseña de Gmail. Cópielo de la otra PC por USB, o copie `.env.example` como `.env` y llénelo. Sin `.env` la app funciona igual, pero al seleccionar un candidato no envía el correo.
5. **Vacantes del grupo:** la base de datos no viaja por git, así que la laptop empieza vacía. Esto crea las 4 vacantes sin evaluar CV:
   ```bash
   python demo.py --vacantes --revisar
   ```
6. **Ensayo general:**
   ```bash
   python demo.py --revisar
   ```
   Tiene que terminar en `Todo listo`. La primera vez crea `.venv`, instala dependencias y compila la interfaz (3–5 min). Cada `[X]` trae debajo cómo arreglarlo.

## 2. El día de la exposición

1. Conecte la laptop al **hotspot de un celular**. Es lo más seguro, porque muchas redes de universidad no dejan que los equipos se vean entre sí.
2. Cierre Chrome con muchas pestañas, Discord, Teams y todo lo que no se use. Con 3 usuarios se usan unos 14 GB.
3. Arranque:
   ```bash
   cd hiremind
   python demo.py
   ```
   Al final muestra algo así:
   ```
   En esta PC:          http://localhost:8000
   Otros dispositivos:  http://192.168.43.120:8000
   ```
4. Los otros 2 conectan su celular al **mismo hotspot** y abren la segunda dirección.
5. Al terminar, **Ctrl+C**. La app deja de estar abierta a la red.

> **Windows:** la primera vez sale el aviso del firewall: marque **Redes privadas** y acepte. Si el hotspot aparece como red pública, cámbielo a privada en Configuración > Red e Internet.
> **Linux con firewall** (Fedora Server, Ubuntu con ufw): `demo.py` avisa y da el comando para abrir el puerto.

## 3. Guion de la demo (≈4 min)

| Quién | Qué hace |
|---|---|
| Laptop principal | Proyecta la app. Abre la vacante **Auxiliar de farmacia** y sube 5 CV de `datos/seeds/farmareds/` |
| Usuario 2 | Al mismo tiempo, vacante **Cocinero/a**, sube 5 CV de `datos/seeds/cocinero/` (puede pasarlos al celular antes) |
| Usuario 3 | Al mismo tiempo, vacante **Técnico/a de redes**, sube 5 CV de `datos/seeds/tecnico_redes/` |
| Todos | Muestran que las 3 barras avanzan en paralelo. Luego abren el ranking de cada vacante |
| Laptop principal | Selecciona a un candidato: correo y preguntas de entrevista |

Qué decir, con los números medidos (`evaluacion/benchmark.json`, diapositiva 14):

- Con 3 usuarios a la vez se procesan **6,8 CV por minuto**, contra 3,6 con uno solo, sin errores.
- Cada CV tarda un poco más (≈26 s contra ≈17 s), porque el modelo atiende a los 3 a la vez.
- Todo corre en esta laptop: ningún CV sale a internet.

## 4. Si algo falla

| Síntoma | Qué hacer |
|---|---|
| El celular no abre la página | ¿Está en el mismo hotspot? Pruebe la dirección en el navegador de la propia laptop. En Windows, revise que la red sea privada |
| `lms` no se encuentra | Abra la app LM Studio y vuelva a correr `python demo.py` |
| "LM Studio no responde" | En la app LM Studio: pestaña Developer > Start Server, y vuelva a correr |
| Va muy lento o se congela | Poca RAM: cierre programas, o use `python demo.py -u 1` y haga la demo con un usuario |
| El puerto 8000 está ocupado | `python demo.py -p 8001` |
| Sin red | **Plan B:** 3 pestañas en la misma laptop con `python demo.py --local`. La concurrencia es igual de real, porque el servidor atiende a las 3 |

## Opciones de `demo.py`

| Opción | Uso |
|---|---|
| `--revisar` | Solo revisa: no arranca la app |
| `-u N` | Usuarios simultáneos para los que se carga el modelo (por defecto 3) |
| `-p PUERTO` | Otro puerto (por defecto 8000) |
| `--local` | Solo en esta PC, sin abrir a la red |
| `--vacantes` | Crea las 4 vacantes del grupo si no existen |

Para el uso normal, solo en la PC, sigue sirviendo `./iniciar.sh`. Con `HOST=0.0.0.0 ./iniciar.sh` se abre a la red, pero sin las revisiones de `demo.py`.
