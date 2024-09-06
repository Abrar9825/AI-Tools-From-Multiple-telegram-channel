from transformers import pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
text_to_classify = "I am Danceing"
labels = ["travel", "dance", "cook","others"]
result = classifier(text_to_classify, candidate_labels=labels)
labels = result['labels']
scores = result['scores']
max_score_index = scores.index(max(scores))
highest_score_label = labels[max_score_index]
print("The label with the highest score is:", highest_score_label)
