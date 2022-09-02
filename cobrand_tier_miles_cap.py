import streamlit as st 
import pandas as pd
import numpy as np
from PIL import Image

st.session_state

st.write(
    """
# 📊 Cobrand Tier Miles - add 50k cap
"""
)



# st.info("ABCD is info")
# st.warning("ABCD is warning")
# st.error("ABCD is error")
# st.success("ABCD is success")


st.session_state.uploaded_file_bool = st.session_state.get('uploaded_file_bool', False)


col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Select weekly transaction file")
    if uploaded_file is not None:
        transactions = pd.read_csv(uploaded_file, thousands=',')
        # st.write("Your file has " + str(transactions.shape[0]) + " rows and " + str(transactions.shape[1]) + " columns")
        st.metric("ROWS", transactions.shape[0])
        st.metric("COLUMNS", transactions.shape[1])

        st.write(transactions.head())
       #opening the image

#         image = Image.open("C:/Users/s428545/OneDrive - Emirates Group/Documents/ipython_stuff/skywards-jira/skya1603/master/images/double-chevron.png")
#         st.image(image, width=100)


with col2:
    rolling_tm_csv = st.file_uploader("Select tier miles rolling total file")
    if rolling_tm_csv is not None:
        # Can be used wherever a "file-like" object is accepted:
        df = pd.read_csv(rolling_tm_csv)
                
        st.metric("ROWS", df.shape[0])
        st.metric("COLUMNS", df.shape[1])

        st.write(df.head())     

#         image = Image.open("C:/Users/s428545/OneDrive - Emirates Group/Documents/ipython_stuff/skywards-jira/skya1603/master/images/double-chevron.png")
#         st.image(image, width=100)


st.session_state.bool_val = st.session_state.get('bool_val', False)


def testing_callback():
    st.session_state.bool_val = True

if uploaded_file is not None and rolling_tm_csv is not None:
  st.button("Abracadabra", on_click=testing_callback)

if st.session_state.bool_val:
    st.write("This callback works")
    



    # Can we wrap the rest of this into a function??

    transactions.columns = [xx.lower().replace(' ', '_') for xx in transactions.columns.tolist()]

    transactions.sort_values(['membership_no', 'miles'], ascending=True, inplace=True)

    transactions.reset_index(drop=True, inplace=True)

    # st.write(transactions.head())


    # CONVERT SKYWARDS MILES TO TIER MILES 4:1 ... and round down
    transactions.miles = transactions.miles.div(4).round()




    # working on df file

    # rename columns and format
    df.columns = [xx.lower().replace(' ', '_') for xx in df.columns.tolist()]


    # do we need this?
    # st.write(df.isnull().sum())




    # Calculate balance tier miles
    df['balance'] = 50000 - df.total_tier_miles
    # set minimum balance to 0
    df.balance = [xx if xx > 0 else 0 for xx in df.balance.tolist()]





    merged = transactions.merge(df, on='membership_no', how='left')


    merged.total_tier_miles.fillna(0, inplace=True)
    merged.balance.fillna(50000, inplace=True)




    tmp = merged.groupby('membership_no', as_index=False).agg({'partner_code' : 'count', 'miles' : 'sum', 'balance' : 'min'})





    def calculate_miles_to_be_posted(onemem):
        starting_balance = onemem.balance.min()
        new_miles_list = list()

        miles_tx = onemem.miles.tolist()
        miles_tx = onemem.miles

        for xx in miles_tx:
            if (xx < starting_balance and starting_balance != 0):
                new_miles_list.append(xx)
                starting_balance = starting_balance - xx
            elif (xx >= starting_balance and starting_balance != 0):
                new_miles_list.append(starting_balance)
                starting_balance = 0
            elif starting_balance == 0:
                new_miles_list.append(0)
        
        return pd.DataFrame(new_miles_list)
    #     return pd.DataFrame(onemem.miles)



    tmp = pd.concat([merged, merged.groupby(['membership_no']).cumcount()], axis=1).rename(columns={0 : 'fake_index'})



    tmp.set_index(['membership_no', 'fake_index'], inplace=True)




    final = pd.concat([tmp   ,   merged.groupby(['membership_no'], as_index=True).apply(calculate_miles_to_be_posted).rename(columns={0 : "miles_to_be_posted"})   ], axis=1)



    # Remove rows where "miles to be posted" is 0
    final = final[final.miles_to_be_posted > 0]


    final.reset_index(inplace=True)


    final.dropna(subset=['membership_no'], inplace=True)


    # final.membership_no.astype('int').astype('str') + "~SWDS~" + final.partner_code + '~TIER~~~~~' + final.miles_to_be_posted.astype('int').astype('str') + '~' + pd.to_datetime('today').normalize().strftime('%d%b%Y')



    df_asstring = pd.DataFrame(final.membership_no.astype('int').astype('str') + "~SWDS~" + final.partner_code + '~TIER~~~~~' + final.miles_to_be_posted.astype('int').astype('str') + '~' + pd.to_datetime('today').normalize().strftime('%d%b%Y'))


    st.write("DONE")

    st.balloons()



else:
    st.stop()



@st.cache
def convert_df(df):
   return df.to_csv(index=False, header=False)

csv = convert_df(df_asstring)  

st.download_button(
   "Click here to Download",
   csv,
   "SWDS_TIER.txt",
   "text/csv",
   key='download_csv_button'
)
