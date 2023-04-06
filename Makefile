lib:
	pip install -r requirements.txt
	pip install ./src/lib/

headline-retrieve:
	python "src/1. Data Retrieval/headline_crawler.py"

reply-retrieve:
	python "src/1. Data Retrieval/reply_crawler.py"

tensorboard:
	tensorboard --logdir "src\4. Modelling and Evaluation\tensorboard\$(MODEL)"