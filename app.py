import nltk
nltk.download('vader_lexicon')
import sentiment
import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties
from pathlib import Path
import warnings
import sentiment


emoji_font = FontProperties(fname=r'C:\Windows\Fonts\seguiemj.ttf')
plt.rcParams['font.family'] = 'Segoe UI Emoji'
warnings.filterwarnings('ignore', category=UserWarning)
plt.style.use('default')

st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stTitle { font-weight: bold; }
    .stPlot > div > img { max-width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("WhatsApp Chat Analyzer")

st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1>👋 Welcome to WhatsApp Chat Analyzer!</h1>
    </div>
    """, unsafe_allow_html=True)

with st.expander("ℹ️ How to Use This Tool", expanded=True):
    st.markdown("""
    ### Steps to Analyze Your WhatsApp Chat:
    
    1. **Export Your Chat:**
        * Open WhatsApp on your phone
        * Go to the chat you want to analyze
        * Tap ⋮ (three dots) > More > Export chat
        * Choose 'Without Media'
        * Send the exported file to your computer
    
    2. **Upload and Analyze:**
        * Upload your chat file using the sidebar
        * Select a user from the dropdown (or keep 'Overall')
        * Click 'Analyze Chat' to see the results
    
    ### What You'll Get:
    * 📊 Total messages, words, media, and links
    * 📅 Monthly and daily activity patterns
    * 🕒 Weekly activity heatmap
    * 👥 Most active users (for group chats)
    * 🔤 Word cloud and common words
    * 😀 Emoji analysis
    
    ### Privacy Note:
    Your chat data is processed locally and is not stored anywhere.
    """)

st.markdown("---")

st.sidebar.markdown("### 📁 Upload Chat File")

uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp chat export file", type=['txt'])

if uploaded_file is not None:
    try:
        with st.spinner('Reading file...'):
            bytes_data = uploaded_file.getvalue()
            try:
                data = bytes_data.decode("utf-8")
            except UnicodeDecodeError:
                data = bytes_data.decode("utf-16")

        with st.spinner('Processing chat data...'):
            df = preprocessor.preprocess(data)
            
        if df is None or df.empty:
            st.error("No valid chat data could be extracted.")
            st.info("Please make sure you're uploading a valid WhatsApp chat export file.")
            st.stop()
        
        st.success(f"Successfully processed {len(df)} messages!")

        user_list = df['user'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.sidebar.selectbox("Show analysis for:", user_list)

        if st.sidebar.button("Analyze Chat"):
            with st.spinner("Analyzing chat data..."):
                try:
                    # Stats Area
                    with st.container():
                        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
                        st.title("Chat Statistics")
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.header("Total Messages")
                            st.title(f"{num_messages:,}")
                        with col2:
                            st.header("Total Words")
                            st.title(f"{words:,}")
                        with col3:
                            st.header("Media Shared")
                            st.title(f"{num_media_messages:,}")
                        with col4:
                            st.header("Links Shared")
                            st.title(f"{num_links:,}")

                    # Timeline Analysis
                    with st.container():
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.title("Monthly Activity")
                            timeline = helper.monthly_timeline(selected_user, df)
                            if not timeline.empty:
                                fig, ax = plt.subplots(figsize=(10, 4))
                                ax.plot(timeline['time'], timeline['message'], color='green', linewidth=2)
                                plt.xticks(rotation=45)
                                plt.tight_layout()
                                st.pyplot(fig)
                                
                        with col2:
                            st.title("Daily Activity")
                            daily_timeline = helper.daily_timeline(selected_user, df)
                            if not daily_timeline.empty:
                                fig, ax = plt.subplots(figsize=(10, 4))
                                ax.plot(daily_timeline['only_date'], daily_timeline['message'], 
                                      color='blue', linewidth=2)
                                plt.xticks(rotation=45)
                                plt.tight_layout()
                                st.pyplot(fig)

                    # Activity Patterns
                    with st.container():
                        st.title("Activity Patterns")
                        col1, col2 = st.columns(2)

                        with col1:
                            st.header("Weekly Activity")
                            busy_day = helper.week_activity_map(selected_user, df)
                            fig, ax = plt.subplots(figsize=(10, 4))
                            ax.bar(busy_day.index, busy_day.values, color='purple')
                            plt.xticks(rotation=45)
                            plt.tight_layout()
                            st.pyplot(fig)

                        with col2:
                            st.header("Monthly Activity")
                            busy_month = helper.month_activity_map(selected_user, df)
                            fig, ax = plt.subplots(figsize=(10, 4))
                            ax.bar(busy_month.index, busy_month.values, color='orange')
                            plt.xticks(rotation=45)
                            plt.tight_layout()
                            st.pyplot(fig)

                    # Heatmap
                    with st.container():
                        st.title("Weekly Activity Heatmap")
                        user_heatmap = helper.activity_heatmap(selected_user, df)
                        if user_heatmap.size > 0:
                            fig, ax = plt.subplots(figsize=(12, 6))
                            sns.heatmap(user_heatmap, cmap='YlOrRd', ax=ax)
                            plt.tight_layout()
                            st.pyplot(fig)

                    # User Analysis
                    if selected_user == 'Overall':
                        with st.container():
                            st.title('Most Active Users')
                            user_stats, percent_df = helper.most_busy_users(df)
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                fig, ax = plt.subplots(figsize=(10, 4))
                                ax.bar(user_stats.index, user_stats.values, color='red')
                                plt.xticks(rotation=45)
                                plt.tight_layout()
                                st.pyplot(fig)
                            with col2:
                                st.dataframe(percent_df.style.format({'Percent': '{:.2f}%'}))

                    # Word Analysis
                    with st.container():
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.title("Word Cloud")
                            word_cloud = helper.create_wordcloud(selected_user, df)
                            if word_cloud:
                                fig, ax = plt.subplots(figsize=(10, 10))
                                ax.imshow(word_cloud)
                                plt.axis('off')
                                st.pyplot(fig)
                                
                        with col2:
                            st.title("Most Common Words")
                            most_common_df = helper.most_common_words(selected_user, df)
                            if not most_common_df.empty:
                                fig, ax = plt.subplots(figsize=(10, 8))
                                ax.barh(most_common_df[0], most_common_df[1])
                                plt.xticks(rotation=45)
                                plt.tight_layout()
                                st.pyplot(fig)

                    # Emoji Analysis
                    with st.container():
                        st.title("Emoji Analysis")
                        emoji_df = helper.emoji_helper(selected_user, df)
                        if not emoji_df.empty:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("### Most Used Emojis")
                                formatted_df = emoji_df.copy()
                                formatted_df.columns = ['Emoji', 'Count']
                                st.dataframe(
                                    formatted_df,
                                    height=400,
                                    use_container_width=True
                                )
                     # Sentiment Analysis
                    with st.container():
                          st.title("Sentiment Analysis")

                          df_sentiment, sentiment_counts = sentiment.analyze_sentiment(df, selected_user)

                          if selected_user == 'Overall':
                            with st.container():
                              st.markdown("### Sentiment by User")
                              sentiment_by_user = df_sentiment.groupby('user')['sentiment'].value_counts().unstack().fillna(0)
                              st.dataframe(sentiment_by_user.style.format(precision=0))


                          if not sentiment_counts.empty:
                               col1, col2 = st.columns(2)

                               with col1:
                                 st.markdown("### Sentiment Distribution")
                                 fig, ax = plt.subplots()
                                 ax.pie(
                                    sentiment_counts['Count'], 
                                    labels=sentiment_counts['Sentiment'], 
                                    autopct='%1.1f%%', 
                                    startangle=140,
                                    colors=['green', 'red', 'grey']
                                )
                                 ax.axis('equal')
                                 st.pyplot(fig)

                               with col2:
                                 st.markdown("### Sentiment Counts Table")
                                 st.dataframe(sentiment_counts)

                          else:
                            st.info("Not enough text data to analyze sentiment.")


                    st.success("Analysis completed successfully!")
                    
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    st.info("Please try again with a different chat file")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.info("Please make sure you're uploading a valid WhatsApp chat export file")
