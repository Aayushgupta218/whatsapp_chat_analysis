import re
import pandas as pd

def preprocess(data):
    try:
        pattern = r'(\d{1,2}/\d{1,2}/\d{2}),\s(\d{1,2}:\d{2})\s-\s'
        
        # Split messages by date pattern
        messages = re.split(pattern, data)[1:]
        dates = re.findall(pattern, data)
        
        if not messages:
            print("No messages found with the given pattern")
            return pd.DataFrame()
            
        processed_data = []
        for date_match, message in zip(dates, messages):
            date = f"{date_match[0]}, {date_match[1]}"
            processed_data.append([date, message.strip()])
                
        df = pd.DataFrame(processed_data, columns=['message_date', 'user_message'])
        
        try:
            df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M')
            df['only_date'] = df['message_date'].dt.date
        except Exception as e:
            print(f"Date parsing error: {e}")
            return pd.DataFrame()
        
        df['year'] = df['message_date'].dt.year
        df['month'] = df['message_date'].dt.strftime('%B')  # Month name
        df['day'] = df['message_date'].dt.day
        df['hour'] = df['message_date'].dt.hour
        df['minute'] = df['message_date'].dt.minute
        df['day_name'] = df['message_date'].dt.day_name()
        
        # Separate users and messages
        users = []
        msgs = []
        
        for message in df['user_message']:
            entry = re.split('([\w\W]+?):\s', message)
            if len(entry) > 2:
                users.append(entry[1])
                msgs.append(entry[2])
            else:
                users.append('group_notification')
                msgs.append(entry[0])
                
        df['user'] = users
        df['message'] = msgs
        df.drop(columns=['user_message'], inplace=True)
        
        return df

    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        return pd.DataFrame()