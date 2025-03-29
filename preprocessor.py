import re
import pandas as pd

def preprocess(data):
    try:
        patterns = [
            r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s',
            r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2})\s-\s',
            r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}\s(?:AM|PM|am|pm))\s-\s',
            r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\]',
            r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2}\s(?:AM|PM|am|pm))\]'
        ]

        for pattern in patterns:
            messages = re.split(pattern, data)[1:]
            dates = re.findall(pattern, data)
            
            if messages and dates:
                break
        
        if not messages:
            print("No messages found with any of the supported patterns")
            return pd.DataFrame()
            
        processed_data = []
        for date_match, time_match, message in zip(dates[::2], dates[1::2], messages[2::2]):
            datetime_str = f"{date_match}, {time_match}"
            processed_data.append([datetime_str, message.strip()])
                
        df = pd.DataFrame(processed_data, columns=['message_date', 'user_message'])
        
        datetime_formats = [
            '%d/%m/%y, %H:%M',
            '%d/%m/%Y, %H:%M',
            '%d/%m/%y, %H:%M:%S',
            '%d/%m/%Y, %H:%M:%S',
            '%d/%m/%y, %I:%M %p',
            '%d/%m/%Y, %I:%M %p',
            '%d/%m/%y, %I:%M:%S %p',
            '%d/%m/%Y, %I:%M:%S %p'
        ]

        for date_format in datetime_formats:
            try:
                df['message_date'] = pd.to_datetime(df['message_date'], format=date_format)
                df['only_date'] = df['message_date'].dt.date
                break
            except ValueError:
                continue
        
        if 'only_date' not in df.columns:
            print("Could not parse dates with any known format")
            return pd.DataFrame()

        df['year'] = df['message_date'].dt.year
        df['month'] = df['message_date'].dt.strftime('%B')
        df['day'] = df['message_date'].dt.day
        df['hour'] = df['message_date'].dt.hour
        df['minute'] = df['message_date'].dt.minute
        df['day_name'] = df['message_date'].dt.day_name()
        
        users = []
        msgs = []
        
        for message in df['user_message']:
            entry = re.split(r'([^:]+?):\s', message, maxsplit=1)
            if len(entry) > 2:
                users.append(entry[1].strip())
                msgs.append(entry[2].strip())
            else:
                users.append('group_notification')
                msgs.append(entry[0].strip())
                
        df['user'] = users
        df['message'] = msgs
        df.drop(columns=['user_message'], inplace=True)
        
        return df

    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        return pd.DataFrame()