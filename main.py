from playsound import playsound
from selenium_driver import SeleniumDriver
from user_inputs import URL, SECTIONS_WITHOUT_DISCOUNT, NUMBER_OF_GUESTS, USERNAME, PASSWORD, IS_SCHEDULED, SCHEDULED_TIMESTAMP

driver = SeleniumDriver(URL, IS_SCHEDULED, SCHEDULED_TIMESTAMP)

success = False

while not success:
    driver.accept_cookies()

    target_section_found = driver.define_target_section(desired_sections=SECTIONS_WITHOUT_DISCOUNT)

    if target_section_found == "none":
        continue  # reinicia loop

    target_section_tab_was_found = driver.go_to_section_tab(target_section_found)
    
    if not target_section_tab_was_found:
        continue  # reinicia loop

    tickets_were_added = driver.add_tickets_to_cart(NUMBER_OF_GUESTS, is_without_discount=True)
    if not tickets_were_added:
        continue  

    success = driver.log_in(USERNAME, PASSWORD)

playsound('audio/success_song.mp3')
