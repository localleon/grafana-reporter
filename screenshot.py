import time
import datetime
from seleniumwire import webdriver  # Import from seleniumwire
import os
import smtplib
from email.message import EmailMessage

# Add a request header
def authenticationInterceptor(request):
    del request.headers["Authorization"]  # Remember to delete the header first
    request.headers["Authorization"] = f"Bearer {bearer_api_token}"


def createSeleniumDriver(browser_width, browser_height):
    ## Setup chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--ignore-ssl-errors=yes")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--headless")  # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f"--window-size={browser_width},{browser_height}")

    # Or create using browser specific options and/or seleniumwire_options options
    driver = webdriver.Chrome(options=chrome_options)

    return driver


def takeScreenShotFromURL(driver, url, filename, timeout):
    # Get page
    driver.get(url)
    time.sleep(timeout)
    driver.save_screenshot(filename)


def sendSimpleMail(from_addr, to_addr_list, attached_file):
    # Create the container email message.
    msg = EmailMessage()
    msg["Subject"] = f"Your requested report ({attached_file})"

    # me == the sender's email address
    # to_addr_list = the list of all recipients' email addresses
    msg["From"] = from_addr
    # msg["To"] = ", ".join(to_addr_list)
    msg["To"] = to_addr_list
    msg.preamble = "To read this message, you will need a MIME aware Mail-Reader.\n"

    # Set Body for E-Mail Message
    msg.set_content(
        "This is an automatically generated report. Please do not reply to this message. You will find your report in the attachment"
    )

    # Open the files in binary mode.
    with open(attached_file, "rb") as fp:
        img_data = fp.read()
    msg.add_attachment(img_data, maintype="image", subtype="png")

    # Send the email via our own SMTP server.
    smtp_s.send_message(msg)


def setupSMTPServer(server):
    s = smtplib.SMTP(server)

    return s


def main():
    # Make API Token accessible for interceptor
    global bearer_api_token
    global smtp_s

    smtp_s = setupSMTPServer(os.environ.get("SCREENSHOT_SMTP_SERVER"))

    # Get Configuration from environment
    bearer_api_token = os.environ.get("SCREENSHOT_BEARER_API_TOKEN")
    dashboard_url = os.environ.get("SCREENSHOT_URL")
    screenshot_name_prefix = os.environ.get("SCREENSHOT_NAME_PREFIX")
    # Browser Settings
    browser_width = os.environ.get("SCREENSHOT_WIDTH")
    browser_height = os.environ.get("SCREENSHOT_HEIGHT")

    # Generate Timestamp for this screenshot and filename format
    timestamp = datetime.datetime.isoformat(datetime.datetime.today())
    filename_format = f"{timestamp}-{screenshot_name_prefix}.png"

    # Create Driver and add our Authentication Interceptor
    driver = createSeleniumDriver(browser_width, browser_height)
    driver.request_interceptor = authenticationInterceptor

    # Create Screenshot
    takeScreenShotFromURL(driver, dashboard_url, filename_format, 3)

    # Send Screenshot via Mail
    sendSimpleMail(
        from_addr=os.environ.get("SCREENSHOT_WIDTH"),
        to_addr_list=os.environ.get("SCREENSHOT_SMTP_TO_ADDR_LIST"),
        attached_file=filename_format,
    )

    # Close Mailserver and Browser
    driver.quit()
    smtp_s.quit()


if __name__ == "__main__":
    main()
