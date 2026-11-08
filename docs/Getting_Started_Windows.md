# Configuración inicial en Windows

Esta guía prepara el computador para abrir y ejecutar Energy Demand Intelligence desde Visual Studio Code. Se ejecuta una sola vez, salvo cuando se actualicen las dependencias.

## 1. Instalar las herramientas

Instala cada programa desde su página oficial.

| Herramienta | Página | Uso |
|---|---|---|
| Visual Studio Code | https://code.visualstudio.com/ | Editor del proyecto. |
| Python | https://www.python.org/downloads/ | Análisis, machine learning y notebooks. |
| Git for Windows | https://git-scm.com/download/win | Historial y control de versiones. |
| R | https://cran.r-project.org/bin/windows/base/ | AutoARIMA. |

Durante la instalación de Python, activa la opción para agregar Python al PATH si el instalador la ofrece. Después de instalar, cierra y vuelve a abrir la terminal.

## 2. Instalar extensiones de VS Code

Abre VS Code y pulsa `Ctrl + Shift + X`. Busca e instala las siguientes extensiones.

- Python, publicada por Microsoft.
- Jupyter, publicada por Microsoft.
- R, publicada por REditorSupport.
- Google Antigravity, publicada por Google. Esta última es opcional y se recomienda instalarla después de comprobar que el proyecto funciona sin asistencia de IA.

La extensión de Python detecta entornos y permite elegir el intérprete. Jupyter habilita la experiencia de notebooks. La extensión R permite trabajar con scripts y una terminal de R.

## 3. Abrir el proyecto

1. Descarga el paquete del repositorio y extrae la carpeta `energy_demand_intelligence_repo`.
2. Abre VS Code.
3. Selecciona `File` y luego `Open Folder`.
4. Elige la carpeta `energy_demand_intelligence_repo`.
5. Acepta la opción de confiar en los archivos solo si reconoces el origen del repositorio.
6. Abre `Terminal` y selecciona `New Terminal`.

La terminal debería abrirse en la carpeta raíz del proyecto. Compruébalo con `pwd` o `Get-Location`.

## 4. Comprobar las instalaciones

Ejecuta estos comandos uno por uno en la terminal integrada.

```powershell
py --version
git --version
Rscript --version
```

Cada comando debe devolver una versión. Si uno no se reconoce, revisa la instalación y vuelve a abrir VS Code.

## 5. Crear el entorno de Python

Desde la carpeta raíz del proyecto ejecuta.

```powershell
py -m venv .venv
```

Activa el entorno.

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, puedes utilizar el intérprete del entorno sin activarlo. Si prefieres habilitar la activación para tu usuario, revisa primero la política local y utiliza `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` únicamente si entiendes el cambio.

Instala las dependencias.

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Registra el kernel que utilizará el notebook.

```powershell
python -m ipykernel install --user --name energy-demand-intelligence --display-name "Python (energy-demand-intelligence)"
```

## 6. Preparar R

Abre una terminal de R desde el menú Inicio o ejecuta `R` en la terminal de VS Code. Instala los paquetes requeridos para el componente inicial.

```r
install.packages("forecast")
install.packages("languageserver")
```

Comprueba que R puede cargar el paquete.

```r
library(forecast)
packageVersion("forecast")
```

La versión instalada deberá registrarse en los resultados de AutoARIMA.

## 7. Abrir el notebook

1. Abre `notebooks/Energy_Demand_Intelligence.ipynb`.
2. En la parte superior derecha, selecciona `Select Kernel`.
3. Elige `Python (energy-demand-intelligence)` o el intérprete situado dentro de `.venv`.
4. Ejecuta primero una celda sencilla que imprima las versiones de Python y pandas.
5. Cuando las dependencias estén verificadas, ejecuta el notebook desde el principio.

No ejecutes celdas fuera de orden. Para comprobar reproducibilidad, reinicia el kernel y selecciona `Run All`.

## 8. Configurar Git por primera vez

Comprueba Git.

```powershell
git --version
```

Configura tu nombre y el correo asociado a tu cuenta de GitHub. Utiliza tu correo real o la dirección privada `noreply` que GitHub te asigne.

```powershell
git config --global user.name "Juan Camilo Sánchez Navarro"
git config --global user.email "TU_CORREO_DE_GITHUB"
```

Comprueba la configuración.

```powershell
git config --global --list
```

No crees el repositorio remoto ni hagas `push` hasta revisar juntos el primer `git status` y el contenido que se publicará.

### Primer commit local

Cuando hayamos revisado el estado y confirmado que no hay credenciales ni archivos personales, inicializaremos Git.

```powershell
git init
git branch -M main
git status
git add .
git status --short
git commit -m "chore: initialize project structure"
```

### Crear el repositorio en GitHub

1. En GitHub, selecciona `New repository`.
2. Usa el nombre `energy-demand-intelligence`.
3. Selecciona `Public` solo después de revisar datos, permisos y licencia.
4. No marques la opción de crear README, `.gitignore` o licencia porque los archivos ya existen localmente.
5. Copia la URL HTTPS que presenta GitHub y agrégala desde la terminal.

```powershell
git remote add origin https://github.com/TU_USUARIO/energy-demand-intelligence.git
git push -u origin main
```

Sustituye `TU_USUARIO` por tu usuario real de GitHub.

### Crear una rama y un Pull Request

Para una tarea nueva se crea una rama independiente.

```powershell
git switch -c feature/auto-arima
```

Después de hacer cambios y revisarlos.

```powershell
git status
git add .
git diff --cached
git commit -m "feat: add automatic arima model"
git push -u origin feature/auto-arima
```

En GitHub aparecerá la opción `Compare & pull request`. Se revisan los archivos y el resumen, se crea el Pull Request, se comprueba el diff y solo entonces se integra en `main` mediante `Merge pull request`. Después se actualiza la rama local.

```powershell
git switch main
git pull
git branch -d feature/auto-arima
```

No ejecutes todavía estos comandos. Los haremos paso a paso cuando el entorno esté comprobado.

## 9. Primera comprobación

Ejecuta este bloque y conserva la salida.

```powershell
python --version
python -m pip --version
git --version
Rscript --version
python -c "import pandas, numpy, sklearn, IPython; print('pandas', pandas.__version__); print('numpy', numpy.__version__); print('scikit-learn', sklearn.__version__)"
```

Cuando todas las versiones aparezcan correctamente, el entorno estará listo para configurar el primer commit y comenzar AutoARIMA.

## 10. Incidencias frecuentes

- Si `py` no se reconoce, reinstala Python o revisa el PATH.
- Si `Rscript` no se reconoce, revisa que R esté instalado y vuelve a abrir VS Code.
- Si PowerShell bloquea la activación, utiliza directamente `.venv\Scripts\python.exe` o revisa la política de ejecución antes de cambiarla.
- Si el notebook no muestra el entorno, usa `Select Kernel` y selecciona el Python de `.venv`.
- Si falta un paquete, instala la dependencia dentro de `.venv` y actualiza `requirements.txt` después de validar el cambio.
