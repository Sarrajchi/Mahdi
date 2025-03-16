import oracledb
import streamlit as st


# تابع برای خواندن رکوردها از پایگاه داده
def fetch_records():
    dsn = oracledb.makedsn('172.16.6.67', 1539, service_name='adadb')
    cursor = None
    connection = None
    results = []

    try:
        connection = oracledb.connect(user='report', password='report', dsn=dsn)
        cursor = connection.cursor()

        # خواندن رکوردها
        cursor.execute("""  
            SELECT ti.ID, ti.URL, t2.TERMINAL_ID, m.MERCHANT_NAME FROM TRANSACTION.TERMINAL t2  
            LEFT JOIN TRANSACTION.MERCHANT m ON m.ID = t2.MERCHANT_ID  
            LEFT JOIN TRANSACTION.MERCHANT_UPDATE_HISTORY muh ON muh.MERCHANT_ID = m.ID  
            LEFT JOIN TRANSACTION.TRANSACTION t1 ON t1.TERMINAL_ID1 = t2.ID   
            LEFT JOIN TRANSACTION.TRANSACTION_IMAGE ti ON ti.TRANSACTION_ID = t1.ID  
            WHERE m.STATUS = 'C' AND m.CHANEL_ID = 5 AND   
            muh.CREATION_DATE > SYSDATE - 30  
            AND ti.URL IS NOT NULL   
            --AND ti.ACTIVE = 'Y'  
            --AND m.APPROVE = 0  
            AND ti.TYPE_ID = 1  
        """)

        results = cursor.fetchall()  # ذخیره نتایج
    except oracledb.DatabaseError as e:
        error, = e.args
        st.error(f"خطا در پایگاه داده: {error.message}")
    except Exception as e:
        st.error(f"خطا: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return results

# بارگذاری رکوردها
records = fetch_records()

# متغیر برای نگه‌داشتن اندیس فعلی
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
# بارگذاری فونت فارسی
st.markdown(
    """  
    <style>  
    @font-face {  
        font-family: 'Tahoma';  
        src: url('data:font/truetype;charset=utf-8;base64,[YOUR_BASE64_ENCODED_FONT]');  
    }  
    .farsi-font {  
        font-family: 'Tahoma', sans-serif;  
        text-align: left;  
    }  
    </style>  
    """,
    unsafe_allow_html=True
)

# نمایش محتوا
if records:
    record = records[st.session_state.current_index]
    image_filename = record[1]
    TERMINAL_ID = record[2]
    merchant_name = record[3]
    base_url = "https://media.asr24.com/static/Transaction_server/"
    full_url = base_url + image_filename

    # نمایش ID تصویر در بالای تصویر
    # st.markdown(f"<h3 style='text-align: center;'>Image ID: {record[0]}</h3>", unsafe_allow_html=True)
    # نمایش اطلاعات در دو ردیف
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<h6 style='text-align: left;'>Image ID: {record[0]}</h6>", unsafe_allow_html=True)
        st.markdown(f"<h7 class='farsi-font'>Merchant Name: {merchant_name}</h7>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<h6 style='text-align: left;'>URL: {image_filename}</h6>", unsafe_allow_html=True)
        st.markdown(f"<h7 class='farsi-font'>Terminal ID: {TERMINAL_ID}</h7>", unsafe_allow_html=True)

    # ایجاد دو ستون برای دکمه‌های Next و Back
    col3, col4, col5 = st.columns([1, 4, 1])  # تنظیم اندازه ستون‌ها به نسبت یکسان
    with col3:  # ستون چپ
        if st.button("Back"):
            # برو به رکورد قبلی
            st.session_state.current_index -= 1
            if st.session_state.current_index < 0:
                st.session_state.current_index = len(records) - 1  # حلقه بزنید به آخر
    with col5:  # ستون راست
        # با استفاده از CSS، محتوا را در سمت راست تراز کنید
        # st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
        # دکمه Next در پالای تصویر
        if st.button("Next"):
            # برو به رکورد بعدی
            st.session_state.current_index += 1
            if st.session_state.current_index >= len(records):
                st.session_state.current_index = 0  # حلقه به اول
        # st.markdown("</div>", unsafe_allow_html=True)

    # نمایش تصویر
    # st.image(full_url, use_column_width=True)
    image_html = f'<a href="{full_url}" target="_blank"><img src="{full_url}" width="100%"></a>'
    st.markdown(image_html, unsafe_allow_html=True)
    # استفاده از container برای فضای بزرگتر
    # st.markdown("<h3 style='text-align: center;'>تصویر:</h3>", unsafe_allow_html=True)
    # st.image(full_url, use_column_width='always', caption='Image Preview', width=800)  # تغییر عرض به 800 پیکسل
else:
    st.info("هیچ داده‌ای یافت نشد.")