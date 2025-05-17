import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time


# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas."""

    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class UrbanRoutesPage:
    # 1 Configurar la dirección
    from_field = (By.ID, 'from')  # Campo "Desde"
    to_field = (By.ID, 'to')  # Campo "Hasta"

    # 2.1 Botón para iniciar la selección de tarifa
    request_taxi_button = (By.XPATH, "//button[contains(text(), 'Pedir un taxi')]")

    # 2.2 Seleccionar la tarifa Comfort
    comfort_tariff = (By.XPATH, "//div[contains(@class, 'tcard') and .//div[text()='Comfort']]")

    # 3.1 Rellenar el número de teléfono
    phone_button = (By.CLASS_NAME, "np-button")  # Botón para activar el campo del número de teléfono
    phone_field = (By.ID, "phone")  # Número de teléfono
    next_button = (By.CLASS_NAME, "button.full")  # Botón "Siguiente" para confirmar el número

    # 3.2 Campo del código SMS y botón de cierre
    sms_code_field = (By.ID, "code")  # Campo para ingresar el código SMS

    # 4.1 Botón para método de pago
    payment_method_button = (By.XPATH, "//div[contains(@class, 'pp-button') and contains(@class, 'filled')]")

    # 4.2 Botón para agregar una tarjeta con el botón +
    add_card_button = (By.CLASS_NAME, "pp-plus-container")
    # 4.3 Agregar una tarjeta de crédito
    card_number_field = (By.ID, "number")  # Campo Número de Tarjeta
    cvv_field = (By.NAME, "code")  # Campo CVV # Campo CVV
    confirm_card_button = (
    By.XPATH, "//button[@type='submit' and text()='Agregar']")  # Botón de confirmación en la tarjeta de crédito

    # 4.4 Botón para cerrar ventana de tarjeta
    close_card_modal_button = (
    By.XPATH, "//button[contains(@class, 'close-button') and contains(@class, 'section-close')]")  # botón de cierre

    # 5 Mensaje para el conductor
    message_field = (By.XPATH, "//div[@class='input-container']//input[@id='comment']")

    def __init__(self, driver):
        self.driver = driver
        self.driver.implicitly_wait(10)  # Espera global para evitar errores de carga

    # 1 Confirmación del establecimiento de  la ruta
    def set_from(self, from_address):
        """Ingresa la dirección de origen"""
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.from_field))
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        """Ingresa la dirección de destino"""
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.to_field))
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        """Obtiene el valor del campo 'Desde'"""
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.from_field))
        return self.driver.find_element(*self.from_field).get_attribute("value")

    def get_to(self):
        """Obtiene el valor del campo 'Hasta'"""
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.to_field))
        return self.driver.find_element(*self.to_field).get_attribute("value")

    # 2 Prueba que verifica que se selecciona la tarifa Comfort
    def select_comfort_tariff(self):
        """Hace clic en 'Pedir un taxi' y luego selecciona la tarifa Comfort."""

        # 1 Hacer clic en "Pedir un taxi"
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.request_taxi_button)
        ).click()

        # 2 Esperar a que la tarifa Comfort sea clickeable
        comfort_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.comfort_tariff)
        )

        # 3 Hacer scroll hasta el botón para asegurarnos de que sea visible
        self.driver.execute_script("arguments[0].scrollIntoView();", comfort_button)

        # 4 Hacer clic en la tarifa Comfort
        comfort_button.click()

        # 5 Confirmar que la selección se hizo correctamente
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'tcard active') and .//div[text()='Comfort']]"))
        )

    # 3 Prueba para agregar número de teléfono
    def enter_phone_number(self, phone_number):
        """Hace clic en 'Número de teléfono' y lo ingresa en el campo correspondiente."""

        # 1 Hacer clic en el botón "Número de teléfono"
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.phone_button)
        ).click()

        # 2 Esperar a que el campo de teléfono sea interactuable
        phone_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.phone_field)
        )

        # 3 Escribir el número
        phone_input.send_keys(phone_number)
        phone_input.send_keys(Keys.TAB)  # Simular cambio de foco para activar el siguiente paso

        # 4 Hacer clic en "Siguiente" para confirmar el número y llevarte al código
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.next_button)
        ).click()

        # 5 Esperar a que aparezca el campo de código SMS
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.sms_code_field)
        )

    def enter_sms_code(self, code):
        """Ingresa el código SMS en el campo correspondiente."""
        # Esperar hasta que el campo de código esté disponible para ser encontrado
        sms_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='code' and @class='input']"))
        )

        # Forzar clic en el elemento con JavaScript
        self.driver.execute_script("arguments[0].click();", sms_input)

        # Borrar cualquier texto previo en el campo
        sms_input.clear()

        # Ingresar el código proporcionado
        sms_input.send_keys(code)

    def confirm_sms_code(self):
        """Hace clic en el botón de Confirmar después de ingresar el código SMS."""
        sms_confirm_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='buttons']/button[@type='submit' and text()='Confirmar']")
            )
        )
        # Asegurarse de que el botón sea visible en pantalla
        self.driver.execute_script("arguments[0].scrollIntoView(true);", sms_confirm_button)
        # Intentar hacer clic con JavaScript
        self.driver.execute_script("arguments[0].click();", sms_confirm_button)

    # 4 Prueba que agrega tarjeta de crédito
    def open_payment_method(self):
        """Hace clic en 'Método de pago' antes de agregar una tarjeta."""
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.payment_method_button)
        ).click()

    def click_add_card_button(self):
        """Hace clic en el botón '+' para agregar una nueva tarjeta."""
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.add_card_button)
        ).click()

    def click_card(self, card_number):
        """Hace clic en el campo de número de tarjeta y escribe el número."""
        self.driver.implicitly_wait(30)
        # Desempaquetar la tupla con *
        card_element = self.driver.find_element(*self.card_number_field)
        card_element.click()
        card_element.send_keys(card_number)

    def add_code_card(self, cvv):
        """Hace clic en el campo CVV y escribe el código, luego presiona TAB."""
        self.driver.implicitly_wait(10)
        # Desempaquetar la tupla con *
        cvv_element = self.driver.find_element(*self.cvv_field)
        cvv_element.click()
        cvv_element.send_keys(cvv + Keys.TAB)

    def card_submit_button(self):
        """Hace clic en el botón 'Agregar' para confirmar la tarjeta."""
        self.driver.implicitly_wait(30)
        # Desempaquetar la tupla con *
        add_button = self.driver.find_element(*self.confirm_card_button)
        add_button.click()

    def close_card_modal(self):
        """Cierra el modal de la tarjeta de crédito dentro del contenedor de pago."""
        payment_picker = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'payment-picker open')]"))
        )
        # Buscar el botón de cierre dentro del contenedor activo
        close_button = payment_picker.find_element(By.XPATH,
                                                   ".//button[contains(@class, 'close-button') and contains(@class, 'section-close')]")
        # Intentar hacer clic en el botón con JavaScript
        self.driver.execute_script("arguments[0].click();", close_button)
        time.sleep(1)

    # 5 Prueba que verifica que se pueda enviar mensaje para el conductor
    def add_driver_message(self, message):
        """Hace clic en el campo de mensaje para el conductor y escribe un texto."""
        # Esperar a que el campo de mensaje sea visible y presente en el DOM
        message_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='comment' and @class='input']"))
        )
        # Forzar clic con JavaScript si el clic normal no funciona
        self.driver.execute_script("arguments[0].click();", message_input)
        # Ingresar el mensaje al conductor
        message_input.clear()
        message_input.send_keys(message)

    # 6 Prueba que verifica que se pueda solicitó una frazada
    def activate_chekbox(self):
        """Activa el checkbox para pedir una manta y pañuelos."""
        checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='switch']/input[@type='checkbox' and @class='switch-input']")
            )
        )
        # Asegurarse de que el botón sea visible en pantalla
        self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        # Intentar hacer clic con JavaScript
        self.driver.execute_script("arguments[0].click();", checkbox)

    # 7 Prueba que verifica que se añadieron helados
    def click_icecream(self, cantidad):
        """Hace clic en el botón '+' para incrementar la cantidad de Helado la cantidad de veces especificada."""
        for _ in range(cantidad):
            icecream = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     "//div[@class='r-group-items']//div[@class='r-counter-container'][.//div[text()='Helado']]//div[@class='counter-plus']")
                )
            )
            # Asegurarse de que el botón sea visible en pantalla
            self.driver.execute_script("arguments[0].scrollIntoView(true);", icecream)
            # Intentar hacer clic con JavaScript
            self.driver.execute_script("arguments[0].click();", icecream)
            time.sleep(0.5)  # Pausa pequeña para que el clic se procese correctamente

    # 8 Prueba que verifica la búsqueda de un conductor
    def order_taxi_final(self):
        """Hace clic en el botón de Confirmar taxi final."""
        order_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 "//button[@type='button' and contains(@class, 'smart-button') and .//span[text()='Pedir un taxi']]")
            )
        )
        # Asegurarse de que el botón sea visible en pantalla
        self.driver.execute_script("arguments[0].scrollIntoView(true);", order_button)
        # Intentar hacer clic con JavaScript
        self.driver.execute_script("arguments[0].click();", order_button)


