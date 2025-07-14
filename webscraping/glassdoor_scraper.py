import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException


def get_jobs(keyword, num_jobs, verbose, path, slp_time):
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''

    # Setup Chrome driver
    options = Options()
    options.add_argument("--no-sandbox")
    # options.add_argument("headless")  # Optional: uncomment to run headless
    service = Service(executable_path=path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1120, 1000)

    url = f'https://www.glassdoor.com/Job/jobs.htm?sc.keyword="{keyword}"&locT=C&locId=1147401&locKeyword=San%20Francisco,%20CA'
    driver.get(url)

    jobs = []

    while len(jobs) < num_jobs:
        time.sleep(slp_time)

        # Dismiss pop-up if it appears
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "modal_closeIcon"))
            ).click()
        except (NoSuchElementException, TimeoutException):
            pass

        # Scroll to bottom to ensure listings are fully loaded
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Get list of job postings
        try:
            job_buttons = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "react-job-listing"))
            )
        except TimeoutException:
            print("No job listings found. Ending scrape.")
            break

        for job_button in job_buttons:
            if len(jobs) >= num_jobs:
                break

            job_button.click()
            time.sleep(1)

            collected_successfully = False
            while not collected_successfully:
                try:
                    company_name = driver.find_element(By.CLASS_NAME, "e1tk4kwz1").text
                    location = driver.find_element(By.CLASS_NAME, "e1tk4kwz5").text
                    job_title = driver.find_element(By.CLASS_NAME, "e1tk4kwz4").text
                    job_description = driver.find_element(By.CLASS_NAME, "jobDescriptionContent").text
                    collected_successfully = True
                except NoSuchElementException:
                    time.sleep(1)

            try:
                salary_estimate = driver.find_element(By.CLASS_NAME, "e2u4hf13").text
            except NoSuchElementException:
                salary_estimate = -1

            try:
                rating = driver.find_element(By.CLASS_NAME, "e1cjmv6j0").text
            except NoSuchElementException:
                rating = -1

            # Debug output
            if verbose:
                print(f"Job Title: {job_title}")
                print(f"Company: {company_name}")
                print(f"Location: {location}")
                print(f"Salary: {salary_estimate}")
                print(f"Rating: {rating}")
                print(f"Description: {job_description[:500]}")
                print("===")

            # Click the Company tab to get additional info
            try:
                driver.find_element(By.XPATH, '//div[@class="tab" and @data-tab-type="overview"]').click()
                time.sleep(1)

                def get_info(label):
                    try:
                        return driver.find_element(
                            By.XPATH,
                            f'.//div[@class="infoEntity"]//label[text()="{label}"]/following-sibling::*'
                        ).text
                    except NoSuchElementException:
                        return -1

                headquarters = get_info("Headquarters")
                size = get_info("Size")
                founded = get_info("Founded")
                type_of_ownership = get_info("Type")
                industry = get_info("Industry")
                sector = get_info("Sector")
                revenue = get_info("Revenue")
                competitors = get_info("Competitors")

            except NoSuchElementException:
                headquarters = size = founded = type_of_ownership = industry = sector = revenue = competitors = -1

            if verbose:
                print(f"Headquarters: {headquarters}")
                print(f"Size: {size}")
                print(f"Founded: {founded}")
                print(f"Ownership: {type_of_ownership}")
                print(f"Industry: {industry}")
                print(f"Sector: {sector}")
                print(f"Revenue: {revenue}")
                print(f"Competitors: {competitors}")
                print("###########################################")

            jobs.append({
                "Job Title": job_title,
                "Salary Estimate": salary_estimate,
                "Job Description": job_description,
                "Rating": rating,
                "Company Name": company_name,
                "Location": location,
                "Headquarters": headquarters,
                "Size": size,
                "Founded": founded,
                "Type of ownership": type_of_ownership,
                "Industry": industry,
                "Sector": sector,
                "Revenue": revenue,
                "Competitors": competitors
            })

        # Click next page
        try:
            driver.find_element(By.XPATH, '//li[@class="next"]//a').click()
        except NoSuchElementException:
            print(f"Scraping finished early: found {len(jobs)} jobs (target was {num_jobs}).")
            break

    driver.quit()
    return pd.DataFrame(jobs)
