import logging
import random
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)


class SeleniumDriver:
    def __init__(self, url: str, is_scheduled: bool = False, scheduled_start: datetime = None):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)  # Não fechar o browser automaticamente
        chrome_options.add_argument("--incognito")

        self.main_url = url
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(url)
        self.driver.maximize_window()

        if is_scheduled:
            time_to_wait = (scheduled_start - datetime.now()).total_seconds()
            if time_to_wait > 0:
                logging.info(f"Aguardando horário agendado: {scheduled_start}")
                time.sleep(time_to_wait)
                logging.info("Iniciando após o horário agendado")

    def accept_cookies(self):
        try:
            cookies_button = self.wait_and_find_clickable_element(method=By.XPATH,
                                                                  timeout=5,
                                                                  element_id_or_xpath="//a[@class='cc-btn cc-dismiss']")
            if cookies_button:
                cookies_button.click()
                logging.info("Cookies aceitos")
        except Exception as e:
            logging.info(f"Erro ao aceitar cookies: {e}")

    def input_cpf(self, cpf):
        try:
            cpf_field = self.wait_and_find_clickable_element(method=By.ID,
                                                             timeout=5,
                                                             element_id_or_xpath="inputPromocode")
            cpf_field.send_keys(cpf)
            cpf_field.submit()

            self.wait_and_find_clickable_element(method=By.XPATH,
                                                 timeout=15,  # Esse pode demorar
                                                 element_id_or_xpath="//button[@data-cy='promocode-button']")
            logging.info("CPF inserido com sucesso")
            return True
        except Exception as e:
            self.driver.refresh()
            logging.info(f"Erro ao inserir CPF: {e}")
            return False

    def go_to_section_tab(self, section_name):
        logging.info(f"Procurando seção: {section_name}")
        section_tab_was_found = False

        while not section_tab_was_found:
            try:
                tab_button = self.wait_and_find_clickable_element(method=By.XPATH,
                                                                  timeout=5,
                                                                  element_id_or_xpath=f"//button[@title='{section_name}']")
                tab_button.click()
                section_tab_was_found = True
                logging.info(f"Seção {section_name} encontrada")
                return True
            except Exception:
                try:
                    next_arrow_button = self.wait_and_find_clickable_element(method=By.ID,
                                                                             timeout=5,
                                                                             element_id_or_xpath="sector-next")
                    next_arrow_button.click()
                except Exception as e:
                    logging.info(f"Setor {section_name} não encontrado: {e}. Tentando próximo setor...")
                    self.driver.refresh()
                    return False

    def add_tickets_to_cart(self, number_of_guests: int, is_without_discount: bool) -> bool:
        logging.info("Tentando adicionar ingressos ao carrinho")
        try:
            if not is_without_discount:
                self.add_membership_tickets(number_of_guests)
            else:
                self.add_tickets_without_discount(number_of_guests)

            # Continuar processo de checkout
            continue_button = self.wait_and_find_clickable_element(method=By.ID,
                                                                   timeout=5,
                                                                   element_id_or_xpath="buttonContinue")
            self.driver.execute_script("arguments[0].click();", continue_button)

            review_continue_button = self.wait_and_find_clickable_element(method=By.XPATH,
                                                                          timeout=5,
                                                                          element_id_or_xpath="//button[@data-cy='review-button-continue']")
            review_continue_button.click()

            # Aceitar termos e condições
            checkbox = self.wait_and_find_clickable_element(method=By.ID,
                                                            timeout=5,
                                                            element_id_or_xpath="tuPpEvent")
            checkbox.click()
            review_continue_button.click()

            return True
        except Exception as e:
            logging.info(f"Erro ao adicionar ingressos ao carrinho: {e}. Tentando outro setor...")
            self.driver.refresh()
            return False

    def add_tickets_without_discount(self, number_of_guests):
        try:
            add_ticket_element = self.wait_and_find_clickable_element(method=By.XPATH,
                                                                      timeout=5,
                                                                      element_id_or_xpath="/html/body/app-root/app-layout/main/app-page-cart/div[2]/app-products-group/div/div/app-product-item[2]/div/div/div[2]/div/button[2]/i")
        except:
            add_ticket_element = self.wait_and_find_clickable_element(method=By.XPATH,
                                                                      timeout=5,
                                                                      element_id_or_xpath="/html/body/app-root/app-layout/main/app-page-cart/div[2]/app-products-group/div/div/app-product-item[1]/div/div/div[2]/div/button[2]/i")

        for i in range(number_of_guests):
            add_ticket_element.click()

    def add_membership_tickets(self, number_of_guests):
        add_main_ticket_element = self.wait_and_find_clickable_element(method=By.XPATH,
                                                                       timeout=5,
                                                                       element_id_or_xpath="/html/body/app-root/app-layout/main/app-page-cart/div[2]/app-products-group/div/div/app-product-item[1]/div/div/div[2]/div/button[2]/i")
        add_main_ticket_element.click()

        for i in range(number_of_guests):
            add_guest_element = self.wait_and_find_clickable_element(method=By.XPATH,
                                                                     timeout=5,
                                                                     element_id_or_xpath="/html/body/app-root/app-layout/main/app-page-cart/div[2]/app-products-group/div/div/app-product-item[2]/div/div/div[2]/div/button[2]/i")
            add_guest_element.click()

    def log_in(self, user: str, password: str):
        try:
            self.wait_and_find_element_to_be_available(method=By.ID,
                                                       timeout=5,
                                                       element_id_or_xpath="swal2-html-container")
            self.driver.get(self.main_url)
            return False
        except:
            pass

        try:
            username_element = self.wait_and_find_clickable_element(method=By.ID,
                                                                    timeout=15,
                                                                    element_id_or_xpath="userLogin")
            username_element.send_keys(user)

            password_element = self.wait_and_find_clickable_element(method=By.ID,
                                                                    timeout=5,
                                                                    element_id_or_xpath="password")
            password_element.send_keys(password)
            password_element.submit()

            if "payment" in self.driver.current_url:
                logging.info("Login efetuado com sucesso")
                return True
            else:
                self.driver.get(self.main_url)
                return False
        except Exception as e:
            logging.info(f"Erro no login: {e}")
            self.driver.get(self.main_url)
            return False

    def check_if_section_is_available(self, section_name: str) -> bool:
        try:
            available_section_divs = self.driver.find_elements(By.XPATH, "//app-product-item")

            # Refiltrar os elementos que têm o nome da seção e não estão esgotados
            desired_section_div = [div for div in available_section_divs if (section_name in div.text) and ('ESGOTADO' not in div.text.upper())]

            if len(desired_section_div) > 0:
                return True
            else:
                return False
        except StaleElementReferenceException as e:
            logging.info(f"Elemento desatualizado: {e}. Recarregando a página e tentando novamente.")
            self.driver.refresh()  # Atualize a página
            time.sleep(2)  # Tempo para a página recarregar
            return False

    def define_target_section(self, desired_sections: list[str]) -> str:
        for section in desired_sections:
            if self.check_if_section_is_available(section):
                logging.info(f"Seção {section} disponível")
                return section
        logging.info("Nenhum dos setores desejados está disponível")
        self.driver.refresh()
        return "none"

    def wait_and_find_clickable_element(self, method, timeout, element_id_or_xpath):
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((method, element_id_or_xpath)))

    def wait_and_find_element_to_be_available(self, method, timeout, element_id_or_xpath):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((method, element_id_or_xpath)))
