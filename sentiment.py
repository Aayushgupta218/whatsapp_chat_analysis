from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd

# Initialize VADER once
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(df, selected_user='Overall'):
    try:
        # Filter by user if needed
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        # Copy to avoid changing original DataFrame
        df_copy = df.copy()
        df_copy['message'] = df_copy['message'].astype(str)

        # Compute sentiment scores
        df_copy['sentiment_score'] = df_copy['message'].apply(lambda text: sia.polarity_scores(text)['compound'])

        # Classify as Positive / Negative / Neutral
        def classify(score):
            if score >= 0.05:
                return 'Positive'
            elif score <= -0.05:
                return 'Negative'
            else:
                return 'Neutral'

        df_copy['sentiment'] = df_copy['sentiment_score'].apply(classify)

        # Aggregate counts
        sentiment_counts = df_copy['sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']

        return df_copy, sentiment_counts

    except Exception as e:
        print(f"Error in analyze_sentiment: {e}")
        return df, pd.DataFrame(columns=['Sentiment', 'Count'])
