import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from models.chatbot import Chatbot


def evaluate(dataset_path: Path, data_dir: Path) -> int:
    chatbot = Chatbot(str(data_dir))
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    rows = data["test_data"]

    correct = 0
    by_intent: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    confusions: Counter[tuple[str, str]] = Counter()
    mistakes = []

    for item in rows:
        text = item["user_input"]
        expected = item["intent"]
        result = chatbot.get_response(text)
        predicted = result["intent"]
        ok = predicted == expected

        correct += int(ok)
        by_intent[expected][0] += int(ok)
        by_intent[expected][1] += 1

        if not ok:
            confusions[(expected, predicted)] += 1
            mistakes.append((text, expected, predicted, result["confidence"], result["source"]))

    total = len(rows)
    print(f"Accuracy: {correct}/{total} = {correct / total * 100:.1f}%")

    print("\nWorst intents:")
    for intent, (ok_count, intent_total) in sorted(
        by_intent.items(),
        key=lambda item: (item[1][0] / item[1][1], item[0]),
    )[:12]:
        print(f"- {intent}: {ok_count}/{intent_total} = {ok_count / intent_total * 100:.0f}%")

    print("\nTop confusions:")
    for (expected, predicted), count in confusions.most_common(15):
        print(f"- {expected} -> {predicted}: {count}")

    print("\nExample mistakes:")
    for text, expected, predicted, confidence, source in mistakes[:20]:
        print(
            f"- {text} | expected={expected} predicted={predicted} "
            f"conf={confidence:.2f} source={source}"
        )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate chatbot intent model on test_data.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("../notebooks/task_management_chatbot_dataset.json"),
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    return evaluate(args.dataset, args.data_dir)


if __name__ == "__main__":
    raise SystemExit(main())
