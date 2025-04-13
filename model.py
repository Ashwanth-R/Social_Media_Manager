# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
# from sklearn.model_selection import train_test_split

# def load_model():
#     kaggle_df = pd.read_csv('train.csv', encoding='latin1')
#     kaggle_df = kaggle_df[['text', 'sentiment']].dropna()
#     label_mapping = {'positive': 1, 'negative': 0, 'neutral': 2}
#     reverse_label_mapping = {1: 'Positive', 0: 'Negative', 2: 'Neutral'}
#     kaggle_df['sentiment'] = kaggle_df['sentiment'].map(label_mapping)
#     kaggle_df = kaggle_df.dropna()

#     vectorizer = TfidfVectorizer(max_features=1000)
#     X = vectorizer.fit_transform(kaggle_df['text'])
#     y = kaggle_df['sentiment']

#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#     model = LogisticRegression(max_iter=1000)
#     model.fit(X_train, y_train)

#     return model, vectorizer, reverse_label_mapping, X_test, y_test

# def perform_sentiment_analysis(comment_texts, model, vectorizer, reverse_label_mapping):
#     X_new = vectorizer.transform(comment_texts)
#     predicted_sentiments = model.predict(X_new)
#     return [reverse_label_mapping[sentiment] for sentiment in predicted_sentiments]

# def evaluate_model(y_test, y_pred):
#     accuracy = accuracy_score(y_test, y_pred)
#     f1 = f1_score(y_test, y_pred, average='weighted')
#     precision = precision_score(y_test, y_pred, average='weighted')
#     recall = recall_score(y_test, y_pred, average='weighted')
#     return accuracy, f1, precision, recall



import pickle
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score

def load_model():
    # Load the pre-trained model and components from pickle files
    with open('sentiment_model_svm.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    
    with open('vectorizer_svm.pkl', 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)
    
    with open('label_mapping_svm.pkl', 'rb') as mapping_file:
        reverse_label_mapping = pickle.load(mapping_file)
    
    with open('metrics.pkl', 'rb') as metrics_file:
        metrics = pickle.load(metrics_file)
    
    return model, vectorizer, reverse_label_mapping, metrics

def perform_sentiment_analysis(comment_texts, model, vectorizer, reverse_label_mapping):
    # Handle empty input case
    if not comment_texts or len(comment_texts) == 0:
        return []
    
    # Handle different types of input (single string vs list)
    if isinstance(comment_texts, str):
        comment_texts = [comment_texts]
    
    try:
        # Transform the text using the pre-trained vectorizer
        X_new = vectorizer.transform(comment_texts)
        
        # Predict sentiments
        predicted_sentiments = model.predict(X_new)
        
        # Map numeric predictions back to text labels
        return [reverse_label_mapping.get(int(sentiment), "Unknown") for sentiment in predicted_sentiments]
    except Exception as e:
        print(f"Error during sentiment analysis: {str(e)}")
        return ["Error"] * len(comment_texts)