class TestUrbanRoutes:
    driver = None  # Definir el driver a nivel de clase

    @classmethod
    def setup_class(cls):
        # no lo modifiques, ya que necesitamos un registro adicional habilitado para recuperar el código de confirmación del teléfono
        from selenium.webdriver import DesiredCapabilities
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {'performance': 'ALL'}

        # Convertimos capabilities en options para evitar el error
        chrome_options = Options()
        for key, value in capabilities.items():
            chrome_options.set_capability(key, value)

        # Usamos Service() para evitar problemas de compatibilidad
        service = Service()
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)

    def test_full_taxi_order(self):
        """Prueba automatizada para pedir un taxi en Urban Routes."""
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)

    def test_set_route(self):
        """Configurar la dirección"""
        address_from = data.address_from
        address_to = data.address_to
        routes_page = UrbanRoutesPage(self.driver)

        routes_page.set_from(address_from)
        routes_page.set_to(address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to

    def test_set_comfort(self):
        """Seleccionar tarifa Comfort"""
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.select_comfort_tariff()
        assert self.driver.find_element(By.XPATH,
                                        "//div[contains(@class, 'tcard active') and .//div[text()='Comfort']]").is_displayed(), "Error: La tarifa Comfort no se seleccionó correctamente."

    def test_set_phone_number(self):
        """Rellenar el número de teléfono"""
        routes_page = UrbanRoutesPage(self.driver)
        phone_number = data.phone_number
        routes_page.enter_phone_number(phone_number)
        # Obtener el código de confirmación SMS usando el driver actual
        sms_code = retrieve_phone_code(self.driver)
        # Ingresar el código SMS en el campo correspondiente
        routes_page.enter_sms_code(sms_code)
        routes_page.confirm_sms_code()
        assert self.driver.find_element(By.ID, "code").get_attribute(
            "value") == sms_code, "Error: El código SMS no se ingresó correctamente."

    def test_add_card(self):
        """Agregar tarjeta de crédito"""
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.open_payment_method()  # Abrir método de pago
        routes_page.click_add_card_button()  # Hacer clic en el botón "+" para agregar una nueva tarjeta

        card_number = data.card_number
        card_code = data.card_code
        routes_page.click_card(card_number)
        routes_page.add_code_card(card_code)
        routes_page.card_submit_button()

        routes_page.close_card_modal()  # Cierre de la ventana de tarjeta
        assert not self.driver.find_elements(By.XPATH,
                                             "//div[contains(@class, 'payment-picker open')]"), "Error: El modal de la tarjeta no se cerró correctamente."

    def test_write_message(self):
        """Escribe el mensaje al conductor"""
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.add_driver_message("Traiga un aperitivo, por favor")
        assert "Traiga un aperitivo, por favor" in self.driver.page_source, "Error: El mensaje al conductor no se ingresó correctamente."

    def test_blanket(self):
        """Activa el checkbox para pedir manta y pañuelos"""
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.activate_chekbox()
        checkbox = self.driver.find_element(By.XPATH,
                                            "//div[@class='switch']/input[@type='checkbox' and @class='switch-input']")
        assert checkbox.is_selected() or checkbox.get_attribute(
            "checked") == "true", "Error: El checkbox de manta no se activó correctamente."

    def test_add_icecream(self):
        """Click para pedir helados"""
        routes_page = UrbanRoutesPage(self.driver)
        initial_icecream_count = int(self.driver.find_element(By.XPATH,
                                                              "//div[@class='r-group-items']//div[@class='r-counter-container'][.//div[text()='Helado']]//div[@class='counter-value']").text)
        routes_page.click_icecream(2)
        final_icecream_count = int(self.driver.find_element(By.XPATH,
                                                            "//div[@class='r-group-items']//div[@class='r-counter-container'][.//div[text()='Helado']]//div[@class='counter-value']").text)
        assert final_icecream_count == initial_icecream_count + 2, "Error: No se agregaron correctamente los helados."

    def test_find_driver(self):
        """Pedir taxi y buscar conductor"""
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.order_taxi_final()
        WebDriverWait(self.driver, 20).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Buscar automóvil"))
        assert "Buscar automóvil" in self.driver.page_source, "Error: No se inició correctamente la búsqueda de un conductor."

    @classmethod
    def teardown_class(cls):
        """Cierra el navegador después de ejecutar las pruebas"""
        cls.driver.quit()
