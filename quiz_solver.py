from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

log = logging.getLogger(__name__)


class QuizSolver:
    def __init__(self, salary: str, qa_file: Path | str = Path("qa.csv")) -> None:
        self.salary = salary
        self.qa_file = Path(qa_file)
        self.answers: dict[str, str] = {}

        if self.qa_file.is_file():
            df = pd.read_csv(self.qa_file)
            for _, row in df.iterrows():
                self.answers[row["Question"]] = row["Answer"]
        else:
            df = pd.DataFrame(columns=["Question", "Answer"])
            df.to_csv(self.qa_file, index=False, encoding="utf-8")

    def process_questions(self, browser: WebDriver, locator: dict[str, tuple[Any, str]], wait: WebDriverWait) -> None:
        time.sleep(1)
        fields = browser.find_elements(locator["fields"][0], locator["fields"][1])
        for field in fields:
            question = field.text
            answer = self.ans_question(question.lower())

            if field.find_elements(locator["radio_select"][0], locator["radio_select"][1]):
                try:
                    radio = field.find_element(
                        By.CSS_SELECTOR,
                        f"input[type='radio'][value={answer}]"
                    )
                    browser.execute_script("arguments[0].click();", radio)
                except Exception as e:
                    log.error(e)
                    continue
                continue

            if field.find_elements(locator["multi_select"][0], locator["multi_select"][1]):
                try:
                    multi_select = field.find_element(locator["multi_select"][0], locator["multi_select"][1])
                    multi_select.send_keys(answer)
                except Exception as e:
                    log.error(e)
                    continue
                continue

            if field.find_elements(locator["text_select"][0], locator["text_select"][1]):
                try:
                    text_input = field.find_element(locator["text_select"][0], locator["text_select"][1])
                    text_input.send_keys(answer)
                except Exception as e:
                    log.error(e)
                    continue
                continue

            if "yes" in answer.lower() or "no" in answer.lower():
                try:
                    radio = field.find_element(
                        By.CSS_SELECTOR,
                        f"input[type='radio'][value={answer}]"
                    )
                    browser.execute_script("arguments[0].click();", radio)
                except Exception:
                    pass
                continue

            try:
                fallback_text = field.find_element(locator["text_select"][0], locator["text_select"][1])
                fallback_text.send_keys(answer)
            except Exception:
                pass

    def ans_question(self, question: str) -> str:
        answer = None
        if "how many" in question:
            answer = "1"
        elif "experience" in question:
            answer = "1"
        elif "sponsor" in question:
            answer = "No"
        elif "do you " in question:
            answer = "Yes"
        elif "have you " in question:
            answer = "Yes"
        elif "us citizen" in question:
            answer = "Yes"
        elif "are you " in question:
            answer = "Yes"
        elif "salary" in question:
            answer = self.salary
        elif "can you" in question:
            answer = "Yes"
        elif "gender" in question:
            answer = "Male"
        elif "race" in question:
            answer = "Wish not to answer"
        elif "lgbtq" in question:
            answer = "Wish not to answer"
        elif "ethnicity" in question:
            answer = "Wish not to answer"
        elif "nationality" in question:
            answer = "Wish not to answer"
        elif "government" in question:
            answer = "I do not wish to self-identify"
        elif "are you legally" in question:
            answer = "Yes"
        else:
            log.info("Not able to answer question automatically. Please provide answer")
            answer = "user provided"
            time.sleep(15)

        log.info("Answering question: %s with answer: %s", question, answer)

        if question not in self.answers:
            self.answers[question] = answer
            new_data = pd.DataFrame({"Question": [question], "Answer": [answer]})
            new_data.to_csv(self.qa_file, mode='a', header=False, index=False, encoding='utf-8')
            log.info("Appended to QA file: '%s' with answer: '%s'.", question, answer)

        return answer
