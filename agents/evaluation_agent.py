import logging
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from agents.agent_state import AgentState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluationAgent:
    all_metrics = {
        "Accuracy": "Accuracy - the degree to which the translation correctly conveys the meaning of the source text",
        "Fluency": "Fluency - the naturalness and readability of the translation in the target language",
        "Coherence": "Coherence - the logical flow and consistency of the translated text",
        "Translation Quality": "Translation Quality - the overall quality of the translation in terms of accuracy, fluency, style, keeping context and preserving the main idea",
        "Cultural Appropriateness": "Cultural Appropriateness - the degree to which the translation is appropriate and respectful of the target culture",
        "Contextual Idiom Accuracy": "Contextual Idiom Accuracy - the accuracy of idioms used in the translation in terms of context and meaning",
        "Style and Tone": "Style and Tone - the preservation of the original style and tone of the source text in the translation",
        "Terminology Consistency": "Terminology Consistency - the consistent use of terminology throughout the translation",
        "Preservation of Main Idea": "Preservation of Main Idea - the extent to which the main idea and key messages of the source text are preserved in the translation",
        "Punctuation and Formatting": "Punctuation and Formatting - the correctness of punctuation and adherence to formatting rules in the target language",
        "Emotional Impact": "Emotional Impact - the ability of the translation to evoke the same emotional response as the source text",
        "Localization": "Localization - the adaptation of the translation to fit the local context, including units of measurement, date formats, and currency",
        "Lexical Choice": "Lexical Choice - the appropriateness of word choice in the translation"
    }

    default_metrics = ["Accuracy", "Fluency", "Cultural Appropriateness", "Punctuation and Formatting"]

    def __init__(self, eval_model):
        self.eval_model = eval_model
        logger.info("EvaluationAgent initialized.")

    def evaluate_translation(self, state: AgentState, selected_metrics):
        try:
            translations = state['translations']
            initial_english_content = state['initial_english_content']
            eval_results = {}

            if not translations:
                logger.warning("No translations available for evaluation.")
                return {'evaluation': "No translations available for evaluation."}

            metrics = [{"name": name, "criteria": self.all_metrics[name]} for name in selected_metrics]
            logger.info(f"Evaluating translations with metrics: {selected_metrics}")

            for lang, translation in translations.items():
                translation_query = (
                    f"Translate the following JSON values into {lang} while preserving the main context, style, tone, and idea. "
                    f"If idioms are used, try to find an idiom with the same idea in the native language.\n"
                    f"{initial_english_content}"
                )

                test_case = LLMTestCase(input=translation_query, actual_output=translation)
                lang_eval_results = []

                for metric in metrics:
                    eval_metric = GEval(
                        name=metric["name"],
                        criteria=metric["criteria"],
                        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
                        model=self.eval_model
                    )

                    eval_metric.measure(test_case)
                    lang_eval_results.append({
                        "name": metric["name"],
                        "score": eval_metric.score,
                        "reason": eval_metric.reason
                    })
                    logger.debug(f"Metric '{metric['name']}' evaluated with score: {eval_metric.score}")

                eval_results[lang] = lang_eval_results
                logger.info(f"Evaluation completed for language: {lang}")

            return {'evaluation': eval_results}
        except Exception as e:
            logger.error(f"Error during translation evaluation: {e}")
            raise