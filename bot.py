import email
import shutil
import imaplib
import smtplib
import pathlib
import os.path
import logging
import webbrowser
from time import sleep
from email import encoders
from pytz import timezone
from datetime import datetime
from selenium import webdriver
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Browser:
    def __init__(self, driver_path, site):
        # Initialize some useful strings to find the elements on the page
        self.prasads_large_screen = "//a[text()='Prasads Multiplex: Hyderabad']"
        self.show_type            = "//div[text()='PCX']"
        self.accept_button        = "//div[@id='btnPopupAccept']"
        self.select_seats         = "//div[@id='proceed-Qty']"
        self.close_btn            = "//a[@id='dismiss']"
        self.not_now              = "//button[@id='wzrk-cancel']"
        self.seat_layout          = "//table[@class='setmain']"
        self.show_time            = "//span[@id='strDate']"
        self.first_row            = "N"
        self.second_row           = "M"
        self.third_row            = "L"
        self.available            = "_available"
        self.blocked              = "_blocked"
        self.start_seat           = 10     ## Change these start and end seats based on your preference
        self.end_seat             = 35
        self.active_show_time     = "_active"
        self.smtp_username        = ""
        self.smtp_password        = ""

        # Initialize the options to be passed to start the browser for masking the automation
        self.option = webdriver.ChromeOptions()
        self.init_option()

        # Initialize the actual browser that will be automated
        self.browser = webdriver.Chrome(executable_path=driver_path, options=self.option)
        self.browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.browser.implicitly_wait(5)
        self.browser.get(site)
        sleep(2)


    def init_option(self):
        self.option.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.option.add_experimental_option('useAutomationExtension', False)

        self.option.add_argument('--disable-blink-features=AutomationControlled')
        # Add this option if you don't want the browser to be shown
        self.option.add_argument("--headless")
        # self.option.add_argument("start-maximized")
        self.option.add_argument("window-size=1280,800")
        self.option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
    
    def wait_for_personalized_update_pop_up(self):
        try:
            element = WebDriverWait(self.browser, 10).until(
                        EC.visibility_of_element_located((By.XPATH, self.not_now)))
            element.click()
        except Exception as e:
            print("Personalized Updates pop-up not seen")
            print(e)

    def is_prasads_available(self):
        try:
            prasads = self.browser.find_element_by_xpath(self.prasads_large_screen)
            # print(prasads)
            return True
        except Exception as e:
            print(self.prasads_large_screen+" not found in the webpage")
            print(e)
            return False
    
    def open_and_find_seats_available(self):
        print("Finding seats available")
        try:
            show_time_list = self.browser.find_elements_by_xpath(self.show_type)
            for show_time in show_time_list:
                self.browser.execute_script("arguments[0].scrollIntoView(false);", show_time)
                show_time.click()
                try:
                    self.browser.find_element_by_xpath(self.accept_button).click()
                except Exception as e:
                    print("Accept button not found")
                    print(e)
                try:
                    element = WebDriverWait(self.browser, 2).until(
                        EC.visibility_of_element_located((By.XPATH, self.select_seats)))
                    element.click()
                except Exception as e:
                    print("Select seats button not found")
                    print(e)
                self.find_best_seats()
                # print("Sleepig 5 seconds")
                # sleep(5)
                try:
                    self.browser.find_element_by_xpath(self.close_btn).click()
                except Exception as e:
                    print("Close button not found")
                    print(e)
        except Exception as e:
            print("Something went wrong in open_and_find_seats_available")
            print(e)
        
    def find_best_seats(self):
        print("Finding seats in top rows")
        try:
            layout = self.browser.find_element_by_xpath(self.seat_layout)
            rows = [tr for tr in layout.find_elements_by_xpath(".//tr")]
            # Skipping dummy row at the top
            rows = rows[1:]
            seat_map = {}
            send_mail = False
            for row in rows:
                tds = [td for td in row.find_elements_by_xpath(".//td")]
                row_id = tds[0].find_element_by_xpath(".//div").text
                if((row_id != self.first_row) and (row_id != self.second_row) and (row_id != self.third_row)):
                    continue
                seats = [div for div in tds[1].find_elements_by_xpath(".//div")]
                # Skipping whitespace coloumn
                seats = seats[1:]
                seats_available = []
                for seat in seats:
                    seat_number = seat.find_element_by_xpath(".//a").text
                    status = seat.find_element_by_xpath(".//a").get_attribute("class")
                    # print("Seat: " + seat_number + ", status: " + status)
                    if(status == self.available):
                        seats_available.append(seat_number)
                print("Row ID: " + row_id, end=", ")
                print("Seats available: ", end=" ")
                print(seats_available)
                # print("\n")
                for seat in seats_available:
                    if int(seat) > self.start_seat and int(seat) < self.end_seat:
                        seat_map[row_id] = seats_available
                        send_mail = True
                        # print(seat_map)
                        break
            if(send_mail):
                self.prepare_and_send_mail(seat_map)
        except Exception as e:
            print("Something went wrong in find_best_seats")
            print(e)
    

    def prepare_and_send_mail(self, seat_map):
        username = self.smtp_username
        sender = username
        '''
        ###  Add receiver emails here like [username, "abc@xyz.com", "def@uvw.com"]
        '''
        receivers = [username]

        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = username
        msg['Subject'] = ("Top rows opened on Prasads")

        message = self.prepare_message(seat_map)
        # print(message)

        msg.attach(MIMEText(message, _charset='UTF-8'))
        # print(msg)
        self.send_mail(sender, receivers, msg)

    def prepare_message(self, seat_map):
        message = ""
        message += "For the showtime: "
        try:
            message += self.browser.find_element_by_xpath(self.show_time).text
        except Exception as e:
            print("Cannot get show time")
            print(e)
        message += "\nSeats available are as follows:\n"
        for row,seats in seat_map.items():
            message += row + ": "
            for seat in seats:
                message += seat + " "
            message += "\n"
        print("Body: " + message)
        return message
    
    def send_mail(self, sender, receivers, msg):
        username = self.smtp_username
        password = self.smtp_password
        try:
            # Yahoo SMTP server is used here. Change this to use another
            # mail server to send mails.
            server = smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465)
            server.ehlo()
            print("Ehlo done for SMTP server")
            # server.starttls()
            server.login(username, password)
            print("Login done for SMTP server")
            # server = smtplib.SMTP('localhost')
            server.sendmail(sender, receivers, msg.as_string())
            print("Sendmail done for SMTP server")
            server.close()
            print("Sent mail sucessfully")
        except Exception as e:
            print("ERROR: Unable to send mail")
            print(e)

    def close(self):
        print("Closing the browser")
        self.browser.quit()



def main(site):
    driver_path   = "./chromedriver"

    browser = Browser(driver_path, site)

    ''' 
    ### Update smtp username and password here so that the script can send the mail
    '''
    browser.smtp_username = "xyz@abc.com" # Enter the email to be used to send the mail from
    browser.smtp_password = "abcdefg"     # Enter the app-password of the email to be used to send the mail from
    browser.wait_for_personalized_update_pop_up()
    if(browser.is_prasads_available()):
        print("Found Prasads, continuing")
        browser.open_and_find_seats_available()
    else:
        "Prasad's Multiplex Option not available in the site provided, please try again. Exiting..."
        exit()
    browser.close()



if __name__ == "__main__":
    print("Enter the BMS site you wish to get informed for: ", end="")
    site=input()
    # for example, site can be:
    # https://in.bookmyshow.com/buytickets/ant-man-and-the-wasp-quantumania-3d-hyderabad/movie-hyd-ET00351697-MT/20230217
    while(True):
        main(site)
        print("Sleeping for 10 mins")
        sleep(600)
        ## TODO: Quit/stop the script for a particular show when email is already sent.