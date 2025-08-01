import yaml

faq = {}

def load_faq_from_yaml(path=r"C:\Users\PMLS\Downloads\SkySuites Agent\app\vector_store\queries.yaml"):
    global faq
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
        for cat in raw["categories"]:
            cat_name = cat["name"]
            faq[cat_name] = {}
            for q in cat["questions"]:
                faq[cat_name][q["question"]] = q["answer"]

def get_answer_by_category_and_question(category: str, question: str) -> str | None:
    return faq.get(category, {}).get(question)
