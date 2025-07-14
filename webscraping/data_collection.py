# .py file
from glassdoor_scraper import get_jobs
path = r"E:\2. Community_Competitions\Kaggle\Lesson-11-Web Scrapping\Selenium\chromedriver-win64\chromedriver-win64\chromedriver.exe"

df = get_jobs("data scientist", 15, True, path, 5)
df.to_csv("glassdoor_jobs.csv", index=False)
