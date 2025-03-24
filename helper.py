from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        num_messages = df.shape[0]

        # Fetch total number of words
        words = []
        for message in df['message']:
            if isinstance(message, str):
                words.extend(message.split())

        # Fetch number of media messages
        num_media_messages = df[df['message'].str.contains('<Media omitted>', na=False)].shape[0]

        # Fetch number of links shared
        links = []
        for message in df['message']:
            if isinstance(message, str):
                links.extend(extract.find_urls(message))

        return num_messages, len(words), num_media_messages, len(links)
    except Exception as e:
        print(f"Error in fetch_stats: {e}")
        return 0, 0, 0, 0

def most_busy_users(df):
    try:
        x = df['user'].value_counts().head()
        df_percent = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
        df_percent.columns = ['name', 'percent']
        return x, df_percent
    except Exception as e:
        print(f"Error in most_busy_users: {e}")
        return pd.Series(), pd.DataFrame()

def create_wordcloud(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        # Filter messages
        temp = df[df['user'] != 'group_notification']
        temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]

        # Load stop words
        try:
            with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
                stop_words = set(f.read().splitlines())
        except:
            stop_words = set()

        def remove_stop_words(message):
            if not isinstance(message, str):
                return ""
            return " ".join([word for word in message.lower().split() if word not in stop_words])

        wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
        temp['message'] = temp['message'].apply(remove_stop_words)
        
        if temp['message'].str.cat(sep=" ").strip():
            return wc.generate(temp['message'].str.cat(sep=" "))
        return None
    except Exception as e:
        print(f"Error in create_wordcloud: {e}")
        return None

def most_common_words(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        # Load stop words
        try:
            with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
                stop_words = set(f.read().splitlines())
        except:
            stop_words = set()

        # Filter messages
        temp = df[df['user'] != 'group_notification']
        temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]

        words = []
        for message in temp['message']:
            if isinstance(message, str):
                words.extend([word for word in message.lower().split() if word not in stop_words])

        return pd.DataFrame(Counter(words).most_common(20))
    except Exception as e:
        print(f"Error in most_common_words: {e}")
        return pd.DataFrame()

def emoji_helper(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        emojis = []
        for message in df['message']:
            if isinstance(message, str):
                emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

        emoji_dict = Counter(emojis)
        if emoji_dict:
            return pd.DataFrame(emoji_dict.most_common(), columns=['Emoji', 'Count'])
        return pd.DataFrame(columns=['Emoji', 'Count'])
    except Exception as e:
        print(f"Error in emoji_helper: {e}")
        return pd.DataFrame()

def monthly_timeline(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        timeline = df.groupby(['year', 'month']).count()['message'].reset_index()
        timeline['time'] = timeline.apply(lambda x: f"{x['month']}-{x['year']}", axis=1)
        return timeline
    except Exception as e:
        print(f"Error in monthly_timeline: {e}")
        return pd.DataFrame()

def daily_timeline(selected_user, df):
    try:
        if 'only_date' not in df.columns:
            print("Missing 'only_date' column")
            return pd.DataFrame()
            
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
            
        daily_timeline = df.groupby('only_date').count()['message'].reset_index()
        return daily_timeline
    except Exception as e:
        print(f"Error in daily_timeline: {e}")
        return pd.DataFrame()

def week_activity_map(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
        return df['day_name'].value_counts()
    except Exception as e:
        print(f"Error in week_activity_map: {e}")
        return pd.Series()

def month_activity_map(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
        return df['month'].value_counts()
    except Exception as e:
        print(f"Error in month_activity_map: {e}")
        return pd.Series()

def activity_heatmap(selected_user, df):
    try:
        df_copy = df.copy()
        
        if selected_user != 'Overall':
            df_copy = df_copy[df_copy['user'] == selected_user]
        
        df_copy.loc[:, 'period'] = df_copy['message_date'].dt.hour

        user_heatmap = df_copy.pivot_table(
            index='day_name', 
            columns='period',
            values='message',
            aggfunc='count'
        ).fillna(0)
        
        return user_heatmap
    
    except Exception as e:
        print(f"Error in activity_heatmap: {e}")
        return pd.DataFrame()