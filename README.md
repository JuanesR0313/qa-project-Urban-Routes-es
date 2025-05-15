qa-project-Urban-Routes-es Automatización
Juan Esteban Rios Henao Cohort 26

#Descripcion
Este proyecto se basa en la automatización de pruebas para la plataforma web Urban Routes,
un servicio que permite a los usuarios solicitar taxis mediante una interfaz gráfica.
El objetivo es automatizar todo el flujo de solicitud de un taxi, desde la selección de
direcciones hasta el pago y envío de un mensaje al conductor

#Tecnologias y Técnicas Utilizadas
Python 3.11.9
Selenium: Para la automatización de la interacción con el navegador.
Pytest: Como framework para la ejecución de pruebas automatizadas.
WebDriver (Google Chrome): Para la simulación de la interacción del navegador.
XPath Selectors: Para la identificación precisa de elementos en la interfaz web.
JavaScript Click Handling: Para asegurar que los elementos sean correctamente activados cuando existan problemas con elementos superpuestos.
Entornos Virtuales: Para un manejo limpio de las dependencias.

#Estructura del proyecto
main.py: Contiene el código principal de las pruebas automatizadas.
data.py: Contiene las configuraciones y datos utilizados durante las pruebas (URL, número de teléfono, etc.).

#Ejecutar las pruebas
las encuentras dentro del main.py
y se identifican como ejemplo: (def test_full_taxi_order)
con un triangulo para correr las pruebas

#Recomendaciones
Asegúrate de tener Google Chrome instalado y actualizado.
Verifica que el chromedriver sea compatible con la versión de Chrome instalada.
Si deseas ver el navegador mientras se realizan las pruebas, comenta las líneas relacionadas con headless en las configuraciones del WebDriver.
